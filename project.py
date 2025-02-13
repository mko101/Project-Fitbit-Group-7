# IMPORTS
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import statsmodels.api as sm

data = pd.read_csv("daily_acivity.csv", header=0)
print(data.head())

#PartI 

# STEP 1: count unique users and total distance for each user and graph it
def calc_unique_graph_total_distance():
    df = pd.DataFrame(data)
    df["Id"] = df["Id"].astype(str)
    total_users = df["Id"].nunique()

    print("number of total users:",total_users)
    # creating dictionary with key as user and sum of totalDistances as values
    user_distance = df.groupby("Id")["TotalDistance"].sum().to_dict()


    user_ids = list(user_distance.keys())
    print(user_ids)
    distances = list(user_distance.values())

    plt.figure(figsize=(9, 15))
    plt.bar(user_ids, distances, color='skyblue', edgecolor='black')

    plt.xticks(rotation= 90) 
    plt.xlabel("User ID")
    plt.ylabel("Total Distance")
    plt.title("Total Distance Covered by Each User")
    plt.subplots_adjust(bottom=0.25)
    plt.show()

calc_unique_graph_total_distance()

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
def frequency_day_barplot():
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

frequency_day_barplot()

# Step 4: Linear Regression Model and Visualization
def linear_regression_visualization(user_id):
    user_data = data[data["Id"] == user_id]
    X = user_data[["TotalSteps", "Id"]]  # decision variables
    y = user_data["Calories"]   # depedent variable
    
    # convert 'Id' to dummy
    X["Id"] = X["Id"].astype("category")
    X = pd.get_dummies(X, columns=["Id"], drop_first=True)
    X = sm.add_constant(X)
    
    # linear regression model
    model = sm.OLS(y, X).fit()
    
    print(model.summary())
    
    plt.figure(figsize=(10, 6))
    plt.scatter(user_data["TotalSteps"], user_data["Calories"], color='skyblue', label='Data points')
    plt.plot(user_data["TotalSteps"], model.predict(X), color='red', label='Regression line')
    plt.xlabel("Total Steps")
    plt.ylabel("Calories Burned")
    plt.title(f"Linear Relationship between Total Steps and Calories Burned for User {user_id}")
    plt.legend()
    plt.show()

# Example usage
linear_regression_visualization(1503960366)