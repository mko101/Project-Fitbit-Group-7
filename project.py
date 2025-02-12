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

workout_counts = data["DayOfWeek"].value_counts().reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
workout_frequency = workout_counts / workout_counts.sum()

plt.figure(figsize=(8, 5))
plt.bar(workout_frequency.index, workout_frequency.values, color='skyblue', edgecolor='black')
plt.xlabel("Day of the Week")
plt.ylabel("Frequency of Workouts")
plt.title('Workout Frequency per Weekday')
for i, freq in enumerate(workout_frequency.values):
    plt.text(i, freq, f'{freq:.2%}', ha='center', va='bottom', fontsize=10)
plt.show()
