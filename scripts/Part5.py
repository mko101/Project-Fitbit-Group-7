# IMPORTS
import sqlite3
import pandas as pd
import random
from scipy.stats import bernoulli
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st


connect = "../data/cleaned_fitbit.db"

def retrieve_average(category, dates):

    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    con = sqlite3.connect(connect)
    cur = con.cursor()
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
    con = sqlite3.connect(connect)
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
    con = sqlite3.connect(connect)
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
    con = sqlite3.connect(connect)
    cur = con.cursor()

    query = "SELECT Time, Value FROM heart_rate"
    cur.execute(query) 
    rows = cur.fetchall()

    data = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    data["Time"] = pd.to_datetime(data["Time"], format="%m/%d/%Y %I:%M:%S %p")
    data["Day"] = data["Time"].dt.date
    data["Hour"] = data["Time"].dt.hour 

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
    con = sqlite3.connect(connect)
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

def heart_rate_and_intensitivity(dates):
    # Connect to the database
    conn = sqlite3.connect(connect)
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
    
    merged_df = pd.merge(avg_heart_rate, avg_intensity, on="Hour")
    
    conn.close()
    return merged_df


def calories_and_active_minutes(dates):
    conn = sqlite3.connect(connect)
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

## NOT SURE IF USEFUL
def heart_rate_and_sleep_value(dates):
    conn = sqlite3.connect(connect)
    cur = conn.cursor()
    dates = pd.to_datetime(dates, format='%m/%d/%Y')

    cur.execute("SELECT Time, Value, Id FROM heart_rate")
    heart_rate_rows = cur.fetchall()
    heart_rate_df = pd.DataFrame(heart_rate_rows, columns=["Time", "HeartRate", "Id"])
    heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"], format="%m/%d/%Y %I:%M:%S %p")

    filtered_heart_rate_data = heart_rate_df[heart_rate_df["Time"].dt.date.isin(dates.date)]
    filtered_heart_rate_data["Minute"] = filtered_heart_rate_data["Time"].dt.floor("min")
    avg_heart_rate = filtered_heart_rate_data.groupby(["Minute", "Id"])["HeartRate"].mean().reset_index()

    cur.execute("SELECT date, value, Id FROM minute_sleep")
    sleep_rows = cur.fetchall()
    sleep_df = pd.DataFrame(sleep_rows, columns=["Minute", "SleepValue", "Id"])
    sleep_df["Minute"] = pd.to_datetime(sleep_df["Minute"], format="%m/%d/%Y %I:%M:%S %p")

    sleep_df = sleep_df[sleep_df["Minute"].dt.date.isin(dates.date)]
    merged_df = pd.merge(avg_heart_rate, sleep_df, on=["Id", "Minute"])

    conn.close()
    return merged_df

def average_distance_per_week(dates):
    conn = sqlite3.connect(connect)
    cur = conn.cursor()
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    query = "SELECT ActivityDate, TotalDistance FROM daily_activity"
    cur.execute(query) 
    data = cur.fetchall()
    data = pd.DataFrame(data, columns=[desc[0] for desc in cur.description]) 
    data["ActivityDate"] = pd.to_datetime(data["ActivityDate"]).dt.normalize()
    filtered_data = data.loc[data["ActivityDate"].isin(dates)]
    filtered_data["DayOfWeek"] = filtered_data["ActivityDate"].dt.weekday
    filtered_data_avr = filtered_data.groupby("DayOfWeek")["TotalDistance"].mean().reset_index()
    conn.close()
    return filtered_data_avr

def average_steps_per_week(dates):
    conn = sqlite3.connect(connect)
    cur = conn.cursor()
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    query = "SELECT ActivityDate, TotalSteps FROM daily_activity"
    cur.execute(query) 
    data = cur.fetchall()
    data = pd.DataFrame(data, columns=[desc[0] for desc in cur.description]) 
    data["ActivityDate"] = pd.to_datetime(data["ActivityDate"]).dt.normalize()
    filtered_data = data.loc[data["ActivityDate"].isin(dates)]
    filtered_data["DayOfWeek"] = filtered_data["ActivityDate"].dt.weekday
    filtered_data_avr = filtered_data.groupby("DayOfWeek")["TotalSteps"].mean().reset_index()

    conn.close()
    return filtered_data_avr

def average_calories_per_week(dates):
    conn = sqlite3.connect(connect)
    cur = conn.cursor()
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    query = "SELECT ActivityDate, Calories FROM daily_activity"
    cur.execute(query) 
    data = cur.fetchall()
    data = pd.DataFrame(data, columns=[desc[0] for desc in cur.description]) 
    data["ActivityDate"] = pd.to_datetime(data["ActivityDate"]).dt.normalize()
    filtered_data = data.loc[data["ActivityDate"].isin(dates)]
    filtered_data["DayOfWeek"] = filtered_data["ActivityDate"].dt.weekday
    filtered_data_avr = filtered_data.groupby("DayOfWeek")["Calories"].mean().reset_index()
    conn.close()
    return filtered_data_avr

def average_active_minutes_per_week(dates):
    conn = sqlite3.connect(connect)
    cur = conn.cursor()
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    query = "SELECT ActivityDate, Calories, VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes FROM daily_activity"
    cur.execute(query) 
    data = cur.fetchall()
    data = pd.DataFrame(data, columns=[desc[0] for desc in cur.description]) 
    data["ActivityDate"] = pd.to_datetime(data["ActivityDate"]).dt.normalize()

    filtered_data = data.loc[data["ActivityDate"].isin(dates)]
    filtered_data["DayOfWeek"] = filtered_data["ActivityDate"].dt.weekday
    filtered_data_avr = filtered_data.groupby("DayOfWeek")[["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes"]].mean().reset_index()
    conn.close()
    return filtered_data_avr

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

def daily_activity(dates):
    dates = pd.to_datetime(dates, format='%m/%d/%Y')

    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()

    steps = cur.execute(f"SELECT * FROM daily_activity")
    rows = steps.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])
    con.close()

    df["ActivityDate"] = pd.to_datetime(df["ActivityDate"])
    df = df[df["ActivityDate"].isin(dates)]

    very_active_distance = df.groupby(["ActivityDate"], as_index=False)["VeryActiveDistance"].mean()
    very_active_minutes = df.groupby(["ActivityDate"], as_index=False)["VeryActiveMinutes"].mean()

    df = pd.merge(very_active_distance, very_active_minutes, on="ActivityDate", how="inner")

    df["Month"] = df["ActivityDate"].dt.month_name()
    df = df.sort_values(by="ActivityDate")

    return df

def categorize_weight(weight):
    if weight >= 110:
        return "110 - 130kg"
    elif weight >= 90:
        return "90 - 110kg"
    elif weight >= 70:
        return "70 - 90kg"
    else:
        return "50 - 70kg"
    
def categorized_weight_data(dates):
    dates = pd.to_datetime(dates, format='%m/%d/%Y')
    
    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()

    cur.execute("SELECT Id, Date, WeightKg FROM weight_log") 
    rows = cur.fetchall()
    data = pd.DataFrame(rows, columns = [x[0] for x in cur.description])

    data["Date"] = pd.to_datetime(data["Date"]).dt.normalize()
    filtered_data = data.loc[data["Date"].isin(dates)]

    filtered_data = filtered_data.groupby(["Id"], as_index=False)["WeightKg"].mean()
    filtered_data["CategoryWeight"] = filtered_data["WeightKg"].apply(categorize_weight)
    
    weights = {
        "50 - 70kg": filtered_data[filtered_data["CategoryWeight"] == "50 - 70kg"].count()["CategoryWeight"],
        "70 - 90kg": filtered_data[filtered_data["CategoryWeight"] == "70 - 90kg"].count()["CategoryWeight"],
        "90 - 110kg": filtered_data[filtered_data["CategoryWeight"] == "90 - 110kg"].count()["CategoryWeight"],
        "110 - 130kg": filtered_data[filtered_data["CategoryWeight"] == "110 - 130kg"].count()["CategoryWeight"]
    }

    df = pd.DataFrame(list(weights.items()), columns=["CategoryWeight", "Count"])

    return df

def sleep_data(dates):
    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM minute_sleep")
    rows = cur.fetchall()
    df_sleep = pd.DataFrame(rows, columns=[x[0] for x in cur.description])

    con.close()

    df_sleep["date"] = pd.to_datetime(df_sleep["date"])
    df_sleep["Hour"] = df_sleep["date"].dt.hour

    df_sleep["date"] = pd.to_datetime(df_sleep["date"]).dt.normalize()
    df_sleep = df_sleep[df_sleep["date"].isin(dates)]

    df_sleep["Hour"] = df_sleep["Hour"].astype('category')
    df_sleep = df_sleep.groupby(["Id", "date", "Hour"], as_index=False)["value"].count().fillna(0).astype(int).reset_index()
    df_sleep["date"] = pd.to_datetime(df_sleep["date"]).dt.normalize()
    df_sleep["DayTotal"] = df_sleep.groupby(["Id", "date"])["value"].transform("sum")
    df_sleep = df_sleep[df_sleep["DayTotal"] > 0]
    df_sleep = df_sleep.reset_index(drop=True)
    df_sleep.rename(columns={"value": "TotalMinutesAsleep"}, inplace=True)

    df_sleep = df_sleep.groupby(["Hour"], as_index=False)["TotalMinutesAsleep"].mean()

    return df_sleep

def create_dataframe_scatterplot_sleep(variable, dates):
    dates = pd.to_datetime(dates, format='%m/%d/%Y')

    con = sqlite3.connect("../data/fitbit_database.db")
    cur = con.cursor()

    sleep_duration = cur.execute(f"SELECT * FROM minute_sleep")
    rows = sleep_duration.fetchall()
    sleep_df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])

    # converts the date column to the type datetime
    sleep_df["date"] = pd.to_datetime(sleep_df["date"]).dt.normalize()
    sleep_df = sleep_df.groupby(["Id", "date"], as_index=False)["value"].count()
    sleep_df.rename(columns={"value": "TotalMinutesAsleep"}, inplace=True)

    if variable == "Steps":
        steps = cur.execute(f"SELECT * FROM hourly_steps")
        rows = steps.fetchall()
        other_df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])

        other_df["date"] = pd.to_datetime(other_df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p").dt.normalize()
        other_df = other_df.groupby(["Id", "date"], as_index=False)["StepTotal"].sum()
    else: 
        calories = cur.execute(f"SELECT * FROM hourly_calories")
        rows = calories.fetchall()
        other_df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])

        other_df["date"] = pd.to_datetime(other_df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p").dt.normalize()
        other_df = other_df.groupby(["Id", "date"], as_index=False)["Calories"].sum()
        
    con.close()

    sleep_df["date"] = pd.to_datetime(sleep_df["date"])
    other_df["date"] = pd.to_datetime(other_df["date"])

    df_merged = pd.merge(sleep_df, other_df, on=["Id", "date"], how="inner")
    filtered_data = df_merged.loc[df_merged["date"].isin(dates)]

    return filtered_data
