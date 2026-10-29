# src/scraper.py
from playwright.sync_api import sync_playwright
import time
import random
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import threading
from src.config import env_int
from src.utils import formatar_telefone

lock = threading.Lock()

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

MAX_ROLAGENS = 40
MAX_RODADAS_ESTAGNADAS = 3

# --- Anti-bloqueio (captcha) -------------------------------------------------
# CAPTCHA_MAX_TENTATIVAS: quantas vezes uma mesma página é tentada antes de
#   abortar a área (1 = nem tenta de novo, só pausa e desiste).
# CAPTCHA_PAUSA_SEGUNDOS: pausa longa feita pela thread que levou o bloqueio.
# CAPTCHA_PAUSA_GLOBAL_SEGUNDOS: pausa compartilhada, aplicada a TODAS as
#   threads assim que uma delas detecta bloqueio (evita que as outras insistam).
CAPTCHA_MAX_TENTATIVAS = max(1, env_int("CAPTCHA_MAX_TENTATIVAS", 2))
CAPTCHA_PAUSA_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_SEGUNDOS", 300))
CAPTCHA_PAUSA_GLOBAL_SEGUNDOS = max(0, env_int("CAPTCHA_PAUSA_GLOBAL_SEGUNDOS", 180))

_MARCADORES_CAPTCHA = (
    "unusual traffic",
    "tráfego incomum",
    "trafego incomum",
    "não é possível acessar",
    "nao e possivel acessar",
    "our systems have detected",
    "digite os caracteres",
    "não sou um robô",
    "i'm not a robot",
)

_SELETORES_BLOQUEIO = (
    'form[action*="sorry"]',
    "#captcha-form",
    "#recaptcha",
    ".g-recaptcha",
    'iframe[src*="recaptcha"]',
    'iframe[src*="hcaptcha"]',
)

_cooldown_ate = 0.0
_cooldown_lock = threading.Lock()


class BloqueioDetectado(Exception):
    """Google Maps devolveu captcha/tela de bloqueio para a busca atual."""


def _montar_query(nicho, termo_busca, cidade, uf):
    if termo_busca.strip().lower() == cidade.strip().lower():
        return f"{nicho} em {cidade}, {uf}"
    return f"{nicho} em {termo_busca}, {cidade}, {uf}"


def _pagina_bloqueada(page, checar_texto=True):
    """Detecta captcha / tela de 'tráfego incomum' do Google."""
    try:
        url = (page.url or "").lower()
    except Exception:
        return False
    if "/sorry/" in url:
        return True

    try:
        for seletor in _SELETORES_BLOQUEIO:
            if page.query_selector(seletor):
                return True
    except Exception:
        return False

    if not checar_texto:
        return False

    try:
        texto = (page.inner_text("body") or "")[:4000].lower()
    except Exception:
        return False
    return any(marcador in texto for marcador in _MARCADORES_CAPTCHA)


def _marcar_bloqueio_global():
    """Coloca todas as threads em pausa (cooldown compartilhado)."""
    global _cooldown_ate
    if CAPTCHA_PAUSA_GLOBAL_SEGUNDOS <= 0:
        return
    with _cooldown_lock:
        _cooldown_ate = max(_cooldown_ate, time.time() + CAPTCHA_PAUSA_GLOBAL_SEGUNDOS)


def _aguardar_cooldown(termo):
    """Espera o cooldown global, se alguma thread detectou bloqueio."""
    with _cooldown_lock:
        restante = _cooldown_ate - time.time()
    if restante <= 0:
        return

    print(f"[{termo}] Pausa global anti-bloqueio: aguardando {int(restante) + 1}s...")
    while restante > 0:
        time.sleep(min(restante, 10))
        with _cooldown_lock:
            restante = _cooldown_ate - time.time()


def _pausar_com_aviso(segundos, termo):
    print(f"[{termo}] Aguardando {segundos}s (pausa longa anti-bloqueio)...")
    restante = segundos
    while restante > 0:
        passo = min(restante, 15)
        time.sleep(passo)
        restante -= passo


def _navegar_com_retry(page, url, tentativas=3, timeout=30000, termo="?"):
    """Navega com retry e backoff; detecta captcha e aplica pausa longa.

    Levanta BloqueioDetectado quando o bloqueio persiste após as tentativas.
    """
    for tentativa in range(1, tentativas + 1):
        _aguardar_cooldown(termo)
        try:
            page.goto(url, timeout=timeout)
        except Exception as e:
            print(f"  Retry {tentativa}/{tentativas} ao navegar para {url}: {type(e).__name__}")
            time.sleep(2 * tentativa)
            continue

        if not _pagina_bloqueada(page):
            return True

        _marcar_bloqueio_global()
        print(f"[{termo}] ⚠ Google Maps bloqueou o acesso (captcha/tráfego incomum).")

        if tentativa >= min(tentativas, CAPTCHA_MAX_TENTATIVAS):
            print(f"[{termo}] Bloqueio persistente após {tentativa} tentativa(s). Abortando esta área.")
            raise BloqueioDetectado(termo)

        _pausar_com_aviso(CAPTCHA_PAUSA_SEGUNDOS, termo)

    return False


def _obter_urls_perfis(page):
    urls = set()
    for link in page.query_selector_all('a[href*="/maps/place/"]'):
        href = link.get_attribute('href')
        if href:
            urls.add(href)
    return urls


def _rolar_resultados(page, termo="?"):
    """Rola a lista até esgotar os resultados (ou atingir o limite de rolagens)."""
    ultimo_total = 0
    rodadas_estagnadas = 0
    for _ in range(MAX_ROLAGENS):
        if _pagina_bloqueada(page, checar_texto=False):
            _marcar_bloqueio_global()
            raise BloqueioDetectado(termo)

        total = len(_obter_urls_perfis(page))
        page.evaluate('''() => {
            const feed = document.querySelector('div[role="feed"]');
            if(feed) feed.scrollTop = feed.scrollHeight;
        }''')
        time.sleep(1.0 + random.uniform(0, 0.6))  # jitter anti-bloqueio

        if total == ultimo_total:
            rodadas_estagnadas += 1
            if rodadas_estagnadas >= MAX_RODADAS_ESTAGNADAS:
                break
        else:
            rodadas_estagnadas = 0
        ultimo_total = total


def extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False):
    query = _montar_query(nicho, termo_busca, cidade, uf)
    url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
    leads = []

    p = sync_playwright().start()
    browser = None
    try:
        browser = p.chromium.launch(headless=not mostrar_navegador)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 768},
            locale="pt-BR",
        )
        page = context.new_page()

        if not _navegar_com_retry(page, url, timeout=60000, termo=termo_busca):
            print(f"[{termo_busca}] Falha ao carregar a busca.")
            return leads

        try:
            page.wait_for_selector('div[role="feed"]', timeout=10000)
        except Exception:
            print(f"[{termo_busca}] Nenhum resultado encontrado.")
            return leads

        print(f"[{termo_busca}] Rolando resultados...")
        _rolar_resultados(page, termo_busca)

        if _pagina_bloqueada(page):
            _marcar_bloqueio_global()
            raise BloqueioDetectado(termo_busca)

        urls = sorted(_obter_urls_perfis(page))
        print(f"[{termo_busca}] {len(urls)} perfis encontrados. Extraindo dados...")

        for i, place_url in enumerate(urls):
            try:
                time.sleep(random.uniform(0.8, 2.5))  # pausa anti-bloqueio entre navegações
                if not _navegar_com_retry(page, place_url, timeout=30000, termo=termo_busca):
                    continue
                time.sleep(random.uniform(1.2, 2.8))

                nome_elem = page.query_selector('h1')
                nome = nome_elem.inner_text() if nome_elem else "Sem nome"
                if nome in ("Resultados", ""):
                    continue

                # Extração do Bairro (Endereço)
                bairro_real = "Não Informado"
                endereco_elem = page.query_selector('button[data-item-id="address"]')
                if endereco_elem:
                    aria_endereco = endereco_elem.get_attribute('aria-label')
                    if aria_endereco:
                        texto_limpo = aria_endereco.replace('Endereço:', '').replace('Address:', '').strip()
                        try:
                            parts = texto_limpo.split(" - ")
                            if len(parts) >= 2:
                                bairro_real = parts[1].split(",")[0].strip()
                        except Exception:
                            pass

                # Extração do Telefone
                telefone_bruto = ""
                tel_elem = page.query_selector('button[data-item-id^="phone:tel:"]')
                if tel_elem:
                    aria = tel_elem.get_attribute('aria-label')
                    if aria:
                        telefone_bruto = aria.replace('Telefone:', '').replace('Phone:', '').strip()

                telefone_limpo, tipo_telefone, whatsapp_link = formatar_telefone(telefone_bruto)

                link_site = ""
                link_insta = ""

                site_elem = page.query_selector('a[data-item-id="authority"]')
                if site_elem:
                    link_site = site_elem.get_attribute('href')

                for a in page.query_selector_all('a'):
                    href = a.get_attribute('href')
                    if href and "instagram.com" in href:
                        link_insta = href
                        break

                leads.append({
                    'nome': nome,
                    'telefone': telefone_limpo,
                    'tipo_telefone': tipo_telefone,
                    'whatsapp_link': whatsapp_link,
                    'instagram': link_insta,
                    'site': link_site,
                    'bairro': bairro_real,
                    'cidade': cidade,
                    'estado': uf,
                    'nicho': nicho
                })
                print(f"[{termo_busca}] {i+1}/{len(urls)} - {nome} | {tipo_telefone} | {telefone_limpo}")

            except BloqueioDetectado:
                raise
            except Exception as e:
                print(f"[{termo_busca}] Erro ao extrair {place_url}: {e}")

    except BloqueioDetectado:
        print(f"[{termo_busca}] Área interrompida por bloqueio do Google Maps "
              f"({len(leads)} lead(s) preservado(s)).")
    finally:
        if browser:
            browser.close()
        p.stop()

    return leads


def rodar_scraper_multithread(nicho, cidade, uf, termos_lista, mostrar_navegador=False, save_callback=None):
    """
    Executa a coleta em multithread. Se save_callback for informado, cada lote
    (por área) é salvo assim que termina, evitando perder a coleta em caso de falha.
    """
    todos_leads = []
    vistos = set()
    max_workers = min(3, len(termos_lista))
    print(f"Iniciando scraper com {max_workers} threads em {len(termos_lista)} área(s)...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = {
            executor.submit(extrair_leads_local, nicho, termo, cidade, uf, mostrar_navegador): termo
            for termo in termos_lista
        }

        for futuro in as_completed(futuros):
            termo = futuros[futuro]
            try:
                leads_area = futuro.result()
                with lock:
                    novos = []
                    for lead in leads_area:
                        chave = (lead['nome'], lead['cidade'])
                        if chave not in vistos:
                            vistos.add(chave)
                            novos.append(lead)
                    todos_leads.extend(novos)

                if novos and save_callback:
                    save_callback(pd.DataFrame(novos))

                print(f"[{termo}] Finalizado. {len(novos)} leads novos (acumulado: {len(todos_leads)}).")
            except Exception as e:
                print(f"Erro na busca {termo}: {e}")

    return pd.DataFrame(todos_leads)