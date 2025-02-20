# IMPORTS
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
import sqlite3

data = pd.read_csv("../data/daily_activity.csv", header=0)

# converting the data to the type datetime
data["ActivityDate"] = pd.to_datetime(data["ActivityDate"], format='%m/%d/%Y')

# SQL
con = sqlite3.connect("../data/fitbit_database.db")
cur = con.cursor()

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

# Part2 verifying data in database
def verifying_TotalSteps_with_hourly_steps():
    query = f"SELECT LEFT(ActivityHour,CHARINDEX(' ',ActivityHour) -1) FROM hourly_steps WHERE StepTotal = 1111"
    cur.execute(query)
    
    rows = cur.fetchall()
    if rows:
        print(rows)
        



# Run the function
verifying_TotalSteps_with_hourly_steps()

def verify_steps_match():

    query = """
    SELECT h.Id, 
        SUBSTR(h.ActivityHour, 1, INSTR(h.ActivityHour, ' ') - 1) AS ActivityDate, 
        SUM(h.StepTotal) AS TotalHourlySteps, 
        d.TotalSteps AS TotalDailySteps, 
        SUM(h.StepTotal) = d.TotalSteps AS is_equal
    FROM hourly_steps h
    JOIN daily_activity d 
        ON h.Id = d.Id 
        AND SUBSTR(h.ActivityHour, 1, INSTR(h.ActivityHour, ' ') - 1) = d.ActivityDate
    GROUP BY h.Id, ActivityDate, d.TotalSteps;

    """

    cur.execute(query)
    results = cur.fetchall()
 #   print("Query Results:", results)
    con.close()

    # Print results
    for user_id, date, hourly_steps, daily_steps, is_equal in results:
        status = "✅ Match" if is_equal else "❌ No Match"
        print(f"User {user_id} on {date}: Hourly Steps = {hourly_steps}, Daily Steps = {daily_steps} → {status}")

# Run the function
# verify_steps_match()