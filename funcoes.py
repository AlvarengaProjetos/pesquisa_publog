from ctypes import *
from classe import Publog
from io import StringIO
import pandas as pd

publog_instance = Publog()  

def consulta_management_future(string_niin):
    query = f"select NIIN, EFFECTIVE_DATE, MOE, AAC, SOS, UI, UNIT_PRICE, QUP, SLC from V_FLIS_MANAGEMENT where NIIN='{string_niin}'"
    matches = publog_instance.search(query)
    data_convertida = matches.replace('<', '').replace('>', '')
    if data_convertida == '':
        return False
    else:
        return(data_convertida)


def consulta_management_padrao(string_niin):     
    query = f"select NIIN, EFFECTIVE_DATE, MOE, AAC, SOS, UI, UNIT_PRICE, QUP, SLC from V_FLIS_MANAGEMENT where NIIN='{string_niin}'"
    matches = publog_instance.search(query)
    data_convertida = matches.replace('<', '').replace('>', '')
    if data_convertida == '':
        return False
    else:
        return data_convertida


def consulta_quantidade_box_pg(string_niin):
    query = f"select PHRASE_STATEMENT, from V_FLIS_PHRASE where NIIN='{string_niin}'"          
    matches = publog_instance.search(query)
    return matches


def converter_qup(qup):
    dicionario_de_qup = {
        'A': 'A=10',
        'B': 'B=12',
        'C': 'C=15',
        'D': 'D=16',
        'E': 'E=18',
        'F': 'F=20',
        'G': 'G=24',
        'H': 'H=25',
        'J': 'J=32',
        'K': 'K=36',
        'L': 'L=48',
        'M': 'M=50',
        'N': 'N=72',
        'P': 'P=75',
        'Q': 'Q=100',
        'R': 'R=120',
        'S': 'S=144',
        'T': 'T=200',
        'U': 'U=250',
        'V': 'V=500',
        'W': 'W=1000',
        'X': 'X=BLK',
        'Y': 'Y=PACKAGER OPTIONS',
        'Z': 'Z=SPECIAL REQUIREMENTS'
    }
    for i in dicionario_de_qup:
        if qup in dicionario_de_qup:
            return dicionario_de_qup[qup]
        else:
            return qup


def filtrar_quantidade_digitos_niin(i): 
    if len(i) < 9:
        i = i.rjust(9, '0')
    while len(i) > 9:
        i = i.replace(i[0], '', 1)
    return i    


def verificar_aac(string_niin):      
    try:
        publog_instance.connect() 
        aac_nao_aceitaveis = ['F', 'L', 'P', 'V', 'X', 'Y', 'T']
        query = f"select AAC, from V_FLIS_MANAGEMENT where NIIN='{string_niin}'"
        matches = publog_instance.search(query)
        data_temporaria = "".join(c for c in matches if c.isalnum())
        data_filtrada = data_temporaria[3:]
        return (set(data_filtrada) <= set(aac_nao_aceitaveis))       
    except: # Ainda são desconhecidos possíveis erros específicos para tratar
        pass
        #print(f'Erro na função verificar_aac. Foi usado o NIIN {string_niin}')


def verificar_ui_box_pg(string_niin):
    try:
        ui_pg = 'PG' 
        ui_bx = 'BX'
        query = f"select UI, from V_FLIS_MANAGEMENT where NIIN='string_niin'"
        matches = publog_instance.search(query)
        data_temporaria = "".join(c for c in matches if c.isalnum())
        data_filtrada = data_temporaria[2:]
        ui_pg_presente = (set(data_filtrada) <= set(ui_pg))
        ui_bx_presente = (set(data_filtrada) <= set(ui_bx))        
        if ui_bx_presente or ui_pg_presente:
            return True    
                    
    except: # Ainda são desconhecidos possíveis erros específicos para tratar
        print(f'Erro na função verificar_ui_box_pg. Foi usado o NIIN {string_niin}.')


def filtro_pos_busca(resultado_busca, niin):
    df = pd.read_csv(StringIO(resultado_busca), sep='|')
    df = pd.DataFrame(df)
    if verificar_ui_box_pg(niin):
        retorno_ui_box_pg = consulta_quantidade_box_pg(niin)
        retorno_ui_box_pg = retorno_ui_box_pg.replace('<PHRASE_STATEMENT>', '')
        retorno_ui_box_pg = (' '.join(dict.fromkeys(retorno_ui_box_pg.split())))
        df['PG_BX'] = retorno_ui_box_pg
    df_final = pd.concat([df_final, df])
    return df_final