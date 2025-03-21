# IMPORTS
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import part1
import part3
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_user_data(user, start_date, end_date):
    # Get user data
    user_data = part1.data[part1.data["Id"] == user].copy()
    user_data.loc[:, "ActivityDate"] = pd.to_datetime(user_data["ActivityDate"], format="%Y-%m-%d")
    
    # Filter data based on selected date range
    filtered_data = user_data[(user_data["ActivityDate"] >= pd.Timestamp(start_date)) & 
                             (user_data["ActivityDate"] <= pd.Timestamp(end_date))]
    
    return filtered_data

def get_all_users_data(start_date, end_date):
    # Get all data
    all_data = part1.data.copy()
    
    # Convert date column to datetime
    all_data.loc[:, "ActivityDate"] = pd.to_datetime(all_data["ActivityDate"], format="%Y-%m-%d")
    
    # Filter data based on selected date range
    filtered_data = all_data[(all_data["ActivityDate"] >= pd.Timestamp(start_date)) & 
                           (all_data["ActivityDate"] <= pd.Timestamp(end_date))]
    
    return filtered_data

def plot_steps_calories_combined(user, start_date, end_date):
    # Get user data
    filtered_data = get_user_data(user, start_date, end_date)
    
    if filtered_data.empty:
        return None
    
    max_steps_day = filtered_data.loc[filtered_data["TotalSteps"].idxmax(), "ActivityDate"]
    max_calories_day = filtered_data.loc[filtered_data["Calories"].idxmax(), "ActivityDate"]
    
    step_colors = ['#00B3BD' if date == max_steps_day else '#CFEBEC' for date in filtered_data["ActivityDate"]]
    calorie_colors = ['#005B8D' if date == max_calories_day else '#006166' for date in filtered_data["ActivityDate"]]
    
    # Create subplot with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add steps as bars on primary y-axis
    fig.add_trace(
        go.Bar(
            x=filtered_data["ActivityDate"],
            y=filtered_data["TotalSteps"],
            name="Steps",
            marker_color=step_colors,
            hovertemplate="<b>Date:</b> %{x}<br><b>Steps:</b> %{y:,.0f}<extra></extra>"
        ),
        secondary_y=False
    )
    
    all_users_data = get_all_users_data(start_date, end_date)
    
    if not all_users_data.empty:
        # Calculate overall average steps across all users and all dates
        overall_avg_steps = all_users_data["TotalSteps"].mean()
        
        # Create a horizontal line at the overall average steps
        fig.add_trace(
            go.Scatter(
                x=[filtered_data["ActivityDate"].min(), filtered_data["ActivityDate"].max()],
                y=[overall_avg_steps, overall_avg_steps],
                name="Avg Steps (All Users)",
                mode="lines",
                line=dict(
                    color="#005B8D", 
                    width=2,
                    dash="dash"
                ),
                hovertemplate="<b>Avg Steps (All Users):</b> %{y:,.0f}<extra></extra>"
            ),
            secondary_y=False
        )
    
    # Add calories as line on secondary y-axis
    fig.add_trace(
        go.Scatter(
            x=filtered_data["ActivityDate"],
            y=filtered_data["Calories"],
            name="Calories",
            mode="lines+markers",
            line=dict(color="#006166", width=3),
            marker=dict(
                size=8,
                color=calorie_colors,
                line=dict(width=2, color="#006166")
            ),
            hovertemplate="<b>Date:</b> %{x}<br><b>Calories:</b> %{y:,.0f} kcal<extra></extra>"
        ),
        secondary_y=True
    )
    
    # Set chart title and axis labels
    fig.update_layout(
        title="Daily Steps and Calories",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            tickangle=-45,
            title=None,
            gridcolor="#f0f0f0"
        ),
        bargap=0.3,
        plot_bgcolor="white"
    )
    
    # Set y-axes titles and ranges
    fig.update_yaxes(
        title_text="Steps",
        secondary_y=False,
        gridcolor="#f0f0f0",
        title=None
    )
    
    fig.update_yaxes(
        title_text="Calories (kcal)",
        secondary_y=True,
        gridcolor="#f0f0f0",
        title=None
    )
    
    # Automatically set ranges to start from 0
    max_steps = filtered_data["TotalSteps"].max() * 1.1  # Add 10% padding
    max_calories = filtered_data["Calories"].max() * 1.1  # Add 10% padding
    
    fig.update_yaxes(range=[0, max_steps], secondary_y=False)
    fig.update_yaxes(range=[0, max_calories], secondary_y=True)
    
    return fig

def get_user_data_with_sleep(user, start_date, end_date):
    # Get user data
    user_data = part1.data[part1.data["Id"] == user].copy()
    user_data.loc[:, "ActivityDate"] = pd.to_datetime(user_data["ActivityDate"], format="%Y-%m-%d")
    
    # Fetch sleep duration and merge with user_data
    sleep_data = part3.compute_sleep_duration(user)
    sleep_data.rename(columns={"MinutesSlept": "TotalSleepMinutes"}, inplace=True)
    sleep_data["TotalSleepHours"] = sleep_data["TotalSleepMinutes"] / 60
    sleep_data["Date"] = pd.to_datetime(sleep_data["Date"], errors="coerce")
    
    # Merge sleep duration into user_data based on date
    filtered_data = user_data.merge(sleep_data, left_on="ActivityDate", right_on="Date", how="left")
    
    # Filter data based on selected date range
    filtered_data = filtered_data[(filtered_data["ActivityDate"] >= pd.Timestamp(start_date)) & 
                                 (filtered_data["ActivityDate"] <= pd.Timestamp(end_date))]
    
    return filtered_data

def plot_daily_steps(user, start_date, end_date):
    filtered_data = get_user_data(user, start_date, end_date)
    
    if filtered_data.empty:
        return None
    
    # Identify the highest step day
    max_steps_day = filtered_data.loc[filtered_data["TotalSteps"].idxmax(), "ActivityDate"]

    filtered_data["Color"] = filtered_data["ActivityDate"].apply(
        lambda x: "#00B3BD" if x == max_steps_day else "#CFEBEC"
    )

    fig_steps = px.bar(
        filtered_data, 
        x="ActivityDate", 
        y="TotalSteps", 
        title="Daily Steps",
        color="Color",
        color_discrete_map="identity"
    )

    fig_steps.update_layout(
        xaxis=dict(
            tickangle=-45,
            title=None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False,
        bargap=0.2
    )

    fig_steps.update_traces(
        hovertemplate="<b>Date:</b> %{x}<br><b>Steps:</b> %{y:.0f}<extra></extra>"
    )
    
    return fig_steps

def plot_daily_calories(user, start_date, end_date):
    filtered_data = get_user_data(user, start_date, end_date)
    
    if filtered_data.empty:
        return None
    
    # Identify the highest calorie burn day
    max_calories_day = filtered_data.loc[filtered_data["Calories"].idxmax(), "ActivityDate"]

    filtered_data["Color"] = filtered_data["ActivityDate"].apply(
        lambda x: "#00B3BD" if x == max_calories_day else "#CFEBEC"
    )

    fig_calories = px.bar(
        filtered_data, 
        x="ActivityDate", 
        y="Calories", 
        title="Calories Burned Per Day",
        color="Color",
        color_discrete_map="identity"
    )

    fig_calories.update_layout(
        xaxis=dict(
            tickangle=-45,
            title=None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False,
        bargap=0.2
    )

    fig_calories.update_traces(
        hovertemplate="<b>Date:</b> %{x}<br><b>Calories:</b> %{y:.0f} kcal<extra></extra>"
    )
    
    return fig_calories

def plot_activity_breakdown(user, start_date, end_date):
    filtered_data = get_user_data(user, start_date, end_date)
    
    if filtered_data.empty:
        return None
    
    # Define the activity columns
    activity_columns = ['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']
    
    # Create a dataframe for the pie chart
    pie_data = pd.DataFrame({
        'Activity': ['Very Active', 'Fairly Active', 'Lightly Active', 'Sedentary'],
        'Minutes': [
            filtered_data[activity_columns[0]].mean(),
            filtered_data[activity_columns[1]].mean(),
            filtered_data[activity_columns[2]].mean(),
            filtered_data[activity_columns[3]].mean()
        ]
    })
    
    # Define the same custom colors as in General_insights.py
    custom_colors = {
        "Very Active": "#005B8D",  
        "Fairly Active": "#006166", 
        "Lightly Active": "#00B3BD", 
        "Sedentary": "#CFEBEC"  
    }
    
    # Create pie chart
    fig = px.pie(
        pie_data, values='Minutes', names='Activity', 
        title="Activity Breakdown",
        hole=0.5, color='Activity', 
        color_discrete_map=custom_colors  
    )
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", 
        )   
    )
    
    # Update traces
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Minutes: %{value:.0f}<extra></extra>"  
    )
    
    return fig

def plot_sleep_duration(user, start_date, end_date):
    filtered_data = get_user_data_with_sleep(user, start_date, end_date)
    
    if filtered_data.empty or filtered_data["TotalSleepHours"].isna().all():
        return None
    
    # Identify the best sleep day
    max_sleep_day = filtered_data.loc[filtered_data["TotalSleepHours"].idxmax(), "ActivityDate"]

    filtered_data["Color"] = filtered_data["ActivityDate"].apply(
        lambda x: "#00B3BD" if x == max_sleep_day else "#CFEBEC"
    )
    
    fig_sleep = px.bar(
        filtered_data, 
        x="ActivityDate", 
        y="TotalSleepHours", 
        title="Sleep Duration (Hours)",
        color="Color",
        color_discrete_map="identity"
    )

    fig_sleep.update_layout(
        xaxis=dict(
            tickangle=-45,
            title=None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False,
        bargap=0.2
    )

    fig_sleep.update_traces(
        hovertemplate="<b>Date:</b> %{x}<br><b>Sleep:</b> %{y:.1f} hours<extra></extra>"
    )
    
    return fig_sleep

def get_heart_rate_data(user, start_date, end_date):
    conn = sqlite3.connect('../data/fitbit_database.db') 
    cur = conn.cursor()
    
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    if user:
        query = f"SELECT Id, Time, Value FROM heart_rate WHERE Id = '{user}'"
    else:
        query = "SELECT Id, Time, Value FROM heart_rate"
    
    cur.execute(query)
    rows = cur.fetchall()
    
    data = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    
    # Convert Time to datetime
    data["Time"] = pd.to_datetime(data["Time"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce')
    
    # Filter by date range
    filtered_data = data[data["Time"].dt.date.isin(date_range.date)]
    
    # Add helpful columns
    if not filtered_data.empty:
        filtered_data["Date"] = filtered_data["Time"].dt.date
        filtered_data["Hour"] = filtered_data["Time"].dt.hour
    
    conn.close()
    
    return filtered_data

def plot_heart_rate_trends(user, start_date, end_date):
    hr_data = get_heart_rate_data(user, start_date, end_date)
    
    if hr_data.empty:
        return None
    
    # Group by hour and calculate the average heart rate
    hourly_data = hr_data.groupby("Hour")["Value"].mean().reset_index()
    hourly_data["Value"] = hourly_data["Value"].round(1)
    
    # Format hour for display
    hourly_data["HourFormatted"] = hourly_data["Hour"].astype(str) + ":00"
    
    # Create the line chart
    fig = px.line(
        hourly_data, 
        x="Hour", 
        y="Value",
        title="Average Heart Rate By Hour",
        labels={"Hour": "Hour of Day", "Value": "Heart Rate (bpm)"},
        line_shape="spline", 
        markers=True
    )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            title=None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False
    )
    
    # Update line properties
    fig.update_traces(line=dict(color="#00B3BD", width=3))
    
    fig.update_traces(
        hovertemplate="<b>Hour:</b> %{x}:00<br><b>Avg Heart Rate:</b> %{y:.1f} bpm<extra></extra>"
    )
    
    return fig

def plot_heart_rate_zones(user, start_date, end_date):
    hr_data = get_heart_rate_data(user, start_date, end_date)
    
    if hr_data.empty:
        return None
    
    # Define simplified heart rate zones (3 categories)
    zones = {
        'Rest (0-70 bpm)': (0, 70),      # Resting/low activity
        'Active (70-120 bpm)': (70, 120),  # Normal activity/moderate exercise
        'Intense (120+ bpm)': (120, 300) # Vigorous exercise
    }
    
    def classify_zone(value):
        for zone_name, (lower, upper) in zones.items():
            if lower <= value < upper:
                return zone_name
        return 'Intense (120+ bpm)'
    
    hr_data['Zone'] = hr_data['Value'].apply(classify_zone)
    
    # Count measurements in each zone
    zone_counts = hr_data['Zone'].value_counts().reset_index()
    zone_counts.columns = ['Zone', 'Count']
    
    # Group data by minute and calculate average heart rate for each minute
    if not hr_data.empty:
        hr_data['MinuteGroup'] = hr_data['Time'].dt.floor('min')
        minute_avg = hr_data.groupby('MinuteGroup')['Value'].mean().reset_index()
        
        minute_avg['Zone'] = minute_avg['Value'].apply(classify_zone)
        
        zone_minutes = minute_avg['Zone'].value_counts().reset_index()
        zone_minutes.columns = ['Zone', 'Minutes']
    else:
        zone_minutes = pd.DataFrame(columns=['Zone', 'Minutes'])
    
    custom_colors = {
        'Rest (0-70 bpm)': '#CFEBEC',
        'Active (70-120 bpm)': '#00B3BD',
        'Intense (120+ bpm)': '#005B8D'
    }
    
    fig = px.pie(
        zone_minutes, 
        values='Minutes', 
        names='Zone', 
        title="Time in Heart Rate Zones",
        hole=0.5, 
        color='Zone', 
        color_discrete_map=custom_colors
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h")
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Minutes: %{value:.0f}<extra></extra>"
    )
    
    return fig

def get_heart_rate_for_day(user, selected_date):
    conn = sqlite3.connect('../data/fitbit_database.db')
    selected_date = pd.Timestamp(selected_date)
    
    # Query all heart rate data for this user without date filtering or ordering
    query = f"""
    SELECT Id, Time, Value
    FROM heart_rate
    WHERE Id = '{user}'
    """
    
    heart_rate_data = pd.read_sql_query(query, conn)
    conn.close()
    
    if not heart_rate_data.empty:
        heart_rate_data['Time'] = pd.to_datetime(heart_rate_data['Time'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
        
        heart_rate_data = heart_rate_data[heart_rate_data['Time'].dt.date == selected_date.date()]
        
        heart_rate_data = heart_rate_data.sort_values(by='Time')
        
        heart_rate_data['Hour'] = heart_rate_data['Time'].dt.hour
        heart_rate_data['Minute'] = heart_rate_data['Time'].dt.minute
        heart_rate_data['TimeOfDay'] = heart_rate_data['Time'].dt.strftime('%H:%M')
    
    return heart_rate_data


def plot_daily_heart_rate(user, selected_date):
    hr_data = get_heart_rate_for_day(user, selected_date)
    
    if hr_data.empty:
        return None
    
    # Format the date for display
    display_date = pd.Timestamp(selected_date).strftime('%B %d, %Y')
    
    # Create the line chart
    fig = px.line(
        hr_data, 
        x='Time', 
        y='Value',
        title=f"Heart Rate Throughout {display_date}",
        labels={"Time": "Time of Day", "Value": "Heart Rate (bpm)"}
    )
    
    # Calculate resting, average, and peak heart rates
    resting_hr = hr_data['Value'].quantile(0.05)  # Approximate resting HR
    avg_hr = hr_data['Value'].mean()
    peak_hr = hr_data['Value'].max()
    
    # Add horizontal lines for reference
    fig.add_hline(y=resting_hr, line_dash="dash", line_color="#CFEBEC", 
                  annotation_text="Resting", annotation_position="top right")
    fig.add_hline(y=avg_hr, line_dash="dash", line_color="#00B3BD", 
                  annotation_text="Average", annotation_position="top right")
    fig.add_hline(y=peak_hr, line_dash="dash", line_color="#005B8D", 
                  annotation_text="Peak", annotation_position="top right")
    
    active_periods = []
    current_start = None
    threshold = avg_hr * 1.1 
    
    for idx, row in hr_data.iterrows():
        if row['Value'] > threshold and current_start is None:
            current_start = row['Time']
        elif row['Value'] <= threshold and current_start is not None:
            active_periods.append((current_start, row['Time']))
            current_start = None
    
    if current_start is not None:
        active_periods.append((current_start, hr_data['Time'].iloc[-1]))
    
    for start, end in active_periods:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="#00B3BD", opacity=0.2,
            layer="below", line_width=0
        )
    
    fig.update_layout(
        xaxis=dict(
            title=None,
            tickformat='%H:%M'
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False
    )
    
    fig.update_traces(
        line=dict(color="#006166", width=2),
        hovertemplate="<b>Time:</b> %{x|%H:%M}<br><b>Heart Rate:</b> %{y} bpm<extra></extra>"
    )
    
    return fig


def get_hourly_calories_data(user, start_date, end_date):
    conn = sqlite3.connect('../data/fitbit_database.db')
    
    query = f"""
    SELECT Id, ActivityHour, Calories
    FROM hourly_calories
    WHERE Id = '{user}'
    """
    
    data = pd.read_sql_query(query, conn)
    conn.close()
    
    data["ActivityHour"] = pd.to_datetime(data["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce')
    
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered_data = data[(data["ActivityHour"] >= start_date) & (data["ActivityHour"] <= end_date)]
    
    filtered_data["Date"] = filtered_data["ActivityHour"].dt.date
    filtered_data["Hour"] = filtered_data["ActivityHour"].dt.hour
    
    return filtered_data

def get_calories_for_day(user, selected_date):
    conn = sqlite3.connect('../data/fitbit_database.db')
    
    query = f"""
    SELECT Id, ActivityHour, Calories
    FROM hourly_calories
    WHERE Id = '{user}'
    """
    
    data = pd.read_sql_query(query, conn)
    conn.close()
    
    data["ActivityHour"] = pd.to_datetime(data["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce')
    
    if not isinstance(selected_date, pd.Timestamp):
        selected_date = pd.Timestamp(selected_date)
        
    filtered_data = data[data["ActivityHour"].dt.date == selected_date.date()]
    filtered_data = filtered_data.sort_values(by='ActivityHour')
    
    filtered_data["Hour"] = filtered_data["ActivityHour"].dt.hour
    filtered_data["HourFormatted"] = filtered_data["ActivityHour"].dt.strftime('%I %p')
    
    return filtered_data

def plot_hourly_calories(user, start_date, end_date):
    data = get_hourly_calories_data(user, start_date, end_date)
    
    if data.empty:
        return None
        
    hourly_data = data.groupby("Hour")["Calories"].mean().reset_index()
    hourly_data["Calories"] = hourly_data["Calories"].round(1)
    
    hourly_data["HourFormatted"] = hourly_data["Hour"].apply(lambda h: f"{h:02d}:00")
    
    fig = px.line(
        hourly_data, 
        x="Hour", 
        y="Calories",
        title="Average Calories Burned By Hour",
        line_shape="spline",
        markers=True
    )
    
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            ticktext=["12 AM", "6 AM", "12 PM", "6 PM", "11 PM"],
            title=None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False
    )
    
    fig.update_traces(
        line=dict(color="#00B3BD", width=3),
        hovertemplate="<b>Hour:</b> %{x}:00<br><b>Avg Calories:</b> %{y:.1f}<extra></extra>"
    )
    
    return fig

def plot_daily_calories_pie(user, start_date, end_date):
    data = get_hourly_calories_data(user, start_date, end_date)
    
    if data.empty:
        return None
    
    data['TimePeriod'] = pd.cut(
        data['Hour'], 
        bins=[0, 6, 12, 18, 24],
        labels=['Night (12AM-6AM)', 'Morning (6AM-12PM)', 'Afternoon (12PM-6PM)', 'Evening (6PM-12AM)']
    )
    
    period_calories = data.groupby('TimePeriod')['Calories'].sum().reset_index()
    
    custom_colors = {
        'Night (12AM-6AM)': '#CFEBEC',    # Light teal
        'Morning (6AM-12PM)': '#00B3BD',  # Medium teal
        'Afternoon (12PM-6PM)': '#006166', # Dark teal
        'Evening (6PM-12AM)': '#005B8D'   # Blue
    }
    
    fig = px.pie(
        period_calories, 
        values='Calories', 
        names='TimePeriod', 
        title="Calories Burned by Time of Day",
        hole=0.5, 
        color='TimePeriod', 
        color_discrete_map=custom_colors
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h")
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Calories: %{value:.0f}<extra></extra>"
    )
    
    return fig

def plot_daily_calories_chart(user, selected_date):
    data = get_calories_for_day(user, selected_date)
    
    if data.empty:
        return None, None, None, None
        
    display_date = pd.Timestamp(selected_date).strftime('%B %d, %Y')
    
    # Calculate metrics
    total_calories = data["Calories"].sum()
    max_calories = data["Calories"].max()
    max_hour = data.loc[data["Calories"].idxmax(), "Hour"]
    max_hour_formatted = f"{max_hour:02d}:00"
    
    # Create line chart similar to heart rate view
    fig = px.line(
        data,
        x="Hour",
        y="Calories",
        title=f"Calories Burned Throughout {display_date}",
        labels={"Hour": "Hour of Day", "Calories": "Calories Burned"}
    )
    
    # Add reference lines
    avg_calories = data["Calories"].mean()
    fig.add_hline(y=avg_calories, line_dash="dash", line_color="#00B3BD", 
                  annotation_text="Average", annotation_position="top right")
    fig.add_hline(y=max_calories, line_dash="dash", line_color="#005B8D", 
                  annotation_text="Peak", annotation_position="top right")
    
    # Highlight high calorie burn periods
    active_periods = []
    current_start = None
    threshold = avg_calories * 1.2  # 20% above average
    
    for idx, row in data.iterrows():
        if row['Calories'] > threshold and current_start is None:
            current_start = row['Hour']
        elif row['Calories'] <= threshold and current_start is not None:
            active_periods.append((current_start, row['Hour']))
            current_start = None
    
    if current_start is not None:
        active_periods.append((current_start, data['Hour'].iloc[-1] + 1))
    
    for start, end in active_periods:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="#00B3BD", opacity=0.2,
            layer="below", line_width=0
        )
    
    fig.update_layout(
        xaxis=dict(
            title=None,
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            ticktext=["12 AM", "6 AM", "12 PM", "6 PM", "11 PM"]
        ),
        yaxis=dict(title=None),
        showlegend=False
    )
    
    fig.update_traces(
        line=dict(color="#006166", width=2),
        mode="lines+markers",
        hovertemplate="<b>Hour:</b> %{x}:00<br><b>Calories:</b> %{y:.0f}<extra></extra>"
    )
    
    return fig, total_calories, max_calories, max_hour_formatted


def get_hourly_steps_data(user, start_date, end_date):
    conn = sqlite3.connect('../data/fitbit_database.db')
    
    query = f"""
    SELECT Id, ActivityHour, StepTotal
    FROM hourly_steps
    WHERE Id = '{user}'
    """
    
    data = pd.read_sql_query(query, conn)
    conn.close()
    
    data["ActivityHour"] = pd.to_datetime(data["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce')
    
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered_data = data[(data["ActivityHour"] >= start_date) & (data["ActivityHour"] <= end_date)]
    
    filtered_data["Date"] = filtered_data["ActivityHour"].dt.date
    filtered_data["Hour"] = filtered_data["ActivityHour"].dt.hour
    
    return filtered_data

def get_steps_for_day(user, selected_date):
    conn = sqlite3.connect('../data/fitbit_database.db')
    
    query = f"""
    SELECT Id, ActivityHour, StepTotal
    FROM hourly_steps
    WHERE Id = '{user}'
    """
    
    data = pd.read_sql_query(query, conn)
    conn.close()
    
    data["ActivityHour"] = pd.to_datetime(data["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce')
    
    if not isinstance(selected_date, pd.Timestamp):
        selected_date = pd.Timestamp(selected_date)
        
    filtered_data = data[data["ActivityHour"].dt.date == selected_date.date()]
    filtered_data = filtered_data.sort_values(by='ActivityHour')
    
    filtered_data["Hour"] = filtered_data["ActivityHour"].dt.hour
    filtered_data["HourFormatted"] = filtered_data["ActivityHour"].dt.strftime('%I %p')
    
    return filtered_data

def plot_hourly_steps(user, start_date, end_date):
    data = get_hourly_steps_data(user, start_date, end_date)
    
    if data.empty:
        return None
        
    hourly_data = data.groupby("Hour")["StepTotal"].mean().reset_index()
    hourly_data["StepTotal"] = hourly_data["StepTotal"].round(0).astype(int)
    
    hourly_data["HourFormatted"] = hourly_data["Hour"].apply(lambda h: f"{h:02d}:00")
    
    fig = px.line(
        hourly_data, 
        x="Hour", 
        y="StepTotal",
        title="Average Steps By Hour",
        line_shape="spline",
        markers=True
    )
    
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            ticktext=["12 AM", "6 AM", "12 PM", "6 PM", "11 PM"],
            title=None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False
    )
    
    fig.update_traces(
        line=dict(color="#00B3BD", width=3),
        hovertemplate="<b>Hour:</b> %{x}:00<br><b>Avg Steps:</b> %{y:,.0f}<extra></extra>"
    )
    
    return fig

def plot_daily_steps_pie(user, start_date, end_date):
    data = get_hourly_steps_data(user, start_date, end_date)
    
    if data.empty:
        return None
    
    # Define time periods
    data['TimePeriod'] = pd.cut(
        data['Hour'], 
        bins=[0, 6, 12, 18, 24],
        labels=['Night (12AM-6AM)', 'Morning (6AM-12PM)', 'Afternoon (12PM-6PM)', 'Evening (6PM-12AM)']
    )
    
    period_steps = data.groupby('TimePeriod')['StepTotal'].sum().reset_index()
    
    custom_colors = {
        'Night (12AM-6AM)': '#CFEBEC',     # Light teal
        'Morning (6AM-12PM)': '#00B3BD',   # Medium teal
        'Afternoon (12PM-6PM)': '#006166', # Dark teal
        'Evening (6PM-12AM)': '#005B8D'    # Blue
    }
    
    fig = px.pie(
        period_steps, 
        values='StepTotal', 
        names='TimePeriod', 
        title="Steps by Time of Day",
        hole=0.5, 
        color='TimePeriod', 
        color_discrete_map=custom_colors
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h")
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Steps: %{value:,.0f}<extra></extra>"
    )
    
    return fig

def plot_daily_steps_chart(user, selected_date):
    data = get_steps_for_day(user, selected_date)
    
    if data.empty:
        return None, None, None, None
        
    display_date = pd.Timestamp(selected_date).strftime('%B %d, %Y')
    
    # Calculate metrics
    total_steps = data["StepTotal"].sum()
    max_steps = data["StepTotal"].max()
    max_hour = data.loc[data["StepTotal"].idxmax(), "Hour"]
    max_hour_formatted = f"{max_hour:02d}:00"
    
    # Create line chart similar to heart rate view
    fig = px.line(
        data,
        x="Hour",
        y="StepTotal",
        title=f"Steps Throughout {display_date}",
        labels={"Hour": "Hour of Day", "StepTotal": "Steps"}
    )
    
    # Add reference lines
    avg_steps = data["StepTotal"].mean()
    fig.add_hline(y=avg_steps, line_dash="dash", line_color="#00B3BD", 
                  annotation_text="Average", annotation_position="top right")
    fig.add_hline(y=max_steps, line_dash="dash", line_color="#005B8D", 
                  annotation_text="Peak", annotation_position="top right")
    
    # Highlight active periods
    active_periods = []
    current_start = None
    threshold = max(avg_steps * 1.5, 100)  # 50% above average or at least 100 steps
    
    for idx, row in data.iterrows():
        if row['StepTotal'] > threshold and current_start is None:
            current_start = row['Hour']
        elif row['StepTotal'] <= threshold and current_start is not None:
            active_periods.append((current_start, row['Hour']))
            current_start = None
    
    if current_start is not None:
        active_periods.append((current_start, data['Hour'].iloc[-1] + 1))
    
    for start, end in active_periods:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="#00B3BD", opacity=0.2,
            layer="below", line_width=0
        )
    
    fig.update_layout(
        xaxis=dict(
            title=None,
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            ticktext=["12 AM", "6 AM", "12 PM", "6 PM", "11 PM"]
        ),
        yaxis=dict(title=None),
        showlegend=False
    )
    
    fig.update_traces(
        line=dict(color="#006166", width=2),
        mode="lines+markers",
        hovertemplate="<b>Hour:</b> %{x}:00<br><b>Steps:</b> %{y:,.0f}<extra></extra>"
    )
    
    return fig, total_steps, max_steps, max_hour_formatted

def get_hourly_intensity_data(user, start_date, end_date):
    conn = sqlite3.connect('../data/fitbit_database.db')
    
    query = f"""
    SELECT Id, ActivityHour, TotalIntensity, AverageIntensity
    FROM hourly_intensity
    WHERE Id = '{user}'
    """
    
    data = pd.read_sql_query(query, conn)
    conn.close()
    
    data["ActivityHour"] = pd.to_datetime(data["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce')
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered_data = data[(data["ActivityHour"] >= start_date) & (data["ActivityHour"] <= end_date)]
    
    filtered_data["Date"] = filtered_data["ActivityHour"].dt.date
    filtered_data["Hour"] = filtered_data["ActivityHour"].dt.hour
    
    return filtered_data

def get_intensity_for_day(user, selected_date):
    conn = sqlite3.connect('../data/fitbit_database.db')
    
    query = f"""
    SELECT Id, ActivityHour, TotalIntensity, AverageIntensity
    FROM hourly_intensity
    WHERE Id = '{user}'
    """
    
    data = pd.read_sql_query(query, conn)
    conn.close()
    
    data["ActivityHour"] = pd.to_datetime(data["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce')
    
    if not isinstance(selected_date, pd.Timestamp):
        selected_date = pd.Timestamp(selected_date)
        
    filtered_data = data[data["ActivityHour"].dt.date == selected_date.date()]
    
    filtered_data = filtered_data.sort_values(by='ActivityHour')
    
    filtered_data["Hour"] = filtered_data["ActivityHour"].dt.hour
    filtered_data["HourFormatted"] = filtered_data["ActivityHour"].dt.strftime('%I %p')
    
    return filtered_data

def plot_hourly_intensity(user, start_date, end_date):
    data = get_hourly_intensity_data(user, start_date, end_date)
    
    if data.empty:
        return None
        
    hourly_data = data.groupby("Hour")["AverageIntensity"].mean().reset_index()
    hourly_data["AverageIntensity"] = hourly_data["AverageIntensity"].round(3)
    
    hourly_data["HourFormatted"] = hourly_data["Hour"].apply(lambda h: f"{h:02d}:00")
    
    fig = px.line(
        hourly_data, 
        x="Hour", 
        y="AverageIntensity",
        title="Average Activity Intensity By Hour",
        line_shape="spline",
        markers=True
    )
    
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            ticktext=["12 AM", "6 AM", "12 PM", "6 PM", "11 PM"],
            title=None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False
    )
    
    fig.update_traces(
        line=dict(color="#00B3BD", width=3),
        hovertemplate="<b>Hour:</b> %{x}:00<br><b>Avg Intensity:</b> %{y:.3f}<extra></extra>"
    )
    
    return fig

def plot_daily_intensity_pie(user, start_date, end_date):
    data = get_hourly_intensity_data(user, start_date, end_date)
    
    if data.empty:
        return None
    
    # Define intensity levels
    def classify_intensity(value):
        if value < 0.2:
            return "Low (0-0.2)"
        elif value < 0.5:
            return "Medium (0.2-0.5)"
        else:
            return "High (0.5+)"
    
    data['IntensityLevel'] = data['AverageIntensity'].apply(classify_intensity)
    
    intensity_distribution = data['IntensityLevel'].value_counts().reset_index()
    intensity_distribution.columns = ['IntensityLevel', 'Count']
    
    custom_colors = {
        "Low (0-0.2)": "#CFEBEC",     # Light teal
        "Medium (0.2-0.5)": "#00B3BD", # Medium teal
        "High (0.5+)": "#005B8D"       # Blue
    }
    
    fig = px.pie(
        intensity_distribution, 
        values='Count', 
        names='IntensityLevel', 
        title="Activity Intensity Distribution",
        hole=0.5, 
        color='IntensityLevel', 
        color_discrete_map=custom_colors
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h")
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Hours: %{value:.0f}<extra></extra>"
    )
    
    return fig


def plot_daily_intensity_chart(user, selected_date):
    data = get_intensity_for_day(user, selected_date)
    
    if data.empty:
        return None, None, None, None
        
    display_date = pd.Timestamp(selected_date).strftime('%B %d, %Y')
    
    # Calculate metrics
    avg_intensity = data["AverageIntensity"].mean()
    max_intensity = data["AverageIntensity"].max()
    max_hour = data.loc[data["AverageIntensity"].idxmax(), "Hour"]
    max_hour_formatted = f"{max_hour:02d}:00"
    
    # Create line chart similar to heart rate view
    fig = px.line(
        data,
        x="Hour",
        y="AverageIntensity",
        title=f"Activity Intensity Throughout {display_date}",
        labels={"Hour": "Hour of Day", "AverageIntensity": "Intensity"}
    )
    
    # Add reference lines
    fig.add_hline(y=avg_intensity, line_dash="dash", line_color="#00B3BD", 
                  annotation_text="Average", annotation_position="top right")
    fig.add_hline(y=max_intensity, line_dash="dash", line_color="#005B8D", 
                  annotation_text="Peak", annotation_position="top right")
    
    # Highlight active periods
    active_periods = []
    current_start = None
    threshold = max(avg_intensity * 1.5, 0.3)  # 50% above average or at least 0.3
    
    for idx, row in data.iterrows():
        if row['AverageIntensity'] > threshold and current_start is None:
            current_start = row['Hour']
        elif row['AverageIntensity'] <= threshold and current_start is not None:
            active_periods.append((current_start, row['Hour']))
            current_start = None
    
    if current_start is not None:
        active_periods.append((current_start, data['Hour'].iloc[-1] + 1))
    
    for start, end in active_periods:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="#00B3BD", opacity=0.2,
            layer="below", line_width=0
        )
    
    fig.update_layout(
        xaxis=dict(
            title=None,
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            ticktext=["12 AM", "6 AM", "12 PM", "6 PM", "11 PM"]
        ),
        yaxis=dict(title=None),
        showlegend=False
    )
    
    fig.update_traces(
        line=dict(color="#006166", width=2),
        mode="lines+markers",
        hovertemplate="<b>Hour:</b> %{x}:00<br><b>Intensity:</b> %{y:.3f}<extra></extra>"
    )
    
    return fig, avg_intensity, max_intensity, max_hour_formatted

def get_sleep_stage_data(user, start_date, end_date):
    conn = sqlite3.connect("../data/fitbit_database.db")
    try:
        query = f"SELECT date, value FROM minute_sleep WHERE Id = {user} ORDER BY date;"
        sleep_stage_data = pd.read_sql(query, conn)
        
        if not sleep_stage_data.empty:
            sleep_stage_data["date"] = pd.to_datetime(sleep_stage_data["date"])
            sleep_stage_data = sleep_stage_data[
                (sleep_stage_data["date"] >= pd.Timestamp(start_date)) &
                (sleep_stage_data["date"] < pd.Timestamp(end_date) + pd.Timedelta(days=1))
            ]
            stage_map = {1: "Asleep", 2: "Restless", 3: "Awake"}
            sleep_stage_data["Stage"] = sleep_stage_data["value"].map(stage_map)
            sleep_stage_data["start"] = sleep_stage_data["date"]
            sleep_stage_data["end"] = sleep_stage_data["start"] + pd.Timedelta(minutes=1)
            
        return sleep_stage_data
    except Exception as e:
        raise e
    finally:
        conn.close()

def plot_sleep_duration_trend(filtered_data, avg_sleep_duration):
    fig = px.line(
        filtered_data,
        x="ActivityDate",
        y="TotalSleepHours",
        title="Sleep Duration Trend",
        labels={"TotalSleepHours": "Hours Slept", "ActivityDate": "Date"},
        color_discrete_sequence=["#00B3BD"],
        template="plotly_white"
    )
    
    fig.update_traces(
        mode="lines+markers",
        line=dict(width=2.5),
        marker=dict(
            size=8,
            color="#006166",
            line=dict(width=1, color="DarkSlateGrey")
        )
    )
    
    if not np.isnan(avg_sleep_duration):
        fig.add_hline(
            y=avg_sleep_duration,
            line_dash="dot",
            line_color="#FF6B6B",
            annotation_text=f"Average: {avg_sleep_duration:.1f}h",
            annotation_font_size=12,
            annotation_bgcolor="rgba(255,255,255,0.7)"
        )
    
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="",
        yaxis_title="Hours Slept",
        margin=dict(t=40),
        height=400
    )
    
    fig.update_traces(
        hovertemplate="<b>%{x|%b %d}</b><br>%{y:.1f} hours<extra></extra>"
    )
    
    if filtered_data["TotalSleepHours"].isna().any():
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.85,
            text="Missing data points indicate days with no sleep records",
            showarrow=False,
            font=dict(color="#666666", size=10)
        )
    
    return fig

def plot_sleep_stage_distribution(sleep_stage_data):
    stage_counts = sleep_stage_data["Stage"].value_counts().reset_index()
    
    fig = px.pie(
        stage_counts,
        values="count",
        names="Stage",
        title="Sleep Stage Distribution",
        hole=0.5,
        color="Stage",
        color_discrete_map={
            "Asleep": "#CFEBEC",
            "Restless": "#0083BD",
            "Awake": "#006166"
        }
    )
    
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value} minutes (%{percent})",
        marker=dict(line=dict(color='#FFFFFF', width=0.5))
    )

    fig.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode="hide",
        showlegend=True,
        legend=dict(
            title=dict(text="Sleep Stages", font=dict(size=12)),
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=40, b=80),
        height=400
    )
    
    return fig

def plot_sleep_timeline(daily_stages, selected_date):
    fig = px.timeline(
        daily_stages,
        x_start="start",
        x_end="end",
        y="Stage",
        color="Stage",
        color_discrete_map={
            "Asleep": "#CFEBEC",
            "Restless": "#0083BD",
            "Awake": "#006166"
        },
        title=f"Sleep Stages Timeline - {selected_date}"
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="",
        yaxis=dict(
            categoryorder="array",
            categoryarray=["Awake", "Restless", "Asleep"]
        ),
        height=300,
        margin=dict(t=40),
        legend=dict(orientation="h", y=1.1)
    )
    
    return fig
