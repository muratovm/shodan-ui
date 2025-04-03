import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from api import ShodanAPI
import yaml

st.title('Shodan API')

#sidebar
st.sidebar.title('Settings')


shodan = ShodanAPI()

api_key = st.sidebar.text_input('API Key:', value=shodan.api_key)
update_key = st.sidebar.button('Update API Key')
if update_key:
    shodan.api_key = api_key
    st.write('API Key updated')

#set sidebar to defalt open



#Horizontal layout
with st.container():

    # Input bar in col1
    query = st.text_input('Query:')

    # Button in col2
    button = st.button('Search', use_container_width=True)

    #on button click
    if button:
        #search for query
        st.write(f'Searching for: {query}')
        #search results 
        results = shodan.search_and_save_query_results(query)
        #if no results
        if not results or len(results) == 0:
            st.write('No results found')
        else:
            #show results
            st.write(f'Total results: {len(results)}')
            df = pd.json_normalize(results)
            st.dataframe(df[["ip_str", "port", "org", "location.country_name", "location.city"]])
            st.write('Results saved')


#horizontal line
st.markdown('---')

st.button('Show cache', key='show_cache')
if st.session_state.show_cache:
    df = shodan.cache.get_dataframe()
    st.dataframe(df)
    st.write('Cache loaded')
else:
    st.write('Cache not loaded')
    