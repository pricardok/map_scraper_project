# src/config.py
"""Carregamento centralizado do arquivo .env e leitura de flags.

Todos os módulos importam este arquivo, então o `.env` é lido uma única vez
por processo, antes de qualquer constante de configuração ser calculada.
"""
import os

PROJETO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_ENV = os.path.join(PROJETO_RAIZ, ".env")


def carregar_env(caminho=None):
    """Carrega variáveis de um arquivo .env (formato CHAVE=VALOR).

    Não sobrescreve variáveis que já existem no ambiente. Ignora linhas em
    branco, comentários (#) e valores entre aspas.
    """
    caminho = caminho or CAMINHO_ENV
    if not os.path.isfile(caminho):
        return

    with open(caminho, "r", encoding="utf-8-sig") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            chave = chave.strip()
            valor = valor.strip().strip('"').strip("'")
            if chave and chave not in os.environ:
                os.environ[chave] = valor


def str_para_bool(valor, padrao=False):
    """Converte strings comuns de booleano ('true', '1', 'sim', 's', 'yes') em bool."""
    if valor is None:
        return padrao
    return str(valor).strip().lower() in ("1", "true", "yes", "s", "sim", "on")


def env_int(nome, padrao):
    """Lê uma variável de ambiente inteira, com fallback para o padrão."""
    valor = os.environ.get(nome, "").strip()
    if not valor:
        return padrao
    try:
        return int(float(valor))
    except ValueError:
        return padrao


# Lido no import: qualquer módulo que importe `src.config` já tem o .env aplicado.
carregar_env()
