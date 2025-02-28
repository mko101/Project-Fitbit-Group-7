# IMPORTS
import sqlite3
import pandas as pd
import random
from scipy.stats import bernoulli

# connect to database
con = sqlite3.connect("../data/fitbit_database.db")
cur = con.cursor()

# Step 1: look for missing values in the weight_log and resolve them
gender_users = {}
age_users = {}

def sample_random_age(user):
    # https://www.coolest-gadgets.com/fitbit-statistics/
    # 18-24: 0.1579, 25-34: 0.2593, 35-44: 0.1940, 45-54: 0.1608, 55-64: 0.1294, 65+: 0.0987
    age_groupes = {0.1579: list(range(18, 25)), 0.2593: list(range(25, 35)), 0.1940: list(range(35, 45)), 0.1608: list(range(45, 55)), 0.1294: list(range(55, 65)), 0.0987: list(range(65, 79))}

    if user not in age_users:
        sum = 0
        random_number = random.random()

        for probabilty, ages in age_groupes.items():
            sum += probabilty

            if random_number <= sum:
                age_users[user] = random.choice(ages)
                break

    return age_users[user]

def sample_random_gender(user):
    # https://www.coolest-gadgets.com/fitbit-statistics/
    # F: 44.66% and M: 55.34%
    if user not in gender_users:
        gender_users[user] = "F" if bernoulli.rvs(0.4466) else "M"
    
    return gender_users[user]


def resolve_missing_values_weight_log():
    weights = cur.execute("SELECT * FROM weight_log")
    rows = weights.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cur.description])

    if df["WeightKg"].isnull().sum() > 0:
        # 1 kg = 2.20462262 pounds
        df["WeightKg"] = df.apply(lambda row: (row["WeightPounds"] / 2.20462262) if pd.isnull(row["WeightKg"]) else row["WeightKg"], axis=1)

    if df["Fat"].isnull().sum() > 0:
        df["Fat"] = df.apply(lambda row: ((row["BMI"] * 1.2) + (0.23 * sample_random_age(row["Id"])) - (5.4 if sample_random_gender(row["Id"]) == "F" else 16.2)) if pd.isnull(row["Fat"]) else row["Fat"], axis=1)
    
    return df

print(resolve_missing_values_weight_log())