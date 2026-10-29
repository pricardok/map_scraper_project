# src/locations.py
import time
import requests
import pandas as pd

# User-Agent identificável é exigido pela política de uso do Nominatim.
# Substitua pelo seu contato real se for usar em produção.
HEADERS = {"User-Agent": "map-scraper-lead-prospecting/1.0 (prospeccao.mapscraper@gmail.com)"}

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def obter_estados():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return pd.DataFrame([{'uf': e['sigla'], 'nome': e['nome']} for e in response.json()])
    except Exception as e:
        print(f"Erro ao buscar estados: {e}")
        return pd.DataFrame()


def obter_cidades(uf):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return [c['nome'] for c in response.json()]
    except Exception as e:
        print(f"Erro ao buscar cidades para {uf}: {e}")
        return []


def _obter_bbox_cidade(cidade, uf):
    """Retorna (sul, norte, oeste, leste) da cidade via Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "format": "json",
        "q": f"{cidade}, {uf}, Brazil",
        "limit": 1,
    }
    try:
        response = requests.get(url, params=params, timeout=15, headers=HEADERS)
        response.raise_for_status()
        resultados = response.json()
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


def _obter_bairros_overpass(sul, norte, oeste, leste):
    """Busca bairros dentro do bbox via Overpass.

    Cobre os principais esquemas usados no OSM para bairros brasileiros:
    place=suburb/neighbourhood/quarter e boundary=administrative (admin_level 9/10).
    """
    bbox = f"({sul},{oeste},{norte},{leste})"

    # Consulta leve: bairros marcados como place=* (nodes + ways).
    # Rodamos primeiro porque responde rápido e raramente dá timeout.
    query_leve = f"""
[out:json][timeout:40];
(
  node["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
  way["place"~"^(suburb|neighbourhood|quarter)$"]{bbox};
);
out center tags;
"""

    # Consulta pesada: fronteiras administrativas (admin_level 9/10).
    # Só usamos como complemento se a leve não trouxer resultado.
    query_admin = f"""
[out:json][timeout:55];
(
  relation["boundary"="administrative"]["admin_level"="9"]{bbox};
  relation["boundary"="administrative"]["admin_level"="10"]{bbox};
);
out center tags;
"""

    data = _consultar_overpass(query_leve)
    if data.get("elements"):
        return data

    # Complementa com fronteiras administrativas, se a consulta leve falhou/vier vazia.
    data_admin = _consultar_overpass(query_admin)
    return data_admin


def _consultar_overpass(query):
    """Tenta a consulta em vários espelhos do Overpass, com retry e backoff."""
    for endpoint in OVERPASS_ENDPOINTS:
        for tentativa in range(1, 3):
            try:
                response = requests.get(endpoint, params={"data": query}, timeout=45, headers=HEADERS)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"  Overpass ({endpoint}) tentativa {tentativa} falhou: {type(e).__name__}")
                time.sleep(1.5 * tentativa)
    return {"elements": []}


def obter_bairros(cidade, uf):
    """
    Descobre os bairros de uma cidade (Nominatim + Overpass).
    Retorna uma lista de nomes de bairros; vazia se não for possível descobrir.
    """
    bbox = _obter_bbox_cidade(cidade, uf)
    if not bbox:
        return []

    sul, norte, oeste, leste = bbox
    data = _obter_bairros_overpass(sul, norte, oeste, leste)

    bairros = set()
    for elemento in data.get("elements", []):
        tags = elemento.get("tags") or {}
        nome = tags.get("name")
        if not nome or not isinstance(nome, str):
            continue
        nome_limpo = nome.strip()
        if nome_limpo and nome_limpo.lower() != cidade.lower():
            bairros.add(nome_limpo)

    return sorted(bairros)


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