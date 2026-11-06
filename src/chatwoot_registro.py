# src/chatwoot_registro.py
"""Registra no Chatwoot os disparos de campanha feitos pelo map_scraper.

O PROBLEMA QUE ISSO RESOLVE
---------------------------
Quando a Meta entrega uma mensagem de saída para o lead, o webhook só manda
`statuses` (sent/delivered/read) — NUNCA o conteúdo. Então o Chatwoot não tem
como saber que uma campanha foi enviada: não existe conversa para receber
aquela mensagem.

Resultado: o atendente abre o Chatwoot e não vê que o lead recebeu o `mkt_01`.

SOLUÇÃO
-------
Depois que a Meta aceita o envio, este módulo cria (ou reaproveita) a conversa
do lead no Chatwoot e grava uma **NOTA PRIVADA**:

    📤 Campanha enviada — template `mkt_01`
    wamid: wamid.HBgM...

Nota privada = o lead NÃO recebe nada. É registro interno para o atendente.

⚠️ REGRA DE OURO: NUNCA criar conversa JÁ COM MENSAGEM
------------------------------------------------------
`POST /conversations` com o campo `message` faz o Chatwoot **enviar** aquela
mensagem ao lead. Como a campanha já foi enviada pela Meta, isso causaria
**duplo envio** (e cobrança dupla). Por isso o fluxo é:

    1. POST /conversations          (sem `message`)
    2. POST /conversations/{id}/messages  com `private: true`

Configuração (.env)
-------------------
CHATWOOT_REGISTRO_ATIVO   "true"                     liga/desliga o registro
CHATWOOT_URL              "https://wps.agendamentoja.com"
CHATWOOT_API_TOKEN        "HJm1..."                  Profile Settings → Token
CHATWOOT_ACCOUNT_ID       "2"
CHATWOOT_INBOX_ID         "1"
CHATWOOT_CRIAR_CONVERSA   "true"   false = só anota em conversa que já existe
CHATWOOT_TIMEOUT          "15"

Custo/efeito colateral
----------------------
Criar conversa para CADA lead disparado enche a caixa de entrada. Se a base
tem 45 mil leads, isso vira 45 mil conversas. Use `CHATWOOT_CRIAR_CONVERSA=false`
se quiser anotar apenas em quem já conversou com você.
"""
import os
import re
import logging

import requests

from src.config import carregar_env, env_int, str_para_bool

carregar_env()

logger = logging.getLogger(__name__)

CHATWOOT_REGISTRO_ATIVO = str_para_bool(
    os.environ.get("CHATWOOT_REGISTRO_ATIVO"), padrao=False
)
CHATWOOT_URL = os.environ.get("CHATWOOT_URL", "").strip().rstrip("/")
CHATWOOT_API_TOKEN = os.environ.get("CHATWOOT_API_TOKEN", "").strip()
CHATWOOT_ACCOUNT_ID = os.environ.get("CHATWOOT_ACCOUNT_ID", "").strip()
CHATWOOT_INBOX_ID = os.environ.get("CHATWOOT_INBOX_ID", "").strip()
CHATWOOT_CRIAR_CONVERSA = str_para_bool(
    os.environ.get("CHATWOOT_CRIAR_CONVERSA"), padrao=True
)
CHATWOOT_TIMEOUT = env_int("CHATWOOT_TIMEOUT", 15) or 15

# Cache em memória: telefone normalizado -> contact_id do Chatwoot.
# Evita 2-3 chamadas HTTP por lead quando o mesmo número se repete na campanha.
_cache_contato = {}


def configurado():
    """True quando há URL, token, account e inbox — mínimo para registrar."""
    return bool(
        CHATWOOT_URL and CHATWOOT_API_TOKEN
        and CHATWOOT_ACCOUNT_ID and CHATWOOT_INBOX_ID
    )


def ativo():
    """True quando o registro está ligado E configurado."""
    return CHATWOOT_REGISTRO_ATIVO and configurado()


def descrever():
    """Texto curto para o menu."""
    if not configurado():
        return "Chatwoot — NÃO CONFIGURADO (faltam URL/token/account/inbox)"
    if not CHATWOOT_REGISTRO_ATIVO:
        return "Chatwoot — desativado (CHATWOOT_REGISTRO_ATIVO=false)"
    modo = "cria conversa" if CHATWOOT_CRIAR_CONVERSA else "só conversa existente"
    return f"Chatwoot — ativo ({modo}), inbox_id={CHATWOOT_INBOX_ID}"


def normalizar_telefone(telefone):
    """'51985171688' -> '+5551985171688' (E.164, formato aceito pelo Chatwoot)."""
    digitos = re.sub(r"\D", "", str(telefone or ""))
    if not digitos:
        return None
    if digitos.startswith("55") and len(digitos) in (12, 13):
        return f"+{digitos}"
    if len(digitos) in (10, 11):
        return f"+55{digitos}"
    return None


class _Cliente:
    """Cliente HTTP mínimo da API do Chatwoot."""

    def __init__(self):
        self.base = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}"
        self.headers = {
            "api_access_token": CHATWOOT_API_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get(self, caminho, params=None):
        return requests.get(
            f"{self.base}{caminho}", headers=self.headers,
            params=params or {}, timeout=CHATWOOT_TIMEOUT,
        )

    def post(self, caminho, json):
        return requests.post(
            f"{self.base}{caminho}", headers=self.headers,
            json=json, timeout=CHATWOOT_TIMEOUT,
        )


def variantes_telefone(telefone):
    """Gera as variantes E.164 brasileiras (com e sem o nono dígito).

    ⚠️ MOTIVO: o MESMO lead pode existir no Chatwoot com dois telefones:

        +5551982824693   (com o 9 — formato do banco de leads / mkt_01)
        +555182824693    (sem o 9 — é o `wa_id` que a Meta reporta no webhook)

    Se buscarmos só uma variante, criamos um CONTATO DUPLICADO para a mesma
    pessoa — e o histórico da conversa fica partido em dois.

    Returns:
        Lista com 1 ou 2 variantes E.164 (+55...), a do banco primeiro.
    """
    e164 = normalizar_telefone(telefone)
    if not e164:
        return []

    digitos = e164.lstrip("+")
    variantes = [e164]

    base = digitos[2:] if digitos.startswith("55") else digitos
    if len(base) == 11 and base[2] == "9":
        # 11 dígitos com o 9 → variante legada de 10 (remove o 9 do índice 2)
        variantes.append(f"+55{base[:2]}{base[3:]}")
    elif len(base) == 10:
        # 10 dígitos sem o 9 → variante moderna de 11 (insere o 9 no índice 2,
        # preservando os 8 dígitos finais)
        variantes.append(f"+55{base[:2]}9{base[2:]}")

    return variantes


def _buscar_contatos_candidatos(cliente, telefone_e164):
    """Retorna TODOS os contact_ids que casam com as variantes do telefone.

    Pode haver mais de um (contato duplicado: um com o 9, outro sem). Quem
    chama decide qual usar — normalmente o que já tem conversa.
    """
    chave = telefone_e164
    if chave in _cache_contato:
        return [_cache_contato[chave]]

    encontrados = []

    for variante in variantes_telefone(telefone_e164):
        try:
            r = cliente.get("/contacts/search", {"q": variante})
            if r.status_code != 200:
                continue
            dados = r.json() or {}
            for contato in dados.get("payload") or []:
                if (contato.get("phone_number") or "") == variante:
                    contact_id = contato.get("id")
                    if contact_id and contact_id not in encontrados:
                        encontrados.append(contact_id)
        except requests.RequestException as e:
            logger.debug("[CHATWOOT] erro ao buscar contato (%s): %s", variante, e)

    return encontrados


def _buscar_contato(cliente, telefone_e164):
    """Retorna o contact_id mais adequado (prefere quem já tem conversa).

    Retorna None quando não existe. Não cria nada.
    """
    chave = telefone_e164
    if chave in _cache_contato:
        return _cache_contato[chave]

    candidatos = _buscar_contatos_candidatos(cliente, telefone_e164)
    if not candidatos:
        return None

    escolhido = candidatos[0]
    if len(candidatos) > 1:
        # Contato duplicado: fica com o que já tem conversa (preserva histórico).
        for cid in candidatos:
            if _buscar_conversa(cliente, cid):
                escolhido = cid
                break
        logger.info(
            "[CHATWOOT] %d contatos para %s — usando id=%s",
            len(candidatos), chave, escolhido,
        )

    for v in variantes_telefone(telefone_e164):
        _cache_contato[v] = escolhido

    return escolhido


def _criar_contato(cliente, nome, telefone_e164):
    """Cria o contato no Chatwoot. Retorna contact_id ou None."""
    try:
        r = cliente.post("/contacts", {
            "name": nome or telefone_e164,
            "phone_number": telefone_e164,
            "inbox_id": int(CHATWOOT_INBOX_ID),
        })
        if r.status_code in (200, 201):
            dados = r.json() or {}
            payload = dados.get("payload") or {}
            contact_id = payload.get("contact", {}).get("id") or payload.get("id")
            if contact_id:
                _cache_contato[telefone_e164] = contact_id
                return contact_id
        logger.debug("[CHATWOOT] criar contato HTTP %s", r.status_code)
    except requests.RequestException as e:
        logger.debug("[CHATWOOT] erro ao criar contato: %s", e)
    return None


def _buscar_conversa(cliente, contact_id):
    """Retorna a conversa mais recente (não resolvida) do contato, ou None."""
    try:
        r = cliente.get(
            f"/contacts/{contact_id}/conversations",
        )
        if r.status_code == 200:
            dados = r.json() or {}
            payload = dados.get("payload") or []
            abertas = [c for c in payload if c.get("status") != "resolved"]
            if abertas:
                return abertas[0].get("id")
            if payload:
                return payload[0].get("id")
    except requests.RequestException as e:
        logger.debug("[CHATWOOT] erro ao buscar conversa: %s", e)
    return None


def _obter_source_id(cliente, contact_id, telefone_e164):
    """Descobre o `source_id` real do contato para o nosso inbox.

    ⚠️ POR QUE ISSO IMPORTA
    ----------------------
    O `source_id` não é necessariamente o telefone que calculamos. Ele depende
    de como o contato foi criado no Chatwoot:

        bridge (Meta webhook) -> '555182824693'   (wa_id, SEM o nono dígito)
        map_scraper           -> '5551982824693'  (com o nono dígito)
        cadastro manual       -> pode ser outro

    Criar a conversa com um `source_id` que não existe no contato retorna
    404 "Resource could not be found". Por isso lemos o `contact_inboxes`
    do próprio contato e usamos o que está lá.

    Returns:
        str com o source_id, ou None se não encontrado.
    """
    try:
        r = cliente.get(f"/contacts/{contact_id}")
        if r.status_code == 200:
            dados = (r.json() or {}).get("payload") or {}
            caixas = dados.get("contact_inboxes") or []
            # Prefere o source_id do nosso inbox; cai para o primeiro.
            for caixa in caixas:
                inbox = caixa.get("inbox") or {}
                if str(inbox.get("id")) == str(CHATWOOT_INBOX_ID):
                    sid = caixa.get("source_id")
                    if sid:
                        return str(sid)
            for caixa in caixas:
                sid = caixa.get("source_id")
                if sid:
                    return str(sid)
    except requests.RequestException as e:
        logger.debug("[CHATWOOT] erro ao obter source_id: %s", e)

    # Fallback: dígitos do telefone (funciona para contatos que nós criamos)
    digitos = re.sub(r"\D", "", str(telefone_e164 or ""))
    return digitos or None


def _criar_conversa(cliente, contact_id, telefone_e164):
    """Cria a conversa SEM mensagem inicial (evita envio ao lead).

    ⚠️ O `source_id` de um inbox WhatsApp Cloud precisa ser **apenas dígitos**:

        \\A(?:\\d{1,15}|[A-Z]{2}\\.(?:ENT\\.)?[A-Za-z0-9]{1,128})\\z

    Mandar o E.164 com '+' retorna:
        422 "Source invalid source id for whatsapp inbox"

    E o valor precisa existir nos `contact_inboxes` do contato — daí
    `_obter_source_id()`.
    """
    source_id = _obter_source_id(cliente, contact_id, telefone_e164)
    if not source_id:
        logger.debug("[CHATWOOT] sem source_id para contato %s", contact_id)
        return None

    try:
        r = cliente.post("/conversations", {
            "source_id": source_id,
            "inbox_id": int(CHATWOOT_INBOX_ID),
            "contact_id": contact_id,
            # ⚠️ SEM 'message': com message o Chatwoot ENVIA ao lead (duplo envio).
        })
        if r.status_code in (200, 201):
            return (r.json() or {}).get("id")
        logger.debug("[CHATWOOT] criar conversa HTTP %s: %s",
                     r.status_code, (r.text or "")[:300])
    except requests.RequestException as e:
        logger.debug("[CHATWOOT] erro ao criar conversa: %s", e)
    return None


def _criar_nota(cliente, conversa_id, texto):
    """Grava uma nota PRIVADA na conversa (o lead não recebe nada)."""
    try:
        r = cliente.post(f"/conversations/{conversa_id}/messages", {
            "content": texto,
            "message_type": "outgoing",
            "private": True,
        })
        return 200 <= r.status_code < 300
    except requests.RequestException as e:
        logger.debug("[CHATWOOT] erro ao criar nota: %s", e)
        return False


def registrar_envio(lead, template_nome, wamid=None, mensagem_log=None):
    """Registra o disparo no Chatwoot como nota privada.

    Args:
        lead: linha do DataFrame de leads (precisa de nome/telefone)
        template_nome: nome do template aprovado enviado
        wamid: id da mensagem retornado pela Meta (útil para rastreio)
        mensagem_log: texto do template do banco (só para a nota)

    Returns:
        True se registrou, False caso contrário.

    NUNCA levanta exceção: falha no Chatwoot não pode derrubar a campanha.
    """
    if not ativo():
        return False

    telefone_e164 = normalizar_telefone(
        lead.get("telefone") if hasattr(lead, "get") else None
    )
    if not telefone_e164:
        return False

    nome = ""
    try:
        nome = str(lead.get("nome") or "").strip()
    except Exception:
        pass

    cliente = _Cliente()

    try:
        contact_id = _buscar_contato(cliente, telefone_e164)
        if not contact_id:
            contact_id = _criar_contato(cliente, nome, telefone_e164)
        if not contact_id:
            logger.debug("[CHATWOOT] não foi possível obter contato de %s", telefone_e164)
            return False

        conversa_id = _buscar_conversa(cliente, contact_id)

        if not conversa_id:
            if not CHATWOOT_CRIAR_CONVERSA:
                # Modo econômico: não cria conversa nova.
                return False
            conversa_id = _criar_conversa(cliente, contact_id, telefone_e164)
            if not conversa_id:
                return False

        linhas = [f"📤 **Campanha enviada** — template `{template_nome}`"]
        if mensagem_log:
            resumo = str(mensagem_log).strip().replace("\n", " ")
            if len(resumo) > 180:
                resumo = resumo[:180] + "…"
            linhas.append(f"\n_{resumo}_")
        if wamid:
            linhas.append(f"\n`{wamid}`")

        return _criar_nota(cliente, conversa_id, "\n".join(linhas))

    except Exception as e:
        logger.warning("[CHATWOOT] Falha ao registrar envio (ignorado): %s", e)
        return False
