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