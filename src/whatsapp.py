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
import re
import time

import requests

from src.config import carregar_env, str_para_bool

carregar_env()

WAHA_API_URL = os.environ.get("WAHA_API_URL", "http://localhost:3000")
WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")

# Se false, o módulo NÃO tenta enviar (desliga o envio de WhatsApp).
WAHA_ATIVO = str_para_bool(os.environ.get("WAHA_ATIVO"), padrao=True)

# Se true, pula a coleta e vai direto para o envio (não coleta nada).
SOMENTE_ENVIO = str_para_bool(os.environ.get("SOMENTE_ENVIO"), padrao=False)

# Intervalo (segundos) entre envios e limite de leads por campanha.
# WAHA_LIMITE vazio = sem limite (envia todos os pendentes).
WAHA_INTERVALO = int(os.environ.get("WAHA_INTERVALO", "13"))
WAHA_LIMITE = os.environ.get("WAHA_LIMITE", "").strip()
WAHA_LIMITE = int(WAHA_LIMITE) if WAHA_LIMITE else None

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
    - intervalo: pausa em segundos entre envios (evita spam e banimento)
    - leads: DataFrame opcional já filtrado; se None, busca pendentes (com limite)
    """
    mensagem_template = mensagem_template or MENSAGEM_PADRAO
    if leads is None:
        leads = db.get_leads_para_envio(limite)

    if leads.empty:
        print("Nenhum lead celular pendente de envio.")
        return

    total = len(leads)
    print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")

    for i, (_, lead) in enumerate(leads.iterrows(), 1):
        chat_id = lead.get("chat_id_waha")
        if not chat_id:
            # Resolve (e cacheia) o chatId uma única vez por lead. Números novos
            # usam @lid; a consulta ao checkNumberStatus é feita só na primeira vez.
            chat_id = _resolver_chatid_waha(lead.get("telefone"))
            if chat_id:
                db.salvar_chat_id_waha(lead["nome"], lead["cidade"], chat_id)
        if not chat_id:
            db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
            print(f"[{i}/{total}] {lead['nome']} - telefone inválido, marcado como falhou.")
            continue

        texto = _renderizar_mensagem(mensagem_template, lead)

        try:
            enviar_texto_waha(chat_id, texto)
            db.marcar_envio(lead["nome"], lead["cidade"], "enviado")
            print(f"[{i}/{total}] ENVIADO -> {lead['nome']} ({chat_id})")
        except Exception as e:
            db.marcar_envio(lead["nome"], lead["cidade"], "falhou")
            print(f"[{i}/{total}] FALHOU -> {lead['nome']} ({chat_id}): {e}")

        if i < total:
            time.sleep(intervalo)

    print("Campanha finalizada.")
