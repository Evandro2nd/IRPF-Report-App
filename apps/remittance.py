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

def LoadExchangeRate(df_temp, usdbrl_rate):
    '''
    Reads the exchange rate table from Banco Central (PTAX) and
    loads the data to the report
    '''
    cot = 0
    cot_list = []
    for row in df_temp.itertuples():
        cot = usdbrl_rate.loc[usdbrl_rate['Date'] == row[1], 'Sell'].item()
        cot_list.append(round(cot,4))
    df_temp['PTAX Rate'] = cot_list

def ComputeMoneySent_USD(df_temp, usdbrl_rate):
    '''
    Calculates the money sent to US by multiplying the
    value in R$ by the newly created column containing the PTAX
    '''
    df_temp['Value in US$'] = df_temp['Value in R$'] / df_temp['PTAX Rate']


def Compute_Average_Rate_to_Date(df_temp):
    '''
    Calculates the Average PTAX paid to date
    '''
    costRS = 0
    costUSD = 0
    avgRate = []
    avg = 0
    for row in df_temp.itertuples():
        costRS = costRS + row[2]
        costUSD = costUSD + row[4]
        avg = costRS / costUSD
        avgRate.append(round(avg,4))
    df_temp['Average Rate to Date (USDBRL)'] = avgRate


def load_data():
    df = pd.DataFrame()
    multiple_files = st.sidebar.file_uploader(
        "Upload remittance events here",
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

    st.title('Remittances to US Report')

    st.sidebar.header('User Input')

    df = load_data()
    usdbrl_rate = load_usdbrl()

    if not (df.empty or usdbrl_rate.empty):
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
        df['Date'] = df['Date'].dt.date
        # df.sort_values('Date', inplace=True, ignore_index=True)
        usdbrl_rate['Date'] = pd.to_datetime(usdbrl_rate['Date'], dayfirst=True)
        usdbrl_rate['Date'] = usdbrl_rate['Date'].dt.date
        usdbrl_rate.sort_values('Date', inplace=True, ignore_index=True)

        st.header("Complete History")
        # st.write(df)
        st.dataframe(df.style.set_precision(2))

        # ===== NEW COLUMN: Exchange Rate USDBRL
        LoadExchangeRate(df, usdbrl_rate)
        # ===== NEW COLUMN: Money sent in US$
        ComputeMoneySent_USD(df, usdbrl_rate)
        # ===== NEW COLUMN: Average exchange rate to date
        Compute_Average_Rate_to_Date(df)


        # ==================================== Generate Report
        st.header('Processed Report')
        # st.write(df_asset)
        st.dataframe(df.style.set_precision(2))

        plot1 = alt.Chart(df).mark_line().encode(
            x='Date',
            y='Average Rate to Date (USDBRL)'
        )
        st.header('Average Rate to Date (USDBRL)')
        st.altair_chart(plot1, use_container_width=True)

        position_date = st.sidebar.date_input("Inform date:")
        last_day = Find_Date(df, position_date)

        if last_day != -1:
            AverageRate = df.loc[df['Date'] == last_day, 'Average Rate to Date (USDBRL)'].item()
            PTAX_buy = usdbrl_rate.loc[usdbrl_rate['Date'] == position_date, 'Buy'].item()

        st.header('Unrealized gain/loss from currency apreciation/depreciation:')
        st.info('''The unrealized gain must be reported in the
        annual Tax Report in Brazil but it is not subject to taxes.''')
        cash_balance_USD = st.number_input('Inform the cash balance on ' + str(position_date))

        st.write('Reference date: ' + str(position_date))
        if last_day != -1:
            st.write('Last date before reference: ' + str(last_day))
            st.write(str(position_date) + ' cash balance in USD: US$ ' + str(cash_balance_USD))

            st.write('Average rate up to ' + str(last_day) + ': R$ ' + str(AverageRate))
            st.write('Cash balance in BRL by average rate: R$ ' + str(round(cash_balance_USD*AverageRate,2)))

            st.write(str(position_date) + ' PTAX (buy): R$ ' + str(PTAX_buy))
            st.write('Cash balance in BRL by PTAX (buy): R$ ' + str(round(cash_balance_USD*PTAX_buy,2)))
            st.write('Unrealized Gain/Loss: R$ ' + str(round(cash_balance_USD*(PTAX_buy-AverageRate),2)))
        else:
            st.write('Last date before reference: No data on record')
