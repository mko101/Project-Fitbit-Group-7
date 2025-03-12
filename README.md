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
`plot_activity_pie_chart_only_active_minutes` - visualizes the proportion of time spent in different active levels (Very Active, Fairly Active, Lightly Active) using a pie chart.

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
* `resolve_missing_values_weight_log()` - 
* `check_correlation_weight_calories()` - Analyzes the correlation between Calories and Weight. It merges daily calories data from daily_activity with weight from weight_logs, forward-fills missing weights, and visualizes the relationship using a scatter plot (in `plot_scatterplot_calculate_correlation(merged_df)`). It also calculates and prints the overall correlation. 
