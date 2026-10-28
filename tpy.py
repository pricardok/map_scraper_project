import pandas as pd
from playwright.sync_api import sync_playwright
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

lock = threading.Lock()

def extrair_leads_bairro(nicho, bairro, cidade, mostrar_navegador=False):
    """Extrai leads de um bairro visitando a URL de cada empresa diretamente."""
    p = sync_playwright().start()
    browser = None
    try:
        browser = p.chromium.launch(headless=not mostrar_navegador)
        page = browser.new_page()
        
        termo_busca = urllib.parse.quote(f"{nicho} em {bairro}, {cidade}")
        url = f"https://www.google.com/maps/search/{termo_busca}"
        page.goto(url, timeout=60000)
        
        try:
            page.wait_for_selector('div[role="feed"]', timeout=15000)
        except:
            print(f"[{bairro}] Nenhum resultado encontrado.")
            return []
        
        print(f"[{bairro}] Rolando página para carregar resultados...")
        # Rola a página para carregar mais resultados
        for _ in range(4):
            page.evaluate('''() => {
                const feed = document.querySelector('div[role="feed"]');
                if(feed) feed.scrollTop = feed.scrollHeight;
            }''')
            time.sleep(2)
        
        # Em vez de clicar nos cards, vamos extrair os links (URLs) de cada empresa
        links_elements = page.query_selector_all('a[href*="/maps/place/"]')
        urls = []
        for link in links_elements:
            href = link.get_attribute('href')
            if href and href not in urls:
                urls.append(href)
        
        total = len(urls)
        print(f"[{bairro}] Encontrados {total} perfis únicos. Iniciando extração...")
        
        leads = []
        for i, place_url in enumerate(urls):
            try:
                # Vai direto para a página da empresa
                page.goto(place_url, timeout=30000)
                time.sleep(2) # Espera a página carregar
                
                # Nome da empresa (agora é o único H1 da página de detalhes)
                nome_elem = page.query_selector('h1')
                nome = nome_elem.inner_text() if nome_elem else "Sem nome"
                
                # Telefone
                telefone = ""
                tel_elem = page.query_selector('button[data-item-id^="phone:tel:"]')
                if tel_elem:
                    aria = tel_elem.get_attribute('aria-label')
                    if aria:
                        telefone = aria.replace('Telefone:', '').replace('Phone:', '').strip()
                
                # Site e Instagram
                link_site = ""
                link_insta = ""
                
                site_elem = page.query_selector('a[data-item-id="authority"]')
                if site_elem:
                    link_site = site_elem.get_attribute('href')
                
                # Procura o Instagram em todos os links da página
                for a in page.query_selector_all('a'):
                    href = a.get_attribute('href')
                    if href and "instagram.com" in href:
                        link_insta = href
                        break
                        
                leads.append({
                    'Nome': nome,
                    'Telefone': telefone,
                    'Instagram': link_insta,
                    'Site': link_site,
                    'Bairro': bairro
                })
                print(f"[{bairro}] {i+1}/{total} - {nome}")
                
            except Exception as e:
                print(f"[{bairro}] Erro ao processar URL {place_url}: {e}")
                continue
                
        return leads
        
    finally:
        if browser:
            browser.close()
        p.stop()

def main(nicho, cidade, mostrar_navegador=False):
    # Lista de bairros de Porto Alegre (você pode alterar para a sua cidade)
    bairros = [
        "Centro Histórico", "Cidade Baixa", "Moinhos de Vento", "Bela Vista", 
        "Menino Deus", "Azenha", "Partenon", "Petrópolis", "Tristeza", "Zona Sul"
    ]
    
    print(f"Bairros a processar: {bairros}")
    todos_leads = []
    
    # Usando 3 threads para não sobrecarregar o computador (cada thread abre um navegador)
    max_workers = min(3, len(bairros))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = {
            executor.submit(extrair_leads_bairro, nicho, bairro, cidade, mostrar_navegador): bairro
            for bairro in bairros
        }
        
        for futuro in as_completed(futuros):
            bairro = futuros[futuro]
            try:
                leads_bairro = futuro.result()
                with lock:
                    todos_leads.extend(leads_bairro)
                print(f"✅ Bairro {bairro} concluído. Total parcial: {len(todos_leads)} leads.")
            except Exception as e:
                print(f"❌ Erro no bairro {bairro}: {e}")
    
    if not todos_leads:
        print("Nenhum lead encontrado.")
        return
    
    df = pd.DataFrame(todos_leads)
    # Remove duplicatas pelo nome (pode acontecer de aparecer em mais de um bairro)
    df = df.drop_duplicates(subset=['Nome'])
    
    nome_arquivo = f'leads_{nicho.replace(" ", "_")}_{cidade.replace(" ", "_")}.xlsx'
    df.to_excel(nome_arquivo, index=False)
    print(f"\n🎉 Processo concluído! {len(df)} leads únicos salvos em '{nome_arquivo}'.")

if __name__ == "__main__":
    MOSTRAR_NAVEGADOR = False
    main("barbearia", "Porto Alegre", mostrar_navegador=MOSTRAR_NAVEGADOR)