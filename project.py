# IMPORTS
import pandas as pd
import matplotlib.pyplot as plt
import datetime
# trytry
# 00000

# udoucdagfa
data = pd.read_csv("daily_acivity.csv", header=0)
print(data.head())

#PartI 

# STEP 2: displays a line graph that shows the calories burnt on each day
def visualise_calories_burned(user_id, dates):
    data["ActivityDate"] = pd.to_datetime(data["ActivityDate"])
    data["ActivityDate"] = data["ActivityDate"].dt.strftime('%m/%d/%Y')

    calories_burned_user = data.loc[(data["ActivityDate"].isin(dates)) & (data["Id"] == user_id)]

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(calories_burned_user["ActivityDate"], calories_burned_user["Calories"])
    ax.set_xticklabels(calories_burned_user["ActivityDate"], fontsize="small", rotation=45)
    ax.set_title(f"Calories burned per day for user {user_id}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Calories burned")
    plt.show()

visualise_calories_burned(1503960366, [datetime.datetime(2016, 3, 25).strftime('%m/%d/%Y'), datetime.datetime(2016, 3, 26).strftime('%m/%d/%Y'), datetime.datetime(2016, 3, 27).strftime('%m/%d/%Y')])

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
