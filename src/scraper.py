# src/scraper.py
from playwright.sync_api import sync_playwright
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import threading
from src.utils import formatar_telefone

lock = threading.Lock()

def extrair_leads_local(nicho, termo_busca, cidade, uf, mostrar_navegador=False):
    query = urllib.parse.quote(f"{nicho} em {termo_busca}, {uf}")
    url = f"https://www.google.com/maps/search/{query}"
    leads = []
    
    p = sync_playwright().start()
    browser = None
    try:
        browser = p.chromium.launch(headless=not mostrar_navegador)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        
        try:
            page.wait_for_selector('div[role="feed"]', timeout=10000)
        except:
            print(f"[{termo_busca}] Nenhum resultado encontrado.")
            return []
            
        print(f"[{termo_busca}] Rolando página...")
        for _ in range(4):
            page.evaluate('''() => {
                const feed = document.querySelector('div[role="feed"]');
                if(feed) feed.scrollTop = feed.scrollHeight;
            }''')
            time.sleep(1.5)
            
        links_elements = page.query_selector_all('a[href*="/maps/place/"]')
        urls = list(set([link.get_attribute('href') for link in links_elements if link.get_attribute('href')]))
        
        print(f"[{termo_busca}] {len(urls)} perfis encontrados. Extraindo dados...")
        
        for i, place_url in enumerate(urls):
            try:
                page.goto(place_url, timeout=30000)
                time.sleep(2)
                
                nome_elem = page.query_selector('h1')
                nome = nome_elem.inner_text() if nome_elem else "Sem nome"
                if nome == "Resultados" or nome == "": continue
                
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
                
                # NOVO: Recebe os 3 valores (limpo, tipo, link_whatsapp)
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
                    'telefone': telefone_limpo,       # Salva apenas números
                    'tipo_telefone': tipo_telefone,
                    'whatsapp_link': whatsapp_link,   # Salva o link pronto
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

def rodar_scraper_multithread(nicho, cidade, uf, termos_lista, mostrar_navegador=False):
    todos_leads = []
    max_workers = min(3, len(termos_lista))
    print(f"Iniciando scraper com {max_workers} threads...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = {
            executor.submit(extrair_leads_local, nicho, termo, cidade, uf, mostrar_navegador): termo
            for termo in termos_lista
        }
        
        for futuro in as_completed(futuros):
            termo = futuros[futuro]
            try:
                leads_bairro = futuro.result()
                with lock:
                    todos_leads.extend(leads_bairro)
                print(f"[{termo}] Finalizado.")
            except Exception as e:
                print(f"Erro na busca {termo}: {e}")
                
    return pd.DataFrame(todos_leads)