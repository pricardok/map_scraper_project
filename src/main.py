# src/main.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.locations import (
    obter_estados,
    obter_cidades,
    obter_termos_busca,
    sincronizar_base_localidades,
)
from src.scraper import rodar_scraper_multithread
from src.database import LeadDatabase
from src.whatsapp import (
    disparar_campanha,
    MENSAGEM_PADRAO,
    WAHA_INTERVALO,
    WAHA_LIMITE,
    WAHA_ATIVO,
    SOMENTE_ENVIO,
)


def coletar_leads():
    df_estados = obter_estados()
    if df_estados.empty:
        return

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

    termos_busca = obter_termos_busca(cidade_escolhida, uf_escolhida)

    mostrar_navegador = input("\nVer o navegador? (S/N): ").strip().upper() == 'S'

    print("\nIniciando extração...")
    db = LeadDatabase()

    df_resultados = rodar_scraper_multithread(
        nicho=nicho,
        cidade=cidade_escolhida,
        uf=uf_escolhida,
        termos_lista=termos_busca,
        mostrar_navegador=mostrar_navegador,
        save_callback=db.save_leads,  # salvamento incremental (UPSERT) a cada área concluída
    )

    if not df_resultados.empty:
        print("\nLeads salvos incrementalmente no DuckDB (UPSERT).")
        db.export_to_excel(nicho, cidade_escolhida)
    else:
        print("Nenhum dado extraído.")

    db.close()


def enviar_whatsapp_menu():
    print("\n=== ENVIO WHATSAPP (WAHA) ===")

    if not WAHA_ATIVO:
        print("Envio de WhatsApp desativado (WAHA_ATIVO=false no .env).")
        return

    db = LeadDatabase()

    pendentes = db.get_leads_para_envio(limite=WAHA_LIMITE)
    if pendentes.empty:
        print("Nenhum lead celular pendente de envio.")
        db.close()
        return

    print(f"{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
    if WAHA_LIMITE:
        print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")

    print(f"Mensagem padrão: {MENSAGEM_PADRAO}")
    mensagem = input("Digite a mensagem (ou Enter para usar a padrão): ").strip()
    if not mensagem:
        mensagem = MENSAGEM_PADRAO

    confirmar = input(f"Enviar para {len(pendentes)} lead(s)? (S/N): ").strip().upper()
    if confirmar != 'S':
        print("Envio cancelado.")
        db.close()
        return

    disparar_campanha(db, mensagem_template=mensagem, intervalo=WAHA_INTERVALO, limite=WAHA_LIMITE)
    db.close()


def menu_interativo():
    # Flag de linha de comando: `python src/main.py --so-enviar` pula a coleta
    # e vai direto para o envio (equivale a SOMENTE_ENVIO=true no .env).
    so_enviar_cli = "--so-enviar" in sys.argv

    if SOMENTE_ENVIO or so_enviar_cli:
        enviar_whatsapp_menu()
        return

    while True:
        print("\n=== MAP SCRAPER ===")
        print("1 - Coletar leads")
        print("2 - Enviar mensagens WhatsApp")
        print("3 - Sincronizar base de localidades (IBGE)")
        print("4 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            coletar_leads()
        elif opcao == "2":
            enviar_whatsapp_menu()
        elif opcao == "3":
            sincronizar_base_localidades()
        elif opcao == "4":
            print("Até mais!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu_interativo()