# IMPORTS
import streamlit as st
import datetime
import part1
import part3
import part4
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Fitbit Dashboard",
    page_icon="../images/logo.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

if "user" not in st.session_state:
    st.session_state.user = None

with st.sidebar:
    st.header("User Selection")
    user_sidebar = st.selectbox(
        "Select a user from the sidebar",
        sorted(part1.data["Id"].unique()),
        index=sorted(part1.data["Id"].unique()).index(st.session_state.user) if st.session_state.user else None,
        placeholder="Select a user",
        key="user_sidebar"
    )

    if user_sidebar != st.session_state.user:
        st.session_state.user = user_sidebar
        st.experimental_rerun() 

    start_date = st.date_input(
        "Select a start date:", 
        datetime.date(2016, 3, 12), 
        min_value=datetime.date(2016, 3, 12), 
        max_value=datetime.date(2016, 4, 12)
    )
    
    end_date = st.date_input(
        "Select an end date:", 
        datetime.date(2016, 4, 12), 
        min_value=datetime.date(2016, 3, 12), 
        max_value=datetime.date(2016, 4, 12)
    )

if st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #005B8D;'>📊 User Analysis - {}</h1>".format(st.session_state.user), unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #005B8D;'>📊 User Analysis</h1>", unsafe_allow_html=True)

selected_user_main = st.selectbox(
    "Select a user from the dropdown",
    sorted(part1.data["Id"].unique()),
    index=sorted(part1.data["Id"].unique()).index(st.session_state.user) if st.session_state.user else None,
    key="user_dropdown_main"
)

# Update the session state and sidebar
if selected_user_main != st.session_state.user:
    st.session_state.user = selected_user_main
    st.experimental_rerun()

if st.session_state.user:
    user = st.session_state.user
    
    user_data = part1.data[part1.data["Id"] == user]
    user_data["ActivityDate"] = pd.to_datetime(user_data["ActivityDate"])
    filtered_data = user_data[(user_data["ActivityDate"] >= pd.Timestamp(start_date)) & (user_data["ActivityDate"] <= pd.Timestamp(end_date))]
    
    if not filtered_data.empty:
        # Summary
        avg_steps = int(filtered_data["TotalSteps"].mean()) 
        avg_distance = round(filtered_data["TotalDistance"].mean(), 3)
        avg_calories = int(filtered_data["Calories"].mean())
        
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Average Steps", value=avg_steps)
        col2.metric(label="Average Distance (km)", value=avg_distance)
        col3.metric(label="Average Calories Burned", value=avg_calories)
        
        # Tabs for Daily Steps, Calories Burned, and Sleep Duration
        tab1, tab2, tab3 = st.tabs(["Daily Steps", "Calories Burned", "Sleep Duration"])
        
        # Tab 1: Daily Steps
        with tab1:
            st.subheader("Daily Steps")
            fig_steps = px.bar(filtered_data, x="ActivityDate", y="TotalSteps", title="Daily Steps")
            st.plotly_chart(fig_steps)
        
        # Tab 2: Calories Burned
        with tab2:
            st.subheader("Calories Burned Per Day")
            fig_calories = px.bar(filtered_data, x="ActivityDate", y="Calories", title="Calories Burned Per Day")
            st.plotly_chart(fig_calories)
        
        # Tab 3: Sleep Duration
        with tab3:
            st.subheader("Sleep Duration Over Time")
        
    else:
        st.warning("No data available for the selected date range.")