# IMPORTS
import sqlite3
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

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