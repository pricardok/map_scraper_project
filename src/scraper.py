# src/scraper.py
from playwright.sync_api import sync_playwright
import time
import random
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import threading
from src.utils import formatar_telefone

lock = threading.Lock()

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

MAX_ROLAGENS = 40
MAX_RODADAS_ESTAGNADAS = 3


def _montar_query(nicho, termo_busca, cidade, uf):
    if termo_busca.strip().lower() == cidade.strip().lower():
        return f"{nicho} em {cidade}, {uf}"
    return f"{nicho} em {termo_busca}, {cidade}, {uf}"


def _navegar_com_retry(page, url, tentativas=3, timeout=30000):
    """Navega com retry e backoff exponencial para erros transitórios."""
    for tentativa in range(1, tentativas + 1):
        try:
            page.goto(url, timeout=timeout)
            return True
        except Exception as e:
            print(f"  Retry {tentativa}/{tentativas} ao navegar para {url}: {e}")
            time.sleep(2 * tentativa)
    return False


def _obter_urls_perfis(page):
    urls = set()
    for link in page.query_selector_all('a[href*="/maps/place/"]'):
        href = link.get_attribute('href')
        if href:
            urls.add(href)
    return urls


def _rolar_resultados(page):
    """Rola a lista até esgotar os resultados (ou atingir o limite de rolagens)."""
    ultimo_total = 0
    rodadas_estagnadas = 0
    for _ in range(MAX_ROLAGENS):
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

        if not _navegar_com_retry(page, url, timeout=60000):
            print(f"[{termo_busca}] Falha ao carregar a busca.")
            return []

        try:
            page.wait_for_selector('div[role="feed"]', timeout=10000)
        except Exception:
            print(f"[{termo_busca}] Nenhum resultado encontrado.")
            return []

        print(f"[{termo_busca}] Rolando resultados...")
        _rolar_resultados(page)

        urls = sorted(_obter_urls_perfis(page))
        print(f"[{termo_busca}] {len(urls)} perfis encontrados. Extraindo dados...")

        for i, place_url in enumerate(urls):
            try:
                time.sleep(random.uniform(0.8, 2.5))  # pausa anti-bloqueio entre navegações
                if not _navegar_com_retry(page, place_url, timeout=30000):
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

            except Exception as e:
                print(f"[{termo_busca}] Erro ao extrair {place_url}: {e}")

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