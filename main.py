import streamlit as st
import pandas as pd



def tratamento_csv_entrada(df):
    df['Valor'] = df['Valor'].str.replace('R$ ', '', regex=False)
    df['Valor'] = df['Valor'].str.replace('.', '', regex=False)
    df['Valor'] = df['Valor'].str.replace(',', '.', regex=False)
    df['Valor'] = df['Valor'].astype(float)
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y').dt.date

    return df



st.set_page_config(page_title='Finanças', page_icon=':classical_building:')

st.markdown('''
    # Bem vindo!
                
    ## Seu APP Financeiro!
                
    Esperamos que você se agrade de nossa solução para suas finanças.
''')

# Widget de leitura dos dados de um csv
file_upload = st.file_uploader(label='Insira seu arquivo', type=['csv'])

if file_upload:
    df = pd.read_csv(file_upload)
    df = tratamento_csv_entrada(df)
    
    # Formatação coluna 'Valor'
    columns_fmt = {
        'Valor':st.column_config.NumberColumn('Valor', format='R$ %.2f')
        }
    
    # Exibição dos dados no App, tabela crua sem tratamentos
    exp1 = st.expander('Dados Brutos')
    # st.dataframe(df, hide_index=True, column_config=columns_fmt)
    exp1.dataframe(df, hide_index=True, column_config=columns_fmt)

    # Visão por instituição
    exp2 = st.expander('Intituições')
    df_instituicao = df.pivot_table(index='Data', columns='Instituição', values='Valor')

    # Abas para diferentes visões (dentro de um "expander")
    tab_data, tab_history, tab_share = exp2.tabs(['Dados', 'Histórico', 'Distribuição'])
    
    # Aba por instituição
    with tab_data: 
        st.dataframe(df_instituicao)
    
    # Aba gráfico de linhas 
    with tab_history:
        st.line_chart(df_instituicao)

    # Aba última data de dados
    with tab_share:

        # Filtro de data
        date = st.selectbox('Data para Distribuição', df_instituicao.index)

        #Gráfico de barras, usando o filtro selecionado
        st.bar_chart(df_instituicao.loc[date])