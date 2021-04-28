

IRPF Report App


Summary:

1. Introduction
2. Usage
   2.1. Data formatting for the App
   2.2. Command line instructions
3. Credits


1. INTRODUCTION

IRPF Report App was designed to help in the filling of the annual tax report in Brazil. Specifically the 
requirements related to portfolios of stocks, reits and ETFs owned in Brazil and United States. 
Unrealized gains (losses) in the appreciation (depreciation) of money held in the US is 
also calculated. Specifics of how the data must be fed to the App can be found below.

This is a Web App based on Streamlit. 

2. USAGE

2.1. Data Formatting for the App

The data in question are the orders of buy and sell as well as corporate events. The data must be loaded 
to the App in csv files. Multiples files are accepted at once.

The columns of the csv files for the Brazillian portfolio must be (in English):

Asset / Order / Date / Quantity / Price of Order R$

For the US portfolio they must be (in English):

Asset / Order / Date / Quantity / Price of Order US$

In all cases, the date must be informed in the format DD/MM/YY.

The Order column also accepts the corporate events. The only possbile values for the column order are 
(in Brazilian Portuguese):

 - compra
 - venda
 - desdobramento
 - grupamento
 - amortizacao
 - bonificacao
 
 Special characters such as ç and accents such as ~ are not allowed. 
 For each value above there is a proper way to fill the columns Quantity and Price of Order R$:
 
 - compra: total quantity bought and total cost
 - venda: total quantity sold and total selling value
 - desdobramento: new amount of shares at zero cost
 - grupamento: amount of shares reduced at zero cost
 - amortizacao: total amount of shares owned at the Ex-date and the total amount of returned capital informed by the Company
 - bonificacao: new shares received at the cost informed by the Company
 
The csv file containing the remittance events must have the following columns:

Date / Value in R$

The date must again be informed in the format DD/MM/YY.

The csv files containing the exchange rates for USDBRL must have the following columns:

Date / Type / Buy / Sell

The exchange rates must be obained from the Central Bank of Brazil website: https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes
 
2.2. Command-line Instructions

Provided you have a virtual environment setup with all libraries listed at the requirements.txt file, 
this Web App must be run following the usual streamlit procedure:

$ streamlit run app.py

3. CREDITS

This Web App was created by using the [streamlit-multiapps](https://github.com/upraneelnihar/streamlit-multiapps)
framework developed by [Praneel Nihar](https://medium.com/@u.praneel.nihar).
Also check out his [Medium article](https://medium.com/@u.praneel.nihar/building-multi-page-web-app-using-streamlit-7a40d55fa5b4).

