import pandas as pd
from instagpy import InstaGPy
# Supondo que você usará a firmoscope como base para a coleta no Maps
# import subprocess

def extrair_leads_maps(nicho, localizacao):
    """
    Executa a extração no Google Maps.
    A firmoscope tem o comando: firmoscope "nicho localizacao" --no-website
    """
    # Aqui você chamaria a firmoscope e leria o CSV gerado por ela.
    # Exemplo: subprocess.run(['firmoscope', f'{nicho} {localizacao}', '--no-website', '--output', 'leads.csv'])
    # df = pd.read_csv('leads.csv')
    # return df
    pass

def buscar_instagram_e_contato(nome_empresa):
    """
    Busca o perfil do Instagram pelo nome da empresa e extrai bio/contato.
    """
    insta = InstaGPy()
    try:
        # A busca por nome pode não ser exata, então o ideal é usar o Google para achar o @.
        # Esta é uma abordagem simplificada.
        perfil = insta.get_user_profile(nome_empresa) 
        bio = perfil.get('biography', '')
        telefone = perfil.get('business_phone_number', '')
        # O instagpy também pode extrair e-mail da bio, se disponível.
        return bio, telefone
    except Exception as e:
        print(f"Não foi possível encontrar o Instagram para {nome_empresa}: {e}")
        return None, None

def main(nicho, localizacao):
    # 1. Coleta base (focando em negócios sem site)
    df_leads = extrair_leads_maps(nicho, localizacao)
    
    # 2. Enriquecimento com Instagram
    resultados = []
    for index, row in df_leads.iterrows():
        nome = row['Name']
        bio, telefone_insta = buscar_instagram_e_contato(nome)
        
        # 3. Consolidação
        resultados.append({
            'Nome': nome,
            'Telefone': row.get('Phone', telefone_insta), # Prioriza o do Maps, se houver
            'Instagram': f"@{nome.replace(' ', '').lower()}" if bio else None, # Exemplo simplificado
            'Bio_Instagram': bio
        })
    
    # 4. Geração do Excel final
    df_final = pd.DataFrame(resultados)
    df_final.to_excel('leads_enriquecidos.xlsx', index=False)
    print("Processo concluído. Arquivo 'leads_enriquecidos.xlsx' gerado.")

# Exemplo de uso
# main("123", "abc")