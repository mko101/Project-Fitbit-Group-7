# IMPORTS
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats

db_path = "../data/fitbit_database.db"  
con = sqlite3.connect(db_path)
cur = con.cursor()

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
