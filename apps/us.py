import pandas as pd
import numpy as np
import streamlit as st
from datetime import date
import altair as alt
import io
import os

# ============================= FUNCTIONS

def Find_Date(df, target_date):
    '''
    Find date imediately previous to a target date
    '''
    earlier_dates = [ed for ed in df['Date'] if ed <= target_date]
    if not earlier_dates:
        # raise ValueError("no earlier dates to choose from")
        return -1
    return max(earlier_dates)

def Compute_Order_Price_Reais(df_temp, usdbrl_rate):
    '''
    Compute the Order Price in R$
    '''
    order_pr_rs = []
    cot = 0
    price = 0
    for row in df_temp.itertuples():
        if row[2] == 'COMPRA':
            cot = usdbrl_rate.loc[usdbrl_rate['Date'] == row[3], 'Sell'].item()
            price = row[5]*cot
        elif row[2] == 'VENDA':
            cot = usdbrl_rate.loc[usdbrl_rate['Date'] == row[3], 'Buy'].item()
            price = row[5]*cot
        elif row[2] == 'DESDOBRAMENTO':
            cot = 0
            price = row[5]*cot
        elif row[2] == 'GRUPAMENTO':
            cot = 0
            price = row[5]*cot
        elif row[2] == 'BONIFICACAO':
            cot = usdbrl_rate.loc[usdbrl_rate['Date'] == row[3], 'Buy'].item()
            price = row[5]*cot
        elif row[2] == 'AMORTIZACAO':
            cot = usdbrl_rate.loc[usdbrl_rate['Date'] == row[3], 'Buy'].item()
            price = row[5]*cot
        order_pr_rs.append(round(price,2))
    df_temp['Price of Order R$'] = order_pr_rs

def Compute_Cumm_Quantity(df_temp):
    '''
    Compute the cummulative quantity of assets
    '''
    cum_quant = []
    total = 0
    for row in df_temp.itertuples():
        if row[2] == 'COMPRA':
            total = total + row[4]
        elif row[2] == 'VENDA':
            total = total - row[4]
        elif row[2] == 'DESDOBRAMENTO':
            total = total + row[4]
        elif row[2] == 'GRUPAMENTO':
            total = total - row[4]
        elif row[2] == 'BONIFICACAO':
            total = total + row[4]
        elif row[2] == 'AMORTIZACAO':
            total = total
        cum_quant.append(total)
    df_temp['Cummulative Quantity'] = cum_quant

def Compute_Cumm_Cost(df_temp):
    '''
    Compute the cummulative cost of the assets
    '''
    cum_cost = []
    cost = 0
    for row in df_temp.itertuples():
        if row[2] == 'COMPRA':
            cost = cost + row[5]
        elif row[2] == 'VENDA':
            cost = (cost/(row[4]+row[9]))*row[9]
        elif row[2] == 'DESDOBRAMENTO':
            cost = cost
        elif row[2] == 'GRUPAMENTO':
            cost = cost
        elif row[2] == 'BONIFICACAO':
            cost = cost + row[5]
        elif row[2] == 'AMORTIZACAO':
            cost = cost - row[5]
        cum_cost.append(round(cost,2))
    df_temp['Cummulative Cost US$'] = cum_cost

def Compute_Average_Price(df_temp):
    '''
    Compute the average price of the asset
    '''
    avg_price = []
    avg = 0
    for row in df_temp.itertuples():
        if row[2] == 'COMPRA':
            avg = row[10]/row[9]
        elif row[2] == 'VENDA':
            avg = avg
        elif row[2] == 'DESDOBRAMENTO':
            avg = row[10]/row[9]
        elif row[2] == 'GRUPAMENTO':
            avg = row[10]/row[9]
        elif row[2] == 'BONIFICACAO':
            avg = row[10]/row[9]
        elif row[2] == 'AMORTIZACAO':
            avg = row[10]/row[9]
        avg_price.append(round(avg,2))
    df_temp['Average Price US$'] = avg_price

def Compute_Cumm_Cost_Reais(df_temp):
    '''
    Compute the cummulative cost in R$
    '''
    cum_cost_rs = []
    cost = 0
    for row in df_temp.itertuples():
        if row[2] == 'COMPRA':
            cost = cost + row[7]
        elif row[2] == 'VENDA':
            cost = (cost/(row[4]+row[9]))*row[9]
        elif row[2] == 'DESDOBRAMENTO':
            cost = cost
        elif row[2] == 'GRUPAMENTO':
            cost = cost
        elif row[2] == 'BONIFICACAO':
            cost = cost + row[7]
        elif row[2] == 'AMORTIZACAO':
            cost = cost - row[7]
        cum_cost_rs.append(round(cost,2))
    df_temp['Cummulative Cost R$'] = cum_cost_rs

def Compute_Average_Price_Reais(df_temp):
    '''
    Compute the average price of the asset in R$
    '''
    avg_price_rs = []
    avg = 0
    for row in df_temp.itertuples():
        if row[2] == 'COMPRA':
            avg = row[12]/row[9]
        elif row[2] == 'VENDA':
            avg = avg
        elif row[2] == 'DESDOBRAMENTO':
            avg = row[12]/row[9]
        elif row[2] == 'GRUPAMENTO':
            avg = row[12]/row[9]
        elif row[2] == 'BONIFICACAO':
            avg = row[12]/row[9]
        elif row[2] == 'AMORTIZACAO':
            avg = row[12]/row[9]
        avg_price_rs.append(round(avg,2))
    df_temp['Average Price R$'] = avg_price_rs

def Compute_Profit_Loss(df_temp):
    '''
    Compute the profit or loss in the selling of an asset
    '''
    profit_loss = []
    money = 0
    for row in df_temp.itertuples():
        if row[2] == 'VENDA':
            money = (row[8]-row[13])*row[4]
        else:
            money = 0
        profit_loss.append(round(money,2))
    df_temp['Profit/Loss R$'] = profit_loss

def Compute_GCAP(df_temp):
    '''
    Compute the capital gains to be paid
    '''
    gcap = []
    tax = 0
    for row in df_temp.itertuples():
        if row[2] == 'VENDA' and row[14] > 0:
            tax = 0.15*row[14] # stocks
        else:
            tax = 0
        gcap.append(round(tax,2))
    df_temp['GCAP R$'] = gcap

# @st.cache(suppress_st_warning=True)
def load_data():
    df = pd.DataFrame()
    multiple_files = st.sidebar.file_uploader(
        "Upload portfolio events here",
        accept_multiple_files=True
    )
    for file in multiple_files:
        fname = io.BytesIO(file.getbuffer())
        df = df.append(pd.read_csv(fname), ignore_index=True)
    return df

def load_usdbrl():
    df = pd.DataFrame()
    multiple_files = st.sidebar.file_uploader(
        "Upload the exchange rates of USDBRL here",
        accept_multiple_files=True
    )
    for file in multiple_files:
        fname = io.BytesIO(file.getbuffer())
        df = df.append(pd.read_csv(fname), ignore_index=True)
    return df

# ====================================== MAIN
def app():

    st.title('US Porfolio Report')

    st.sidebar.header('User Input')

    df = load_data()
    usdbrl_rate = load_usdbrl()

    if not (df.empty or usdbrl_rate.empty):
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
        df['Date'] = df['Date'].dt.date
        df.sort_values('Date', inplace=True, ignore_index=True)
        usdbrl_rate['Date'] = pd.to_datetime(usdbrl_rate['Date'], dayfirst=True)
        usdbrl_rate['Date'] = usdbrl_rate['Date'].dt.date
        usdbrl_rate.sort_values('Date', inplace=True, ignore_index=True)

        st.header("Complete Portfolio History")
        # st.write(df)
        st.dataframe(df.style.set_precision(2))

        list_of_assets = sorted(list(set(df['Asset'].to_list())))
        selected_asset = st.sidebar.selectbox('Asset',list_of_assets)

        df_asset = df[df['Asset'] == selected_asset].copy()
        df_asset['Unit Price US$'] = round(df_asset['Price of Order US$'] / df_asset['Quantity'],2)

        # ===== NEW COLUMN: Order Price in R$
        Compute_Order_Price_Reais(df_asset, usdbrl_rate)
        df_asset['Unit Price R$'] = round(df_asset['Price of Order R$']/df_asset['Quantity'],2)
        # ====== NEW COLUMN: Cummulative Quantity
        Compute_Cumm_Quantity(df_asset)
        # ====== NEW COLUMN: Cummulative Cost
        Compute_Cumm_Cost(df_asset)
        # ====== NEW COLUMN: Average Price
        Compute_Average_Price(df_asset)
        # ====== NEW COLUMN: Cummulative Cost in R$
        Compute_Cumm_Cost_Reais(df_asset)
        # ====== NEW COLUMN: Average Price in R$
        Compute_Average_Price_Reais(df_asset)
        # ====== NEW COLUMN: Profit/Loss
        Compute_Profit_Loss(df_asset)
        # ====== NEW COLUMN: GCAP
        Compute_GCAP(df_asset)

        # ==================================== Generate Report
        st.header('Asset History: ' + str(selected_asset))
        # st.write(df_asset)
        st.dataframe(df_asset.style.set_precision(2))

        plot1 = alt.Chart(df_asset).mark_line().encode(
            x='Date',
            y='Cummulative Cost R$'
        )

        st.header('Cumulative Cost R$')
        st.altair_chart(plot1, use_container_width=True)

        plot2 = alt.Chart(df_asset).mark_line().encode(
            x='Date',
            y='Average Price R$'
        )

        st.header('Average Price R$')
        st.altair_chart(plot2, use_container_width=True)

        position_date = st.sidebar.date_input("Inform date:")
        last_day = Find_Date(df_asset, position_date)

        CumQ = 0
        CumC_rs = 0
        AvgPr_rs = 0
        CumC = 0
        AvgPr = 0

        if last_day != -1:
            CumQ = df_asset.loc[df_asset['Date'] == last_day, 'Cummulative Quantity'].item()
            CumC_rs = df_asset.loc[df_asset['Date'] == last_day, 'Cummulative Cost R$'].item()
            AvgPr_rs = df_asset.loc[df_asset['Date'] == last_day, 'Average Price R$'].item()
            CumC = df_asset.loc[df_asset['Date'] == last_day, 'Cummulative Cost US$'].item()
            AvgPr = df_asset.loc[df_asset['Date'] == last_day, 'Average Price US$'].item()

        st.header('Position for ' + str(selected_asset) + ' on ' + str(position_date))
        st.write('Reference date: ' + str(position_date))
        if last_day != -1:
            st.write('Last date before reference: ' + str(last_day))
        else:
            st.write('Last date before reference: No data on record')
        st.write('Cumulative Quantity: ' + str(CumQ))
        st.write('Cumulative Cost: R$ ' + str(CumC_rs))
        st.write('Average Price: R$ ' + str(AvgPr_rs))
        st.write('Cumulative Cost: US$ ' + str(CumC))
        st.write('Average Price: US$ ' + str(AvgPr))
