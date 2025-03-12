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

def hourly_average_calories(dates):
    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()
    query = "SELECT ActivityHour, Calories FROM hourly_calories"
    cur.execute(query) 
    rows = cur.fetchall()
    data = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description]) 
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    data["ActivityHour"] = pd.to_datetime(data["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    filtered_data = data[data["ActivityHour"].dt.date.isin(dates.date)]

    # Extract the hour part from ActivityHour, group and calculate average
    filtered_data["Hour"] = filtered_data["ActivityHour"].dt.hour
    hourly_avg = filtered_data.groupby("Hour")["Calories"].mean().reset_index()
    con.close()

    return hourly_avg

def heart_rate_and_intensitibity(dates):
    # Connect to the database
    conn = sqlite3.connect("../data/fitbit_database.db")
    cur = conn.cursor()
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    # Fetch heart rate data and compute hourly average
    cur.execute("SELECT Time, Value FROM heart_rate")
    heart_rate_rows = cur.fetchall()
    heart_rate_df = pd.DataFrame(heart_rate_rows, columns=["Time", "HeartRate"])
    heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"], format="%m/%d/%Y %I:%M:%S %p")
    filtered_heart_rate_data = heart_rate_df[heart_rate_df["Time"].dt.date.isin(dates.date)]
    filtered_heart_rate_data["Hour"] = filtered_heart_rate_data["Time"].dt.hour
    avg_heart_rate = filtered_heart_rate_data.groupby("Hour")["HeartRate"].mean().reset_index()
    
    # Fetch intensity data and compute hourly average
    cur.execute("SELECT ActivityHour, TotalIntensity FROM hourly_intensity")
    intensity_rows = cur.fetchall()
    intensity_df = pd.DataFrame(intensity_rows, columns=["ActivityHour", "TotalIntensity"])
    intensity_df["ActivityHour"] = pd.to_datetime(intensity_df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    filtered_intensitivity_data = intensity_df[intensity_df["ActivityHour"].dt.date.isin(dates.date)]
    filtered_intensitivity_data["Hour"] = filtered_intensitivity_data["ActivityHour"].dt.hour
    avg_intensity = filtered_intensitivity_data.groupby("Hour")["TotalIntensity"].mean().reset_index()
    
    # Merge on hourly timestamps
    merged_df = pd.merge(avg_heart_rate, avg_intensity, on="Hour")
    
    conn.close()
    return merged_df

def heart_rate_and_intensitibity(dates):
    # Connect to the database
    conn = sqlite3.connect("../data/fitbit_database.db")
    cur = conn.cursor()
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    # Fetch heart rate data and compute hourly average
    cur.execute("SELECT Time, Value FROM heart_rate")
    heart_rate_rows = cur.fetchall()
    heart_rate_df = pd.DataFrame(heart_rate_rows, columns=["Time", "HeartRate"])
    heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"], format="%m/%d/%Y %I:%M:%S %p")
    filtered_heart_rate_data = heart_rate_df[heart_rate_df["Time"].dt.date.isin(dates.date)]
    filtered_heart_rate_data["Hour"] = filtered_heart_rate_data["Time"].dt.hour
    avg_heart_rate = filtered_heart_rate_data.groupby("Hour")["HeartRate"].mean().reset_index()
    
    # Fetch intensity data and compute hourly average
    cur.execute("SELECT ActivityHour, TotalIntensity FROM hourly_intensity")
    intensity_rows = cur.fetchall()
    intensity_df = pd.DataFrame(intensity_rows, columns=["ActivityHour", "TotalIntensity"])
    intensity_df["ActivityHour"] = pd.to_datetime(intensity_df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    filtered_intensitivity_data = intensity_df[intensity_df["ActivityHour"].dt.date.isin(dates.date)]
    filtered_intensitivity_data["Hour"] = filtered_intensitivity_data["ActivityHour"].dt.hour
    avg_intensity = filtered_intensitivity_data.groupby("Hour")["TotalIntensity"].mean().reset_index()
    
    # Merge on hourly timestamps
    merged_df = pd.merge(avg_heart_rate, avg_intensity, on="Hour")
    
    conn.close()
    return merged_df

def calories_and_active_minutes(dates):
    conn = sqlite3.connect("../data/fitbit_database.db")
    cur = conn.cursor()
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    query = "SELECT ActivityDate, VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes, Calories FROM daily_activity"
    cur.execute(query) 
    data = cur.fetchall()
    data = pd.DataFrame(data, columns=[desc[0] for desc in cur.description]) 
    data["ActivityDate"] = pd.to_datetime(data["ActivityDate"])
    filtered_data = data.loc[data["ActivityDate"].isin(dates)]
    filtered_data["TotalActiveMinutes"] = (
        filtered_data["VeryActiveMinutes"] + 
        filtered_data["FairlyActiveMinutes"] + 
        filtered_data["LightlyActiveMinutes"]
    )
    scatter_data = filtered_data[["TotalActiveMinutes", "Calories"]]

    conn.close()
    
    return scatter_data




# Maybe add correlation between calories and active minutes
# add graphs not per hour but per day


