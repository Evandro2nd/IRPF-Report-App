import streamlit as st

def app():
    st.title('Home')

    # st.write('This is the `home page` of this IRPF Report App.')

    st.write('''Brazil and US portfolio reports as well as the unrealized gain/loss for currency appreciation/depreciation report
    are generated in order to fill the annual Tax Report in Brazil. The appreciation of money held in unpaid accounts outside
    Brazil must be reported as non-taxable earnings.''')

    st.markdown('''
    ### Credits:
    This Web App was created by using the [streamlit-multiapps](https://github.com/upraneelnihar/streamlit-multiapps)
    framework developed by [Praneel Nihar](https://medium.com/@u.praneel.nihar).
    Also check out his [Medium article](https://medium.com/@u.praneel.nihar/building-multi-page-web-app-using-streamlit-7a40d55fa5b4).
    ''')

    # st.markdown("""
    # ### NOTE:
    # When changing countries, remember to re-upload the portfolio files.
    # """)
