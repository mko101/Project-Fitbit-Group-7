# IMPORTS
import streamlit as st
import part1

st.set_page_config(
    page_title="Fitbit Dashboard",
    page_icon="../images/logo.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    selected_user = st.session_state.user if "user" in st.session_state else None
    
    user = st.selectbox(
        "Pick a user",
        sorted(part1.data["Id"].unique()),
        index=sorted(part1.data["Id"].unique()).index(selected_user) if selected_user else None,
        placeholder="Select a user",
    )
    
st.write("This is the user specific page")