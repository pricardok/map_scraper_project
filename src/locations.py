# src/locations.py
import requests
from geopy.geocoders import Nominatim
import pandas as pd

def obter_estados():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return pd.DataFrame([{'uf': e['sigla'], 'nome': e['nome']} for e in response.json()])
    except Exception as e:
        print(f"Erro ao buscar estados: {e}")
        return pd.DataFrame()

def obter_cidades(uf):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return [c['nome'] for c in response.json()]
    except Exception as e:
        print(f"Erro ao buscar cidades para {uf}: {e}")
        return []

def obter_termos_busca(cidade, uf):
    """
    Como o Google Maps já traz o endereço completo da empresa,
    não precisamos mais tentar adivinhar os bairros da cidade.
    Vamos buscar a cidade inteira de uma vez (ou dividir se houver muitos resultados).
    """
    print(f"Preparando busca para {cidade} - {uf}...")
    # Retorna uma lista com a própria cidade para usar como termo de busca
    return [cidade]