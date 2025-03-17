# Data Engineering Project: Analysing Fitbit Data

## Table of Contents
1. [Introduction](#introduction)
2. [Data](#data)
    1. [daily_activity](#daily_activitycsv)
    2. [fitbit_database](#fitbit_databasedb)
    3. [weather_Chicago](#weather_chicagocsv)
3. [Scripts](#scripts)
    1. [main](#main)
    2. [part1](#part1)
    3. [part3](#part3)
    4. [part4](#part4)


## Introduction
This project studies a dataset obtained from fitbits of 35 different respondence from amazon survey in 2016 that submited censored usage data. This library will provide tools to study various statistical analysis of the users.

## Data

### daily_activity.csv
Data file is csv and it contains information about ID of the user and Activity date, Total steps, Total distance, Step size, Tracker distance, Logged activities distance, Very active distance, Fairly active, Moderate active distance, Light active distance, Sedentary active distance, Very active minutes, Fairly active minutes, Lightly active minutes, Sedentary Minutes, Calories. 

### fitbit_database.db
This database contains the following tabular data:
* `daily_activity`: The file same as `daily_activity.csv`
* `heart_rate`: Heart rate of each individual measured every 5/10/15 seconds.
* `hourly_calories`: Calories burnt per hour.
* `hourly_intensity`: Intensity of exercise, given both in total per hour and average per hour.
* `hourly_steps`: Total amount of steps taken per hour.
* `minute_sleep`: Information on every minute that the participant in sleep.
* `weight_log`: Information on the weight, fat, BMI for each of the participants.

### weather_Chicago.csv
It is given that all participants in the sample live in Chicago. Fitbit data collected concerns dates in March and April, 2016. This `.csv` file contains the weather information in Chicago from 2016-03-01 to 2016-04-30 downloaded from [visualcrossing](https://www.visualcrossing.com/weather-query-builder/). The weather information contains factors such as (min/max) temperature, (min/max) feelslike, humidity, precipation, snow, snowdepth, conditions, etc.

## Scripts

### main
Data file "daily_activity.csv" is csv and it contains information about ID of the user and Activity date, Total steps, Total distance, Step size, Tracker distance, Logged activities distance, Very active distance, Fairly active, Moderate active distance, Light active distance, Sedentary active distance, Very active minutes, Fairly active minutes, Lightly active minutes, Sedentary Minutes, Calories. 

### Part 1: Getting acquainted with the data
Script `part1.py` contains functions that help explore the `daily_activity.csv` dataset with computations and visualizations.
* `calc_unique_graph_total_distance()` - prints the number of unique users and graphs the total distance over all active dates per user.
* `visualise_calories_burned(user_id, dates)` - displays a line graph that shows the calories burnt on each day based on a `user_id` and a list of dates.
* `frequency_day_barplot()` - display a bar plot that shows the frequency (in percentage) at which all individuals work out on each day of the week.
* `linear_regression_visualization(user_id)` - follows a linear regression model to investigate and display the relationship between the amount of steps taken and the amount of calories burnt based on input `user_id`.
* `calories_totalsteps_scatter()` - display a scatter plot that graphs the relationship between total daily steps and the calories burnt, also comparing with the median of both.
* `calories_totalhours_scatter()` - displays a scatter plot that graphs the relationship between total hours recorded and calories burnt, with the median of both.
* `plot_activity_pie_chart()` - visualizes the proportion of time spent in different activity levels (Very Active, Fairly Active, Lightly Active, and Sedentary) using a pie chart. It calculates the total minutes for each activity category and displays their relative distribution as percentages.
* `frequency_day_barplot()` - displays a bar plot that shows the frequency at which all individuals work out on each day of the week
* `plot_activity_pie_chart()` - visualizes the proportion of time spent in different activity levels (Very Active, Fairly Active, Lightly Active, and Sedentary) using a pie chart. It calculates the total minutes for each activity category and displays their relative distribution as percentages.
* `make_correlation_heatmap()` - visualizes the correlation between all numerical columns of the dataset in a heatmap
* `describe_columns(user_id)` - describes the count, mean, standard deviation, minimum, 25% quantile, 50% quantile, 75% quantile and maximum of each column based on a user_id. Pass None as an argument to get the description of all users.
* `plot_activity_pie_chart_only_active_minutes` - visualizes the proportion of time spent in different active levels (Very Active, Fairly Active, Lightly Active) using a pie chart.

REMEMBER TO MENTION OUTLIERS of the data o steps 2000 calories

For the second part the "fitbit_database.db" is used. SHOULD ADD SOME DESCRIPTION

### Part 3: Interacting with the database
Script `part3.py` contains functions that help explore the `fitbit_database.db` database with computations and visualizations.
* `create_new_dataframe()` - creates, displays, and returns a new DataFrame with two columns: "Id" (unique user IDs) and "Class" (user category: Heavy, Moderate, or Light). The classification is based on how frequently each user appears in the original CSV file "daily_activity.csv". The resulting DataFrame is sorted in descending order, from Heavy to Light users.
* `run_analysis(data_type)` - This function takes parameter "steps" or "calories" and verifies its data by retrieving daily and hourly records, merging them, and comparing total daily values with summed hourly values (in `get_verified_data(data_type)`). It identifies matches and mismatches, calculates statistics like match percentage and absolute differences (in `calculate_statistics(merged_df, label, total_column, value_column)`), and visualizes the results through pie, bar, and line charts (in `plot_graphs(merged_df, label)`).
* `compute_sleep_duration(user_id)` - computes the duration of each moment of sleep of a specific user, where the total sleep duration is calculated as the time the user wakes up minus the time the user goes to sleep
* `compare_activity_and_sleep(user_id)` - calculates the total active minutes as the sum of the very active, fairly active and light active minutes on a day and then performs a regression based on the minutes the user is asleep on that day.
* `compare_sedentary_activity_and_sleep()` – Retrieves and merges daily sedentary minutes and sleep duration, performs linear regression to analyze their relationship, generates visualizations (scatter plot with regression line, correlation heatmap, histogram of residuals), and evaluates normality of residuals using the Shapiro-Wilk test.
* `compute_block_averages()` – Calculates average steps, calories burnt, and sleep minutes within each 4-hour time block (0-4, 4-8, etc.), and visualizes these averages through bar charts.
* `plot_heart_rate_intensity(user_id)` - Retrieves and plots heart rate and hourly exercise intensity data for a given user, indicates if either heart rate or hourly intensity data is missing for the user, and only compares the period when both heart rate and intensity are recorded.
* `visualize_weather_activity()` - Retrieves weather data in Chicago and daily activity records, merges them based on date, visualizes the distribution of activity levels across different weather conditions, and analyzes the relationship between weather factors and individual activity levels using regression models.


### Part 4: Interacting with the database continued
* `sample_random_age(user)` - 
* `sample_random_gender(user)` - 
* `resolve_missing_values_weight_log()` - 
* `check_correlation_weight_calories()` - Analyzes the correlation between Calories and Weight. It merges daily calories data from daily_activity with weight from weight_logs, forward-fills missing weights, and visualizes the relationship using a scatter plot (in `plot_scatterplot_calculate_correlation(merged_df)`). It also calculates and prints the overall correlation. 

## Cleaning Fitbit database: MAYBE ADD SOME MORE IF WE ARE GONNA USE CLEANED DATABASE
* `data_cleaning()` - This function cleans and processes Fitbit activity data. It removes duplicate entries, filters out invalid records (such as days with no activity or incomplete data), and ensures meaningful activity tracking. After cleaning, it transfers the refined data, along with other unmodified tables, to a new database (cleaned_fitbit.db). 

## Part 5: Functions to retrieve data for dashboard
*  `retrieve_average(category, dates)` - returns average for one of given categories with given date list: "total_user" , "TotalSteps", "Calories", "TotalDistance", "ActiveMinutes", "SedentaryMinutes" 
*  `activity_sum_data(dates)` - return dataframe with two columns one with the type of activity (Very, Fairly, Lightly Active or Sedentary) and average minutes per day for given period passed as list
* `average_steps_per_hour(dates)` - return dataframe with columns Hour and mean of TotalSteps per hour for given period passed as list
* `average_heart_rate_per_hour()` - This function retrieves heart rate data from the database, processes the timestamps to extract hourly values, and calculates the average heart rate per hour for each day. It returns a DataFrame with daily hourly averages.
* `hourly_average_heart_rate_dates(dates)` - This function filters the heart rate data to include only the specified dates and computes the average heart rate per hour across those dates. It returns a DataFrame containing the final hourly averages.
* `hourly_average_calories(dates)` - return dataframe with columns Hour and mean of Calories burned per hour for given period passed as list
* ` heart_rate_and_intensitivity(dates)` - This function retrieves heart rate and intensity data from the database, filters it based on the given dates, calculates the average heart rate and total intensity per hour, and merges both datasets into a single DataFrame.
* `calories_and_active_minutes(dates)` - This function extracts activity and calorie data, filters it by date, calculates the total active minutes (sum of very active, fairly active, and lightly active minutes), and returns a DataFrame with total active minutes and calories for further analysis 
* `heart_rate_and_sleep_value(dates)` - NOT SURE IF WE WILL USE THIS ONE AT THE END
This function extracts heart rate and sleep value data, filters it by date, calculates the average heart rate per minute, and returns a DataFrame with heart per minute and sleep value for further analysis 
* `average_distance_per_week(dates)` - This function retrieves daily distance data from the database, filters it based on the given dates, and calculates the average total distance traveled for each day of the week. The days are then ordered from Monday to Sunday before returning the final DataFrame.
* `average_steps_per_week(dates)` - This function retrieves daily total steps data from the database, filters it based on the given dates, and calculates the average total steps walked for each day of the week. The days are then ordered from Monday to Sunday before returning the final DataFrame.
* `average_calories_per_week(dates)` - This function retrieves daily total calories data from the database, filters it based on the given dates, and calculates the average calories burned for each day of the week. The days are then ordered from Monday to Sunday before returning the final DataFrame.
* `average_active_minutes_per_week(dates)` - This function retrieves daily very, fairly and lightly active minutes data from the database, filters it based on the given dates, and calculates the average very, fairly and lightly active minutes for each day of the week. The days are then ordered from Monday to Sunday before returning the final DataFrame.

## Graphing functions for dashboard: Functions to create graphs in dashboard
* ` create_metric_block(col, title, value, unit="", bg_color="#CFEBEC"):` - This function creates a block with specific color, given title and value which later can be used to present data in it for the dashboard
* `plot_activity_pie_chart(dates)` -  This function creates a pie chart to visualize the average daily activity breakdown based on user-selected dates. It retrieves activity data, categorizes minutes into different activity levels (Very Active, Fairly Active, Lightly Active, Sedentary), and assigns custom colors for better distinction. The pie chart includes percentage labels and an interactive hover feature displaying the exact minutes per activity category.
* `bar_chart_hourly_average_steps(dates)` - This function generates a bar chart displaying the average number of steps taken per hour for the given dates. It highlights the top three most active hours with a distinct color. 
* `plot_heart_rate(dates)` - This function generates a line chart displaying the average heart rate per hour for the given dates.
* `bar_chart_hourly_average_calories(dates)` - This function generates a bar chart displaying the average number of calories burned per hour for the given dates. It highlights the top three most calories burned hours with a distinct color. 
* `scatterplot_heart_rate_intensityvity(dates)` - This function generates the scatterplot between heart rate and exercise intensitivity for the given dates.
* `scatterplot_calories_and_active_minutes(dates)` - This function generates the scatterplot between calories and active minutes for the given dates.
* `scatterplot_heart_rate_sleep_value(dates)` - This function generates the scatterplot between heart rate and sleep value for the given dates. NOT USED FOR NOW
* `lineplot_heart_rate_over_night(dates)` - This function generates a line plot displaying the average heart rate per hour over night for the given dates. NOT USED FOR NOW
* `bar_chart_average_distance_per_week(dates)` - This function generates a bar chart displaying the average distance walked per day per week for the given dates. It highlights the most active day with a distinct color. 
* `bar_chart_average_steps_per_week(dates)` - This function generates a bar chart displaying the average steps taken per day per week for the given dates. It highlights the most active day with a distinct color. 
* `bar_chart_average_calories_per_day_for_week(dates)` - This function generates a bar chart displaying the average calories burned per day per week for the given dates. It highlights the most active day with a distinct color. 
* `plot_active_minutes_bar_chart_per_day(dates)` - This function generates a bar chart displaying the average different type of active minutes per day per week for the given dates. It highlights the most active day with a distinct color. 


## General insights: Creating dashboard by calling functions from Graphing_functions_for_dashboard.py