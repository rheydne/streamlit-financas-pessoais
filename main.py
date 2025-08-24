import streamlit as st
import pandas as pd

def tratamento_csv_entrada(df):
    df['Valor'] = df['Valor'].str.replace('R$ ', '', regex=False)
    df['Valor'] = df['Valor'].str.replace('.', '', regex=False)
    df['Valor'] = df['Valor'].str.replace(',', '.', regex=False)
    df['Valor'] = df['Valor'].astype(float)
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y').dt.date

    return df

def calc_general_stats(df):
    df_data = df.groupby(by='Data')[['Valor']].sum()
     
    df_data['lag_1'] = df_data['Valor'].shift(1)

    df_data['Diferença Mensal'] = df_data['Valor'] - df_data['lag_1']

    df_data['Dif Mensal Média 6M'] = df_data['Diferença Mensal'].rolling(6).mean()
    df_data['Dif Mensal Média 12M'] = df_data['Diferença Mensal'].rolling(12).mean()
    df_data['Dif Mensal Média 24M'] = df_data['Diferença Mensal'].rolling(24).mean()

    df_data['Dif Mensal Relativa'] = (df_data['Valor'] / df_data['lag_1'] - 1)

    df_data['Evolução Total 6M'] = df_data['Valor'].rolling(6).apply(lambda x: x[-1] - x[0])
    df_data['Evolução Total 12M'] = df_data['Valor'].rolling(12).apply(lambda x: x[-1] - x[0])
    df_data['Evolução Total 24M'] = df_data['Valor'].rolling(24).apply(lambda x: x[-1] - x[0])
     
    df_data['Evolução Rel 6M'] = df_data['Valor'].rolling(6).apply(lambda x: x[-1] / x[0] - 1)
    df_data['Evolução Rel 12M'] = df_data['Valor'].rolling(12).apply(lambda x: x[-1] / x[0] - 1)
    df_data['Evolução Rel 24M'] = df_data['Valor'].rolling(24).apply(lambda x: x[-1] / x[0] - 1)

    df_data = df_data.drop('lag_1', axis=1)

    return df_data

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
        # Gráfico de barras, usando o filtro selecionado
        st.bar_chart(df_instituicao.loc[date])

    # Visão de Estatísticas Gerais
    exp3 = st.expander('Estatísticas Gerais')

    columns_fmt = {
        'Valor':st.column_config.NumberColumn('Valor', format='R$ %.2f'),
        'Diferença Mensal':st.column_config.NumberColumn('Diferença Mensal', format='R$ %.2f'),
        'Dif Mensal Média 6M':st.column_config.NumberColumn('Dif Mensal Média 6M', format='R$ %.2f'),
        'Dif Mensal Média 12M':st.column_config.NumberColumn('Dif Mensal Média 12M', format='R$ %.2f'),
        'Dif Mensal Média 24M':st.column_config.NumberColumn('Dif Mensal Média 24M', format='R$ %.2f'),
        'Dif Mensal Relativa':st.column_config.NumberColumn('Dif Mensal Relativa', format='percent'),
        'Evolução Total 6M':st.column_config.NumberColumn('Evolução Total 6M', format='R$ %.2f'),
        'Evolução Total 12M':st.column_config.NumberColumn('Evolução Total 12M', format='R$ %.2f'),
        'Evolução Total 24M':st.column_config.NumberColumn('Evolução Total 24M', format='R$ %.2f'),
        'Evolução Rel 6M':st.column_config.NumberColumn('Evolução Rel 6M', format='percent'),
        'Evolução Rel 12M':st.column_config.NumberColumn('Evolução Rel 12M', format='percent'),
        'Evolução Rel 24M':st.column_config.NumberColumn('Evolução Rel 24M', format='percent')
    }

    df_stats = calc_general_stats(df)

    tab_stats, tab_abs, tab_rel = exp3.tabs(tabs=['Dados', 'Histórico de Evolução', 'Crescimento Relativo'])

    with tab_stats:
        st.dataframe(df_stats, column_config=columns_fmt)

    with tab_abs:
        abs_cols = [
            'Diferença Mensal',
            'Dif Mensal Média 6M',
            'Dif Mensal Média 12M',
            'Dif Mensal Média 24M'
        ]
        st.line_chart(df_stats[abs_cols])
    
    with tab_rel:
        rel_cols = [
            'Dif Mensal Relativa',
            'Evolução Rel 6M',
            'Evolução Rel 12M',
            'Evolução Rel 24M'
        ]
        st.line_chart(data=df_stats[rel_cols])