# IMPORTS 
import pandas as pd
import numpy as np
import plotly.express as px
import part3
import Part5 as part5
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st

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

def create_correlation_block(title, value, unit="", bg_color="#CFEBEC"):
        container = st.container()
        container.markdown(
            f"""
            <style>
            .correlation-box {{
                background-color: {bg_color};
                padding: 10px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            }}
            .correlation-title {{
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 2px;
            }}
            .correlation-value {{
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }}
            </style>
            <div class="correlation-box">
                <div class="correlation-title">{title}</div>
                <div class="correlation-value">{value} {unit}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def is_empty_dataframe(df):
    if df.empty:
        create_correlation_block("", "Sorry, no data is available for the selected date range in this graph.", "")

def plot_activity_pie_chart(dates): 
    custom_colors = {
        "Very Active": "#005B8D",  
        "Fairly Active": "#006166", 
        "Lightly Active": "#00B3BD", 
        "Sedentary": "#CFEBEC"  
    }
    
    data = part5.activity_sum_data(dates)

    if data["Minutes"].sum() == 0:
        create_correlation_block("", "Sorry, no data is available for the selected date range in this graph.", "")

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
        ),   
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Minutes: %{value:.0f}<extra></extra>"  
    )
    
    return fig

def bar_chart_hourly_average_steps(dates):
    hourly_data = part5.average_steps_per_hour(dates)

    is_empty_dataframe(hourly_data)

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

    is_empty_dataframe(heart_rate_data)

    fig = px.line(
        heart_rate_data, 
        x="Hour", 
        y="Value",
        title="Heart Rate Per Hour",
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

    is_empty_dataframe(hourly_data)

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

    is_empty_dataframe(data)

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

    is_empty_dataframe(data)

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

def plot_correlation_sleep_sedentary_minutes(dates):
    data = part3.compare_sedentary_activity_and_sleep(dates)

    is_empty_dataframe(data)

    corr = data["SedentaryMinutes"].corr(data["TotalMinutesAsleep"])
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="SedentaryMinutes", 
        y="TotalMinutesAsleep",
        title="Correlation between Sedentary Minutes <br>and Minutes Asleep ",
        labels={"SedentaryMinutes": "Sedentary Minutes", "TotalMinutesAsleep": "Total Sleep Minutes"},
        trendline="ols"
    )

    fig.update_layout(
        xaxis=dict(
            title = "Sedentary Minutes"
        ),
        yaxis=dict(
            title="Total Minutes Asleep"
        ),
        yaxis_range=[0, 515],
        showlegend=False
    )

    fig.update_traces(
        marker=dict(color="#00B3BD"),
        line=dict(color="#005B8D")
    )
    
    fig.update_traces(
        hovertemplate="<b>Sedentary Minutes:</b> %{x}<br><b>Total Sleep Minutes:</b> %{y:.0f}<extra></extra>"
    )

    return fig, corr

def plot_correlation_sleep_active_minutes(dates):
    data = part3.compare_activity_and_sleep(None, dates)

    is_empty_dataframe(data)

    corr = data["ActiveMinutes"].corr(data["TotalMinutesAsleep"]) 
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="ActiveMinutes", 
        y="TotalMinutesAsleep",
        title="Correlation between Active Minutes <br>and Minutes Asleep",
        labels={"ActiveMinutes": "Active Minutes", "TotalMinutesAsleep": "Total Sleep Minutes"},
        trendline="ols"
    )

    fig.update_layout(
        xaxis=dict(
            title = "Active Minutes"
        ),
        yaxis=dict(
            title=None
        ),
        yaxis_range=[0, 515],
        showlegend=False
    )

    fig.update_traces(
        marker=dict(color="#00B3BD"),
        line=dict(color="#005B8D")
    )
    
    fig.update_traces(
        hovertemplate="<b>Active Minutes:</b> %{x}<br><b>Total Sleep Minutes:</b> %{y:.0f}<extra></extra>"
    )

    return fig, corr

def plot_correlation_weather_steps(hours, days, dates):
    data = part5.create_scatterplot_weather(part5.hourly_weather, part5.hourly_steps, hours, days, dates)

    is_empty_dataframe(data)

    corr = data["StepTotal"].corr(data["temp"]) 
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="StepTotal", 
        y="temp",
        title="Correlation between Temperature and Hourly Steps",
        labels={"StepTotal": "Hourly Steps", "temp": "Temperature (in F)"},
        trendline="ols"
    )

    fig.update_layout(
        xaxis=dict(
            title="Hourly Steps"
        ),
        yaxis=dict(
            title="Temperature (in F)"
        ),
        showlegend=False
    )

    fig.update_traces(
        marker=dict(color="#00B3BD"),
        line=dict(color="#005B8D")
    )
    
    fig.update_traces(
        hovertemplate="<b>Hourly Steps:</b> %{x}<br><b>Temperature:</b> %{y:.0f} (in F)<extra></extra>"
    )

    return fig, corr

def plot_correlation_weather_intensity(hours, days, dates):
    data = part5.create_scatterplot_weather(part5.hourly_weather, part5.hourly_intensity, hours, days, dates)

    is_empty_dataframe(data)

    corr = data["TotalIntensity"].corr(data["temp"]) 
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="TotalIntensity", 
        y="temp",
        title="Correlation between Temperature and <br> Hourly Total Intensity",
        labels={"TotalIntensity": "Hourly Total Intensity", "temp": "Temperature (in F)"},
        trendline="ols"
    )

    fig.update_layout(
        xaxis=dict(
            title="Hourly Total Intensity"
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False
    )

    fig.update_traces(
        marker=dict(color="#00B3BD"),
        line=dict(color="#005B8D")
    )
    
    fig.update_traces(
        hovertemplate="<b>Hourly Total Intensity:</b> %{x}<br><b>Temperature:</b> %{y:.0f} (in F)<extra></extra>"
    )

    return fig, corr

def bar_chart_daily_intensity(dates):
    hourly_data = part5.create_scatterplot_weather(part5.hourly_weather, part5.hourly_intensity, ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"], ["Weekdays", "Weekend"], dates)
    hourly_data = hourly_data.groupby(["Hour"], as_index=False)["TotalIntensity"].mean() 

    is_empty_dataframe(hourly_data)

    # Identify top 3 most intensive hours
    top_hours = hourly_data.nlargest(3, "TotalIntensity")["Hour"].tolist()

    hourly_data["Color"] = hourly_data["Hour"].apply(lambda x: "#00B3BD" if x in top_hours else "#CFEBEC")
    hourly_data["HourFormatted"] = hourly_data["Hour"].astype(str) + ":00"

    # Plot histogram using Plotly
    fig = px.bar(
        hourly_data, 
        x="HourFormatted",
        y="TotalIntensity",
        title="Average Total Intensity Per Hour",
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
        hovertemplate="<b>Hour:</b> %{x}<br><b>Avg Total Intensitys:</b> %{y:.0f}<extra></extra>"
    )

    return fig

def plot_active_minutes_active_distance(dates):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df = part5.daily_activity(dates)

    is_empty_dataframe(df)

    fig.add_trace(
        go.Scatter(
            x=df["ActivityDate"], 
            y=df["VeryActiveDistance"],
            name="Very Active Distance",
            line_shape="spline",  # Smooth curve
            marker=dict(color="#00B3BD"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["ActivityDate"],  
            y=df["VeryActiveMinutes"],
            name="Very Active Minutes",
            line_shape="spline",  # Smooth curve
            marker=dict(color="#005B8D"),
            yaxis="y2",
        )
    )

    fig.update_layout(
        title="Average Very Active Distance against Average Very Active Minutes",
        xaxis=dict(
            tickformat="%d<br>%B",
            tickangle=0,
            title="Month"
        ),
        yaxis=dict(
            title="Very Active Distance"
        ),
        yaxis2=dict(
            title="Very Active Minutes"
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5
        )   
    )

    fig.update_traces(
        hovertemplate="<b>Date:</b> %{x}<br><b>Avg Very Active Distance:</b> %{y:.0f} km<extra></extra>",
        selector=dict(name="Very Active Distance")
    )

    fig.update_traces(
        hovertemplate="<b>Date:</b> %{x}<br><b>Avg Very Active Minutes:</b> %{y:.0f}<extra></extra>",
        selector=dict(name="Very Active Minutes")
    )

    return fig

def plot_weight_pie_chart(): 
    custom_colors = {
        "50 - 70kg": "#CFEBEC",  
        "70 - 90kg": "#00B3BD", 
        "90 - 110kg": "#006166", 
        "110 - 130kg": "#005B8D" 
    }
    
    data = part5.categorized_weight_data()

    if data["Count"].sum() == 0:
        create_correlation_block("", "Sorry, no data is available for the selected date range in this graph.", "")

    fig = px.pie(
        data, values="Count", names="CategoryWeight", 
        title="Weight Breakdown over All Participants",
        hole=0.5, color="CategoryWeight", 
        color_discrete_map=custom_colors  
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal layout
        ),   
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Participants: %{value:.0f}<extra></extra>"  
    )
    
    return fig

def bar_chart_daily_sleep(dates):
    hourly_data = part5.sleep_data(dates)

    is_empty_dataframe(hourly_data)

    # Identify top 3 most intensive hours
    top_hours = hourly_data.nlargest(3, "TotalMinutesAsleep")["Hour"].tolist()

    hourly_data["Color"] = hourly_data["Hour"].apply(lambda x: "#00B3BD" if x in top_hours else "#CFEBEC")
    hourly_data["HourFormatted"] = hourly_data["Hour"].astype(str) + ":00"

    # Plot histogram using Plotly
    fig = px.bar(
        hourly_data, 
        x="HourFormatted",
        y="TotalMinutesAsleep",
        title="Average Minutes Asleep Per Hour",
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
        hovertemplate="<b>Hour:</b> %{x}<br><b>Avg Total Minutes Asleep:</b> %{y:.0f}<extra></extra>"
    )

    return fig

def bar_chart_weekly_sleep(dates):
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    weekly_data = part3.compute_sleep_on_day(None)
    weekly_data["date"] = pd.to_datetime(weekly_data["date"]).dt.normalize()
    weekly_data = weekly_data[weekly_data["date"].isin(dates)]
    weekly_data = weekly_data.groupby(["Day"], as_index=False)["TotalMinutesAsleep"].mean() 

    is_empty_dataframe(weekly_data)

    # Identify top 3 most intensive hours
    top_hours = weekly_data.nlargest(1, "TotalMinutesAsleep")["Day"].tolist()

    weekly_data["Color"] = weekly_data["Day"].apply(lambda x: "#0095B2" if x in top_hours else "#8BC5D5")
    weekly_data["DayFormatted"] = weekly_data["Day"].astype(str) + ":00"

    # Plot histogram using Plotly
    fig = px.bar(
        weekly_data, 
        x="DayFormatted",
        y="TotalMinutesAsleep",
        title="Average Total Minutes Asleep Per Day of the Week",
        color="Color",
        color_discrete_map="identity",
        category_orders={"DayFormatted": [f"{h}:00" for h in sorted(weekly_data["Day"].unique())]}  # Ensure correct order
    )

    # Customize layout
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            title = None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False,  
        bargap=0.2
    )

    fig.update_traces(
        hovertemplate="<b>Day:</b> %{x}<br><b>Avg Total Minutes Asleep:</b> %{y:.0f}<extra></extra>"
    )

    return fig

def plot_correlation_sleep_steps(dates):
    data = part5.create_dataframe_scatterplot_sleep("Steps", dates)

    is_empty_dataframe(data)

    corr = data["StepTotal"].corr(data["TotalMinutesAsleep"]) 
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="StepTotal", 
        y="TotalMinutesAsleep",
        title="Correlation between Total Steps <br>and Minutes Asleep",
        labels={"StepTotal": "Total Steps", "TotalMinutesAsleep": "Total Sleep Minutes"},
        trendline="ols"
    )

    fig.update_layout(
        xaxis=dict(
            title = "Total Steps"
        ),
        yaxis=dict(
            title="Total Minutes Asleep"
        ),
        showlegend=False
    )

    fig.update_traces(
        marker=dict(color="#00B3BD"),
        line=dict(color="#005B8D")
    )
    
    fig.update_traces(
        hovertemplate="<b>Total Steps:</b> %{x}<br><b>Total Sleep Minutes:</b> %{y:.0f}<extra></extra>"
    )

    return fig, corr

def plot_correlation_sleep_calories(dates):
    data = part5.create_dataframe_scatterplot_sleep("Calories", dates)

    is_empty_dataframe(data)

    corr = data["Calories"].corr(data["TotalMinutesAsleep"]) 
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="Calories", 
        y="TotalMinutesAsleep",
        title="Correlation between Calories <br>and Minutes Asleep",
        labels={"Calories": "Calories", "TotalMinutesAsleep": "Total Sleep Minutes"},
        trendline="ols"
    )

    fig.update_layout(
        xaxis=dict(
            title = "Calories"
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False
    )

    fig.update_traces(
        marker=dict(color="#00B3BD"),
        line=dict(color="#005B8D")
    )
    
    fig.update_traces(
        hovertemplate="<b>Calories:</b> %{x}<br><b>Total Sleep Minutes:</b> %{y:.0f}<extra></extra>"
    )

    return fig, corr

def plot_user_pie_chart(): 
    custom_colors = {
        "Light User (≤ 10 daily records)": "#CFEBEC",  
        "Moderate User (11 - 15 daily records)": "#00B3BD", 
        "Heavy User (≥ 16 daily records)": "#006166"
    }
    
    data = part3.create_new_dataframe()

    users = {
        "Light User (≤ 10 daily records)": data[data["Class"] == "Light User"].count()["Class"],
        "Moderate User (11 - 15 daily records)": data[data["Class"] == "Moderate User"].count()["Class"],
        "Heavy User (≥ 16 daily records)": data[data["Class"] == "Heavy User"].count()["Class"],
    }

    data = pd.DataFrame(list(users.items()), columns=["Class", "Count"])

    if data["Count"].sum() == 0:
        create_correlation_block("", "Sorry, no data is available for the selected date range in this graph.", "")
      
    fig = px.pie(
        data, values="Count", names="Class", 
        title="User Breakdown over All Participants",
        hole=0.5, color="Class", 
        color_discrete_map=custom_colors  
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal layout
        ),   
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Participants: %{value:.0f}<extra></extra>"  
    )
    
    return fig

def bar_chart_average_distance_per_week(dates):
    total_distance_avr = part5.average_distance_per_week(dates)
    max_distance = total_distance_avr["TotalDistance"].max()
    total_distance_avr["Color"] = total_distance_avr["TotalDistance"].apply(lambda x: "#0095B2" if x == max_distance else "#8bc5d5")
    
    is_empty_dataframe(total_distance_avr)

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
        yaxis_title="Kilometers", 
    )

    fig.update_traces(
        hovertemplate="<b>Day of week:</b> %{x}<br><b>Total Distance:</b> %{y:.2f} km<extra></extra>",
    )

    return fig

def bar_chart_average_steps_per_week(dates):
    data_avr = part5.average_steps_per_week(dates)
    max_distance = data_avr["TotalSteps"].max()
    data_avr["Color"] = data_avr["TotalSteps"].apply(lambda x: "#0095B2" if x == max_distance else "#8bc5d5")

    is_empty_dataframe(data_avr)

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
    data_avr["Color"] = data_avr["Calories"].apply(lambda x: "#0095B2" if x == max_distance else "#8bc5d5")

    is_empty_dataframe(data_avr)
    
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

    is_empty_dataframe(df_melted)

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
    data_avr["Color"] = data_avr["WorkoutFrequency"].apply(lambda x: "#0095B2" if x == max_distance else "#8bc5d5")

    is_empty_dataframe(data_avr)

    fig = px.bar(
        data_avr, 
        x="DayOfWeek", 
        y="WorkoutFrequency",
        title="Workout Frequency per Day of the Week",
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
        hovertemplate="<b>Day of week:</b> %{x}<br><b> Workout Frequency:</b> %{y:.2f} % <extra></extra>",
    )

    return fig