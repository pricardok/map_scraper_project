# src/whatsapp.py
"""Integração com a WAHA (WhatsApp HTTP API) para envio de mensagens aos leads.

Configuração via variáveis de ambiente:
    WAHA_API_URL   -> URL base da WAHA (padrão: http://localhost:3000)
    WAHA_API_KEY   -> chave de API da WAHA (obrigatória se a instância exigir)
    WAHA_SESSION   -> nome da sessão conectada na WAHA (padrão: "default")

O módulo só envia para leads:
    - status = 'ativo'
    - tipo_telefone = 'Celular'  (nunca fixo)
    - ainda não enviados (status_whatsapp = 'pendente' ou NULL)
"""
import os
import random
import re
import time
from datetime import datetime, timedelta

import requests

from src import backend
from src.config import carregar_env, env_int, str_para_bool

carregar_env()

WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")

# Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)

# Se true, pula a coleta e vai direto para o envio (não coleta nada).
SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)

# ---------------------------------------------------------------------------
# Cadência de envio (anti-bloqueio)
# ---------------------------------------------------------------------------
# Formato "X a cada Y segundos", ex.: WAHA_CADENCIA=3:60  -> 3 envios por minuto.
# Os envios são distribuídos ALEATORIAMENTE dentro da janela de Y segundos,
# evitando pausas fixas (15s, 15s, ...) que são mais fáceis de detectar.
WAHA_CADENCIA = os.environ.get("WAHA_CADENCIA", "").strip()

# Legado: WAHA_INTERVALO (pausa fixa) continua funcionando quando WAHA_CADENCIA
# não é informado.
WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))

# Limite de leads por campanha (uma execução do envio). Vazio = sem limite.
# ATENÇÃO: é por campanha, NÃO por dia. Para teto diário use WAHA_LIMITE_DIA.
WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None

# ---------------------------------------------------------------------------
# Janela de envio (horário permitido) e limite diário
# ---------------------------------------------------------------------------
# Teto de mensagens enviadas por dia, somando TODAS as campanhas. O contador é
# lido do log (`whatsapp_envios_log`, status='enviado'), então reiniciar o
# processo não "zera" o limite. Vazio/0 = sem teto diário.
WAHA_LIMITE_DIA = env_int("WAHA_LIMITE_DIA", 0) or None

# Horário permitido para envio: "08:00-19:00" (ou "8-19").
# Vazio = envia a qualquer hora. Aceita janela que atravessa a meia-noite
# (ex.: "22:00-06:00"). O dia do teto diário começa junto com a janela.
WAHA_JANELA_ENVIO = os.environ.get("WAHA_JANELA_ENVIO", "").strip()

_PADRAO_JANELA = re.compile(
    r"^\s*(\d{1,2})(?::(\d{2}))?\s*(?:-|–|a|as|às)\s*(\d{1,2})(?::(\d{2}))?\s*$",
    re.IGNORECASE,
)


def _parse_janela(valor):
    """Interpreta "08:00-19:00" -> (minuto_inicio, minuto_fim).

    Retorna None para vazio/inválido ou quando começa e termina no mesmo
    horário (24h). A janela pode atravessar a meia-noite (início > fim).
    """
    if not valor:
        return None
    casamento = _PADRAO_JANELA.match(valor)
    if not casamento:
        print(f"Aviso: WAHA_JANELA_ENVIO inválida ({valor!r}). "
              f"Use '08:00-19:00' ou deixe vazio para enviar a qualquer hora.")
        return None

    h1, m1, h2, m2 = casamento.groups()
    horas = (int(h1), int(m1 or 0), int(h2), int(m2 or 0))
    if horas[0] > 23 or horas[1] > 59 or horas[2] > 23 or horas[3] > 59:
        print(f"Aviso: WAHA_JANELA_ENVIO inválida ({valor!r}). "
              f"Use '08:00-19:00' ou deixe vazio para enviar a qualquer hora.")
        return None

    inicio = horas[0] * 60 + horas[1]
    fim = horas[2] * 60 + horas[3]
    if inicio == fim:
        return None
    return inicio, fim


_JANELA = _parse_janela(WAHA_JANELA_ENVIO)


def descrever_janela():
    """Texto da janela configurada (ex.: '08:00-19:00')."""
    if not _JANELA:
        return "24h (sem janela)"
    inicio, fim = _JANELA
    return f"{inicio // 60:02d}:{inicio % 60:02d}-{fim // 60:02d}:{fim % 60:02d}"


def janela_aberta(agora=None):
    """True quando o horário atual está dentro da janela de envio."""
    if not _JANELA:
        return True
    agora = agora or datetime.now()
    atual = agora.hour * 60 + agora.minute
    inicio, fim = _JANELA
    if inicio < fim:
        return inicio <= atual < fim
    return atual >= inicio or atual < fim  # atravessa a meia-noite


def inicio_da_janela_diaria(agora=None):
    """Início do ciclo atual da janela (base da contagem do teto diário).

    Sem janela configurada, o dia começa à meia-noite. Com janela, começa na
    abertura dela — então o teto diário "renova" quando o horário permitido abre.
    """
    agora = agora or datetime.now()
    inicio_min = _JANELA[0] if _JANELA else 0
    inicio = agora.replace(
        hour=inicio_min // 60, minute=inicio_min % 60, second=0, microsecond=0
    )
    if agora < inicio:
        inicio -= timedelta(days=1)
    return inicio


def proxima_abertura(agora=None):
    """Próximo momento em que o envio volta a ser permitido (agora, se aberto)."""
    agora = agora or datetime.now()
    if janela_aberta(agora):
        return agora
    inicio_min = _JANELA[0]
    abertura = agora.replace(
        hour=inicio_min // 60, minute=inicio_min % 60, second=0, microsecond=0
    )
    if agora >= abertura:
        abertura += timedelta(days=1)
    return abertura


def aviso_fora_da_janela():
    """Informa que o envio está bloqueado e quando ele volta a ser permitido."""
    abertura = proxima_abertura()
    print(f"Fora da janela de envio ({descrever_janela()}). "
          f"Próximo envio a partir de {abertura:%d/%m às %H:%M}.")


def envios_hoje(db, desde=None):
    """Quantidade de envios concluídos na janela do dia atual.

    Usa o log de envios (uma linha por tentativa) como fonte de verdade, então
    vale para qualquer campanha/processo que use o mesmo banco. Se a tabela de
    log ainda não existir, cai para `leads.data_envio_whatsapp`.
    """
    desde = desde or inicio_da_janela_diaria()
    p = backend.ph()
    try:
        total = backend.query_one(db.conn, f"""
            SELECT COUNT(*) FROM whatsapp_envios_log
            WHERE status = {p} AND data_envio >= {p}
        """, ["enviado", desde])
    except Exception:
        total = backend.query_one(db.conn, f"""
            SELECT COUNT(*) FROM leads
            WHERE data_envio_whatsapp IS NOT NULL AND data_envio_whatsapp >= {p}
        """, [desde])
    return int((total or [0])[0] or 0)


def resumo_limite_dia(db):
    """(enviados_hoje, restante). `restante` é None quando não há teto diário."""
    if not WAHA_LIMITE_DIA:
        return 0, None
    enviados = envios_hoje(db)
    return enviados, max(0, WAHA_LIMITE_DIA - enviados)


def _parse_cadencia(valor):
    """Interpreta "N:Y" -> (envios_por_janela, janela_segundos).

    Retorna None quando o valor está vazio/inválido (usa o intervalo fixo).
    """
    if not valor:
        return None
    try:
        envios, janela = valor.split(":", 1)
        envios = int(envios.strip())
        janela = int(janela.strip())
    except (ValueError, AttributeError):
        return None
    if envios <= 0 or janela <= 0:
        return None
    return envios, janela


def _intervalos_aleatorios(quantidade, janela_segundos):
    """Gera as pausas (em segundos) para `quantidade` envios numa janela.

    Distribui os envios em pontos aleatórios crescentes dentro da janela e
    retorna a diferença entre pontos consecutivos — o intervalo entre cada envio
    varia, mas o total da janela é respeitado.
    """
    if quantidade <= 1:
        return [0]
    # Pontos aleatórios crescentes: 1 envio em cada "fatia" da janela, com
    # jitter dentro da fatia, garantindo tempos diferentes entre os envios.
    pontos = sorted(
        random.uniform((i * janela_segundos) / quantidade,
                       ((i + 1) * janela_segundos) / quantidade)
        for i in range(quantidade)
    )
    return [round(pontos[i + 1] - pontos[i], 2) for i in range(quantidade - 1)]


def _pausas_cadencia(total, envios_janela, janela_segundos):
    """Gera as pausas da campanha inteira respeitando a cadência.

    Agrupa os `total` envios em janelas de `janela_segundos` segundos, com
    `envios_janela` envios por janela (distribuídos aleatoriamente). Retorna uma
    lista com `total - 1` pausas (uma entre cada par consecutivo).
    """
    if total <= 1:
        return [0]

    # Timestamp de envio de cada lead: janela + posição aleatória dentro dela.
    tempos = []
    for idx in range(total):
        janela_idx = idx // envios_janela
        pos_na_janela = idx % envios_janela
        inicio = janela_idx * janela_segundos
        # posição aleatória dentro da fatia correspondente a este envio
        p = random.uniform(
            inicio + (pos_na_janela * janela_segundos) / envios_janela,
            inicio + ((pos_na_janela + 1) * janela_segundos) / envios_janela,
        )
        tempos.append(p)

    tempos.sort()
    return [round(tempos[i + 1] - tempos[i], 2) for i in range(len(tempos) - 1)]

# Mensagem padrão (placeholder). Use {nome}, {bairro} e {cidade}.
MENSAGEM_PADRAO = "Olá {nome}! Vi que vocês atendem no bairro {bairro}, em {cidade}. Podemos conversar?"


def _normalizar_chatid(telefone):
    """Converte o telefone salvo em um chatId clássico do WAHA (55DDDNUMERO@c.us)."""
    numero = re.sub(r"\D", "", str(telefone or ""))
    if not numero:
        return None

    # Se veio com DDI 55 e tem mais de 11 dígitos, remove o prefixo.
    if numero.startswith("55") and len(numero) > 11:
        numero = numero[2:]

    # Celular brasileiro tem 11 dígitos (DDD + 9 dígitos).
    if len(numero) != 11:
        return None

    return f"55{numero}@c.us"


def _resolver_chatid_waha(telefone, session=None, api_url=None, api_key=None):
    """Resolve o chatId correto via /api/checkNumberStatus.

    Números recentes no WhatsApp usam o formato @lid (hidden user ID) em vez do
    clássico @c.us. Enviar com @c.us para esses números retorna HTTP 500.
    A WAHA responde o chatId certo via checkNumberStatus; usamos ele e, se a
    consulta falhar ou o número não existir, caímos no formato clássico @c.us.
    """
    session = session or WAHA_SESSION
    api_url = api_url or WAHA_API_URL
    api_key = api_key if api_key is not None else WAHA_API_KEY

    numero = re.sub(r"\D", "", str(telefone or ""))
    if not numero:
        return None

    if numero.startswith("55") and len(numero) > 11:
        numero = numero[2:]
    if len(numero) != 11:
        return None

    telefone_internacional = f"55{numero}"

    headers = {"Accept": "application/json"}
    if api_key:
        headers["X-Api-Key"] = api_key

    url = f"{api_url.rstrip('/')}/api/checkNumberStatus"
    params = {"session": session, "phone": telefone_internacional}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        dados = response.json()
        if dados.get("numberExists") and dados.get("chatId"):
            return dados["chatId"]
    except Exception:
        pass

    # Fallback: formato clássico @c.us (funciona para números mais antigos).
    return f"{telefone_internacional}@c.us"


def _limpar_markdown_whatsapp(texto):
    """Remove marcação de markdown (negrito e links) antes de enviar ao WhatsApp.

    - **texto**  -> texto
    - [rótulo](url) -> url (quando o rótulo já é a própria URL) ou "rótulo (url)"
    """
    texto = re.sub(r"\*\*([^*]+)\*\*", r"\1", texto)

    def _sub_link(match):
        rotulo = match.group(1)
        url = match.group(2)
        if rotulo.strip() == url.strip():
            return url
        return f"{rotulo} ({url})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _sub_link, texto)


def _renderizar_mensagem(template, lead):
    """Substitui {nome}, {bairro} e {cidade} de forma segura e limpa o markdown."""
    bairro = str(lead.get("bairro") or "sua região")
    cidade = str(lead.get("cidade") or "")
    texto = (
        template
        .replace("{nome}", str(lead.get("nome") or ""))
        .replace("{bairro}", bairro)
        .replace("{cidade}", cidade)
    )
    return _limpar_markdown_whatsapp(texto)


def enviar_texto_waha(chat_id, texto, session=None, api_url=None, api_key=None):
    """Envia uma mensagem de texto via WAHA."""
    session = session or WAHA_SESSION
    api_url = api_url or WAHA_API_URL
    api_key = api_key if api_key is not None else WAHA_API_KEY
    url = f"{api_url.rstrip('/')}/api/sendText"

    payload = {
        "session": session,
        "chatId": chat_id,
        "text": texto,
    }

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["X-Api-Key"] = api_key

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def enviar_texto_numero(numero, texto, session=None, api_url=None, api_key=None):
    """Envia uma mensagem de texto para um número bruto (com DDD), já normalizado.

    Útil para o envio de teste, sem precisar de um lead no banco.
    """
    texto = _limpar_markdown_whatsapp(texto)
    chat_id = _resolver_chatid_waha(numero, session=session, api_url=api_url, api_key=api_key)
    if not chat_id:
        raise ValueError(f"Número inválido para envio: {numero}")
    return enviar_texto_waha(chat_id, texto, session=session, api_url=api_url, api_key=api_key)


def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None, leads=None):
    """Envia mensagens para os leads celulares pendentes.

    - db: instância de LeadDatabase
    - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
    - intervalo: pausa fixa em segundos entre envios (usado se não houver cadência)
    - leads: DataFrame opcional já filtrado; se None, busca pendentes (com limite)

    Respeita dois tetos independentes:
    - `leads`/`limite`: quantos enviar nesta campanha;
    - `WAHA_LIMITE_DIA`: quantos enviar no dia (soma todas as campanhas).
    E a janela de horário `WAHA_JANELA_ENVIO` (ex.: 08:00-19:00): fora dela nada
    é enviado, e a campanha para se a janela fechar no meio.
    """
    mensagem_template = mensagem_template or MENSAGEM_PADRAO
    if leads is None:
        leads = db.get_leads_para_envio(limite)

    if leads.empty:
        print("Nenhum lead celular pendente de envio.")
        return

    total = len(leads)

    # Fora do horário permitido: não inicia a campanha.
    if not janela_aberta():
        aviso_fora_da_janela()
        return

    # Teto diário (soma todas as campanhas do dia, lido do log de envios).
    enviados_hoje = 0
    if WAHA_LIMITE_DIA:
        enviados_hoje = envios_hoje(db)
        restante_dia = WAHA_LIMITE_DIA - enviados_hoje
        if restante_dia <= 0:
            print(f"Limite diário atingido: {enviados_hoje}/{WAHA_LIMITE_DIA} envios hoje.")
            print(f"Os envios voltam na próxima janela ({descrever_janela()}).")
            return
        if total > restante_dia:
            print(f"Limite diário: {enviados_hoje}/{WAHA_LIMITE_DIA} já enviados hoje; "
                  f"reduzindo esta campanha para {restante_dia} envio(s).")
            leads = leads.head(restante_dia)
            total = len(leads)

    # Cadência aleatória (ex.: 3 a cada 60s) tem prioridade sobre o intervalo fixo.
    cadencia = _parse_cadencia(WAHA_CADENCIA)
    if cadencia:
        envios_janela, janela = cadencia
        pausas = _pausas_cadencia(total, envios_janela, janela)
        print(f"Enviando para {total} lead(s), cadência {envios_janela} a cada {janela}s "
              f"(intervalos aleatórios)...")
    else:
        pausas = [intervalo] * max(0, total - 1)
        print(f"Enviando para {total} lead(s), com intervalo fixo de {intervalo}s...")

    for i, (_, lead) in enumerate(leads.iterrows(), 1):
        # Reconfere janela e teto a cada envio: cobre campanha longa que cruza
        # o fim do horário permitido ou a virada do dia.
        if not janela_aberta():
            print(f"Janela de envio encerrada ({descrever_janela()}). "
                  f"Interrompendo; os {total - i + 1} lead(s) restantes continuam "
                  f"pendentes para o próximo horário.")
            break

        if WAHA_LIMITE_DIA:
            enviados_hoje = envios_hoje(db)
            if enviados_hoje >= WAHA_LIMITE_DIA:
                print(f"Limite diário atingido ({enviados_hoje}/{WAHA_LIMITE_DIA}). "
                      f"Interrompendo; os demais leads continuam pendentes.")
                break

        texto = _renderizar_mensagem(mensagem_template, lead)
        lead_id = lead.get("lead_id")
        telefone = lead.get("telefone")
        nome = lead.get("nome")
        cidade = lead.get("cidade")

        chat_id = lead.get("chat_id_waha")
        if not chat_id:
            # Resolve (e cacheia) o chatId uma única vez por lead. Números novos
            # usam @lid; a consulta ao checkNumberStatus é feita só na primeira vez.
            chat_id = _resolver_chatid_waha(telefone)
            if chat_id:
                db.salvar_chat_id_waha(nome, cidade, chat_id)

        if not chat_id:
            db.marcar_envio(nome, cidade, "falhou")
            db.salvar_log_envio(
                lead_id, nome, cidade, telefone, chat_id, "falhou",
                mensagem=texto, erro="telefone inválido",
            )
            print(f"[{i}/{total}] {nome} - telefone inválido, marcado como falhou.")
            continue

        try:
            resposta = enviar_texto_waha(chat_id, texto)
            db.marcar_envio(nome, cidade, "enviado")
            db.salvar_log_envio(
                lead_id, nome, cidade, telefone, chat_id, "enviado",
                mensagem=texto, payload=resposta,
            )
            print(f"[{i}/{total}] ENVIADO -> {nome} ({chat_id})")
        except Exception as e:
            payload_erro = None
            if getattr(e, "response", None) is not None:
                try:
                    payload_erro = e.response.text
                except Exception:
                    payload_erro = None
            erro = f"{type(e).__name__}: {e}"
            db.marcar_envio(nome, cidade, "falhou")
            db.salvar_log_envio(
                lead_id, nome, cidade, telefone, chat_id, "falhou",
                mensagem=texto, payload=payload_erro, erro=erro,
            )
            print(f"[{i}/{total}] FALHOU -> {nome} ({chat_id}): {erro}")

        if i < total:
            time.sleep(pausas[i - 1])

    print("Campanha finalizada.")
