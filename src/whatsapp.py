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
    """Converte o telefone salvo em um chatId do WAHA (55DDDNUMERO@c.us)."""
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


def _renderizar_mensagem(template, lead):
    """Substitui {nome}, {bairro} e {cidade} de forma segura (sem quebrar com chaves soltas)."""
    bairro = str(lead.get("bairro") or "sua região")
    cidade = str(lead.get("cidade") or "")
    return (
        template
        .replace("{nome}", str(lead.get("nome") or ""))
        .replace("{bairro}", bairro)
        .replace("{cidade}", cidade)
    )


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


def disparar_campanha(db, mensagem_template=None, intervalo=13, limite=None):
    """Envia mensagens para todos os leads celulares pendentes.

    - db: instância de LeadDatabase
    - mensagem_template: texto com {nome}, {bairro}, {cidade} (usa MENSAGEM_PADRAO se None)
    - intervalo: pausa em segundos entre envios (evita spam e banimento)
    """
    mensagem_template = mensagem_template or MENSAGEM_PADRAO
    leads = db.get_leads_para_envio(limite)

    if leads.empty:
        print("Nenhum lead celular pendente de envio.")
        return

    total = len(leads)
    print(f"Enviando para {total} lead(s) celular(es), com intervalo de {intervalo}s...")

    for i, (_, lead) in enumerate(leads.iterrows(), 1):
        chat_id = _normalizar_chatid(lead.get("telefone"))
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
