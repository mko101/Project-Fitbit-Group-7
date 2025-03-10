# IMPORTS 
import streamlit as st
import datetime
import part1

st.set_page_config(
    page_title="Fitbit Dashboard",
    page_icon="../images/logo.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    user = st.selectbox(
        "Select a user",
        sorted(part1.data["Id"].unique()),
        index=None,
        placeholder="Select a user",
    )

    if user:
        st.session_state.user = user
        st.switch_page("pages/1_User-specific_data.py")

    start_date = st.date_input("Select a start date:", datetime.date(2016, 3, 12), min_value=datetime.date(year=2016, month=3, day=12), max_value=datetime.date(year=2016, month=4, day=12))
    end_date = st.date_input("Select a end date:", datetime.date(2016, 4, 12), min_value=datetime.date(year=2016, month=3, day=12), max_value=datetime.date(year=2016, month=4, day=12))

st.write("This is the general page")