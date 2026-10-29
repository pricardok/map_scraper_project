# src/locations.py
"""Localidades (UF, cidade e bairros) com cache local em DuckDB.

Fonte oficial: API de Localidades do IBGE.
    estados    -> /api/v1/localidades/estados
    municipios -> /api/v1/localidades/municipios
    distritos  -> /api/v1/localidades/distritos

Com LOCALIDADES_USAR_CACHE=true (padrão), a base local é consultada primeiro;
só vai para a rede o que ainda não existe no banco. Com a flag false, os dados
são sempre buscados na API (e a base local é atualizada com o resultado).

Observação: os "distritos" do IBGE são divisões administrativas e, em muitos
municípios, resumem-se à própria sede. Quando não há distritos suficientes,
a lista é complementada com bairros do OpenStreetMap (Nominatim + Overpass).
"""
import os
import time
import unicodedata

import pandas as pd
import requests

from src import localidades_db
from src.config import env_int, str_para_bool

IBGE_API = "https://servicodados.ibge.gov.br/api/v1/localidades"

# User-Agent identificável é exigido pela política de uso do Nominatim.
HEADERS = {"User-Agent": "map-scraper-lead-prospecting/1.0 (prospeccao.mapscraper@gmail.com)"}

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# Se true: consulta o banco antes da API. Se false: sempre busca na API.
USAR_CACHE = str_para_bool(os.environ.get("LOCALIDADES_USAR_CACHE"), padrao=True)

# Se false: NUNCA grava na base local (nem cria tabelas). Funciona como
# "somente leitura": o banco é consultado, mas nada é alterado.
SALVAR = str_para_bool(os.environ.get("LOCALIDADES_SALVAR"), padrao=True)

# Reflete a flag no módulo de acesso ao banco (controla a criação das tabelas).
localidades_db.CRIAR_TABELAS = SALVAR

# Quantidade mínima de distritos úteis para não precisar do OpenStreetMap.
# Abaixo disso, a cidade é complementada com bairros do OSM.
MIN_BAIRROS = max(1, env_int("LOCALIDADES_MIN_BAIRROS", 3))

# Pausa (segundos) entre cidades no aquecimento por UF, aplicada apenas quando o
# OpenStreetMap foi consultado (política de uso do Nominatim: 1 req/s).
AQUECER_PAUSA_PADRAO = max(0, env_int("AQUECER_PAUSA_SEGUNDOS", 2))

_avisou_cache_indisponivel = False
_avisou_sem_gravacao = False


def _cache(funcao, *args, **kwargs):
    """Executa uma operação na base local, tolerando banco travado/indisponível."""
    global _avisou_cache_indisponivel
    try:
        return funcao(*args, **kwargs)
    except localidades_db.CacheIndisponivel as e:
        if not _avisou_cache_indisponivel:
            print(f"  Aviso: base local de localidades indisponível ({e}).")
            print("         Seguindo apenas com as APIs (IBGE/OSM).")
            _avisou_cache_indisponivel = True
        return None


def _salvar(funcao, *args, **kwargs):
    """Grava na base local, respeitando LOCALIDADES_SALVAR=false."""
    global _avisou_sem_gravacao
    if not SALVAR:
        if not _avisou_sem_gravacao:
            print("  LOCALIDADES_SALVAR=false: a base local não será alterada.")
            _avisou_sem_gravacao = True
        return None
    return _cache(funcao, *args, **kwargs)


# ---------------------------------------------------------------------------
# IBGE
# ---------------------------------------------------------------------------
def _get_json(url, params=None, timeout=60, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(url, params=params, timeout=timeout, headers=HEADERS)
            resposta.raise_for_status()
            return resposta.json()
        except Exception as e:
            print(f"  IBGE indisponível (tentativa {tentativa}/{tentativas}): {type(e).__name__}")
            if tentativa < tentativas:
                time.sleep(1.5 * tentativa)
    return None


def _baixar_estados():
    dados = _get_json(f"{IBGE_API}/estados", params={"orderBy": "nome"}, timeout=30)
    if not dados:
        return None
    return [{"uf": e["sigla"], "nome": e["nome"]} for e in dados]


def _uf_do_municipio(municipio):
    try:
        return municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
    except (KeyError, TypeError):
        try:
            return municipio["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
        except (KeyError, TypeError):
            return None


def _baixar_municipios(uf=None):
    url = f"{IBGE_API}/estados/{uf}/municipios" if uf else f"{IBGE_API}/municipios"
    dados = _get_json(url, params={"orderBy": "nome"})
    if not dados:
        return None

    registros = []
    for municipio in dados:
        sigla = uf or _uf_do_municipio(municipio)
        if not sigla:
            continue
        registros.append({
            "id_municipio": municipio["id"],
            "nome": municipio["nome"],
            "uf": sigla,
        })
    return registros


def _baixar_distritos(id_municipio=None):
    url = (f"{IBGE_API}/municipios/{id_municipio}/distritos"
           if id_municipio else f"{IBGE_API}/distritos")
    dados = _get_json(url)
    if not dados:
        return None

    registros = []
    for distrito in dados:
        municipio = distrito.get("municipio") or {}
        registros.append({
            "id_distrito": distrito.get("id"),
            "nome": (distrito.get("nome") or "").strip(),
            "id_municipio": municipio.get("id"),
        })
    return [r for r in registros if r["id_municipio"] and r["nome"]]


_municipios_memoria = {}


def _municipios_da_uf(uf):
    """Lista de municípios da UF, memorizada na execução para não baixar duas vezes."""
    if uf not in _municipios_memoria:
        print(f"  Baixando a lista de municípios de {uf} do IBGE...")
        municipios = _baixar_municipios(uf)
        if municipios is None:
            return None
        _municipios_memoria[uf] = municipios
    return _municipios_memoria[uf]


# ---------------------------------------------------------------------------
# OpenStreetMap (fallback de bairros)
# ---------------------------------------------------------------------------
def _obter_bbox_cidade(cidade, uf):
    """Retorna (sul, norte, oeste, leste) da cidade via Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "q": f"{cidade}, {uf}, Brazil", "limit": 1}
    try:
        resposta = requests.get(url, params=params, timeout=15, headers=HEADERS)
        resposta.raise_for_status()
        resultados = resposta.json()
        if not resultados:
            return None
        bb = resultados[0].get("boundingbox")
        if not bb or len(bb) != 4:
            return None
        sul, norte, oeste, leste = (float(v) for v in bb)
        return (sul, norte, oeste, leste)
    except Exception as e:
        print(f"Erro ao localizar a cidade no Nominatim: {e}")
        return None


def _consultar_overpass(query):
    """Tenta a consulta em vários espelhos do Overpass, com retry e backoff.

    Retorna o JSON da resposta, ou None quando nenhum espelho respondeu
    (serviço indisponível) — o que é diferente de responder vazio.
    """
    for endpoint in OVERPASS_ENDPOINTS:
        for tentativa in range(1, 3):
            try:
                resposta = requests.get(endpoint, params={"data": query}, timeout=45, headers=HEADERS)
                resposta.raise_for_status()
                return resposta.json()
            except Exception as e:
                print(f"  Overpass ({endpoint}) tentativa {tentativa} falhou: {type(e).__name__}")
                time.sleep(1.5 * tentativa)
    return None


def _obter_bairros_overpass(sul, norte, oeste, leste):
    """Busca bairros dentro do bbox via Overpass (place=* e admin_level 9/10)."""
    bbox = f"({sul},{oeste},{norte},{leste})"

    query_leve = f"""
[out:json][timeout:40];
(
  node["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
  way["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
);
out center tags;
"""

    query_admin = f"""
[out:json][timeout:55];
(
  relation["boundary"="administrative"]["admin_level"="9"]{bbox};
  relation["boundary"="administrative"]["admin_level"="10"]{bbox};
);
out center tags;
"""

    data = _consultar_overpass(query_leve)
    if data is None:
        return None
    if data.get("elements"):
        return data
    return _consultar_overpass(query_admin)


def _bairros_via_overpass(cidade, uf):
    """Retorna a lista de bairros do OSM, ou None se o serviço estiver indisponível."""
    bbox = _obter_bbox_cidade(cidade, uf)
    if not bbox:
        return None

    data = _obter_bairros_overpass(*bbox)
    if data is None:
        return None

    nomes = set()
    for elemento in data.get("elements", []):
        tags = elemento.get("tags") or {}
        nome = tags.get("name")
        if not isinstance(nome, str):
            continue
        nome = nome.strip()
        if nome and nome.lower() != cidade.strip().lower():
            nomes.add(nome)
    return sorted(nomes)


# ---------------------------------------------------------------------------
# API pública do módulo
# ---------------------------------------------------------------------------
def obter_estados():
    if USAR_CACHE:
        estados = _cache(localidades_db.ler_estados)
        if estados:
            print(f"Base local: {len(estados)} estados.")
            return pd.DataFrame(estados)

    estados = _baixar_estados()
    if estados is None:
        estados = _cache(localidades_db.ler_estados)
        if estados:
            print("IBGE indisponível. Usando os estados gravados na base local.")
            return pd.DataFrame(estados)
        print("Erro ao buscar estados.")
        return pd.DataFrame()

    _salvar(localidades_db.salvar_estados, estados)
    return pd.DataFrame(estados)


def obter_cidades(uf):
    if USAR_CACHE:
        municipios = _cache(localidades_db.ler_municipios, uf)
        if municipios:
            print(f"Base local: {len(municipios)} cidades em {uf}.")
            return [m["nome"] for m in municipios]

    municipios = _municipios_da_uf(uf)
    if municipios is None:
        municipios = _cache(localidades_db.ler_municipios, uf)
        if municipios:
            print(f"IBGE indisponível. Usando as cidades de {uf} gravadas na base local.")
            return [m["nome"] for m in municipios]
        print(f"Erro ao buscar cidades para {uf}.")
        return []

    _salvar(localidades_db.salvar_municipios, municipios)
    return sorted(m["nome"] for m in municipios)


def _normalizar(texto):
    """Minúsculas e sem acentos, para comparar nomes digitados pelo usuário."""
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    return "".join(c for c in texto if not unicodedata.combining(c)).strip().casefold()


def filtrar_cidades(cidades, termo):
    """Filtra a lista de cidades por um trecho, ignorando acentos e maiúsculas."""
    alvo = _normalizar(termo)
    if not alvo:
        return []
    return [c for c in cidades if alvo in _normalizar(c)]


def _descobrir_bairros(cidade, uf, municipio):
    """Monta a lista final de bairros: distritos do IBGE + complemento do OSM.

    Retorna (registros, fonte). fonte=None significa "não gravar no cache" —
    usado quando houve falha de rede, para tentar de novo na próxima execução.
    """
    registros = []
    total_distritos = 0
    if municipio:
        distritos = _baixar_distritos(municipio["id_municipio"]) or []
        total_distritos = len(distritos)
        for distrito in distritos:
            if _normalizar(distrito["nome"]) == _normalizar(cidade):
                continue
            registros.append({"nome": distrito["nome"], "id_distrito": distrito["id_distrito"]})

    if len(registros) >= MIN_BAIRROS:
        print(f"  IBGE: {len(registros)} distritos de {cidade}-{uf} serão usados como áreas de busca.")
        return registros, localidades_db.FONTE_IBGE

    # A API de Localidades do IBGE só tem distritos/subdistritos — não tem bairros.
    # Quando o município tem apenas o distrito-sede, não há o que aproveitar.
    if total_distritos <= 1:
        print(f"  IBGE não publica bairros para {cidade}-{uf}: o município tem apenas "
              f"{total_distritos} distrito (a sede).")
    else:
        print(f"  IBGE: apenas {len(registros)} distrito(s) além da sede em {cidade}-{uf}.")

    print("  Buscando bairros no OpenStreetMap...")
    bairros_osm = _bairros_via_overpass(cidade, uf)

    if bairros_osm is None:
        print("  OpenStreetMap indisponível. Esta cidade NÃO será gravada no cache;")
        print("  os distritos do IBGE serão usados apenas nesta execução.")
        return registros, None

    vistos = {_normalizar(r["nome"]) for r in registros}
    for nome in bairros_osm:
        if _normalizar(nome) not in vistos:
            vistos.add(_normalizar(nome))
            registros.append({"nome": nome, "id_distrito": None})

    if bairros_osm:
        return registros, localidades_db.FONTE_OVERPASS
    if registros:
        return registros, localidades_db.FONTE_IBGE
    return [], localidades_db.FONTE_CIDADE


def _resolver_municipio(cidade, uf):
    """Descobre o município no IBGE: id e nome oficial.

    Primeiro tenta a base local; se não achar, baixa a lista da UF (e grava, se
    LOCALIDADES_SALVAR permitir). Retorna None quando o nome não existe na UF.
    """
    alvo = _normalizar(cidade)

    municipios = _cache(localidades_db.ler_municipios, uf) or []
    for item in municipios:
        if _normalizar(item["nome"]) == alvo:
            return {
                "id_municipio": item["id_municipio"],
                "nome": item["nome"],
                "uf": uf,
                "bairros_fonte": item.get("bairros_fonte"),
            }

    baixados = _municipios_da_uf(uf) or []
    _salvar(localidades_db.salvar_municipios, baixados)

    for item in baixados:
        if _normalizar(item["nome"]) == alvo:
            return {
                "id_municipio": item["id_municipio"],
                "nome": item["nome"],
                "uf": item["uf"],
                "bairros_fonte": None,
            }

    if mun := _cache(localidades_db.buscar_municipio, cidade, uf):
        return mun
    return None


def obter_municipio(cidade, uf):
    """Retorna o município do IBGE para o nome digitado (id, nome oficial e uf).

    Útil para gravar sempre o nome oficial, mesmo que o usuário digite sem
    acento ou em minúsculas (ex.: "canoas" -> "Canoas").
    """
    return _resolver_municipio(cidade, uf)


def obter_bairros(cidade, uf):
    """
    Retorna os bairros de uma cidade, usando a base local quando possível.
    Lista vazia significa "buscar a cidade inteira".
    """
    municipio = _resolver_municipio(cidade, uf)

    # Nome oficial do IBGE: evita divergência de acento/caixa nas buscas.
    nome_oficial = municipio["nome"] if municipio else cidade

    if USAR_CACHE and municipio and municipio.get("bairros_fonte"):
        bairros = _cache(localidades_db.ler_bairros, municipio["id_municipio"]) or []
        # O distrito-sede tem o mesmo nome da cidade e não ajuda na busca por área.
        bairros = [b for b in bairros if _normalizar(b) != _normalizar(nome_oficial)]
        fonte = municipio["bairros_fonte"]
        if fonte == localidades_db.FONTE_CIDADE or not bairros:
            print(f"Base local: {nome_oficial}-{uf} sem bairros (fonte: {fonte}).")
            return []
        print(f"Base local: {len(bairros)} bairros de {nome_oficial}-{uf} (fonte: {fonte}).")
        return bairros

    bairros, fonte = _descobrir_bairros(nome_oficial, uf, municipio)

    if municipio and fonte:
        _salvar(localidades_db.salvar_bairros, municipio["id_municipio"], bairros, fonte)

    return [b["nome"] for b in bairros]


def obter_termos_busca(cidade, uf, max_bairros=30):
    """
    Divide a coleta por bairros para ampliar a cobertura do Google Maps
    (que pagina os resultados e não entrega a cidade inteira em uma única busca).
    Se nenhum bairro for descoberto, busca a cidade inteira como fallback.
    """
    print(f"Descobrindo bairros de {cidade} - {uf}...")
    bairros = obter_bairros(cidade, uf)

    if bairros:
        bairros = bairros[:max_bairros]
        print(f"{len(bairros)} bairros encontrados. A coleta será dividida por bairro.")
        return bairros

    print("Nenhum bairro encontrado. Buscando a cidade inteira.")
    return [cidade]


def listar_municipios_pendentes(uf):
    """Lista os municípios da UF que ainda não têm bairros resolvidos.

    Se a UF ainda não estiver na base local, baixa a lista do IBGE (e grava, se
    LOCALIDADES_SALVAR permitir). Retorna [] quando todos já estão resolvidos.
    """
    pendentes = _cache(localidades_db.ler_municipios_pendentes, uf)
    if pendentes is None:
        return []
    if pendentes:
        return pendentes

    # Nada pendente: só é "tudo pronto" se a UF estiver na base local.
    if _cache(localidades_db.ler_municipios, uf):
        return []

    print(f"  {uf} ainda não está na base local. Baixando a lista de municípios do IBGE...")
    municipios = _baixar_municipios(uf)
    if not municipios:
        return []
    _salvar(localidades_db.salvar_municipios, municipios)
    return [{"id_municipio": m["id_municipio"], "nome": m["nome"]} for m in municipios]


def aquecer_bairros_uf(uf, cidades=None, max_cidades=0, pausa_segundos=None):
    """Resolve e grava os bairros de todas as cidades de uma UF (uma única vez).

    Útil para preparar o cache e depois rodar a coleta sem nenhuma consulta de
    rede. A pausa entre cidades é aplicada só quando o OpenStreetMap foi de fato
    consultado (cidades cobertas pelo IBGE são instantâneas).

    Retorna um dicionário com o resumo da execução.
    """
    if not SALVAR:
        print("\nLOCALIDADES_SALVAR=false: não é possível aquecer a base local.")
        print("Ative a flag LOCALIDADES_SALVAR para gravar os bairros.")
        return None

    pausa_segundos = AQUECER_PAUSA_PADRAO if pausa_segundos is None else pausa_segundos

    if cidades is None:
        print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
        cidades = listar_municipios_pendentes(uf)

    total_pendente = len(cidades)
    if not total_pendente:
        print(f"Todas as cidades de {uf} já têm bairros na base local. Nada a fazer.")
        return {"uf": uf, "pendentes": 0, "processadas": 0, "ibge": 0,
                "osm": 0, "sem_bairros": 0, "falhas": 0}

    if max_cidades and max_cidades > 0:
        cidades = cidades[:max_cidades]

    print(f"\nAquecendo bairros de {len(cidades)} cidade(s) de {uf} "
          f"({total_pendente} pendente(s) no total).")
    print(f"Pausa entre cidades que usam OpenStreetMap: {pausa_segundos}s")
    print("Interrompa com Ctrl+C — o progresso já gravado é preservado.\n")

    resumo = {"uf": uf, "pendentes": total_pendente, "processadas": 0,
              "ibge": 0, "osm": 0, "sem_bairros": 0, "falhas": 0}

    try:
        for indice, cidade in enumerate(cidades, 1):
            nome = cidade["nome"]
            print(f"[{indice}/{len(cidades)}] {nome}-{uf}")

            bairros = obter_bairros(nome, uf)
            municipio = _cache(localidades_db.buscar_municipio, nome, uf)
            fonte = (municipio or {}).get("bairros_fonte")
            resumo["processadas"] += 1

            if fonte is None:
                resumo["falhas"] += 1
                print(f"  Falhou (nada gravado). Pulando.")
            elif fonte == localidades_db.FONTE_OVERPASS:
                resumo["osm"] += 1
            elif fonte == localidades_db.FONTE_IBGE:
                resumo["ibge"] += 1
            else:
                resumo["sem_bairros"] += 1

            usou_osm = fonte in (localidades_db.FONTE_OVERPASS,
                                 localidades_db.FONTE_CIDADE)
            if usou_osm and indice < len(cidades):
                time.sleep(pausa_segundos)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário. O que já foi gravado está preservado.")

    print(f"\nResumo de {uf}: {resumo['processadas']} cidade(s) processada(s) "
          f"de {total_pendente} pendente(s).")
    print(f"  via IBGE: {resumo['ibge']} | via OpenStreetMap: {resumo['osm']} | "
          f"sem bairros: {resumo['sem_bairros']} | falhas: {resumo['falhas']}")
    restantes = total_pendente - resumo["processadas"]
    if restantes > 0:
        print(f"  {restantes} cidade(s) continuam pendentes — rode novamente para retomar.")
    return resumo


def _descrever_gravacao(total, recebidos):
    """Texto do resumo da sincronização (distingue gravado de apenas baixado)."""
    if total is None:
        return f"{recebidos} recebidos, NÃO gravados (base local indisponível)"
    return f"{total} gravados"


def sincronizar_base_localidades():
    """Baixa estados, municípios e distritos do IBGE para o DuckDB.

    Depois disso, com LOCALIDADES_USAR_CACHE=true, a coleta não faz chamadas de
    rede para descobrir bairros — exceto nas cidades em que o IBGE não tem
    distritos úteis (aí o OSM é consultado uma única vez e o resultado é gravado).
    """
    if not SALVAR:
        print("\nLOCALIDADES_SALVAR=false: a sincronização está desativada.")
        print("Nada foi baixado nem gravado. Ative a flag para popular a base local.")
        return False

    print("\nSincronizando base de localidades do IBGE...")

    estados = _baixar_estados()
    if estados is None:
        print("Falha ao baixar os estados. Sincronização abortada.")
        return False
    total = _salvar(localidades_db.salvar_estados, estados)
    print(f"  Estados: {_descrever_gravacao(total, len(estados))}.")

    municipios = _baixar_municipios()
    if municipios is None:
        print("Falha ao baixar os municípios. Sincronização abortada.")
        return False
    total = _salvar(localidades_db.salvar_municipios, municipios)
    print(f"  Municípios: {_descrever_gravacao(total, len(municipios))}.")

    print("  Baixando distritos (pode levar alguns segundos)...")
    distritos = _baixar_distritos()
    if distritos is None:
        print("Falha ao baixar os distritos. Estados e municípios foram gravados.")
        return False
    total = _salvar(localidades_db.salvar_distritos_bulk, distritos, MIN_BAIRROS)
    print(f"  Distritos: {_descrever_gravacao(total, len(distritos))}.")

    stats = _cache(localidades_db.estatisticas) or {}
    print(f"\nBase local: {stats.get('estados', 0)} estados, "
          f"{stats.get('municipios', 0)} municípios, {stats.get('bairros', 0)} bairros "
          f"({stats.get('cidades_prontas', 0)} cidades com bairros prontos).")
    print("Sincronização concluída.")
    return True
