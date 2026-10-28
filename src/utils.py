# src/utils.py
import re

def formatar_telefone(telefone_bruto):
    """
    Limpa o telefone, identifica o tipo e gera o link do WhatsApp.
    Retorna: (telefone_limpo, tipo, whatsapp_link)
    """
    if not telefone_bruto:
        return "", "Não Informado", ""
    
    # Remove tudo que não for número
    apenas_numeros = re.sub(r'\D', '', str(telefone_bruto))
    
    # Se o número já vier com DDI (55) e tiver 12 ou 13 dígitos, removemos o 55 
    # temporariamente para classificar o tipo corretamente (Fixo/Celular)
    if apenas_numeros.startswith('55') and len(apenas_numeros) > 11:
        numero_sem_ddi = apenas_numeros[2:]
    else:
        numero_sem_ddi = apenas_numeros

    # Classificação e formatação do Link
    if len(numero_sem_ddi) == 11: # Celular com 9 dígito
        tipo = "Celular"
        whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
    elif len(numero_sem_ddi) == 10: # Fixo
        tipo = "Fixo"
        whatsapp_link = f"https://wa.me/55{numero_sem_ddi}"
    elif len(apenas_numeros) > 0:
        tipo = "Desconhecido"
        whatsapp_link = f"https://wa.me/{apenas_numeros}"
    else:
        return "", "Não Informado", ""
        
    # Retorna apenas os números na coluna telefone, o tipo e o link pronto
    return apenas_numeros, tipo, whatsapp_link