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
    RETOMAR_COLETA   pular cidades já concluídas (true/false, default true)
    RECAPTURA_DIAS   refazer cidades concluídas há mais de N dias (default 30;
                     0 = nunca refazer)
    SEMEAR_PROGRESSO marcar como concluídas as cidades que já têm leads no banco
                     na primeira execução (true/false, default true)

Uso:
    python src/coleta_auto.py
"""
import os
import sys
import time
from datetime import datetime, timedelta

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
RETOMAR = str_para_bool(os.environ.get("RETOMAR_COLETA"), padrao=True)
RECAPTURA_DIAS = max(0, env_int("RECAPTURA_DIAS", 30))
SEMEAR_PROGRESSO = str_para_bool(os.environ.get("SEMEAR_PROGRESSO"), padrao=True)


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
    if RETOMAR:
        db.progresso_iniciar(NICHO, uf, cidade, len(termos))

    stats = {}
    df = rodar_scraper_multithread(
        nicho=NICHO,
        cidade=cidade,
        uf=uf,
        termos_lista=termos,
        mostrar_navegador=MOSTRAR_NAVEGADOR,
        save_callback=db.save_leads,
        estatisticas=stats,
    )

    if RETOMAR:
        # Área que falhou (bloqueio/timeout) deixa a cidade como parcial, para
        # ser tentada de novo em vez de ficar 30 dias marcada como concluída.
        if stats.get("areas_erro"):
            db.progresso_parcial(
                NICHO, uf, cidade, len(df),
                f"{stats['areas_erro']}/{stats.get('areas_total', 0)} área(s) sem coleta",
            )
        else:
            db.progresso_concluir(NICHO, uf, cidade, len(df))

    if EXPORTAR_EXCEL and not df.empty:
        db.export_to_excel(NICHO, cidade)


def _cidade_ja_coletada(registro):
    """True quando a cidade já foi concluída dentro da janela de recaptura.

    Com RETOMAR_COLETA=false nada é pulado (comportamento antigo, que recomeça
    o país inteiro a cada ciclo).
    """
    if not RETOMAR or not registro:
        return False
    if (registro.get("status") or "").lower() != "concluida":
        return False
    if RECAPTURA_DIAS <= 0:
        return True

    concluido = registro.get("concluido_em")
    if concluido is None:
        return True
    return concluido >= datetime.now() - timedelta(days=RECAPTURA_DIAS)


def _carregar_progresso(db):
    """Carrega o progresso do nicho, semeando a partir dos leads na 1ª execução."""
    if not RETOMAR:
        return {}

    progresso = db.progresso_carregar(NICHO)
    if not progresso and SEMEAR_PROGRESSO:
        semeadas = db.semear_progresso_de_leads(NICHO)
        if semeadas:
            print(f"[progresso] {semeadas} cidade(s) com leads já gravados foram "
                  f"marcadas como concluídas (SEMEAR_PROGRESSO=true).")
        progresso = db.progresso_carregar(NICHO)

    if progresso:
        concluidas = sum(
            1 for r in progresso.values()
            if (r.get("status") or "").lower() == "concluida"
        )
        print(f"[progresso] {concluidas} cidade(s) concluída(s) no banco "
              f"(recaptura após {RECAPTURA_DIAS} dia(s)).")
    return progresso


def executar_ciclo():
    db = LeadDatabase()
    try:
        if SINCRONIZAR:
            sincronizar_base_localidades()

        ufs = _resolver_ufs()
        if not ufs:
            print("Nenhuma UF disponível. Abortando ciclo.")
            return

        progresso = _carregar_progresso(db)

        for uf in ufs:
            cidades = obter_cidades(uf)
            if not cidades:
                print(f"[{uf}] nenhuma cidade encontrada. Pulando.")
                continue

            if AQUECER_BAIRROS:
                aquecer_bairros_uf(uf, max_cidades=MAX_CIDADES)

            pendentes = [c for c in cidades if not _cidade_ja_coletada(progresso.get((uf, c)))]
            if not pendentes:
                print(f"[{uf}] {len(cidades)} cidade(s) já coletada(s). Pulando.")
                continue

            if MAX_CIDADES:
                pendentes = pendentes[:MAX_CIDADES]

            print(f"\n[{uf}] {len(pendentes)} de {len(cidades)} cidade(s) pendente(s) "
                  f"(nicho={NICHO}).")
            for cidade in pendentes:
                try:
                    _coletar_cidade(db, cidade, uf)
                except Exception as e:
                    print(f"[{cidade}-{uf}] ERRO: {type(e).__name__}: {e}")
                    if RETOMAR:
                        try:
                            db.progresso_erro(NICHO, uf, cidade, f"{type(e).__name__}: {e}")
                        except Exception:
                            pass
    finally:
        db.close()


def main():
    print(f"Map Scraper (auto) | nicho={NICHO} | UFs={UFS or 'todas'} | "
          f"max_cidades={MAX_CIDADES or 'todas'} | loop={LOOP} | "
          f"retomar={RETOMAR} | recaptura={RECAPTURA_DIAS}d")
    while True:
        executar_ciclo()
        if not LOOP:
            break
        print(f"\nCiclo concluído. Aguardando {LOOP_PAUSA_SEGUNDOS}s para o próximo...")
        time.sleep(LOOP_PAUSA_SEGUNDOS)


if __name__ == "__main__":
    main()
