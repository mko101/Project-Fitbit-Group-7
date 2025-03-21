# Data Engineering Project: Analysing Fitbit Data

## Table of Contents
1. [Introduction](#introduction)
2. [Dependencies](#dependencies)
3. [Data](#data)
    1. [daily_activity](#daily_activitycsv)
    2. [fitbit_database](#fitbit_databasedb)
    3. [weather_Chicago](#weather_chicagocsv)
4. [Scripts](#scripts)
    1. [main](#main)
    2. [part1](#part1)
    3. [part3](#part3)
    4. [part4](#part4)
    5. [part5](#part-5-functions-to-retrieve-data-for-dashboard)
    6. [Graphing functions for dashboard](#graphing-functions-for-dashboard-functions-to-create-graphs-in-dashboard)
    7. [General insights dashboard](#general-insights-creating-dashboard-by-calling-functions-from-plots_general_insightspy)
    8. [User Graphing functions for dashboard](#user-graphing-functions)
    9. [User-specific data dashboard](#user-specific-data-dashboard)


## Introduction
This project studies a dataset obtained from fitbits of 35 different respondence from amazon survey in 2016 that submited censored usage data. This library will provide tools to study various statistical analysis of the users.

## Dependencies

### Core Requirements
- **Python 3.12+**
- **SQLite 3** 

### Python Libraries

#### Data Processing
- **pandas** 
- **numpy** 

#### Visualization
- **plotly 6.0.1** 
  - plotly.express
  - plotly.graph_objects
  - plotly.subplots
- **matplotlib**
- **seaborn** 

#### Dashboard
- **streamlit 1.43.2**

#### Analysis
- **scipy** 
- **statsmodels**

#### Database
- **sqlite3**



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

### weather_Chicago_hourly.csv
This file contains hourly weather data for Chicago, covering the period from 2016-03-12 to 2016-04-12. It includes detailed information on various weather factors such as temperature, feels-like temperature, humidity, precipitation, snow, snow depth, and conditions, among others. The data was sourced from [visualcrossing](https://www.visualcrossing.com/weather-query-builder/).

### cleaned_fitbit.db
The cleaned Fitbit database is created from the original dataset by removing duplicates, filtering out invalid records, and ensuring meaningful activity tracking. Entries with no recorded activity, incomplete data (possibly due to device battery depletion), or inconsistencies are excluded. This process enhances the accuracy of average values and correlations, making the data more reliable for analysis. The cleaning process is implemented in cleaning_fitbit_database.py. For the General Analysis the cleaned database_fitbit.db is used.

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
* `make_correlation_heatmap()` - visualizes the correlation between all numerical columns of the dataset in a heatmap.
* `describe_columns(user_id)` - describes the count, mean, standard deviation, minimum, 25% quantile, 50% quantile, 75% quantile and maximum of each column based on a user_id. Pass None as an argument to get the description of all users.
* `plot_activity_pie_chart()` - visualizes the proportion of time spent in different activity levels (Very Active, Fairly Active, Lightly Active, and Sedentary) using a pie chart. It calculates the total minutes for each activity category and displays their relative distribution as percentages.
* `plot_activity_pie_chart_only_active_minutes()` - visualizes the proportion of time spent in different active levels (Very Active, Fairly Active, Lightly Active) using a pie chart.

### Part 3: Interacting with the database
Script `part3.py` contains functions that help explore the `fitbit_database.db` database with computations and visualizations.
* `create_new_dataframe()` - creates, displays, and returns a new DataFrame with two columns: "Id" (unique user IDs) and "Class" (user category: Heavy, Moderate, or Light). The classification is based on how frequently each user appears in the original CSV file "daily_activity.csv". The resulting DataFrame is sorted in descending order, from Heavy to Light users.
* `run_analysis(data_type)` - this function takes parameter "steps" or "calories" and verifies its data by retrieving daily and hourly records, merging them, and comparing total daily values with summed hourly values (in `get_verified_data(data_type)`). It identifies matches and mismatches, calculates statistics like match percentage and absolute differences (in `calculate_statistics(merged_df, label, total_column, value_column)`), and visualizes the results through pie, bar, and line charts (in `plot_graphs(merged_df, label)`).
* `compute_sleep_duration(user_id)` - computes the duration of each moment of sleep of a specific user, where the total sleep duration is calculated as the time the user wakes up minus the time the user goes to sleep
* `compute_sleep_on_day(user_id)` - computes the total minutes of sleep for each date by counting the number of rows for each unique combination of `Id`, `date`, and weekday. This can be done for a specific user by passing the `user_id`, or for all users if `None` is provided as the argument.
* `compare_activity_and_sleep(user_id, dates)` - calculates the total active minutes as the sum of the `VeryActiveMinutes`, `FairlyActiveMinutes` and `LightlyActiveMinutes` on a day and then performs a regression based on the minutes the user is asleep on that day calculated based on the `compute_sleep_on_day(user_id)` function. This can be done for a specific user by passing the `user_id`, or for all users if `None` is provided as the argument based on a specific date range provided by the dates' argument as a list.
* `compare_sedentary_activity_and_sleep(user_id, dates)` – retrieves and merges daily sedentary minutes and sleep duration, performs linear regression to analyze their relationship, generates visualizations (scatter plot with regression line, correlation heatmap, histogram of residuals), and evaluates normality of residuals using the Shapiro-Wilk test. This can be done for a specific date range provided by the dates' argument as a list.
* `compute_block_averages()` – calculates average steps, calories burnt, and sleep minutes within each 4-hour time block (0-4, 4-8, etc.), and visualizes these averages through bar charts.
* `plot_heart_rate_intensity(user_id)` - retrieves and plots heart rate and hourly exercise intensity data for a given user, indicates if either heart rate or hourly intensity data is missing for the user, and only compares the period when both heart rate and intensity are recorded.
* `visualize_weather_activity()` - retrieves weather data in Chicago and daily activity records, merges them based on date, visualizes the distribution of activity levels across different weather conditions, and analyzes the relationship between weather factors and individual activity levels using regression models. 

### Part 4: Interacting with the database continued
* `sample_random_age(user)` - randomly selects an age from an empirical distribution based on Fitbit users' age classifications and assigns it to the specified user_id.
* `sample_random_gender(user)` - randomly assigns a gender to the specified user_id based on available gender data from Fitbit users.
* `resolve_missing_values_weight_log()` - fills in any missing `WeightKg` values and makes corrections to the database when needed. Additionally, it includes a query to remove the `Fat` column from the table, as only two values were provided in that column, and it's challenging to fill in this data without knowing the gender and age. It's recommended to run this query once, before using data from this table. Alternatively, the code offers a method to fill in the missing `Fat` values, but this approach is not advised.
* `check_correlation_weight_calories()` - analyzes the correlation between `Calories` and `Weight`. It merges daily calories data from daily_activity with weight from weight_logs, forward-fills missing weights, and visualizes the relationship using a scatter plot (in `plot_scatterplot_calculate_correlation(merged_df)`). It also calculates and prints the overall correlation.

### Cleaning Fitbit database:
* `data_cleaning()` - This function cleans and processes Fitbit activity data. It removes duplicate entries, filters out invalid records (such as days with no activity or incomplete data), and ensures meaningful activity tracking. After cleaning, it transfers the refined data, along with other unmodified tables, to a new database (cleaned_fitbit.db). 

### Part 5: Functions to retrieve data for dashboard
* `retrieve_average(category, dates)` - returns average for one of given categories with given date list: `total_user` , `TotalSteps`, `Calories`, `TotalDistance`, `ActiveMinutes`, `SedentaryMinutes`. 
* `activity_sum_data(dates)` - returns a dataframe with two columns one with the type of activity (Very, Fairly, Lightly Active or Sedentary) and average minutes per day for given period passed as list.
* `average_steps_per_hour(dates)` - returns a dataframe with columns Hour and mean of TotalSteps per hour for given period passed as list.
* `average_heart_rate_per_hour()` - this function retrieves heart rate data from the database, processes the timestamps to extract hourly values, and calculates the average heart rate per hour for each day. It returns a DataFrame with daily hourly averages.
* `hourly_average_heart_rate_dates(dates)` - this function filters the heart rate data to include only the specified dates and computes the average heart rate per hour across those dates. It returns a DataFrame containing the final hourly averages.
* `hourly_average_calories(dates)` - returns a dataframe with columns `Hour` and mean of `Calories` burned per hour for given period passed as list
* ` heart_rate_and_intensitivity(dates)` - this function retrieves heart rate and intensity data from the database, filters it based on the given dates, calculates the average heart rate and total intensity per hour, and merges both datasets into a single DataFrame.
* `calories_and_active_minutes(dates)` - this function extracts activity and calorie data, filters it by date, calculates the total active minutes (sum of very active, fairly active, and lightly active minutes), and returns a DataFrame with total active minutes and calories for further analysis 
* `heart_rate_and_sleep_value(dates)` - NOT SURE IF WE WILL USE THIS ONE AT THE END
This function extracts heart rate and sleep value data, filters it by date, calculates the average heart rate per minute, and returns a DataFrame with heart per minute and sleep value for further analysis 
* `average_distance_per_week(dates)` - this function retrieves daily distance data from the database, filters it based on the given dates, and calculates the average total distance traveled for each day of the week. The days are then ordered from Monday to Sunday before returning the final DataFrame.
* `average_steps_per_week(dates)` - this function retrieves daily total steps data from the database, filters it based on the given dates, and calculates the average total steps walked for each day of the week. The days are then ordered from Monday to Sunday before returning the final DataFrame.
* `average_calories_per_week(dates)` - this function retrieves daily total calories data from the database, filters it based on the given dates, and calculates the average calories burned for each day of the week. The days are then ordered from Monday to Sunday before returning the final DataFrame.
* `average_active_minutes_per_week(dates)` - this function retrieves daily very, fairly and lightly active minutes data from the database, filters it based on the given dates, and calculates the average very, fairly and lightly active minutes for each day of the week. The days are then ordered from Monday to Sunday before returning the final DataFrame.
* `hourly_weather_data()` - returns a dataframe containing all the weather data from `weather_Chicago_hourly.csv`, along with two additional columns for the hours and days of the dates.
* `compute_steps_hourly()` - returns a dataframe containing the hourly step count data for users, along with two additional columns for the hours and days of the dates.
* `compute_intensity_hourly()` - returns a dataframe containing the hourly intensity data for users, along with two additional columns for the hours and days of the dates.
* `create_scatterplot_weather(df1, df2, hours, days, dates)` - creates a dataframe and scatterplot for `df1` and `df2`, where the functions `hourly_weather_data()`, `compute_steps_hourly()`, and `compute_intensity_hourly()` can be used as arguments for the dataframe variables. The function will then merge the dataframes based on the provided hours, days, and dates. The hours should be passed in the following format: `["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]`, the days can be either `["Weekdays", "Weekend"]` or a combination of both, and the dates should be a list containing any number of dates.
* `daily_activity(dates)` - returns a dataframe containing both `VeryActiveDistance` and `VeryActiveMinutes` for the dates specified in a list passed to the function, calculated as the mean of all data collected on each date.
* `categorized_weight_data()` - returns a dataframe containing users' weight data, along with an additional column, `CategoryWeight`, in which each user's weight is categorized into one of the following ranges: 50-70kg, 70-90kg, 90-110kg, or 110-130kg.
* `sleep_data(dates)` - returns a dataframe containing hourly sleep information for users, where the minutes asleep in each hour are calculated based on the count of minutes recorded as asleep. If no sleep is recorded for a particular hour but the user has other data for the same date, the minutes asleep for that hour will be assumed to be zero.
* `create_dataframe_scatterplot_sleep(variable, dates)` - returns a dataframe containing the total minutes a user slept on a specified date, calculated by counting all minutes recorded as asleep. It also includes either the total number of steps the user took that day or the total number of calories burned, depending on whether `Steps` or `Calories` is passed as the variable. This information is provided for the dates specified in the list passed to the dates variable.
* `workout_frequency_per_period(data)` - this function retrieves the daily activity, total active and fairly active minutes from the database. It is assumed that workout is made by user if he has either very active minutes or fairly active minutes value more than zero.  Function returns dataframe the total number of workouts per given period for all users.
* `average_steps_calories_per_period(dates)` - this function retrieves daily total steps and calories data from the database, filters it based on the given dates, and calculates the average total steps walked for period returning the final DataFrame.


### Graphing functions for dashboard: Functions to create graphs in dashboard
* `create_metric_block(col, title, value, unit="", bg_color="#CFEBEC")` - this function creates a block with specific color, given title and value which later can be used to present data in it for the dashboard
* `create_correlation_block(title, value, unit="", bg_color="#CFEBEC")` - similar to `create_metric_block()`, this function creates a block with a specified color, title, value, and optionally a unit, but with slightly smaller text size.
* `is_empty_dataframe(df)` - checks if the given dataframe is empty, and if so, displays a colored text block saying, "Sorry, no data is available for the selected date range in this graph."
* `plot_activity_pie_chart(dates)` -  this function creates a pie chart to visualize the average daily activity breakdown based on user-selected dates. It retrieves activity data, categorizes minutes into different activity levels (Very Active, Fairly Active, Lightly Active, Sedentary), and assigns custom colors for better distinction. The pie chart includes percentage labels and an interactive hover feature displaying the exact minutes per activity category.
* `bar_chart_hourly_average_steps(dates)` - this function generates a bar chart displaying the average number of steps taken per hour for the given dates. It highlights the top three most active hours with a distinct color. 
* `plot_heart_rate(dates)` - this function generates a line chart displaying the average heart rate per hour for the given dates.
* `bar_chart_hourly_average_calories(dates)` - this function generates a bar chart displaying the average number of calories burned per hour for the given dates. It highlights the top three most calories burned hours with a distinct color. 
* `scatterplot_heart_rate_intensityvity(dates)` - this function generates the scatterplot between heart rate and exercise intensitivity for the given dates.
* `scatterplot_calories_and_active_minutes(dates)` - this function generates the scatterplot between calories and active minutes for the given dates.
* `plot_correlation_sleep_sedentary_minutes(dates)` - creates a figure with a scatterplot displaying the relationship between Sedentary Minutes and Total Minutes Asleep for the given dates, and calculates the correlation between the two variables.
* `plot_correlation_sleep_active_minutes(dates)` - creates a figure with a scatterplot displaying the relationship between Active Minutes and Total Minutes Asleep for the given dates, and calculates the correlation between the two variables.
* `plot_correlation_weather_steps(hours, days, dates)` - creates a figure with a scatterplot displaying the relationship between Hourly Steps and Temperature based on the hours, days, and dates passed to the function. The hours should be provided in the following format: `["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]`, the days can be either `["Weekdays", "Weekend"]` or a combination of both, and the dates should be a list containing any number of dates.
* `plot_correlation_weather_intensity(hours, days, dates)` - creates a figure with a scatterplot displaying the relationship between Hourly Total Intensity and Temperature based on the hours, days, and dates passed to the function. The hours should be provided in the following format: `["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]`, the days can be either `["Weekdays", "Weekend"]` or a combination of both, and the dates should be a list containing any number of dates.
* `bar_chart_daily_intensity(dates)` - generates a bar chart displaying the average Total Intensity per hour for the given dates, highlighting the top three most intense hours with a distinct color.
* `plot_active_minutes_active_distance(dates)` - generates a figure with two line graphs illustrating the relationship between Very Active Distance and Very Active Minutes for the specified date range.
* `plot_weight_pie_chart()` - generates a pie chart displaying the weight distribution among all participants, categorizing the weights into the following ranges: 50-70kg, 70-90kg, 90-110kg, and 110-130kg.
* `bar_chart_daily_sleep(dates)` - generates a bar chart showing the average minutes asleep per hour for the given dates, highlighting the top three hours with the most sleep in a distinct color.
* `bar_chart_weekly_sleep(dates)` - generates a bar chart displaying the average minutes asleep per day for the given dates, highlighting the day with the most sleep in a distinct color.
* `plot_correlation_sleep_steps(dates)` - creates a figure with a scatterplot displaying the relationship between Step Total and Total Minutes Asleep for the given dates, and calculates the correlation between the two variables.
* `plot_correlation_sleep_calories(dates)` - creates a figure with a scatterplot displaying the relationship between Calories and Total Minutes Asleep for the given dates, and calculates the correlation between the two variables.
* `plot_user_pie_chart()` - generates a pie chart showing the distribution of users among all participants, categorizing them into the following groups: Light User (≤ 10 daily records), Moderate User (11-15 daily records), and Heavy User (≥ 16 daily records).
* `bar_chart_average_distance_per_week(dates)` - this function generates a bar chart displaying the average distance walked per day per week for the given dates. It highlights the most active day with a distinct color. 
* `bar_chart_average_steps_per_week(dates)` - this function generates a bar chart displaying the average steps taken per day per week for the given dates. It highlights the most active day with a distinct color.
* `bar_chart_average_calories_per_day_for_week(dates)` - this function generates a bar chart displaying the average calories burned per day per week for the given dates. It highlights the most active day with a distinct color. 
* `plot_active_minutes_bar_chart_per_day(dates)` - this function generates a bar chart displaying the average different type of active minutes per day per week for the given dates. It highlights the most active day with a distinct color. 
* `bar_chart_total_workout_frequency_for_period(dates)` - this function plots the barchart about the total workout frequency during the given period. 
* `scatterplot_heart_rate_sleep_value(dates)` - this function generates the scatterplot between heart rate and sleep value for the given dates. NOT USED FOR NOW
* `lineplot_heart_rate_over_night(dates)` - this function generates a line plot displaying the average heart rate per hour over night for the given dates. NOT USED FOR NOW
* `plot_steps_calories_combined_general(dates)` - plots the average calories burned and average steps taken per given period for all users

### General insights: Creating dashboard by calling functions from plots_general_insights.py
This module provides a general analysis of all users' fitness data, offering insights into overall activity patterns. It includes interactive scatterplots to visualize correlations between different variables and barcharts to helps identify monthly, weekly, and daily trends over a chosen period. The module features intuitive and interactive graphs, making it easy to explore Fitbit tracking data and understand users' activity behaviors.

### User Graphing Functions
This module contains specialized visualization functions for analyzing individual user fitness data. It's designed to create detailed, interactive charts and dashboards to help understand personal activity patterns from Fitbit tracking data.

#### Data Retrieval
* `get_user_data(user, start_date, end_date)` - Retrieves filtered data for a specific user within a date range
* `get_all_users_data(start_date, end_date)` - Retrieves filtered data for all users within a date range
* `get_user_data_with_sleep(user, start_date, end_date)` - Retrieves user data with sleep metrics incorporated
* `get_heart_rate_data(user, start_date, end_date)` - Retrieves heart rate data from the database
* `get_heart_rate_for_day(user, selected_date)` - Retrieves detailed heart rate data for a specific day
* `get_hourly_calories_data(user, start_date, end_date)` - Retrieves hourly calorie burn data
* `get_calories_for_day(user, selected_date)` - Retrieves detailed calorie data for a specific day
* `get_hourly_steps_data(user, start_date, end_date)` - Retrieves hourly step count data
* `get_steps_for_day(user, selected_date)` - Retrieves detailed step data for a specific day
* `get_hourly_intensity_data(user, start_date, end_date)` - Retrieves hourly activity intensity data
* `get_intensity_for_day(user, selected_date)` - Retrieves detailed intensity data for a specific day
* `get_sleep_stage_data(user, start_date, end_date)` - Retrieves sleep stage information

#### Step & Calorie Analysis
* `plot_steps_calories_combined(user, start_date, end_date)` - Creates a dual-axis chart showing steps and calories with user average comparison
* `plot_daily_steps(user, start_date, end_date)` - Bar chart of daily step counts
* `plot_daily_calories(user, start_date, end_date)` - Bar chart of daily calorie burn
* `plot_hourly_steps(user, start_date, end_date)` - Line chart showing step patterns throughout the day
* `plot_hourly_calories(user, start_date, end_date)` - Line chart showing calorie burn patterns by hour
* `plot_daily_steps_pie(user, start_date, end_date)` - Pie chart breaking down steps by time of day
* `plot_daily_calories_pie(user, start_date, end_date)` - Pie chart of calories burned by time of day
* `plot_daily_steps_chart(user, selected_date)` - Detailed analysis of steps for a specific day
* `plot_daily_calories_chart(user, selected_date)` - Detailed analysis of calorie burn for a specific day

#### Activity Analysis
* `plot_activity_breakdown(user, start_date, end_date)` - Donut chart showing proportion of activity levels
* `plot_hourly_intensity(user, start_date, end_date)` - Line chart of activity intensity by hour
* `plot_daily_intensity_pie(user, start_date, end_date)` - Pie chart showing distribution of activity intensity
* `plot_daily_intensity_chart(user, selected_date)` - Detailed view of activity intensity for a specific day
* `plot_active_hours_heatmap(user, start_date, end_date)` - Heatmap visualization of active hours by day of week

#### Heart Rate Analysis
* `plot_heart_rate_trends(user, start_date, end_date)` - Line chart of heart rate patterns by hour
* `plot_heart_rate_zones(user, start_date, end_date)` - Pie chart showing time spent in different heart rate zones
* `plot_daily_heart_rate(user, selected_date)` - Detailed heart rate chart for a specific day

#### Sleep Analysis
* `plot_sleep_duration_trend(filtered_data, avg_sleep_duration)` - Generates interactive line chart showing daily sleep duration trends.
* `plot_sleep_stage_distribution(sleep_stage_data)` - Creates pie chart visualizing proportion of sleep stages.
* `plot_sleep_timeline(daily_stages, selected_date)` - Displays hourly sleep stages as Gantt-style timeline.

### User-specific Data Dashboard

This Streamlit dashboard provides personalized fitness insights for individual Fitbit users. It allows for detailed exploration of activity patterns, heart rate, sleep, calories, steps, and exercise intensity through interactive visualizations and metrics.

#### User Selection and Data Filtering
- User ID selection from dropdown menu
- Date range selection with appropriate validation
- Automatic filtering of data based on user selection and date range

#### User Profile Information
- Displays user category (Heavy, Moderate, or Light user)
- Shows latest weight and BMI measurements when available

#### Summary Metrics
Provides at-a-glance performance metrics for the selected time period:
- Average daily steps
- Average daily distance (km)
- Average daily calories burned
- Average daily active minutes
- Average daily sedentary minutes
- Average sleep duration (when available)

#### Interactive Dashboard Tabs

- Combined steps and calories visualization with comparison to overall average
- Activity breakdown by type (Very Active, Fairly Active, Lightly Active, Sedentary)
- Active hours heatmap showing patterns across days of the week

##### Heart Rate
- Hourly heart rate trend analysis
- Heart rate zone distribution (Rest, Active, Intense)
- Detailed daily heart rate analysis with:
  - Interactive date selection
  - Average, maximum, and resting heart rate metrics
  - Timeline visualization with highlighted active periods

##### Sleep Duration
- Sleep duration trend over the selected period
- Sleep stage distribution (Asleep, Restless, Awake)
- Daily sleep details with timeline visualization

##### Calories
- Hourly calorie burn patterns throughout the day
- Time-of-day calorie distribution (Morning, Afternoon, Evening, Night)
- Detailed daily calorie analysis with:
  - Total calories burned
  - Maximum hourly calorie burn
  - Peak calorie-burning hour

##### Steps
- Hourly step patterns throughout the day
- Time-of-day step distribution
- Detailed daily step analysis with:
  - Total steps
  - Maximum hourly steps
  - Most active hour

##### Intensity
- Hourly intensity patterns
- Intensity level distribution (Low, Medium, High)
- Detailed daily intensity analysis with average and peak metrics


