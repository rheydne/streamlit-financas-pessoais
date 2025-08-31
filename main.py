import streamlit as st
import pandas as pd
from datetime import date

# Configuração da Página
st.set_page_config(page_title='Finanças', page_icon=':classical_building:')

# ==========================
# Funções Auxiliares
# ==========================

def tratamento_csv_entrada(df):
    df['Valor'] = (
        df['Valor']
        .str.replace('R$ ', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y').dt.date
    return df

def calc_general_stats(df):
    df_data = df.groupby('Data')[['Valor']].sum()
    df_data['lag_1'] = df_data['Valor'].shift(1)

    df_data['Diferença Mensal'] = df_data['Valor'] - df_data['lag_1']
    df_data['Dif Mensal Relativa'] = df_data['Valor'] / df_data['lag_1'] - 1

    for meses in [6, 12, 24]:
        df_data[f'Dif Mensal Média {meses}M'] = df_data['Diferença Mensal'].rolling(meses).mean()
        df_data[f'Evolução Total {meses}M'] = df_data['Valor'].rolling(meses).apply(lambda x: x[-1] - x[0])
        df_data[f'Evolução Rel {meses}M'] = df_data['Valor'].rolling(meses).apply(lambda x: x[-1] / x[0] - 1)

    df_data.drop('lag_1', axis=1, inplace=True)
    return df_data

def formatador_valores():
    fmt = {'Valor': st.column_config.NumberColumn('Valor', format='R$ %.2f'),
           'Diferença Mensal': st.column_config.NumberColumn('Diferença Mensal', format='R$ %.2f'),
           'Dif Mensal Relativa': st.column_config.NumberColumn('Dif Mensal Relativa', format='percent')}
    
    for meses in [6, 12, 24]:
        fmt[f'Dif Mensal Média {meses}M'] = st.column_config.NumberColumn(f'Dif Mensal Média {meses}M', format='R$ %.2f')
        fmt[f'Evolução Total {meses}M'] = st.column_config.NumberColumn(f'Evolução Total {meses}M', format='R$ %.2f')
        fmt[f'Evolução Rel {meses}M'] = st.column_config.NumberColumn(f'Evolução Rel {meses}M', format='percent')
    return fmt

# ==========================
# Interface
# ==========================

st.markdown('''
    # Bem-vindo!
    ## Seu APP Financeiro!
    Esperamos que você se agrade de nossa solução para suas finanças.
''')

# Upload
file_upload = st.file_uploader('Insira seu arquivo', type=['csv'])

if file_upload:
    df = pd.read_csv(file_upload)
    df = tratamento_csv_entrada(df)

    # ==========================
    # Dados Brutos
    # ==========================
    with st.expander('Dados Brutos'):
        st.dataframe(df, hide_index=True, column_config={'Valor': st.column_config.NumberColumn('Valor', format='R$ %.2f')})

    # ==========================
    # Visão por Instituição
    # ==========================
    with st.expander('Instituições'):
        df_instituicao = df.pivot_table(index='Data', columns='Instituição', values='Valor')

        tab_data, tab_history, tab_share = st.tabs(['Dados', 'Histórico', 'Distribuição'])

        with tab_data:
            st.dataframe(df_instituicao)

        with tab_history:
            st.line_chart(df_instituicao)

        with tab_share:
            selected_date = st.selectbox('Data para Distribuição', df_instituicao.index)
            st.bar_chart(df_instituicao.loc[selected_date])

    # ==========================
    # Estatísticas Gerais
    # ==========================
    with st.expander('Estatísticas Gerais'):
        df_stats = calc_general_stats(df)
        column_fmt = formatador_valores()

        tab_stats, tab_abs, tab_rel = st.tabs(['Dados', 'Histórico de Evolução', 'Crescimento Relativo'])

        with tab_stats:
            st.dataframe(df_stats, column_config=column_fmt)

        with tab_abs:
            abs_cols = [col for col in df_stats.columns if 'Dif' in col and 'Relativa' not in col]
            st.line_chart(df_stats[abs_cols])

        with tab_rel:
            rel_cols = [col for col in df_stats.columns if 'Rel' in col]
            st.line_chart(df_stats[rel_cols])

    # ==========================
    # Metas
    # ==========================
    with st.expander('Metas'):
        col1, col2 = st.columns(2)

        max_data = max(df_stats.index) if not df_stats.empty else date.today()
        data_inicio_meta = col1.date_input('Início da Meta', max_value=max_data)

        data_filtrada = max([d for d in df_stats.index if d <= data_inicio_meta], default=max_data)

        col2.number_input('**Salário Bruto**', min_value=0.0, format='%.2f')
        sal_liq = col2.number_input('**Salário Líquido**', min_value=0.0, format='%.2f')
        custos_fixos = col1.number_input('**Custos Fixos**', min_value=0.0, format='%.2f')

        valor_inicio = df_stats.loc[data_filtrada]['Valor'] if data_filtrada in df_stats.index else 0.0
        col1.markdown(f'**Patrimônio no Início da Meta:** R$ {valor_inicio:.2f}')

        mensal = sal_liq - custos_fixos
        anual = mensal * 12

        col1_pot, col2_pot = st.columns(2)
        with col1_pot.container(border=True):
            st.markdown(f'**Potencial Arrecadação Mensal:**\n\nR$ {mensal:.2f}')
        with col2_pot.container(border=True):
            st.markdown(f'**Potencial Arrecadação Anual:**\n\nR$ {anual:.2f}')

        col1_meta, col2_meta = st.columns(2)
        meta_estipulada = col1_meta.number_input('**Meta Sugerida R$**', min_value=0.0, format='%.2f', value=anual)
        patrimonio_final = meta_estipulada + valor_inicio

        with col2_meta.container(border=True):
            st.markdown(f'**Patrimônio Estimado Pós Meta:**\n\nR$ {patrimonio_final:.2f}')
