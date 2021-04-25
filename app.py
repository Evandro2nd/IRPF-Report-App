import streamlit as st
from multiapp import MultiApp
from apps import home, brazil, us, remittance

app = MultiApp()

st.set_page_config(layout='wide')
st.markdown("""
# IRPF Report App

Choose the country of the portfolio for which the report
must be generated or choose Remittance for a report on
unrealized gain/loss by currency appreciation/depreciation
in the Navigation below:

""")

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Brazil", brazil.app)
app.add_app("US", us.app)
app.add_app("Remittance", remittance.app)
# The main app
app.run()
