import pandas as pd
import streamlit as st
from classe import Publog
import os
from ctypes import *
from io import StringIO
from funcoes import consulta_management_future, consulta_management_padrao, consulta_quantidade_box_pg, converter_qup, filtrar_quantidade_digitos_niin, verificar_aac, verificar_ui_box_pg


def main():
    st.title('Pesquisa de Preço do PUBLOG')
    st.subheader('INTRUÇÕES')
    st.write(
        'Para usar esse aplicativo é necessário criar uma planilha no '
        'formato CSV de uma coluna só nela contendo os niins que se desejam buscar '
        ' no PUBLOG. A primeira célula da coluna deverá conter apenas a palavra NIIN '
        'e nas demais colunas os respectivos niins.'
        )  
    st.write(
        'Também é necessário que exista uma pasta chamada "publog", sem aspas duplas'
        ' no diretório \C:, nela deverá estar o conteúdo do PUBLOG.'
    )  
    
    try: 
        publog_instance = Publog()
        publog_instance.connect()

    except FileNotFoundError:
        st.write(
            '## #### AVISO #### Não foi encontrado a pasta "publog" no diretório C:,'     
            ' favor corrigir esse erro antes de tentar colocar a planilha abaixo.'
            )    

    uploaded_file = st.file_uploader(
        "Escolha uma planilha no arquivo .csv. Você pode arrastar o arquivo até a "
        "caixa abaixo ou clicar no botão 'Browse files' para escolher uma planilha:",
        type='csv',
    )
    st.text('')

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        lista_coluna_nsn = df.NSN.values.tolist()
    
        df_vazio = {
            'NIIN': [], 'EFFECTIVE_DATE': [], 'MOE': [], 'AAC': [], 'SOS': [], 
            'UI': [], 'UNIT_PRICE': [], 'QUP': [], 'SLC': [], 'PG_BX': [],
            }
        df_final = pd.DataFrame(df_vazio)
        print('Aguarde, o programa está rodando.')
        
        for niin in lista_coluna_nsn: 
            niin = filtrar_quantidade_digitos_niin(str(niin))       
            if verificar_aac(niin): 
                df_aac = pd.DataFrame(
                    {
                    'NIIN': [niin],
                    'AAC': ['Item não encontrado ou AAC não desejável: F, L, P, V, X, Y, T']
                    }
                )
                df_para_concatenar = [df_final, df_aac]
                df_final = pd.concat(df_para_concatenar)
                continue  
                
            if consulta_management_future(niin):
                resultado_busca = (consulta_management_future(niin)) 
                df = pd.read_csv(StringIO(resultado_busca), sep='|')
                df = pd.DataFrame(df)
                if verificar_ui_box_pg(niin):
                    retorno_ui_box_pg = consulta_quantidade_box_pg(niin)
                    retorno_ui_box_pg = retorno_ui_box_pg.replace('<PHRASE_STATEMENT>', '')
                    retorno_ui_box_pg = (' '.join(dict.fromkeys(retorno_ui_box_pg.split())))
                    df['PG_BX'] = retorno_ui_box_pg
                df_final = pd.concat([df_final, df])
                continue
                
            if consulta_management_padrao(niin):
                resultado_busca = (consulta_management_padrao(niin)) 
                df = pd.read_csv(StringIO(resultado_busca), sep='|')
                df = pd.DataFrame(resultado_busca)
                if verificar_ui_box_pg(niin):
                    retorno_ui_box_pg = consulta_quantidade_box_pg(niin)
                    retorno_ui_box_pg = retorno_ui_box_pg.replace('<PHRASE_STATEMENT>', '')
                    retorno_ui_box_pg = (' '.join(dict.fromkeys(retorno_ui_box_pg.split())))
                    df['PG_BX'] = retorno_ui_box_pg
                df_final = pd.concat([df_final, df])
          
        lista_coluna_qup = df_final.QUP.values.tolist()
        lista_vazia_qup = []
        
        for i in lista_coluna_qup:
            a = converter_qup(i)
            lista_vazia_qup.append(a)    

        df_qup = pd.DataFrame(
                {
                'QUP': lista_vazia_qup,
                }
            )
        coluna_extraida = df_qup['QUP']
        df_final = df_final.assign(QUP=pd.Series(coluna_extraida).values)    
        
        conditions = [
        (df_final['MOE'] == 'DF') & (df_final['SOS'] == 'SMS'),
        (df_final['MOE'] == 'DS') & (df_final['SOS'] == 'SMS'),
        ((df_final['MOE'] == 'DF') | (df_final['MOE'] == 'DS')) & (df_final['SOS'] != 'SMS'),
        (df_final['MOE'] == 'DN') & (df_final['SOS'] == 'SMS'),
        (df_final['AAC'] == 'J'),
        #(df_final['SLC'].isin(['0', '1', '1.1', '0.0'])),  
        ]

        # Define corresponding values for 'CAGE'
        values = [
            'KCQ', 'QAQ', 'QAQ', 'JZO', 'Favor verificar o PubLog para maiores detalhes',
            ]

        # Loop through conditions and assign values to 'CAGE'
        for condition, value in zip(conditions, values):
            df_final.loc[condition, 'CAGE'] = value   
                  
        # Mostrar planilha na tela
        st.write(df_final)
        print(df_final)
        
        # Botão de download
        df_download = df_final.to_csv().encode('utf-8')
        st.download_button(label='Baixar planilha em formato csv', data=df_download, file_name='planilha.csv')
        st.download_button(label='Baixar planilha em formato osd', data=df_download, file_name='planilha.osd')

if __name__ == '__main__':
    os.system('cls')
    main()
