import pandas as pd
from playwright.sync_api import sync_playwright
import time
import urllib.parse

def extrair_leads_maps(nicho, localizacao):
    print(f"Buscando {nicho} em {localizacao} no Google Maps...")
    
    # Prepara a URL de busca
    termo_busca = urllib.parse.quote(f"{nicho} em {localizacao}")
    url = f"https://www.google.com/maps/search/{termo_busca}"

    leads = []

    with sync_playwright() as p:
        # headless=False abre o navegador para você ver o que está acontecendo
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        page.goto(url, timeout=60000)
        
        # Espera o painel de resultados carregar
        page.wait_for_selector('div[role="feed"]', timeout=15000)
        
        # O Google Maps carrega os resultados conforme você rola a página.
        # Vamos rolar o painel lateral 5 vezes para pegar mais resultados.
        print("Rolando a página para carregar mais resultados...")
        scrollable_div = page.query_selector('div[role="feed"]')
        for _ in range(5):
            page.evaluate('(element) => element.scrollTop = element.scrollHeight', scrollable_div)
            time.sleep(2) # Espera carregar

        # Pega todos os cards de empresas
        cards = page.query_selector_all('div[role="feed"] > div')
        
        print(f"Analisando {len(cards)} resultados encontrados...")

        for card in cards:
            try:
                # Nome da empresa
                nome_element = card.query_selector('div.fontHeadlineSmall')
                nome = nome_element.inner_text() if nome_element else ""
                
                if not nome: continue # Pula se não for um card válido

                # Link do site/Instagram (o Maps esconde os links dentro de um botão)
                # Vamos pegar todos os links que existem no card
                links = card.query_selector_all('a')
                link_insta = ""
                link_site = ""
                
                for a in links:
                    href = a.get_attribute('href')
                    if href:
                        if "instagram.com" in href:
                            link_insta = href
                        elif "http" in href and "google" not in href:
                            link_site = href

                # Telefone (tenta achar a classe do telefone)
                # Nota: O Maps só mostra o telefone se você clicar na empresa. 
                # Para pegar no painel, precisamos buscar o texto que parece telefone.
                # (Isso é uma aproximação, alguns podem vir vazios)
                telefone = ""
                text_content = card.inner_text()
                # Lógica simples para achar telefone no texto
                import re
                match = re.search(r'\(?\d{2}\)?\s?\d{4,5}-\d{4}', text_content)
                if match:
                    telefone = match.group(0)

                leads.append({
                    'Nome': nome,
                    'Telefone': telefone,
                    'Instagram': link_insta,
                    'Site': link_site
                })
                
            except Exception as e:
                # Se der erro em um card, apenas ignora e vai pro próximo
                pass

        browser.close()
    
    return pd.DataFrame(leads)

def main(nicho, localizacao):
    df_leads = extrair_leads_maps(nicho, localizacao)
    
    if df_leads.empty:
        print("Nenhum lead encontrado.")
        return

    nome_arquivo = f'leads_{nicho.replace(" ", "_")}.xlsx'
    df_leads.to_excel(nome_arquivo, index=False)
    print(f"\nProcesso concluído! Arquivo '{nome_arquivo}' gerado com {len(df_leads)} leads.")

if __name__ == "__main__":
    main("barbearia", "Porto Alegre")