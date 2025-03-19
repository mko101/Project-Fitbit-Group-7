# IMPORTS 
import streamlit as st
import pandas as pd
import datetime
import part1
import plotly.express as px
import Part5 as part5
import numpy as np

# Define a function for styled containers
def create_metric_block(col, title, value, unit="", bg_color="#CFEBEC"):
    with col:
        container = st.container()
        container.markdown(
            f"""
            <style>
            .metric-box {{
                background-color: {bg_color};
                padding: 15px;
                border-radius: 13px;
                text-align: center;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                height: 130px;
                display: inline-block; 
                justify-content: center;  
                align-items: center; 
                text-align: center;
                display: flex;
                flex-direction: column;
                padding: 10px;
            }}
            .metric-title {{
                font-size: 17px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .metric-value {{
                font-size: 20px;
                font-weight: bold;
                color: #333;
            }}
            </style>
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value} {unit}</div>
            </div>
            """,
            unsafe_allow_html=True  
        )

def plot_activity_pie_chart(dates): 
    custom_colors = {
        "Very Active": "#005B8D",  
        "Fairly Active": "#006166", 
        "Lightly Active": "#00B3BD", 
        "Sedentary": "#CFEBEC"  
    }
    
    data = part5.activity_sum_data(dates)

    fig = px.pie(
        data, values='Minutes', names='Activity', 
        title="Average Activity Breakdown Per Day",
        hole=0.5, color='Activity', 
        color_discrete_map=custom_colors  
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", 
        )   
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Minutes: %{value:.0f}<extra></extra>"  
    )
    
    return fig

def bar_chart_hourly_average_steps(dates):
    hourly_data = part5.average_steps_per_hour(dates)

    # Identify top 3 most intensive hours
    top_hours = hourly_data.nlargest(3, "StepTotal")["Hour"].tolist()

    hourly_data["Color"] = hourly_data["Hour"].apply(lambda x: "#00B3BD" if x in top_hours else "#CFEBEC")
    hourly_data["HourFormatted"] = hourly_data["Hour"].astype(str) + ":00"

    fig = px.bar(
        hourly_data, 
        x="HourFormatted",
        y="StepTotal",
        title="Average Steps Per Hour",
        color="Color",
        color_discrete_map="identity",
        category_orders={"HourFormatted": [f"{h}:00" for h in sorted(hourly_data['Hour'].unique())]}  # Ensure correct order
    )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            title = None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False,  
        bargap=0.2
    )

    fig.update_traces(
        hovertemplate="<b>Hour:</b> %{x}<br><b>Avg Steps:</b> %{y:.0f}<extra></extra>"
    )

    return fig

def plot_heart_rate(dates):

    heart_rate_data = part5.hourly_average_heart_rate_dates(dates)
    heart_rate_data['Hour'] = heart_rate_data['Hour'].astype(str) + ":00"

    fig = px.line(
        heart_rate_data, 
        x="Hour", 
        y="Value",
        title="Average Heart Rate Per Hour",
        labels={"Hour": "Hour of Day", "Value": "Avg Heart Rate (bpm)"},
        line_shape="spline",  
        markers=True
    )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            title = None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False
    )

    fig.update_traces(line=dict(color="#00B3BD"))
    fig.update_traces(
        hovertemplate="<b>Hour:</b> %{x}<br><b>Avg Heart Rate:</b> %{y:.0f} bmp<extra></extra>"
    )

    return fig

def bar_chart_hourly_average_calories(dates):
    hourly_data = part5.hourly_average_calories(dates)

    # Identify top 3 most intensive hours
    top_hours = hourly_data.nlargest(3, "Calories")["Hour"].tolist()

    hourly_data["Color"] = hourly_data["Hour"].apply(lambda x: "#00B3BD" if x in top_hours else "#CFEBEC")
    hourly_data["HourFormatted"] = hourly_data["Hour"].astype(str) + ":00"

    # Plot histogram using Plotly
    fig = px.bar(
        hourly_data, 
        x="HourFormatted",
        y="Calories",
        title="Average Burned Calories Per Hour", 
        color="Color",
        color_discrete_map="identity",
        category_orders={"HourFormatted": [f"{h}:00" for h in sorted(hourly_data['Hour'].unique())]}  # Ensure correct order
    )

    # Customize layout
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            title = None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False,  
        bargap=0.2
    )

    fig.update_traces(
        hovertemplate="<b>Hour:</b> %{x}<br><b>Avg Calories:</b> %{y:.0f} kcal <extra></extra>"
    )

    return fig

def scatterplot_heart_rate_intensityvity(dates):
    data = part5.heart_rate_and_intensitivity(dates)

    corr = data["TotalIntensity"].corr(data["HeartRate"]) 
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"
    
    # Scatter plot with regression line 
    fig = px.scatter(
        data, 
        x="TotalIntensity", 
        y="HeartRate", 
        trendline="ols",
        labels={"TotalIntensity": "Exercise Intensity", "HeartRate": "Heart Rate (bpm)"},
        title="Correlation between Heart Rate<br>and Exercise Intensity"
    )

    fig.update_traces(
        hovertemplate="<b>Exercise Intensity:</b> %{x:.2f}<br><b>Heart Rate:</b> %{y:.0f} bpm<extra></extra>",
        marker=dict(color="#00B3BD"),
        line=dict(color="#005B8D")
    )
    
    return fig, corr

def scatterplot_calories_and_active_minutes(dates):
    data = part5.calories_and_active_minutes(dates)

    corr = data["Calories"].corr(data["TotalActiveMinutes"]) 
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="TotalActiveMinutes", 
        y="Calories", 
        trendline="ols",
        labels={"TotalActiveMinutes": "Active Minutes", "Calories": "Calories (kcal)"},
        title="Correlation between Calories <br>and Active Minutes"
    )

    fig.update_traces(
        hovertemplate="<b>Active Minutes:</b> %{x:.2f}<br><b>Calories:</b> %{y:.0f} kcal<extra></extra>",
        marker=dict(color="#00B3BD"),
        line=dict(color="#005B8D")
    )
    
    return fig, corr  

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

def bar_chart_average_distance_per_week(dates):
    total_distance_avr = part5.average_distance_per_week(dates)
    max_distance = total_distance_avr["TotalDistance"].max()
    total_distance_avr["Color"] = total_distance_avr["TotalDistance"].apply(
        lambda x: "#0095B2" if x == max_distance else "#8bc5d5"
    )
    fig = px.bar(
        total_distance_avr, 
        x="DayOfWeek", 
        y="TotalDistance",
        title="Average Total Distance Per Day of the Week",
        color="Color",
        color_discrete_map="identity"
    )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            title = None
        ),
        xaxis_title="", 
        yaxis_title="", 
    )
    fig.update_traces(
        hovertemplate="<b>Day of week:</b> %{x}<br><b>Total Distance:</b> %{y:.2f} km<extra></extra>",
    )
    return fig

def bar_chart_average_steps_per_week(dates):
    data_avr = part5.average_steps_per_week(dates)
    max_distance = data_avr["TotalSteps"].max()
    data_avr["Color"] = data_avr["TotalSteps"].apply(
        lambda x: "#0095B2" if x == max_distance else "#8bc5d5"
    )
    fig = px.bar(
        data_avr, 
        x="DayOfWeek", 
        y="TotalSteps",
        title="Average Total Steps Per Day of the Week",
        color="Color",
        color_discrete_map="identity"
    )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            title = None
        ),
        xaxis_title="", 
        yaxis_title="", 
    )
    fig.update_traces(
        hovertemplate="<b>Day of week:</b> %{x}<br><b>Total Steps:</b> %{y:.0f} <extra></extra>",
    )
    return fig

def bar_chart_average_calories_per_day_for_week(dates):
    data_avr = part5.average_calories_per_week(dates)
    max_distance = data_avr["Calories"].max()
    data_avr["Color"] = data_avr["Calories"].apply(
        lambda x: "#0095B2" if x == max_distance else "#8bc5d5"
    )
    fig = px.bar(
        data_avr, 
        x="DayOfWeek", 
        y="Calories",
        title="Average Total Calories Per Day of the Week",
        color="Color",
        color_discrete_map="identity"
    )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            title = None
        ),
        xaxis_title="", 
        yaxis_title="", 
    )
    fig.update_traces(
        hovertemplate="<b>Day of week:</b> %{x}<br><b> Calories:</b> %{y:.0f} kcal <extra></extra>",
    )
    return fig

def plot_active_minutes_bar_chart_per_day(dates):
    df = part5.average_active_minutes_per_week(dates)
    df_melted = df.melt(
        id_vars=["DayOfWeek"], 
        value_vars=["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes"], 
        var_name="ActivityLevel", 
        value_name="Minutes"
    )

    color_map = {
        "VeryActiveMinutes": "#006166",   
        "FairlyActiveMinutes": "#0095B2", 
        "LightlyActiveMinutes": "#8bc5d5" 
    }

    fig = px.bar(
        df_melted, 
        x="DayOfWeek", 
        y="Minutes", 
        color="ActivityLevel",
        title="Average Total Active Minutes Per Day of the Week",
        barmode="stack", 
        color_discrete_map=color_map
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", 
            title= ""
        ),  
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            title = None
        ),
        xaxis_title="", 
        yaxis_title="", 
    )
    fig.update_traces(
        hovertemplate="<b>Day:</b> %{x}<br>" 
                      "<b>Minutes:</b> %{y:.0f}<extra></extra>"
    )

    return fig

def bar_chart_workout_frequency_for_week(dates):
    data_avr = part5.workout_frequency_per_period(dates)
    max_distance = data_avr["WorkoutFrequency"].max()
    data_avr["Color"] = data_avr["WorkoutFrequency"].apply(
        lambda x: "#0095B2" if x == max_distance else "#8bc5d5"
    )
    fig = px.bar(
        data_avr, 
        x="DayOfWeek", 
        y="WorkoutFrequency",
        title="Total Number of Workouts per Period",
        color="Color",
        color_discrete_map="identity"
    )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            title = None
        ),
        xaxis_title="", 
        yaxis_title="", 
    )
    fig.update_traces(
        hovertemplate="<b>Day of week:</b> %{x}<br><b> Total number of workouts  </b> %{y:.0f} <extra></extra>",
    )
    return fig
    
    