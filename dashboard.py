import numpy as np
import pandas as pd
import streamlit as st

st.title('Shodan API')

#sidebar
st.sidebar.title('Settings')
api_key = st.sidebar.text_input('API Key:')
#set sidebar to defalt open


#Horizontal layout
with st.container():

    # Input bar in col1
    query = st.text_input('Query:')

    # Button in col2
    button = st.button('Search', use_container_width=True)


    #on button click