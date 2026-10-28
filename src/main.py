# src/main.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.locations import obter_estados, obter_cidades, obter_termos_busca
from src.scraper import rodar_scraper_multithread
from src.database import LeadDatabase

def menu_interativo():
    print("=== 🗺️  MAP SCRAPER PRO - V3 ===")
    
    df_estados = obter_estados()
    if df_estados.empty: return

    uf_escolhida = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
    if uf_escolhida not in df_estados['uf'].values:
        print("UF inválida.")
        return

    cidades = obter_cidades(uf_escolhida)
    termo_cidade = input("Digite o nome da cidade: ").strip().title()
    cidades_filtradas = [c for c in cidades if termo_cidade in c]
    
    if not cidades_filtradas:
        print("Cidade não encontrada.")
        return
    elif len(cidades_filtradas) > 1:
        cidade_escolhida = input(f"Várias encontradas ({', '.join(cidades_filtradas[:3])}...). Digite o nome exato: ").strip().title()
    else:
        cidade_escolhida = cidades_filtradas[0]

    nicho = input(f"\nQual o nicho para {cidade_escolhida}-{uf_escolhida}? ").strip().lower()

    # Agora busca a cidade inteira
    termos_busca = obter_termos_busca(cidade_escolhida, uf_escolhida)
    
    mostrar_navegador = input("\nVer o navegador? (S/N): ").strip().upper() == 'S'
    
    print("\nIniciando extração...")
    df_resultados = rodar_scraper_multithread(
        nicho=nicho, 
        cidade=cidade_escolhida, 
        uf=uf_escolhida, 
        termos_lista=termos_busca, 
        mostrar_navegador=mostrar_navegador
    )

    if not df_resultados.empty:
        print("\nSalvando dados no DuckDB (UPSERT)...")
        db = LeadDatabase()
        qtd_salvos = db.save_leads(df_resultados)
        print(f"Processados {qtd_salvos} leads (novos ou atualizados).")
        
        db.export_to_excel(nicho, cidade_escolhida)
        db.close()
    else:
        print("Nenhum dado extraído.")

if __name__ == "__main__":
    menu_interativo()