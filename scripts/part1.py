# IMPORTS
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns

data = pd.read_csv("../data/daily_activity.csv", header=0)

# converting the data to the type datetime
data["ActivityDate"] = pd.to_datetime(data["ActivityDate"], format='%m/%d/%Y')

# Part I 

# Step 1: count unique users and total distance for each user and graph it
def calc_unique_graph_total_distance():
    total_users = data["Id"].nunique()
    print("Number of total users:", total_users)

    # creating dictionary with key as user and sum of totalDistances as values
    user_distance = data.groupby("Id")["TotalDistance"].sum().to_dict()

    user_ids = list(map(str, user_distance.keys()))
    distances = list(user_distance.values())

    plt.figure(figsize=(9, 15))
    plt.bar(user_ids, distances, color="skyblue", edgecolor="black")

    plt.xticks(rotation= 90) 
    plt.xlabel("User ID")
    plt.ylabel("Total Distance")
    plt.title("Total Distance Covered by Each User")
    plt.subplots_adjust(bottom=0.25)
    plt.show()

calc_unique_graph_total_distance()

# Step 2: displays a line graph that shows the calories burnt on each day
def visualise_calories_burned(user_id, dates):
    # convert the type of dates to datetime
    dates = pd.to_datetime(dates, format='%m/%d/%Y')

    # selects the rows from the dataframe that have the right user_id and dates
    calories_burned_user = data.loc[(data["ActivityDate"].isin(dates)) & (data["Id"] == user_id)]

    # plots the calories burned for the user and dates passed to the function
    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(calories_burned_user["ActivityDate"], calories_burned_user["Calories"])
    ax.set_xticks(calories_burned_user["ActivityDate"])
    ax.set_xticklabels(calories_burned_user["ActivityDate"].dt.strftime('%m/%d/%Y'), fontsize="small", rotation=45)
    ax.set_title(f"Calories Burned per Day for User {user_id}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Calories Burned")
    plt.show()

visualise_calories_burned(1503960366, ["3/25/2016", "3/26/2016", "3/27/2016", "3/28/2016", "3/29/2016", "3/30/2016", "3/31/2016", "4/1/2016", "4/2/2016", "4/3/2016"])

# Step 3: DateTime make a barplot Frequency and day
def frequency_day_barplot():
    data["DayOfWeek"] = data["ActivityDate"].dt.day_name()

    workout_counts = data["DayOfWeek"].value_counts().reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    workout_frequency = workout_counts / workout_counts.sum()

    plt.figure(figsize=(8, 5))
    plt.bar(workout_frequency.index, workout_frequency.values, color='skyblue', edgecolor='black')
    plt.xlabel("Day of the Week")
    plt.ylabel("Frequency of Workouts")
    plt.title('Workout Frequency per Weekday')
    for i, freq in enumerate(workout_frequency.values):
        plt.text(i, freq, f'{freq:.2%}', ha="center", va="bottom", fontsize=10)
    plt.show()

frequency_day_barplot()

# Step 4: Linear Regression Model and Visualization
def linear_regression_visualization(user_id):
    user_data = data[data["Id"] == user_id]
    X = user_data[["TotalSteps", "Id"]]  # decision variables
    y = user_data["Calories"]   # depedent variable
    
    # convert 'Id' to dummy
    X = X.copy()
    X["Id"] = X["Id"].astype("category")
    X = pd.get_dummies(X, columns=["Id"], drop_first=True)
    X = sm.add_constant(X)
    
    # linear regression model
    model = sm.OLS(y, X).fit()
    
    print(model.summary())
    
    plt.figure(figsize=(10, 6))
    plt.scatter(user_data["TotalSteps"], user_data["Calories"], color="skyblue", label="Data points")
    plt.plot(user_data["TotalSteps"], model.predict(X), color="red", label="Regression line")
    plt.xlabel("Total Steps")
    plt.ylabel("Calories Burned")
    plt.title(f"Linear Relationship between Total Steps and Calories Burned for User {user_id}")
    plt.legend()
    plt.show()

# Example usage
linear_regression_visualization(4020332650)

# Step 5: Creativity visualization
def calories_totalsteps_scatter():
    plt.figure(figsize=(10, 6))
    plt.scatter(data.TotalSteps, data.Calories, c=data.Calories)

    # Compute median values
    median_steps = data["TotalSteps"].median()
    median_calories = data["Calories"].median()

    plt.axhline(median_calories, color='b', label='Median of Calories')
    plt.axvline(median_steps, color='r', label='Median of Steps')

    plt.xlabel("Steps")
    plt.ylabel("Calories")
    plt.title("Calories & TotalSteps")

    plt.legend()
    plt.show()
    
calories_totalsteps_scatter()


def calories_totalhours_scatter():
    data['TotalMinutes']=data.VeryActiveMinutes + data.FairlyActiveMinutes + data.LightlyActiveMinutes + data.SedentaryMinutes
    data['TotalHours']=round(data.TotalMinutes / 60)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(data.TotalHours, data.Calories, c=data.Calories)

    # Compute median values
    median_veryactiveminutes = data["TotalHours"].median()
    median_calories = data["Calories"].median()

    plt.axhline(median_calories, color='b', label='Median of Calories')
    plt.axvline(median_veryactiveminutes, color='r', label='Median of TotalHours')

    plt.xlabel("TotalHours")
    plt.ylabel("Calories")
    plt.title("Calories & TotalHours")

    plt.legend()
    plt.show()
    
calories_totalhours_scatter()

def make_correlation_heatmap():
    corr = data.corr(numeric_only=True)
    plt.figure(figsize=(11, 6))
    sns.heatmap(corr, annot=True, annot_kws={'size': 6})
    plt.title("Correlation between variables")
    plt.tick_params(axis='both', which='major', labelsize=6)
    plt.subplots_adjust(left=0.2)
    plt.subplots_adjust(bottom=0.2)
    plt.show()

make_correlation_heatmap()

def describe_columns(user_id):

    df = data.loc[data["Id"] == user_id] if user_id else data

    for column in df:
        if column not in ["Id", "ActivityDate", "DayOfWeek"]:
            print(df[column].describe())
            print()

describe_columns(None)
describe_columns(4020332650)

def plot_activity_pie_chart():

    minutes = [
        data["VeryActiveMinutes"].sum(), 
        data["FairlyActiveMinutes"].sum(),
        data["LightlyActiveMinutes"].sum(),  # Corrected name
        data["SedentaryMinutes"].sum()
    ]
    
    labels = ['Very Active', 'Fairly Active', 'Lightly Active', 'Sedentary']
    plt.figure(figsize=(8, 8))
    plt.pie(minutes, labels=labels, autopct='%1.1f%%', explode=[0, 0, 0, 0.15], colors=['red', 'orange', 'yellow', 'gray'])
    plt.title("Activity Breakdown by Minutes")
    plt.show()

plot_activity_pie_chart()
