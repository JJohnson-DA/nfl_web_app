import streamlit as st
import funcs


def app():
    with st.container():
        st.title("NFL Data Exploration App")
        st.write(
            """
            Thanks for exploration our page! We hope you find some cool insights while you\'re here. 
            
            Use the filters in the sidebar to navigate between pages and choose filters.
            """
        )
        st.write("---")
    # with st.container():
    #     st.write(
    #         "Data for this app was sourced from nfl_data_py. This is a Python library for interacting with NFL data from nflfastR, nfldata, dynastyprocess, and Draft Scout."
    #     )

