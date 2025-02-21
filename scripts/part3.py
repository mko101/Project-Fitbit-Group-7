#step 4 Analyse the relationship between sedentary activity and sleep duration
# IMPORTS
import sqlite3
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.stats import shapiro

# Connect to SQLite database
db_path = "../data/fitbit_database.db"  # Update if needed
con = sqlite3.connect(db_path)
cur = con.cursor()

# Function to fetch data
def fetch_data():
    query = "SELECT Id, date, logId, value FROM minute_sleep"
    cur.execute(query)
    rows = cur.fetchall()
    df_sleep = pd.DataFrame(rows, columns=[x[0] for x in cur.description])
    
    query = "SELECT Id, ActivityDate, SedentaryMinutes FROM daily_activity"
    cur.execute(query)
    rows = cur.fetchall()
    df_activity = pd.DataFrame(rows, columns=[x[0] for x in cur.description])
    
    return df_sleep, df_activity

df_sleep, df_activity = fetch_data()

# Convert date columns to datetime
df_sleep["date"] = pd.to_datetime(df_sleep["date"]).dt.date
df_activity["ActivityDate"] = pd.to_datetime(df_activity["ActivityDate"]).dt.date

# Aggregate sleep data (sum total sleep per day per individual)
df_sleep_agg = df_sleep.groupby(["Id", "date"]).agg(TotalMinutesAsleep=("value", "sum")).reset_index()

# Merge activity and sleep data
df_merged = pd.merge(df_activity, df_sleep_agg, left_on=["Id", "ActivityDate"], right_on=["Id", "date"], how="inner")

# Drop missing values
df_merged.dropna(inplace=True)

# Convert to numeric values
df_merged["SedentaryMinutes"] = pd.to_numeric(df_merged["SedentaryMinutes"], errors='coerce')
df_merged["TotalMinutesAsleep"] = pd.to_numeric(df_merged["TotalMinutesAsleep"], errors='coerce')

# Remove top 1% outliers
df_merged = df_merged[(df_merged["SedentaryMinutes"] < df_merged["SedentaryMinutes"].quantile(0.99)) & 
                      (df_merged["TotalMinutesAsleep"] < df_merged["TotalMinutesAsleep"].quantile(0.99))]

### 1️⃣ LINEAR REGRESSION (OLS) ###
X = df_merged["SedentaryMinutes"]
y = df_merged["TotalMinutesAsleep"]
X = sm.add_constant(X)  # Add intercept
model = sm.OLS(y, X).fit()

# Get residuals
residuals = model.resid

### 2️⃣ CHECKING NORMALITY OF RESIDUALS ###

# Correlation heatmap
plt.figure(figsize=(6,5))
correlation_matrix = df_merged[['SedentaryMinutes', 'TotalMinutesAsleep']].corr()
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
plt.title("Correlation Between Sedentary Minutes and Sleep Duration")
plt.show()

# Scatterplot with regression line
plt.figure(figsize=(8,6))
sns.scatterplot(x=df_merged["SedentaryMinutes"], y=df_merged["TotalMinutesAsleep"], alpha=0.5)
plt.plot(df_merged["SedentaryMinutes"], model.predict(X), color="red", linewidth=2)
plt.xlabel("Sedentary Minutes")
plt.ylabel("Total Sleep Minutes")
plt.title("Linear Regression: Sedentary Minutes vs. Sleep Duration")
plt.show()

# Histogram of residuals
plt.figure(figsize=(8,5))
sns.histplot(residuals, bins=30, kde=True, color="blue")
plt.title("Histogram of Residuals")
plt.xlabel("Residuals")
plt.ylabel("Frequency")
plt.show()

# QQ-Plot of residuals
sm.qqplot(residuals, line="45")
plt.title("QQ-Plot of Residuals")
plt.show()

# Shapiro-Wilk test for normality
stat, p_value = shapiro(residuals)
print(f"Shapiro-Wilk Test: p-value = {p_value:.4f}")

# Print OLS model summary
print(model.summary())


#step5 Compute 4-hours block Average of Steps,Sleep,Calories
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

db_path = "../data/fitbit_database.db"  
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT Id, ActivityHour, StepTotal FROM hourly_steps")
rows = cursor.fetchall()
df_steps = pd.DataFrame(rows, columns=["Id", "ActivityHour", "StepTotal"])

cursor.execute("SELECT Id, ActivityHour, Calories FROM hourly_calories")
rows = cursor.fetchall()
df_calories = pd.DataFrame(rows, columns=["Id", "ActivityHour", "Calories"])

cursor.execute("SELECT Id, date, value AS MinutesAsleep FROM minute_sleep")
rows = cursor.fetchall()
df_sleep = pd.DataFrame(rows, columns=["Id", "date", "MinutesAsleep"])

datetime_format = "%m/%d/%Y %I:%M:%S %p"  

df_steps["ActivityHour"] = pd.to_datetime(df_steps["ActivityHour"], format=datetime_format)
df_calories["ActivityHour"] = pd.to_datetime(df_calories["ActivityHour"], format=datetime_format)
df_sleep["date"] = pd.to_datetime(df_sleep["date"], format="%m/%d/%Y %I:%M:%S %p")  

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

df_steps["TimeBlock"] = df_steps["ActivityHour"].dt.hour.apply(categorize_time)
df_calories["TimeBlock"] = df_calories["ActivityHour"].dt.hour.apply(categorize_time)
df_sleep["TimeBlock"] = df_sleep["date"].dt.hour.apply(categorize_time)

steps_avg = df_steps.groupby("TimeBlock")["StepTotal"].mean().reindex(["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"])

calories_avg = df_calories.groupby("TimeBlock")["Calories"].mean().reindex(["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"])

df_sleep_block = df_sleep.groupby("TimeBlock")["MinutesAsleep"].sum()
df_sleep_block /= df_sleep["Id"].nunique()  
df_sleep_block = df_sleep_block.reindex(["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"])

# Steps
plt.figure(figsize=(10, 5))
steps_avg.plot(kind="bar", color="skyblue", edgecolor="black")
plt.xlabel("Time Block (Hours)")
plt.ylabel("Average Steps")
plt.title("Average Steps per 4-Hour Block")
plt.xticks(rotation=0)
plt.show()

# Calories
plt.figure(figsize=(10, 5))
calories_avg.plot(kind="bar", color="salmon", edgecolor="black")
plt.xlabel("Time Block (Hours)")
plt.ylabel("Average Calories Burnt")
plt.title("Average Calories Burnt per 4-Hour Block")
plt.xticks(rotation=0)
plt.show()

# Sleep
plt.figure(figsize=(10, 5))
df_sleep_block.plot(kind="bar", color="purple", edgecolor="black")
plt.xlabel("Time Block (Hours)")
plt.ylabel("Average Minutes of Sleep")
plt.title("Corrected Sleep per 4-Hour Block")
plt.xticks(rotation=0)
plt.show()
