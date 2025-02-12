# IMPORTS
import pandas as pd
# trytry
# 00000

# udoucdagfa
data = pd.read_csv("daily_acivity.csv", index_col=0)
print(data.head())

#PartI 
##3rd step: DateTime make a barplot Frequency and day##
import matplotlib.pyplot as plt

data["ActivityDate"] = pd.to_datetime(data["ActivityDate"])
data["DayOfWeek"] = data["ActivityDate"].dt.day_name()

day_counts = data["DayOfWeek"].value_counts()
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_counts = day_counts.reindex(day_order)

plt.figure(figsize=(8, 5))
plt.bar(day_counts.index, day_counts.values)
plt.xlabel("Day of the Week")
plt.ylabel("Frequency of Workouts")
plt.title("Workouts per Day of the Week")
plt.xticks(rotation=45)
plt.show()
