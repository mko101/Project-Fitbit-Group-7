# IMPORTS
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import statsmodels.api as sm
import requests
import json
from scipy import stats

# connect to database
con = sqlite3.connect("../data/fitbit_database.db")
cur = con.cursor()

# read the CSV file
data = pd.read_csv("../data/daily_activity.csv", header=0)

# converting the data to the type datetime
data["ActivityDate"] = pd.to_datetime(data["ActivityDate"], format='%m/%d/%Y')

# Part1 creating new dataframe of unique users and the class they belong to
def create_new_dataframe():

    user_counts = data['Id'].value_counts()
    new_data = pd.DataFrame({'Id': user_counts.index})

    # Assign user types based on counts
    def categorize_user(user_id):
        count = user_counts[user_id]
        if count <= 10:
            return "LightUser"
        elif 11 <= count <= 15:
            return "ModerateUser"
        else:
            return "HeavyUser"

    new_data["Class"] = new_data["Id"].map(categorize_user)

    print(new_data)
    return new_data

# create_new_dataframe()

# Part2: Verifying data
def get_verified_data(data_type):
    if data_type == "steps":
        query = "SELECT Id, ActivityDate, TotalSteps FROM daily_activity"
        query_2 = "SELECT Id, ActivityHour, StepTotal FROM hourly_steps"
        value_column = "StepTotal"
        total_column = "TotalSteps"
        label = "Steps"
    elif data_type == "calories":
        query = "SELECT Id, ActivityDate, Calories FROM daily_activity"
        query_2 = "SELECT Id, ActivityHour, Calories FROM hourly_calories"
        value_column = "Calories"
        total_column = "Calories"
        label = "Calories"
    else:
        raise ValueError("Invalid data_type. Please choose either 'steps' or 'calories'.")

    # Fetch data from database
    cur.execute(query)
    rows = cur.fetchall()
    daily_activity = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description]) 

    cur.execute(query_2)
    rows_2 = cur.fetchall()
    hourly_data = pd.DataFrame(rows_2, columns=[desc[0] for desc in cur.description]) 

    # Convert date format
    hourly_data["ActivityHour"] = pd.to_datetime(hourly_data["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    hourly_data["ActivityDate"] = hourly_data["ActivityHour"].dt.date

    # Aggregate hourly data
    sum_daily_hourly_data = hourly_data.groupby(["Id", "ActivityDate"])[value_column].sum().reset_index()
    daily_activity["ActivityDate"] = pd.to_datetime(daily_activity["ActivityDate"]).dt.date

    # Merge
    merged_df = daily_activity.merge(sum_daily_hourly_data, on=["Id", "ActivityDate"], how="left")

    # Rename columns after merge (for calories)
    if data_type == "calories":
        merged_df.rename(columns={"Calories_x": "TotalCalories", "Calories_y": "HourlyCalories"}, inplace=True)
        total_column = "TotalCalories"
        value_column = "HourlyCalories"

    # Match check
    merged_df["DataMatch"] = merged_df[total_column] == merged_df[value_column]
    merged_df["Id"] = merged_df["Id"].astype(int)

    return merged_df, label, total_column, value_column


# Part 2: Compute Statistics
def calculate_statistics(merged_df, label, total_column, value_column):
    false_count = (~merged_df["DataMatch"]).sum()
    true_count = merged_df["DataMatch"].sum()
    total_count = merged_df["DataMatch"].count()
    match_percentage = round(true_count / total_count * 100, 2) if total_count > 0 else 0
    match_ratio = round(true_count / false_count, 2) if false_count != 0 else "All matched"

    # Calculate absolute and raw differences
    merged_df["Difference"] = merged_df[total_column] - merged_df[value_column]
    abs_diff_avg = round(merged_df["Difference"].abs().mean(), 2)  # Absolute difference average

    # Calculate averages for total and hourly datasets
    total_avg = round(merged_df[total_column].mean(), 2)
    hourly_avg = round(merged_df[value_column].mean(), 2)
    
    # Relative difference percentage
    relative_diff_percentage = round((abs_diff_avg / total_avg) * 100, 2) if total_avg != 0 else 0

    # Print statistics
    print(f"Count of unmatched {label}: {false_count}")
    print(f"Count of matched {label}: {true_count}")
    print(f"Total count: {total_count}")
    print(f"Percentage of matching {label}: {match_percentage} %")
    print(f"Ratio of matched to unmatched {label}: {match_ratio}")
    print(f"Absolute difference average: {abs_diff_avg}")
    print(f"Average {label} per day (Total Dataset): {total_avg}")
    print(f"Average {label} per day (Hourly Sum): {hourly_avg}")
    print(f"Relative Difference Percentage: {relative_diff_percentage} %")


# Part 3: Graphing
def plot_graphs(merged_df, label):
    false_count = (~merged_df["DataMatch"]).sum()
    true_count = merged_df["DataMatch"].sum()

    # Pie chart: Matched vs Unmatched
    plt.pie([true_count, false_count], labels=["Matched", "Unmatched"], autopct='%1.1f%%', colors=["green", "red"])
    plt.title(f"Percentage of Matched vs Unmatched {label}")
    plt.show()

    # Matching Percentage Per User
    user_match_percentage = merged_df.groupby("Id")["DataMatch"].mean() * 100
    plt.figure(figsize=(16, 8))
    plt.bar(user_match_percentage.index.astype(str), user_match_percentage.values, color='purple')
    plt.xlabel('User ID')
    plt.ylabel(f'Match Percentage (%)')
    plt.title(f'Matching Percentage Per User ({label})')
    plt.xticks(rotation=90)
    plt.ylim(0, 105)
    plt.subplots_adjust(bottom=0.25)
    plt.show()

    # Matching Percentage Per Day
    day_match_percentage = merged_df.groupby("ActivityDate")["DataMatch"].mean() * 100
    plt.figure(figsize=(14, 8))
    plt.plot(day_match_percentage.index, day_match_percentage.values, marker='o', color='violet')
    plt.xlabel('Date')
    plt.ylabel(f'Match Percentage (%)')
    plt.title(f'Daily Matching Percentage Over Time ({label})')
    plt.xticks(pd.date_range(start=day_match_percentage.index.min(), end=day_match_percentage.index.max(), freq='D'), rotation=90)
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.25)
    plt.ylim(-5, 105)
    plt.show()


# Run everything
def run_analysis(data_type):
    valid_options = ["steps", "calories"]

    if data_type not in valid_options:
        print(f"Error: Invalid data type '{data_type}'. Please choose from {valid_options}.")
        return 

    merged_df, label, total_column, value_column = get_verified_data(data_type)
    calculate_statistics(merged_df, label, total_column, value_column)
    plot_graphs(merged_df, label)

# Run for both steps and calories
run_analysis("steps")
run_analysis("calories")

# Step 3: compute the sleep duration for each moment of sleep of an individual
def compute_sleep_duration(user_id):
    # gets data from the database and adds it to a dataframe
    sleep_duration = cur.execute(f"SELECT Id, date, logId FROM minute_sleep WHERE Id={user_id}")
    rows = sleep_duration.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])

    # converts the date column to the type datetime
    df["date"] = pd.to_datetime(df["date"])

    # calculates the time asleep for each logId 
    sleep_durations = df.groupby('logId').agg(start_time=('date', 'min'), end_time=('date', 'max')).reset_index()
    sleep_durations['MinutesSlept'] = (sleep_durations['end_time'] - sleep_durations['start_time']).dt.total_seconds() / 60
    
    # takes the date to be the day the user woke up
    sleep_durations['Date'] = sleep_durations['end_time'].dt.date

    # drops the unnecessary columns from the dataframe
    sleep_durations = sleep_durations.drop(["logId", "start_time", "end_time"], axis=1)
    
    return sleep_durations

print(compute_sleep_duration(1503960366))

# Step 4: analyse the relationship between the duration of sleep and the active minutes for an individual
def compare_activity_and_sleep(user_id):
    # gets data from the database and adds it to a dataframe
    active_minutes = cur.execute(f"SELECT Id, ActivityDate, VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes FROM daily_activity WHERE Id={user_id}")
    rows = active_minutes.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])

    # converts the date column to the type datetime
    df["ActivityDate"] = pd.to_datetime(df["ActivityDate"]).dt.date

    # calculates the time the user is active by summing the active minutes for that day
    df['ActiveMinutes'] = (df['VeryActiveMinutes'] + df['FairlyActiveMinutes'] + df['LightlyActiveMinutes'])
    daily_activity = df.groupby('ActivityDate')['ActiveMinutes'].sum().reset_index()

    # renames the ActivityDate column to Date
    daily_activity.rename(columns={"ActivityDate": "Date"}, inplace=True)

    # sums the duration of sleep based on date
    daily_sleep = compute_sleep_duration(1503960366)
    daily_sleep = daily_sleep.groupby('Date')['MinutesSlept'].sum().reset_index()

    # merges the total active minutes and the duration of sleep based on the date, leaving out any dates where no active minutes or sleep duration is available
    data_sleep_and_activity = pd.merge(daily_activity, daily_sleep, on="Date", how="inner")

    # linear regression model
    X = data_sleep_and_activity["MinutesSlept"] # independent variable
    y = data_sleep_and_activity["ActiveMinutes"] # dependent variable

    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    print(model.summary())

    plt.figure(figsize=(10, 6))
    plt.scatter(data_sleep_and_activity["MinutesSlept"], data_sleep_and_activity["ActiveMinutes"], color="skyblue", label="Data points")
    plt.plot(data_sleep_and_activity["MinutesSlept"], model.predict(X), color="red", label="Regression line")
    plt.xlabel("Minutes Slept")
    plt.ylabel("Active Minutes")
    plt.title(f"Linear Relationship between Active Minutes and Minutes Slept for User {user_id}")
    plt.legend()
    plt.show()

compare_activity_and_sleep(1503960366)

# Step 5: analyse the relationship between sedentary activity and sleep duration
def compare_sedentary_activity_and_sleep():
    cur.execute("SELECT Id, date, logId, value FROM minute_sleep")
    rows = cur.fetchall()
    df_sleep = pd.DataFrame(rows, columns=[x[0] for x in cur.description])

    df_sleep["date"] = pd.to_datetime(df_sleep["date"]).dt.date
    df_sleep_agg = df_sleep.groupby(["Id", "date"]).agg(TotalMinutesAsleep=("value", "sum")).reset_index()

    cur.execute("SELECT Id, ActivityDate, SedentaryMinutes FROM daily_activity")
    rows = cur.fetchall()
    df_activity = pd.DataFrame(rows, columns=[x[0] for x in cur.description])

    df_activity["ActivityDate"] = pd.to_datetime(df_activity["ActivityDate"]).dt.date
    df_activity.rename(columns={"ActivityDate": "date"}, inplace=True)

    df_merged = pd.merge(df_activity, df_sleep_agg, on=["Id", "date"], how="inner")

    X = df_merged["SedentaryMinutes"] # explanatory variable
    y = df_merged["TotalMinutesAsleep"] # response variable

    X = sm.add_constant(X)  
    model = sm.OLS(y, X).fit()

    print(model.summary())

    residuals = model.resid

    plt.figure(figsize=(6,5))
    correlation_matrix = df_merged[['SedentaryMinutes', 'TotalMinutesAsleep']].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
    plt.title("Correlation Between Sedentary Minutes and Sleep Duration")
    plt.show()

    plt.figure(figsize=(8,6))
    sns.scatterplot(x=df_merged["SedentaryMinutes"], y=df_merged["TotalMinutesAsleep"], alpha=0.5)
    plt.plot(df_merged["SedentaryMinutes"], model.predict(X), color="red", linewidth=2)
    plt.xlabel("Sedentary Minutes")
    plt.ylabel("Total Sleep Minutes")
    plt.title("Linear Regression: Sedentary Minutes vs. Sleep Duration")
    plt.show()

    plt.figure(figsize=(8,5))
    sns.histplot(residuals, bins=30, kde=True, color="blue")
    plt.title("Histogram of Residuals")
    plt.xlabel("Residuals")
    plt.ylabel("Frequency")
    plt.show()

    p_value = stats.shapiro(residuals.tolist()).pvalue
    print(f"Shapiro-Wilk Test: p-value = {p_value:.4f}")

compare_sedentary_activity_and_sleep()

# Step 6: compute 4-hours block Average Steps, Sleep, Calories
def categorize_time(hour):
    if 0 <= hour < 4:
        return "0-4"
    elif 4 <= hour < 8:
        return "4-8"
    elif 8 <= hour < 12:
        return "8-12"
    elif 12 <= hour < 16:
        return "12-16"
    elif 16 <= hour < 20:
        return "16-20"
    else:
        return "20-24"

def compute_block_averages():
    cur.execute("SELECT Id, ActivityHour, StepTotal FROM hourly_steps")
    rows = cur.fetchall()
    df_steps = pd.DataFrame(rows, columns=[x[0] for x in cur.description])

    cur.execute("SELECT Id, ActivityHour, Calories FROM hourly_calories")
    rows = cur.fetchall()
    df_calories = pd.DataFrame(rows, columns=[x[0] for x in cur.description])

    cur.execute("SELECT Id, date, value AS MinutesAsleep FROM minute_sleep")
    rows = cur.fetchall()
    df_sleep = pd.DataFrame(rows, columns=[x[0] for x in cur.description])

    df_steps["ActivityHour"] = pd.to_datetime(df_steps["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    df_calories["ActivityHour"] = pd.to_datetime(df_calories["ActivityHour"], format="%m/%d/%Y %I:%M:%S %p")
    df_sleep["date"] = pd.to_datetime(df_sleep["date"], format="%m/%d/%Y %I:%M:%S %p")  

    df_steps["TimeBlock"] = df_steps["ActivityHour"].dt.hour.apply(categorize_time)
    df_calories["TimeBlock"] = df_calories["ActivityHour"].dt.hour.apply(categorize_time)
    df_sleep["TimeBlock"] = df_sleep["date"].dt.hour.apply(categorize_time)

    steps_avg = df_steps.groupby("TimeBlock")["StepTotal"].mean().reindex(["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"])

    calories_avg = df_calories.groupby("TimeBlock")["Calories"].mean().reindex(["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"])

    df_sleep["date"] = pd.to_datetime(df_sleep["date"]).dt.normalize()
    df_sleep_block = df_sleep.groupby(["Id", "date", "TimeBlock"])["MinutesAsleep"].count()
    df_sleep_block = df_sleep_block.groupby("TimeBlock").mean().reindex(["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"])

    for label, values in {"Average Steps": steps_avg, "Average Calories Burnt": calories_avg, "Average Minutes of Sleep": df_sleep_block}.items():
        print(values)
        plt.figure(figsize=(10, 5))
        values.plot(kind="bar", color="skyblue", edgecolor="black")
        plt.xlabel("Time Block (Hours)")
        plt.ylabel(f"{label}")
        plt.title(f"{label} per 4-Hour Block")
        plt.xticks(rotation=0)
        plt.show()

compute_block_averages()

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