# IMPORTS
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import statsmodels.api as sm
import requests
import json

# SQL
con = sqlite3.connect("../data/fitbit_database.db")
cur = con.cursor()

# Part 7: Compare heart rate and hourly intensity for given user_id
# Plot heart rate and hourly intensity for given user_id
# Indicate when given user_id is missing in either heart_rate or hourly_intensity
def plot_heart_rate_intensity(user_id):
    # Find all unique heart_rate_ids with query
    cur.execute("SELECT DISTINCT Id FROM heart_rate")
    heart_rate_ids = set(int(row[0]) for row in cur.fetchall())
    
    # Find all unique intensity_ids with query
    cur.execute("SELECT DISTINCT Id FROM hourly_intensity")
    intensity_ids = set(int(row[0]) for row in cur.fetchall())
    
    # Case 1: user_id missing in both tables
    if user_id not in heart_rate_ids and user_id not in intensity_ids:
        print(f"❌ User {user_id}: Not Found")
        return
    
    # Case 2: user_id missing in either one of the tables
    if user_id in heart_rate_ids and user_id not in intensity_ids:
        print(f"❗️ User {user_id}: Hourly Intensity Missing")
        return
    if user_id not in heart_rate_ids and user_id in intensity_ids:
        print(f"❗️ User {user_id}: Heart Rate Missing")
        return
    
    # Fetch heart rate data
    cur.execute(f"SELECT Time, Value FROM heart_rate WHERE Id = ?", (user_id,))
    heart_rate_rows = cur.fetchall()
    heart_rate_df = pd.DataFrame(heart_rate_rows, columns=["Time", "Value"])
    heart_rate_df["Time"] = pd.to_datetime(heart_rate_df["Time"], format="%m/%d/%Y %I:%M:%S %p")
    
    # Fetch intensity data
    cur.execute(f"SELECT ActivityHour, TotalIntensity FROM hourly_intensity WHERE Id = ?", (user_id,))
    intensity_rows = cur.fetchall()
    intensity_df = pd.DataFrame(intensity_rows, columns=["ActivityHour", "TotalIntensity"])
    intensity_df["ActivityHour"] = pd.to_datetime(intensity_df["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")

    # Find the overlapping time range
    min_time = max(heart_rate_df["Time"].min(), intensity_df["ActivityHour"].min())
    max_time = min(heart_rate_df["Time"].max(), intensity_df["ActivityHour"].max())

    # Filter data to include only the overlapping time range
    heart_rate_filtered = heart_rate_df[(heart_rate_df["Time"] >= min_time) & (heart_rate_df["Time"] <= max_time)]
    intensity_filtered = intensity_df[(intensity_df["ActivityHour"] >= min_time) & (intensity_df["ActivityHour"] <= max_time)]

    fig, ax1 = plt.subplots(figsize=(20, 5))

    # Plot Heart Rate (Red)
    ax1.plot(heart_rate_filtered["Time"], heart_rate_filtered["Value"], color='red', label="Heart Rate")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Heart Rate (bpm)", color='red')
    ax1.tick_params(axis='y', labelcolor='red')

    # Create a second y-axis for exercise intensity (blue)
    ax2 = ax1.twinx()
    ax2.plot(intensity_filtered["ActivityHour"], intensity_filtered["TotalIntensity"], color='blue', label="Exercise Intensity")
    ax2.set_ylabel("Total Exercise Intensity", color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    # Title and legend
    plt.title(f"Heart Rate and Hourly Exercise Intensity for User {user_id}")
    fig.tight_layout()
    plt.show()


plot_heart_rate_intensity(7007744171)
plot_heart_rate_intensity(1503960366)
plot_heart_rate_intensity(9999999999)


# Part 8: Fetch weather information with API and visualize relation between weather factors and activity of individuals
def visualize_weather_activity():
    # Fetch unique dates from daily_activity
    cur.execute("SELECT DISTINCT ActivityDate FROM daily_activity")
    unique_dates = [row[0] for row in cur.fetchall()]
    unique_dates = pd.to_datetime(unique_dates, format='%m/%d/%Y')
    
    # start_date = unique_dates.min().strftime('%Y-%m-%d')
    # end_date = unique_dates.max().strftime('%Y-%m-%d')
    # print(start_date, end_date)
    
    # Fetch weather data for these dates (units: celcius, kilometer) using API
    # limited daily record
    # url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Chicago/2016-03-12/2016-04-12?unitGroup=metric&key=4V73XKTGAFN3SAXS9U4MRBHUM&contentType=json"
    # # url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Chicago/{start_date}/{end_date}?unitGroup=metric&key=4V73XKTGAFN3SAXS9U4MRBHUM&contentType=json"
    # print(f"{url}")
    # req = requests.get(url)
    # print(f"Response Status Code: {req.status_code}")
    # print(f"Response Content: {req.text}")
    # weather_data = req.json()
    # daily_weather = weather_data["days"]
    # df_weather = pd.DataFrame(daily_weather, columns=["datetime", "temp", "feelslike", "precip", "humidity", "windspeed", "visibility"])
    # df_weather["datetime"] = pd.to_datetime(df_weather["datetime"])
    # df_filtered_weather = df_weather[df_weather["datetime"].isin(unique_dates)]
    
    weather_file = "../data/weather_Chicago.csv"
    df_weather = pd.read_csv(weather_file)
    df_weather["datetime"] = pd.to_datetime(df_weather["datetime"])
    df_filtered_weather = df_weather[df_weather["datetime"].isin(unique_dates)]
    
    cur.execute("""
        SELECT ActivityDate, 
            AVG(TotalSteps) AS TotalSteps,
            AVG(VeryActiveMinutes) AS VeryActiveMinutes, 
            AVG(FairlyActiveMinutes) AS FairlyActiveMinutes, 
            AVG(LightlyActiveMinutes) AS LightlyActiveMinutes, 
            AVG(SedentaryMinutes) AS SedentaryMinutes,
            AVG(Calories) AS Calories
        FROM daily_activity
        GROUP BY ActivityDate;
    """)
    df_activity = pd.DataFrame(cur.fetchall(), columns=["ActivityDate", "TotalSteps", "VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes", "SedentaryMinutes", "Calories"])
    df_activity["ActivityDate"] = pd.to_datetime(df_activity["ActivityDate"])
    df_merged = df_activity.merge(df_filtered_weather, left_on="ActivityDate", right_on="datetime")
    
    # Display effect of weather condition on activity
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    
    # Pie chart: Proportion of weather conditions
    weather_counts = df_merged["icon"].value_counts()
    axes[0, 0].pie(weather_counts, labels=weather_counts.index, autopct='%1.1f%%', startangle=140)
    axes[0, 0].set_title("Proportion of Weather Conditions")

    # BOX PLOT: Activity distribution per weather condition
    sns.boxplot(data=df_merged, x="icon", y="TotalSteps", ax=axes[0, 1])
    axes[0, 1].set_title("Distribution of Total Steps Across Weather Conditions")
    axes[0, 1].set_xlabel("Weather Condition")
    axes[0, 1].set_ylabel("Total Steps")
    axes[0, 1].set_xticks(range(len(df_merged["icon"].unique())))
    axes[0, 1].set_xticklabels(df_merged["icon"].unique(), rotation=45)
    axes[0, 1].grid(True)

    sns.boxplot(data=df_merged, x="icon", y="Calories", ax=axes[1, 0])
    axes[1, 0].set_title("Distribution of Calories Across Weather Conditions")
    axes[1, 0].set_xlabel("Weather Condition")
    axes[1, 0].set_ylabel("Calories")
    axes[1, 0].set_xticks(range(len(df_merged["icon"].unique())))
    axes[1, 0].set_xticklabels(df_merged["icon"].unique(), rotation=45)
    axes[1, 0].grid(True)

    sns.boxplot(data=df_merged, x="icon", y="SedentaryMinutes", ax=axes[1, 1])
    axes[1, 1].set_title("Distribution of Sedentary Minutes Across Weather Conditions")
    axes[1, 1].set_xlabel("Weather Condition")
    axes[1, 1].set_ylabel("Sedentary Minutes")
    axes[1, 1].set_xticks(range(len(df_merged["icon"].unique())))
    axes[1, 1].set_xticklabels(df_merged["icon"].unique(), rotation=45)
    axes[1, 1].grid(True)

    plt.tight_layout()
    plt.show()
    
    # Display relation between weather factors and activity and apply linear regression model
    scatter_plots = [
        ("temp", "VeryActiveMinutes", "red", "Temperature (°C)", "Very Active Minutes"),
        ("temp", "SedentaryMinutes", "green", "Temperature (°C)", "Sedentary Minutes"),
        ("temp", "Calories", "orange", "Temperature (°C)", "Calories Burnt"),
        ("precip", "VeryActiveMinutes", "blue", "Precipitation (mm)", "Very Active Minutes"),
        ("precip", "SedentaryMinutes", "purple", "Precipitation (mm)", "Sedentary Minutes"),
        ("precip", "Calories", "brown", "Precipitation (mm)", "Calories Burnt"),
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 9))

    for idx, (x_col, y_col, color, x_label, y_label) in enumerate(scatter_plots):
        ax = axes[idx // 3, idx % 3]
        
        ax.scatter(df_merged[x_col], df_merged[y_col], color=color, alpha=0.6, label = "Data points")

        # Fit OLS regression model
        X = sm.add_constant(df_merged[x_col])
        y = df_merged[y_col]
        model = sm.OLS(y, X).fit()
        
        # Print regression summary
        print(f"<Regression Summary for {y_col} vs {x_col}>\n")
        print(model.summary())
        print("\n------------------------------------------------------------------------------\n")
        
        x_range = np.linspace(df_merged[x_col].min(), df_merged[x_col].max(), 100)
        y_pred = model.predict(sm.add_constant(x_range))

        ax.plot(x_range, y_pred, color="darkgrey", label="Regression line")
        
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(f"{x_label} vs. {y_label}")
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    plt.show()
    
visualize_weather_activity()


