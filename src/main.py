# src/main.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.locations import (
    obter_estados,
    obter_cidades,
    obter_termos_busca,
    obter_municipio,
    filtrar_cidades,
    sincronizar_base_localidades,
    listar_municipios_pendentes,
    aquecer_bairros_uf,
    SALVAR as LOCALIDADES_SALVAR,
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
    termo_cidade = input("Digite o nome da cidade: ").strip()
    cidades_filtradas = filtrar_cidades(cidades, termo_cidade)

    if not cidades_filtradas:
        print("Cidade não encontrada.")
        return
    elif len(cidades_filtradas) > 1:
        cidade_escolhida = input(
            f"Várias encontradas ({', '.join(cidades_filtradas[:3])}...). Digite o nome exato: "
        ).strip()
        exatos = filtrar_cidades(cidades, cidade_escolhida)
        cidade_escolhida = exatos[0] if exatos else cidade_escolhida
    else:
        cidade_escolhida = cidades_filtradas[0]

    # Confirma o município no IBGE e passa a usar o nome oficial (com acentos).
    municipio = obter_municipio(cidade_escolhida, uf_escolhida)
    if municipio:
        cidade_escolhida = municipio["nome"]
        print(f"Município (IBGE): {cidade_escolhida}-{uf_escolhida} | código {municipio['id_municipio']}")
    else:
        print(f"Aviso: {cidade_escolhida}-{uf_escolhida} não foi confirmado no IBGE.")

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


def aquecer_bairros_menu():
    """Prepara o cache de bairros de uma UF inteira (sem raspar leads)."""
    print("\n=== AQUECER BAIRROS DE UMA UF ===")

    if not LOCALIDADES_SALVAR:
        print("LOCALIDADES_SALVAR=false: o aquecimento está desativado.")
        print("Ative a flag LOCALIDADES_SALVAR no .env para gravar os bairros.")
        return

    print("Resolve e grava os bairros de todas as cidades da UF, uma única vez.")
    print("Depois disso a coleta por cidade não consulta mais IBGE/OSM.")

    df_estados = obter_estados()
    if df_estados.empty:
        print("Não foi possível obter a lista de estados.")
        return

    uf = input("Digite a UF (ex: RS, SP, RJ): ").strip().upper()
    if uf not in df_estados['uf'].values:
        print("UF inválida.")
        return

    print(f"\nVerificando quais cidades de {uf} ainda precisam de bairros...")
    pendentes = listar_municipios_pendentes(uf)
    if not pendentes:
        print(f"Todas as cidades de {uf} já estão na base local. Nada a fazer.")
        return

    print(f"{len(pendentes)} cidade(s) pendente(s) em {uf}.")
    print("As cidades cobertas pelo IBGE são instantâneas; as demais usam o")
    print("OpenStreetMap (Nominatim + Overpass), com pausa entre elas.")

    limite = input("Quantas cidades processar agora? (Enter = todas): ").strip()
    max_cidades = 0
    if limite:
        try:
            max_cidades = max(1, int(limite))
        except ValueError:
            print("Valor inválido. Usando todas.")
            max_cidades = 0

    previstas = min(max_cidades, len(pendentes)) if max_cidades else len(pendentes)
    confirmar = input(f"Processar {previstas} cidade(s)? (S/N): ").strip().upper()
    if confirmar != 'S':
        print("Operação cancelada.")
        return

    aquecer_bairros_uf(uf, cidades=pendentes, max_cidades=max_cidades)


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
        print("4 - Aquecer bairros de uma UF (OpenStreetMap)")
        print("5 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            coletar_leads()
        elif opcao == "2":
            enviar_whatsapp_menu()
        elif opcao == "3":
            sincronizar_base_localidades()
        elif opcao == "4":
            aquecer_bairros_menu()
        elif opcao == "5":
            print("Até mais!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu_interativo()