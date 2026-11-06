# src/meta_whatsapp.py
"""Envio de WhatsApp pela API OFICIAL da Meta (Cloud API) — provedor padrão.

Por que existe
--------------
O map_scraper originalmente só falava com a WAHA (WhatsApp Web não oficial).
Para disparar campanhas pelo número oficial (+55 51 8151-6260) é preciso usar
a Graph API da Meta com um **template aprovado** — mensagem de texto livre só
funciona dentro da janela de 24h após o lead responder.

Diferença fundamental em relação à WAHA
---------------------------------------
    WAHA          -> manda TEXTO livre (o `templates_whatsapp` do banco)
    Meta (oficial)-> manda TEMPLATE aprovado (identificado por NOME)

Ou seja: com `WHATSAPP_PROVIDER=meta` o campo `mensagem` do template do banco
NÃO é enviado — quem define o conteúdo é o template aprovado na Meta.
O texto do banco continua útil para o log (`whatsapp_envios_log.mensagem`).

Configuração (.env)
-------------------
META_ACCESS_TOKEN      "EAA..."            token permanente (System User)
META_PHONE_NUMBER_ID   "1121736814366847"  ID do número oficial
META_API_VERSION       "v25.0"            (opcional)
META_TEMPLATE_NOME     "mkt_01"           template aprovado a usar
META_TEMPLATE_IDIOMA   "pt_BR"            (opcional, padrão pt_BR)
META_TEMPLATE_PARAMS   ""                 (opcional) CSV de campos do lead
                                          enviados como parâmetros do corpo.
                                          Vazio = template sem variáveis
                                          (é o caso do mkt_01).
                                          Ex.: "nome,cidade"
META_TIMEOUT           "30"               (opcional)

Telefone
--------
O banco de leads guarda SEM o código do país:  '51985171688'
A Meta exige COM o código do país e sem '+':   '5551985171688'
`formatar_telefone_meta()` faz essa conversão e valida o DDD.
"""
import os
import re
import logging

import requests

from src.config import carregar_env, env_int

carregar_env()

logger = logging.getLogger(__name__)

META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "").strip()
META_PHONE_NUMBER_ID = os.environ.get("META_PHONE_NUMBER_ID", "").strip()
META_API_VERSION = os.environ.get("META_API_VERSION", "v25.0").strip() or "v25.0"

META_TEMPLATE_NOME = os.environ.get("META_TEMPLATE_NOME", "").strip()
META_TEMPLATE_IDIOMA = os.environ.get("META_TEMPLATE_IDIOMA", "pt_BR").strip() or "pt_BR"
META_TEMPLATE_PARAMS = os.environ.get("META_TEMPLATE_PARAMS", "").strip()

META_TIMEOUT = env_int("META_TIMEOUT", 30) or 30

# DDDs brasileiros válidos — evita chamar a Meta com número inválido
# (que gastaria uma tentativa e poluiria a qualidade do número).
_DDD_VALIDOS = {
    '11', '12', '13', '14', '15', '16', '17', '18', '19',
    '21', '22', '24', '27', '28',
    '31', '32', '33', '34', '35', '37', '38',
    '41', '42', '43', '44', '45', '46', '47', '48', '49',
    '51', '53', '54', '55',
    '61', '62', '63', '64', '65', '66', '67', '68', '69',
    '71', '73', '74', '75', '77', '79',
    '81', '82', '83', '84', '85', '86', '87', '88', '89',
    '91', '92', '93', '94', '95', '96', '97', '98', '99',
}


def configurado():
    """True quando há token e phone_number_id — pré-requisito para enviar."""
    return bool(META_ACCESS_TOKEN and META_PHONE_NUMBER_ID)


def template_configurado():
    """True quando um template foi informado no .env."""
    return bool(META_TEMPLATE_NOME)


def descrever():
    """Texto curto para exibir no menu (sem vazar o token)."""
    if not configurado():
        return "Meta API oficial — NÃO CONFIGURADA (faltam META_ACCESS_TOKEN / META_PHONE_NUMBER_ID)"
    if not template_configurado():
        return "Meta API oficial — configurada, mas META_TEMPLATE_NOME vazio"
    return (
        f"Meta API oficial — template '{META_TEMPLATE_NOME}' ({META_TEMPLATE_IDIOMA}), "
        f"phone_number_id={META_PHONE_NUMBER_ID}"
    )


def formatar_telefone_meta(telefone):
    """Converte '51985171688' / '(51) 98517-1688' no formato da Meta.

    Retorna '5551985171688' (com 55, sem '+') ou None se inválido.

    A Meta aceita o número com ou sem o nono dígito — ela própria resolve o
    `wa_id` final. Aqui só garantimos país + DDD válido + tamanho plausível.
    """
    if not telefone:
        return None

    digitos = re.sub(r"\D", "", str(telefone))
    if not digitos:
        return None

    # Remove o DDI 55 se já vier junto
    if digitos.startswith("55") and len(digitos) in (12, 13):
        digitos = digitos[2:]

    if len(digitos) not in (10, 11):
        return None

    if digitos[:2] not in _DDD_VALIDOS:
        return None

    return f"55{digitos}"


def _params_do_lead(lead, template_params_csv=None):
    """Monta a lista de parâmetros do corpo do template a partir do lead.

    `META_TEMPLATE_PARAMS` é um CSV de chaves do DataFrame de leads:
        META_TEMPLATE_PARAMS=nome,cidade
    produz ["Barbearia X", "Porto Alegre"].

    Vazio → retorna None (template sem variáveis, como o mkt_01).
    """
    bruto = (template_params_csv if template_params_csv is not None
             else META_TEMPLATE_PARAMS)
    if not bruto:
        return None

    chaves = [c.strip() for c in bruto.split(",") if c.strip()]
    if not chaves:
        return None

    valores = []
    for chave in chaves:
        valor = lead.get(chave) if hasattr(lead, "get") else None
        valores.append("" if valor is None else str(valor))

    return valores or None


def montar_payload(telefone, template_nome=None, idioma=None, body_params=None):
    """Monta o JSON de envio de template da Graph API."""
    template_nome = template_nome or META_TEMPLATE_NOME
    idioma = idioma or META_TEMPLATE_IDIOMA

    template = {
        "name": template_nome,
        "language": {"code": idioma},
    }

    if body_params:
        template["components"] = [{
            "type": "body",
            "parameters": [
                {"type": "text", "text": str(p)}
                for p in body_params
            ],
        }]

    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": formatar_telefone_meta(telefone),
        "type": "template",
        "template": template,
    }


def enviar_template(telefone, template_nome=None, idioma=None, body_params=None):
    """Envia um template aprovado pela API oficial da Meta.

    Returns:
        dict com {status_code, ok, wamid, response, erro}

    Nunca levanta exceção: devolve `ok=False` e o motivo em `erro`. Isso é
    proposital — a campanha precisa continuar para os outros leads mesmo que
    um número esteja inválido ou a Meta recuse.
    """
    if not configurado():
        return {
            "status_code": None, "ok": False, "wamid": None, "response": None,
            "erro": "META_ACCESS_TOKEN / META_PHONE_NUMBER_ID não configurados",
        }

    destino = formatar_telefone_meta(telefone)
    if not destino:
        return {
            "status_code": None, "ok": False, "wamid": None, "response": None,
            "erro": f"telefone inválido para a Meta: {telefone!r}",
        }

    payload = montar_payload(destino, template_nome, idioma, body_params)
    url = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        resposta = requests.post(url, json=payload, headers=headers, timeout=META_TIMEOUT)
    except requests.RequestException as e:
        return {
            "status_code": None, "ok": False, "wamid": None, "response": None,
            "erro": f"{type(e).__name__}: {e}",
        }

    corpo = None
    try:
        corpo = resposta.json()
    except Exception:
        corpo = resposta.text

    wamid = None
    if isinstance(corpo, dict):
        mensagens = corpo.get("messages") or []
        if mensagens:
            wamid = mensagens[0].get("id")

    ok = 200 <= resposta.status_code < 300

    erro = None
    if not ok:
        if isinstance(corpo, dict):
            e = corpo.get("error") or {}
            erro = f"HTTP {resposta.status_code}: {e.get('message') or corpo}"
        else:
            erro = f"HTTP {resposta.status_code}: {str(corpo)[:300]}"

    return {
        "status_code": resposta.status_code,
        "ok": ok,
        "wamid": wamid,
        "response": corpo,
        "erro": erro,
    }
