import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import numpy as np
import random
from datetime import date
from dateutil.relativedelta import relativedelta

# define global data

symbols = ['SBSP3','CPLE6','RENT3','VALE3','EQTL3','ITUB4','MELI34','PRIO3']

print('--------------------------')


def get_fake_tickers(assets, start_dt, end_dt):
    """ Create sample data """
    print(f'** get_fake_tickers({assets},{start_dt},{end_dt}) ')
    tickers = pd.DataFrame()
    for asset in assets:
        dth = pd.date_range(start_dt.strftime('%m/%d/%Y 00:00:00'), end_dt.strftime('%m/%d/%Y 23:59:59'), freq='30min')
        prices = np.random.random() * 100 + np.random.randn(len(dth)).cumsum()
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

        # grafico de cotacoes
        chart1.write(tickers)

    else:
        header.warning('Nenhum ativo selecionado')

    return True

# do the magic...
with st.sidebar:
    st.title('Assets Dashboard')
    sel_assets = st.multiselect(label="Select assets", options=symbols, placeholder='Assets')
    col = st.columns([6,6,3], vertical_alignment='bottom')
    start_date = col[0].date_input("From", format="DD/MM/YYYY", value=date.today() + relativedelta(months=-3))
    end_date = col[1].date_input("To", format="DD/MM/YYYY", value="today")
    col[2].button("GO", on_click=go, args=(sel_assets, start_date, end_date))
