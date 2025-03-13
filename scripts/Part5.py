# IMPORTS
import sqlite3
import pandas as pd
import random
from scipy.stats import bernoulli
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st


def retrieve_average(category, dates):

    dates = pd.to_datetime(dates, format='%m/%d/%Y') # if dates is already a list of datetime values from Streamlit, this step might not be needed. ???????
    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()

    # filtering dates using sql might be more efficient ????????
    query = "SELECT Id, ActivityDate, TotalSteps, Calories, TotalDistance, VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes, SedentaryMinutes FROM daily_activity" 

    cur.execute(query) 
    rows = cur.fetchall()
    daily_activity = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description]) 

    daily_activity["ActivityDate"] = pd.to_datetime(daily_activity["ActivityDate"])
    daily_activity = daily_activity.loc[(daily_activity["ActivityDate"].isin(dates))]

    con.close()
    # If no data is found, return 0
    if daily_activity.empty:
        return 0  
        
    if category == "total_users":
        return daily_activity["Id"].nunique()
    elif category == "TotalSteps":
        return int(daily_activity["TotalSteps"].mean())
    elif category == "Calories":
        return int(daily_activity["Calories"].mean())
    elif category == "TotalDistance":
        return round(daily_activity["TotalDistance"].mean(), 2)
    elif category == "ActiveMinutes":
        daily_activity["TotalActiveMinutes"] = (daily_activity["VeryActiveMinutes"] + 
                                                daily_activity["FairlyActiveMinutes"] + 
                                                daily_activity["LightlyActiveMinutes"])
        return  int(daily_activity["TotalActiveMinutes"].mean())
    elif category == "SedentaryMinutes":
        return int(daily_activity["SedentaryMinutes"].mean())
    

def activity_sum_data(dates):

    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()
    query = "SELECT ActivityDate, VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes, SedentaryMinutes FROM daily_activity"
    cur.execute(query) 
    rows = cur.fetchall()
    data = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description]) 

    data["ActivityDate"] = pd.to_datetime(data["ActivityDate"])
    filtered_data = data.loc[data["ActivityDate"].isin(dates)]
    

    minutes = {
        "Very Active": filtered_data["VeryActiveMinutes"].mean(),
        "Fairly Active": filtered_data["FairlyActiveMinutes"].mean(),
        "Lightly Active": filtered_data["LightlyActiveMinutes"].mean(),
        "Sedentary": filtered_data["SedentaryMinutes"].mean()
    }

    df = pd.DataFrame(list(minutes.items()), columns=['Activity', 'Minutes'])
    return df

def average_steps_per_hour(dates):
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()
    query ="SELECT ActivityHour, StepTotal FROM hourly_steps"
    cur.execute(query) 
    rows = cur.fetchall()
    data = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description]) 
    data["ActivityHour"] = pd.to_datetime(data["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    filtered_data = data[data["ActivityHour"].dt.date.isin(dates.date)]

    # Extract the hour part from ActivityHour, group and calculate average
    filtered_data["Hour"] = filtered_data["ActivityHour"].dt.hour
    hourly_avg = filtered_data.groupby("Hour")["StepTotal"].mean().reset_index()
    con.close()
    
    return hourly_avg

def average_heart_rate_per_hour():
    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()
    
    # Fetch heart rate data
    query = "SELECT Time, Value FROM heart_rate"
    cur.execute(query) 
    rows = cur.fetchall()
    
    # Convert to DataFrame
    data = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    data["Time"] = pd.to_datetime(data["Time"], format="%m/%d/%Y %I:%M:%S %p")
    data["Day"] = data["Time"].dt.date
    data["Hour"] = data["Time"].dt.hour  # Rounds down to the nearest hour
    
    # Group by the hour and calculate the average heart rate
    data_avg = data.groupby(["Day", "Hour"], as_index=False)["Value"].mean().reset_index()
    
    con.close()
    
    return data_avg

heart_rates = average_heart_rate_per_hour()

def hourly_average_heart_rate_dates(dates):
    dates = pd.to_datetime(dates, format='%m/%d/%Y')

    filtered_data = heart_rates[heart_rates["Day"].isin(dates.date)]

    data_avg = filtered_data.groupby(["Hour"], as_index=False)["Value"].mean().reset_index()    

    return data_avg

print(average_steps_per_hour(["4/4/2016", "4/5/2016", "4/6/2016"]))

# weather data
def hourly_weather_data():
    weather = pd.read_csv("../data/weather_Chicago_hourly.csv", header=0)

    weather["datetime"] = pd.to_datetime(weather["datetime"])
    weather["Hour"] = weather["datetime"].dt.hour
    weather["Day"] = weather["datetime"].dt.weekday

    return weather

# hourly steps
def compute_steps_hourly():
    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()

    steps = cur.execute(f"SELECT * FROM hourly_steps")
    rows = steps.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])
    con.close()

    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    df.rename(columns={"ActivityHour": "datetime"}, inplace=True)
    df["Hour"] = df["datetime"].dt.hour
    df["Day"] = df["datetime"].dt.weekday

    df = df.groupby(["datetime", "Hour", "Day"], as_index=False)["StepTotal"].mean()  

    return df

# hourly intensity
def compute_intensity_hourly():
    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()

    steps = cur.execute(f"SELECT * FROM hourly_intensity")
    rows = steps.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])
    con.close()

    df["ActivityHour"] = pd.to_datetime(df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    df.rename(columns={"ActivityHour": "datetime"}, inplace=True)
    df["Hour"] = df["datetime"].dt.hour
    df["Day"] = df["datetime"].dt.weekday

    df = df.groupby(["datetime", "Hour", "Day"], as_index=False)["TotalIntensity"].mean()  

    return df

def create_scatterplot_weather(df1, df2, hours, days, dates):
    dates = pd.to_datetime(dates)

    hour_ranges = {
        "0-4": range(0, 4),
        "4-8": range(4, 8),
        "8-12": range(8, 12),
        "12-16": range(12, 16),
        "16-20": range(16, 20),
        "20-24": range(20, 24)
    }

    hours_converted = [hour for range_str in hours if range_str in hour_ranges for hour in hour_ranges[range_str]]

    days_ranges = {
        "Weekdays": range(0, 5),
        "Weekend": range(5, 7)
    }
    
    days_converted = [day for day_str in days if day_str in days_ranges for day in days_ranges[day_str]]

    df_merged = pd.merge(df1, df2, on=["datetime", "Hour", "Day"], how="inner")
    df_merged["datetime"] = pd.to_datetime(df_merged["datetime"]).dt.normalize()
    
    df_merged = df_merged[df_merged["Hour"].isin(hours_converted)]
    df_merged = df_merged[df_merged["Day"].isin(days_converted)]
    df_merged = df_merged[df_merged["datetime"].isin(dates)]

    if "StepTotal" not in df_merged.columns:
        var = "TotalIntensity"
    else:
        var = "StepTotal"

    plt.figure(figsize=(8,6))
    sns.scatterplot(x=df_merged["temp"], y=df_merged[var], alpha=0.5)
    plt.title(f"Scatterplot temp vs {var}")
    plt.show()

    return df_merged

hourly_weather = hourly_weather_data()
hourly_steps = compute_steps_hourly()
hourly_intensity = compute_intensity_hourly()