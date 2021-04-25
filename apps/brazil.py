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

def Compute_Cumm_Quantity(df_temp):
    '''
    Computes the cummulative quantity of an asset
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
    Computes the cummulative cost of an asset
    '''
    cum_cost = []
    cost = 0
    for row in df_temp.itertuples():
        if row[2] == 'COMPRA':
            cost = cost + row[5]
        elif row[2] == 'VENDA':
            cost = (cost/(row[4]+row[7]))*row[7]
        elif row[2] == 'DESDOBRAMENTO':
            cost = cost
        elif row[2] == 'GRUPAMENTO':
            cost = cost
        elif row[2] == 'BONIFICACAO':
            cost = cost + row[5]
        elif row[2] == 'AMORTIZACAO':
            cost = cost - row[5]
        cum_cost.append(round(cost,2))
    df_temp['Cummulative Cost'] = cum_cost

def Compute_Average_Price(df_temp):
    '''
    Computes the average price paid for an asset
    '''
    avg_price = []
    avg = 0
    for row in df_temp.itertuples():
        if row[2] == 'COMPRA':
            avg = row[8]/row[7]
        elif row[2] == 'VENDA':
            avg = avg
        elif row[2] == 'DESDOBRAMENTO':
            avg = row[8]/row[7]
        elif row[2] == 'GRUPAMENTO':
            avg = row[8]/row[7]
        elif row[2] == 'BONIFICACAO':
            avg = row[8]/row[7]
        elif row[2] == 'AMORTIZACAO':
            avg = row[8]/row[7]
        avg_price.append(round(avg,2))
    df_temp['Average Price'] = avg_price


def Compute_Profit_Loss(df_temp):
    '''
    Computes the average profit or loss obataind on selling an asset
    '''
    profit_loss = []
    money = 0
    for row in df_temp.itertuples():
        if row[2] == 'VENDA':
            money = (row[6]-row[9])*row[4]
        else:
            money = 0
        profit_loss.append(round(money,2))
    df_temp['Profit/Loss'] = profit_loss


def Compute_GCAP(df_temp):
    '''
    Computes the tax to be paid on capital gains
    after selling an asset with profit
    '''
    gcap = []
    tax = 0
    for row in df_temp.itertuples():
        if row[2] == 'VENDA' and row[10] > 0:
            if row[1].endswith("3"): # ação
                tax = 0.15*row[10]
            elif row[1].endswith("11"): # FII
                tax = 0.20*row[10]
        else:
            tax = 0
        gcap.append(round(tax,2))
    df_temp['GCAP'] = gcap


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

# ====================================== MAIN
def app():

    st.title('Brazil Porfolio Report')

    st.sidebar.header('User Input')

    df = load_data()

    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
        df['Date'] = df['Date'].dt.date
        df.sort_values('Date', inplace=True, ignore_index=True)

        st.header("Complete Portfolio History")
        # st.write(df)
        st.dataframe(df.style.set_precision(2))

        list_of_assets = sorted(list(set(df['Asset'].to_list())))
        selected_asset = st.sidebar.selectbox('Asset',list_of_assets)

        df_asset = df[df['Asset'] == selected_asset].copy()
        df_asset['Unit Price'] = round(df_asset['Price of Order R$'] / df_asset['Quantity'],2)

        # ====== NEW COLUMN: Cummulative Quantity
        Compute_Cumm_Quantity(df_asset)
        # ====== NEW COLUMN: Cummulative Cost
        Compute_Cumm_Cost(df_asset)
        # ====== NEW COLUMN: Average Price
        Compute_Average_Price(df_asset)
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
            y='Cummulative Cost'
        )

        st.header('Cumulative Cost')
        st.altair_chart(plot1, use_container_width=True)

        plot2 = alt.Chart(df_asset).mark_line().encode(
            x='Date',
            y='Average Price'
        )

        st.header('Average Price')
        st.altair_chart(plot2, use_container_width=True)

        position_date = st.sidebar.date_input("Inform date:")
        last_day = Find_Date(df_asset, position_date)

        CumQ = 0
        CumC = 0
        AvgPr = 0

        if last_day != -1:
            CumQ = df_asset.loc[df_asset['Date'] == last_day, 'Cummulative Quantity'].item()
            CumC = df_asset.loc[df_asset['Date'] == last_day, 'Cummulative Cost'].item()
            AvgPr = df_asset.loc[df_asset['Date'] == last_day, 'Average Price'].item()

        st.header('Position for ' + str(selected_asset) + ' on ' + str(position_date))
        st.write('Reference date: ' + str(position_date))
        if last_day != -1:
            st.write('Last date before reference: ' + str(last_day))
        else:
            st.write('Last date before reference: No data on record.')
        st.write('Cumulative Quantity: ' + str(CumQ))
        st.write('Cumulative Cost: R$ ' + str(CumC))
        st.write('Average Price: R$ ' + str(AvgPr))
