# IMPORTS
import pandas as pd


data = pd.read_csv("daily_acivity.csv", index_col=0)
print(data.head())