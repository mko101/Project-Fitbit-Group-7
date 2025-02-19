# IMPORTS
import sqlite3
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# connect to database
con = sqlite3.connect("../data/fitbit_database.db")
cur = con.cursor()

# Step 3: compute the sleep duration for each moment of sleep of an individual
def compute_sleep_duration(user_id):
    sleep_duration = cur.execute(f"SELECT Id, date, logId FROM minute_sleep WHERE Id={user_id}")
    rows = sleep_duration.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])
    df["date"] = pd.to_datetime(df["date"])

    sleep_durations = df.groupby('logId').agg(start_time=('date', 'min'), end_time=('date', 'max')).reset_index()
    sleep_durations['MinutesSlept'] = (sleep_durations['end_time'] - sleep_durations['start_time']).dt.total_seconds() / 60
    sleep_durations['Date'] = sleep_durations['start_time'].dt.date
    sleep_durations = sleep_durations.groupby('Date')['MinutesSlept'].sum().reset_index()
    
    return sleep_durations

# Step 4: analyse the relationship between the duration of sleep and the active minutes for an individual
def compare_activity_and_sleep(user_id):
    active_minutes = cur.execute(f"SELECT Id, ActivityDate, VeryActiveMinutes, FairlyActiveMinutes, LightlyActiveMinutes FROM daily_activity WHERE Id={user_id}")
    rows = active_minutes.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])
    df["ActivityDate"] = pd.to_datetime(df["ActivityDate"]).dt.date

    df['ActiveMinutes'] = (df['VeryActiveMinutes'] + df['FairlyActiveMinutes'] + df['LightlyActiveMinutes'])
    daily_activity = df.groupby('ActivityDate')['ActiveMinutes'].sum().reset_index()

    daily_activity.rename(columns={"ActivityDate": "Date"}, inplace=True)

    daily_sleep = compute_sleep_duration(1503960366)
    data_sleep_and_activity = pd.merge(daily_activity, daily_sleep, on="Date", how="inner")

    X = data_sleep_and_activity['ActiveMinutes'] # decision variable
    y = data_sleep_and_activity['MinutesSlept'] # dependent variable

    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    print(model.summary())

    plt.figure(figsize=(10, 6))
    plt.scatter(data_sleep_and_activity["ActiveMinutes"], data_sleep_and_activity["MinutesSlept"], color="skyblue", label="Data points")
    plt.plot(data_sleep_and_activity["ActiveMinutes"], model.predict(X), color="red", label="Regression line")
    plt.xlabel("Active Minutes")
    plt.ylabel("Minutes Slept")
    plt.title(f"Linear Relationship between Active Minutes and Minutes Slept for User {user_id}")
    plt.legend()
    plt.show()

compare_activity_and_sleep(1503960366)