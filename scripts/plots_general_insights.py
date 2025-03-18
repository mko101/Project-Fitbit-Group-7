# IMPORTS 
import pandas as pd
import numpy as np
import plotly.express as px
import part3
import Part5 as part5
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
            orientation="h",  # Horizontal layout
        ),   
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Minutes: %{value:.0f}<extra></extra>"  
    )
    
    return fig

def hist_daily_average_steps(dates):
    hourly_data = part5.average_steps_per_hour(dates)

    # Identify top 3 most intensive hours
    top_hours = hourly_data.nlargest(3, "StepTotal")["Hour"].tolist()

    hourly_data["Color"] = hourly_data["Hour"].apply(lambda x: "#00B3BD" if x in top_hours else "#CFEBEC")
    hourly_data["HourFormatted"] = hourly_data["Hour"].astype(str) + ":00"

    # Plot histogram using Plotly
    fig = px.bar(
        hourly_data, 
        x="HourFormatted",
        y="StepTotal",
        title="Average Steps Per Hour",
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
        title="Heart Rate Per Hour",
        labels={"Hour": "Hour of Day", "Value": "Avg Heart Rate (bpm)"},
        line_shape="spline",  # Smooth curve
        markers=True
    )

    # Format x-axis for better readability
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

def plot_correlation_sleep_sedentary_minutes(dates):
    data = part3.compare_sedentary_activity_and_sleep(dates)

    corr = data["SedentaryMinutes"].corr(data["TotalMinutesAsleep"])
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="SedentaryMinutes", 
        y="TotalMinutesAsleep",
        title="Correlation between Sedentary Minutes and Total Sleep Minutes",
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

def plot_correlation_sleep_active_minutes(user_id, dates):
    data = part3.compare_activity_and_sleep(user_id, dates)

    corr = data["ActiveMinutes"].corr(data["TotalMinutesAsleep"]) 
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="ActiveMinutes", 
        y="TotalMinutesAsleep",
        title="Correlation between Active Minutes and Total Sleep Minutes",
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

    corr = data["TotalIntensity"].corr(data["temp"]) 
    corr = "Sorry, there is not enough data for this statistic" if np.isnan(corr) else f"{corr:.4f}"

    fig = px.scatter(
        data, 
        x="TotalIntensity", 
        y="temp",
        title="Correlation between Temperature and Hourly Total Intensity",
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

def hist_daily_intensity(dates):
    hourly_data = part5.create_scatterplot_weather(part5.hourly_weather, part5.hourly_intensity, ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"], ["Weekdays", "Weekend"], dates)
    hourly_data = hourly_data.groupby(["Hour"], as_index=False)["TotalIntensity"].mean() 

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
            marker=dict(color="#CFEBEC"),
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
        hovertemplate="<b>Date:</b> %{x}<br><b>Avg Very Active Distance:</b> %{y:.0f}<extra></extra>",
        selector=dict(name="Very Active Distance")
    )

    fig.update_traces(
        hovertemplate="<b>Date:</b> %{x}<br><b>Avg Very Active Minutes:</b> %{y:.0f}<extra></extra>",
        selector=dict(name="Very Active Minutes")
    )

    return fig

def plot_weight_pie_chart(dates): 
    custom_colors = {
        "50 - 70kg": "#CFEBEC",  
        "70 - 90kg": "#00B3BD", 
        "90 - 110kg": "#006166", 
        "110 - 130kg": "#005B8D" 
    }
    
    data = part5.categorized_weight_data(dates)

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

def hist_daily_sleep(dates):
    hourly_data = part5.sleep_data(dates)

    # Identify top 3 most intensive hours
    top_hours = hourly_data.nlargest(3, "TotalMinutesAsleep")["Hour"].tolist()

    hourly_data["Color"] = hourly_data["Hour"].apply(lambda x: "#00B3BD" if x in top_hours else "#CFEBEC")
    hourly_data["HourFormatted"] = hourly_data["Hour"].astype(str) + ":00"

    # Plot histogram using Plotly
    fig = px.bar(
        hourly_data, 
        x="HourFormatted",
        y="TotalMinutesAsleep",
        title="Average Total Minutes Asleep Per Hour",
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

def hist_weekly_sleep(dates):
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    weekly_data = part3.compute_sleep_on_day(None)
    weekly_data["date"] = pd.to_datetime(weekly_data["date"]).dt.normalize()
    weekly_data = weekly_data[weekly_data["date"].isin(dates)]
    weekly_data = weekly_data.groupby(["Day"], as_index=False)["TotalMinutesAsleep"].mean() 

    # Identify top 3 most intensive hours
    top_hours = weekly_data.nlargest(2, "TotalMinutesAsleep")["Day"].tolist()

    weekly_data["Color"] = weekly_data["Day"].apply(lambda x: "#00B3BD" if x in top_hours else "#CFEBEC")
    weekly_data["DayFormatted"] = weekly_data["Day"].astype(str) + ":00"

    # Plot histogram using Plotly
    fig = px.bar(
        weekly_data, 
        x="DayFormatted",
        y="TotalMinutesAsleep",
        title="Average Total Minutes Asleep Per Week",
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