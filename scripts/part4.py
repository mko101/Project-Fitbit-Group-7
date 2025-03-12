# IMPORTS
import sqlite3
import pandas as pd
import random
from scipy.stats import bernoulli
import matplotlib.pyplot as plt
import seaborn as sns

# connect to database
con = sqlite3.connect("../data/fitbit_database.db")
cur = con.cursor()

# Step 1: look for missing values in the weight_log and resolve them
# gender_users = {}
# age_users = {}

# def sample_random_age(user):
#     # https://www.coolest-gadgets.com/fitbit-statistics/
#     # 18-24: 0.1579, 25-34: 0.2593, 35-44: 0.1940, 45-54: 0.1608, 55-64: 0.1294, 65+: 0.0987
#     age_groupes = {0.1579: list(range(18, 25)), 0.2593: list(range(25, 35)), 0.1940: list(range(35, 45)), 0.1608: list(range(45, 55)), 0.1294: list(range(55, 65)), 0.0987: list(range(65, 79))}

#     if user not in age_users:
#         sum = 0
#         random_number = random.random()

#         for probabilty, ages in age_groupes.items():
#             sum += probabilty

#             if random_number <= sum:
#                 age_users[user] = random.choice(ages)
#                 break

#     return age_users[user]

# def sample_random_gender(user):
#     # https://www.coolest-gadgets.com/fitbit-statistics/
#     # F: 44.66% and M: 55.34%
#     if user not in gender_users:
#         gender_users[user] = "F" if bernoulli.rvs(0.4466) else "M"
    
#     return gender_users[user]


def resolve_missing_values_weight_log():
    # the following query was run once, to remove the Fat column from the weight_log table (as there were only 2 values and no "good" way to fill them in)
    # cur.execute("ALTER TABLE weight_log DROP COLUMN Fat")

    weights = cur.execute("SELECT * FROM weight_log")
    rows = weights.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])

    corrected_df = df.copy()

    if corrected_df["WeightKg"].isnull().sum() > 0:
        # 1 kg = 2.20462262 pounds
        corrected_df["WeightKg"] = corrected_df.apply(lambda row: (row["WeightPounds"] / 2.20462262) if pd.isnull(row["WeightKg"]) else row["WeightKg"], axis=1)

    # if df["Fat"].isnull().sum() > 0:
    #     df["Fat"] = df.apply(lambda row: ((row["BMI"] * 1.2) + (0.23 * sample_random_age(row["Id"])) - (5.4 if sample_random_gender(row["Id"]) == "F" else 16.2)) if pd.isnull(row["Fat"]) else row["Fat"], axis=1)
    
    # corrects the values in the database itself
    for index, row in df.iterrows():
        if pd.isnull(row["WeightKg"]):
            print(row["WeightKg"])
            update_query = "UPDATE weight_log SET WeightKg = ? WHERE Id = ? AND Date = ?"

            cur.execute(update_query, (corrected_df.at[index, "WeightKg"], row["Id"], row["Date"]))
    
    con.commit()

    return corrected_df

print(resolve_missing_values_weight_log())

# Step 2: check correlation between weight and calories
def check_correlation_weight_calories():
    query = "SELECT Id, ActivityDate, Calories FROM daily_activity"

    cur.execute(query)
    rows = cur.fetchall()
    daily_activity = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    weight_log = resolve_missing_values_weight_log().loc[:,["Id", "Date", "WeightKg"]]
    
    weight_log["Date"] = pd.to_datetime(weight_log["Date"], format="%m/%d/%Y %I:%M:%S %p")
    weight_log["Date"] = weight_log["Date"].dt.date
    daily_activity["ActivityDate"] = pd.to_datetime(daily_activity["ActivityDate"]).dt.date
    merged_df = pd.merge(daily_activity, weight_log, left_on=["Id", "ActivityDate"], right_on=["Id", "Date"], how="left")
    merged_df = merged_df.drop(columns=["Date"])

    # Forward fill the weight after it is first available
    merged_df["WeightKg"] = merged_df.groupby("Id")["WeightKg"].ffill()

    merged_df = merged_df.dropna(subset=["WeightKg"])
    merged_df["Id"] = merged_df["Id"].astype(int)

    #plot scatterplot and calculate correlation
    # plot_scatterplot_calculate_correlation(merged_df)
    # print(f"Number of unique users: {daily_activity['Id'].nunique()}")
    # print(f"Number of unique users: {weight_log['Id'].nunique()}")
    # print(f"Number of unique users: {merged_df['Id'].nunique()}")


def plot_scatterplot_calculate_correlation(merged_df):
    #scatterplot
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x="Calories", y="WeightKg", data=merged_df)

    plt.title("Relationship between Calories and Weight")
    plt.xlabel("Calories")
    plt.ylabel("Weight (kg)")
    plt.show()

    correlation = merged_df["Calories"].corr(merged_df["WeightKg"])
    print(f"Correlation between Calories and WeightKg: {correlation}")

# check_correlation_weight_calories()