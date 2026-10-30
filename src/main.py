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
    enviar_texto_numero,
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


def _confirmar(texto):
    """Pergunta S/N e retorna True para respostas afirmativas."""
    return input(texto).strip().upper() in ("S", "SIM", "Y", "YES")


def _escolher_template(templates):
    """Lista os templates ativos e retorna a mensagem escolhida pelo usuário."""
    print("\nTemplates ativos:")
    for t in templates:
        segmento = t.get("segmento")
        sufixo = f"  [{segmento}]" if segmento else ""
        print(f"  {t['id']} - {t['descricao']}{sufixo}")

    escolha = input("Escolha o template (Enter = primeiro): ").strip()
    if not escolha:
        return templates[0]["mensagem"]

    for t in templates:
        if str(t["id"]) == escolha:
            return t["mensagem"]

    print("Opção inválida. Usando o primeiro template.")
    return templates[0]["mensagem"]


def _escolher_filtros():
    """Pergunta os filtros de envio; Enter = sem filtro (todos os leads)."""
    print("\n=== FILTROS DE ENVIO ===")
    print("0 - Todos (sem filtro)")
    print("1 - Por número")
    print("2 - Por cidade")
    print("3 - Por nicho")
    opcao = input("Escolha um filtro (Enter = 0): ").strip() or "0"

    numero = cidade = nicho = None
    if opcao == "1":
        numero = input("Número (completo ou parte): ").strip() or None
    elif opcao == "2":
        cidade = input("Cidade: ").strip() or None
    elif opcao == "3":
        nicho = input("Nicho: ").strip() or None
    elif opcao != "0":
        print("Opção inválida. Usando 'Todos'.")
    return numero, cidade, nicho


def testar_envio(db, mensagem, pendentes=None):
    """Envia um teste para um número digitado ou para um lead pendente.

    `pendentes` (opcional): DataFrame já filtrado; se None, busca até 10 pendentes.
    """
    print("\n--- TESTE DE ENVIO ---")
    print("1 - Digitar um número de teste")
    print("2 - Escolher um lead pendente")
    opcao = input("Escolha: ").strip()

    numero = None
    if opcao == "1":
        numero = input("Digite o número com DDD (ex: 51999998888): ").strip()
    elif opcao == "2":
        if pendentes is None:
            pendentes = db.get_leads_para_envio(limite=10)
        if pendentes.empty:
            print("Nenhum lead pendente para testar.")
            return
        amostra = pendentes.head(10)
        print("Leads pendentes:")
        for i, (_, lead) in enumerate(amostra.iterrows(), 1):
            print(f"  {i} - {lead['nome']} ({lead['telefone']})")
        escolha = input("Escolha o número do lead: ").strip()
        if not escolha.isdigit() or not (1 <= int(escolha) <= len(amostra)):
            print("Escolha inválida.")
            return
        numero = amostra.iloc[int(escolha) - 1]["telefone"]
    else:
        print("Opção inválida.")
        return

    if not numero:
        print("Nenhum número informado.")
        return

    try:
        enviar_texto_numero(numero, mensagem)
        print(f"✅ Teste enviado para {numero}")
    except Exception as e:
        print(f"❌ Falha no teste para {numero}: {e}")


def enviar_whatsapp_menu():
    print("\n=== ENVIO WHATSAPP (WAHA) ===")

    if not WAHA_ATIVO:
        print("Envio de WhatsApp desativado (WAHA_ATIVO=false no .env).")
        return

    db = LeadDatabase()

    templates = db.listar_templates_ativos()
    if not templates:
        print("Nenhum template ativo. Cadastre um template na tabela templates_whatsapp.")
        db.close()
        return

    mensagem = _escolher_template(templates)

    numero_f, cidade_f, nicho_f = _escolher_filtros()

    pendentes = db.get_leads_para_envio(
        limite=WAHA_LIMITE, numero=numero_f, cidade=cidade_f, nicho=nicho_f
    )

    if _confirmar("Deseja fazer um envio de teste antes? (S/N): "):
        testar_envio(db, mensagem, pendentes=pendentes)

    if pendentes.empty:
        print("Nenhum lead celular pendente de envio (com os filtros aplicados).")
        db.close()
        return

    print(f"\n{len(pendentes)} lead(s) celular(es) pendentes (fixos são ignorados).")
    if WAHA_LIMITE:
        print(f"Limite configurado: {WAHA_LIMITE} lead(s) por campanha.")

    if not _confirmar(f"Enviar para {len(pendentes)} lead(s)? (S/N): "):
        print("Envio cancelado.")
        db.close()
        return

    disparar_campanha(
        db,
        mensagem_template=mensagem,
        intervalo=WAHA_INTERVALO,
        limite=WAHA_LIMITE,
        leads=pendentes,
    )
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