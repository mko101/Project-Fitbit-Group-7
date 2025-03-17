# IMPORTS 
import streamlit as st
import pandas as pd
import datetime
import Graphing_functions_for_dashboard as gf
import part1
import plotly.express as px
import Part5 as part5
import numpy as np

st.set_page_config(
    page_title="Fitbit Dashboard",
    page_icon="../images/logo.png",
    layout="wide",
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

    start_date = st.date_input("Select a start date:", datetime.date(2016, 3, 12), min_value=datetime.date(year=2016, month=3, day=12), max_value=datetime.date(year=2016, month=4, day=12), format="MM/DD/YYYY")
    end_date = st.date_input("Select an end date:", datetime.date(2016, 4, 12), min_value=datetime.date(year=2016, month=3, day=12), max_value=datetime.date(year=2016, month=4, day=12), format="MM/DD/YYYY")

    if start_date and end_date:
        if start_date > end_date:
            st.error("Please ensure that the end date is later than the start date.")
        else:
            dates = pd.date_range(start_date, end_date, freq='d').strftime("%m/%d/%Y")

# Row of average metrics
col1, col2, col3, col4, col5, col6 = st.columns(6)

# Retrieve data
steps = part5.retrieve_average("TotalSteps", dates)
users = part5.retrieve_average("total_users", dates) 
distance = part5.retrieve_average("TotalDistance", dates) 
calories = part5.retrieve_average("Calories", dates) 
active_minutes = part5.retrieve_average("ActiveMinutes", dates) 
sedentary_minutes = part5.retrieve_average("SedentaryMinutes", dates) 

# Display each metric
gf.create_metric_block(col1, "Total Users", users, "")
gf.create_metric_block(col2, "Average Steps", steps, "")
gf.create_metric_block(col3, "Average Distance", distance, "km")
gf.create_metric_block(col4, "Average Calories", calories, "kcal")
gf.create_metric_block(col5, "Avr. Active Min", active_minutes, "")
gf.create_metric_block(col6, "Avr. Sedentary Min", sedentary_minutes, "")

# First row of graphs
col1, col2, col3 = st.columns([1, 1.5, 1.5])  

with col1:
    st.plotly_chart(gf.plot_activity_pie_chart(dates), use_container_width=True)
with col2:
    st.plotly_chart(gf.bar_chart_hourly_average_steps(dates), use_container_width=True)
with col3:
    st.plotly_chart(gf.plot_heart_rate(dates), use_container_width=True)

# Second row of graphs
col1, col2, col3 = st.columns([1.5, 1.5, 1.5])  

with col1:
    st.plotly_chart(gf.bar_chart_hourly_average_calories(dates), use_container_width=True)
with col2:
    st.plotly_chart(gf.scatterplot_heart_rate_intensityvity(dates), use_container_width=True)
with col3:
    st.plotly_chart(gf.scatterplot_calories_and_active_minutes(dates), use_container_width=True)

col1, col2 = st.columns([2,2])  

# Third row of graphs
with col1:
    st.plotly_chart(gf.bar_chart_average_distance_per_week(dates), use_container_width=True)
with col2:
    st.plotly_chart(gf.bar_chart_average_steps_per_week(dates), use_container_width=True)


# Fourth row of graphs
col1, col2 = st.columns([2,2])  

with col1:
    st.plotly_chart(gf.bar_chart_average_calories_per_day_for_week(dates), use_container_width=True)
with col2:
    st.plotly_chart(gf.plot_active_minutes_bar_chart_per_day(dates), use_container_width=True)


