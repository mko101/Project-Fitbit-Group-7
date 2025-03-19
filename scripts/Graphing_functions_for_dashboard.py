# IMPORTS 
import streamlit as st
import plotly.express as px
import Part5 as part5
import numpy as np

# VERY LONG ACUISITION, NOT SURE IF USEFUL
def scatterplot_heart_rate_sleep_value(dates):
    data = part5.heart_rate_and_sleep_value(dates)
    
    # Scatter plot with regression line using Plotly
    fig = px.scatter(
        data, 
        x="SleepValue", 
        y="HeartRate", 
        trendline="ols",
        labels={"SleepValue": "Sleep Value", "HeartRate": "Heart Rate (bpm)"},
        title="Correlation between Heart Rate and Sleep Value"
    )

    fig.update_traces(
        hovertemplate="<b>Sleep Value:</b> %{x}<br><b>Heart Rate:</b> %{y:.0f} bpm<extra></extra>",
        marker=dict(color="#00B3BD"),
        line=dict(color="#005B8D")
    )
    
    return fig

# NOT SURE IF USEFUL
def lineplot_heart_rate_over_night(dates):
    data = part5.heart_rate_over_night(dates)

    fig = px.line(
        data, 
        x="Time", 
        y="HeartRate",
        labels={"Time": "Hour of Night", "HeartRate": "Average Heart Rate (bpm)"},
        title="Average Heart Rate Throughout the Night (Per Hour)"
    )
    fig.update_xaxes(
        tickmode="array", 
        tickvals=list(range(20, 9, -1)),  # Convert the range to a list
        ticktext=[f"{i}:00" for i in range(20, 9, -1)]  # Corresponding labels from 20:00 to 10:00
    )


    return fig