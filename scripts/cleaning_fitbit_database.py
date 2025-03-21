# IMPORTS
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import statsmodels.api as sm


def data_cleaning():
    # Paths to the databases
    original_db_path = "data/fitbit_database.db"
    cleaned_db_path = "data/cleaned_fitbit.db"

    # Connect to the original database
    con = sqlite3.connect(original_db_path)

    # Load and clean dailyActivity table
    df_daily = pd.read_sql_query("SELECT * FROM daily_activity", con)

    # Remove duplicates
    df_daily_cleaned = df_daily.drop_duplicates()

    # Filter out rows where all three key columns are zero
    df_daily_cleaned = df_daily_cleaned[~((df_daily_cleaned["TotalSteps"] == 0) & 
                                        (df_daily_cleaned["LoggedActivitiesDistance"] == 0) & 
                                        (df_daily_cleaned["LightlyActiveMinutes"] == 0))]
    # Remove rows where TotalSteps > 0 but all active minutes (Lightly, Fairly, Very) are zero
    df_daily_cleaned = df_daily_cleaned[~((df_daily_cleaned["TotalSteps"] > 0) & 
                                      (df_daily_cleaned["LightlyActiveMinutes"] == 0) & 
                                      (df_daily_cleaned["FairlyActiveMinutes"] == 0) & 
                                      (df_daily_cleaned["VeryActiveMinutes"] == 0))]
    
    df_daily_cleaned = df_daily_cleaned[(
                                        (df_daily_cleaned["SedentaryMinutes"] + 
                                        df_daily_cleaned["LightlyActiveMinutes"] + 
                                        df_daily_cleaned["FairlyActiveMinutes"] + 
                                        df_daily_cleaned["VeryActiveMinutes"]) >= 1000)]

    # List of additional tables to copy
    tables_to_copy = ["heart_rate", "hourly_calories", "hourly_intensity", 
                    "hourly_steps", "minute_sleep", "weight_log"]

    # Read all tables into pandas DataFrames
    table_data = {table: pd.read_sql_query(f"SELECT * FROM {table}", con) for table in tables_to_copy}

    # Close the original database connection
    con.close()

    # Connect to the new cleaned database
    cleaned_con = sqlite3.connect(cleaned_db_path)

    # Save cleaned dailyActivity table
    df_daily_cleaned.to_sql("daily_activity", cleaned_con, if_exists="replace", index=False)

    # Save all other tables without modification
    for table, df in table_data.items():
        df.to_sql(table, cleaned_con, if_exists="replace", index=False)

    # Close the new database connection
    cleaned_con.close()

    print("All data has been cleaned and transferred to 'cleaned_fitbit.db'.")

data_cleaning()
