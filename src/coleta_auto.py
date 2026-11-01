# src/coleta_auto.py
"""Coleta automática não-interativa (para rodar em container/servidor).

Substitui o menu interativo por um loop contínuo orientado a variáveis de
ambiente — nada de `input()`. Toda a configuração vem do `.env`:

    NICHO            nicho a coletar (default: barbearias)
    UFS              lista de UFs separadas por vírgula (vazio = todas)
    MAX_CIDADES      quantas cidades coletar por UF (0 = todas)
    MAX_BAIRROS      quantos bairros usar por cidade (default: 30)
    AQUECER_BAIRROS  pré-resolver bairros da UF antes de coletar (true/false)
    SINCRONIZAR      baixar estados/municípios/distritos do IBGE antes (true/false)
    MOSTRAR_NAVEGADOR abrir o Chromium visível (true/false, default false)
    EXPORTAR_EXCEL   gerar Excel por cidade (true/false, default false)
    LOOP             rodar em loop contínuo (true/false, default false)
    LOOP_PAUSA_SEGUNDOS pausa entre ciclos quando LOOP=true (default 3600)

Uso:
    python src/coleta_auto.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import carregar_env, str_para_bool, env_int
from src.locations import (
    obter_estados,
    obter_cidades,
    obter_termos_busca,
    aquecer_bairros_uf,
    sincronizar_base_localidades,
)
from src.scraper import rodar_scraper_multithread
from src.database import LeadDatabase

carregar_env()

NICHO = os.environ.get("NICHO", "barbearias").strip().lower()
UFS = [u.strip().upper() for u in os.environ.get("UFS", "").split(",") if u.strip()]
MAX_CIDADES = max(0, env_int("MAX_CIDADES", 0))
MAX_BAIRROS = max(1, env_int("MAX_BAIRROS", 30))
AQUECER_BAIRROS = str_para_bool(os.environ.get("AQUECER_BAIRROS"), padrao=False)
SINCRONIZAR = str_para_bool(os.environ.get("SINCRONIZAR"), padrao=False)
MOSTRAR_NAVEGADOR = str_para_bool(os.environ.get("MOSTRAR_NAVEGADOR"), padrao=False)
EXPORTAR_EXCEL = str_para_bool(os.environ.get("EXPORTAR_EXCEL"), padrao=False)
LOOP = str_para_bool(os.environ.get("LOOP"), padrao=False)
LOOP_PAUSA_SEGUNDOS = max(0, env_int("LOOP_PAUSA_SEGUNDOS", 3600))


def _resolver_ufs():
    """UFs alvo: as da env, ou todas do IBGE se vazio."""
    if UFS:
        return UFS
    df = obter_estados()
    if df.empty:
        return []
    return sorted(df["uf"].tolist())


def _coletar_cidade(db, cidade, uf):
    print(f"\n=== {cidade}-{uf} ({NICHO}) ===")
    termos = obter_termos_busca(cidade, uf, max_bairros=MAX_BAIRROS)
    df = rodar_scraper_multithread(
        nicho=NICHO,
        cidade=cidade,
        uf=uf,
        termos_lista=termos,
        mostrar_navegador=MOSTRAR_NAVEGADOR,
        save_callback=db.save_leads,
    )
    if EXPORTAR_EXCEL and not df.empty:
        db.export_to_excel(NICHO, cidade)


def executar_ciclo():
    db = LeadDatabase()
    try:
        if SINCRONIZAR:
            sincronizar_base_localidades()

        ufs = _resolver_ufs()
        if not ufs:
            print("Nenhuma UF disponível. Abortando ciclo.")
            return

        for uf in ufs:
            cidades = obter_cidades(uf)
            if not cidades:
                print(f"[{uf}] nenhuma cidade encontrada. Pulando.")
                continue

            if AQUECER_BAIRROS:
                aquecer_bairros_uf(uf, max_cidades=MAX_CIDADES)

            if MAX_CIDADES:
                cidades = cidades[:MAX_CIDADES]

            print(f"\n[{uf}] {len(cidades)} cidade(s) a coletar (nicho={NICHO}).")
            for cidade in cidades:
                try:
                    _coletar_cidade(db, cidade, uf)
                except Exception as e:
                    print(f"[{cidade}-{uf}] ERRO: {type(e).__name__}: {e}")
    finally:
        db.close()


def main():
    print(f"Map Scraper (auto) | nicho={NICHO} | UFs={UFS or 'todas'} | "
          f"max_cidades={MAX_CIDADES or 'todas'} | loop={LOOP}")
    while True:
        executar_ciclo()
        if not LOOP:
            break
        print(f"\nCiclo concluído. Aguardando {LOOP_PAUSA_SEGUNDOS}s para o próximo...")
        time.sleep(LOOP_PAUSA_SEGUNDOS)


if __name__ == "__main__":
    main()
