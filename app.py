import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import numpy as np
import random
from datetime import date
from dateutil.relativedelta import relativedelta

import altair as alt

# define global data

symbols = ['SBSP3','CPLE6','RENT3','VALE3','EQTL3','ITUB4','MELI34','PRIO3']

print('--------------------------')


def get_fake_tickers(assets, start_dt, end_dt):
    """ Create sample data """
    print(f'** get_fake_tickers({assets},{start_dt},{end_dt}) ')
    tickers = pd.DataFrame()
    for asset in assets:
        dth = pd.date_range(start_dt.strftime('%m/%d/%Y 00:00:00'), end_dt.strftime('%m/%d/%Y 23:59:59'), freq='60min')
        prices = 20 + np.random.random() * 50 + np.random.randn(len(dth)).cumsum()
        more_tickers = pd.DataFrame({
            'ticker': dth,
            'price': prices,
        })
        more_tickers['symbol'] = asset
        tickers = pd.concat([tickers, more_tickers])
    return tickers


def go(assets, start_dt, end_dt):
    """ get data and analyze it """
    print(f'* go({assets},{start_dt},{end_dt}) ')

    # define main page containers
    header = st.container()
    chart1, chart2 = st.columns(2)


    if len(assets) > 0:
        header.success(f'Ativos secionados:   {assets}')
        print(f'* go: selected=({assets}) ')
        tickers = get_fake_tickers(assets, start_dt, end_dt)

        # price chart / grafico de cotacoes

        base = alt.Chart(tickers,
                         title = alt.TitleParams('Price Chart', anchor='middle')
        ).mark_line().encode(
            alt.Y('price:Q'), #.axis(title=None),
            alt.X('ticker').axis(title=None),
            color=alt.Color('symbol:N', title='',
                            legend=alt.Legend(orient='bottom'))
        ).interactive()
        chart1.altair_chart(base, use_container_width=True)

        # calculo da performance de cada ativo
        #
        # para normalizar os precos, tem que identificar o preco inicial de cada ativo, e depois
        # dividir cada preco pelo preco inicial. assim o preco inicial sera 1 e os demais serao
        # calculados como um fator em relacao ao preco inicial. e acumulando os precos ao longo
        # das ocorrencias teremos a performance de cada ativo na mesma unidade (% do preco inicial)
        #
        # o preco normalizado sera calculado dividindo o valor do preco atual em relacao ao preco inicial
        # o retorno do investimento sera calculado com o o preco final em relacao ao preco inicial
        # a volatiidade sera calculada como a variacao do desvio padrao... ????

        tickers = tickers.sort_values(by='ticker')
        start_prices = tickers.groupby('symbol')['price'].first().reset_index()
        start_prices = start_prices.rename(columns={'price': 'initial_price'})

        end_prices = tickers.groupby('symbol')['price'].last().reset_index()
        end_prices = end_prices.rename(columns={'price': 'end_price'})

        df_assets = pd.merge(start_prices, end_prices, on='symbol')
        df_assets['ret'] = (df_assets['end_price'] - df_assets['initial_price']) / df_assets['initial_price']

        tickers = pd.merge(tickers, df_assets[['symbol','initial_price']], on='symbol')
        tickers['norm'] = tickers['price'] / tickers['initial_price']
        tickers.drop(columns=['initial_price'], inplace=True)

        tickers['price_change'] = tickers['price'].pct_change()[1:]
        vols = tickers.groupby('symbol')['price_change'].std().reset_index()
        vols = vols.rename(columns={'price_change': 'vols'})
        vols['vols'] = vols['vols'] * np.sqrt(252)
        df_assets = pd.merge(df_assets, vols, on='symbol')

        # grafico de performance / return chart

        base = alt.Chart(tickers,
                         title = alt.TitleParams('Return Chart', anchor='middle')
        ).mark_line().encode(
            alt.Y('norm:Q'), #.axis(title=None),
            alt.X('ticker:T').axis(title=None),
            color=alt.Color('symbol:N', title='',
                            legend=alt.Legend(orient='bottom'))
        ).interactive()
        chart2.altair_chart(base, use_container_width=True)

        st.write(df_assets)



    else:
        header.warning('Nenhum ativo selecionado')

    return True

# do the magic...
with st.sidebar:
    st.title('Assets Dashboard')
    sel_assets = st.multiselect(label="Select assets", options=symbols, placeholder='Assets')
    col = st.columns([6,6,3], vertical_alignment='bottom')
    start_date = col[0].date_input("From", format="DD/MM/YYYY", value=date.today() + relativedelta(months=-1))
    end_date = col[1].date_input("To", format="DD/MM/YYYY", value="today")
    col[2].button("GO", on_click=go, args=(sel_assets, start_date, end_date))
