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

...

### part1
Script `part1.py` contains functions that help explore the `daily_activity.csv` dataset with computations and visualizations.
* `calc_unique_graph_total_distance()` - prints the number of unique users and graphs the total distance over all active dates per user.
* `visualise_calories_burned(user_id, dates)` - displays a line graph that shows the calories burnt on each day based on a `user_id` and a list of dates.
* `frequency_day_barplot()` - display a bar plot that shows the frequency (in percentage) at which all individuals work out on each day of the week.
* `linear_regression_visualization(user_id)` - follows a linear regression model to investigate and display the relationship between the amount of steps taken and the amount of calories burnt based on input `user_id`.
* `calories_totalsteps_scatter()` - display a scatter plot that graphs the relationship between total daily steps and the calories burnt, also comparing with the median of both.
* `calories_totalhours_scatter()` - displays a scatter plot that graphs the relationship between total hours recorded and calories burnt, with the median of both.
* `make_correlation_heatmap()` - ...
* `describe_columns(user_id)` - ...
* `plot_activity_pie_chart()` - visualizes the proportion of time spent in different activity levels (Very Active, Fairly Active, Lightly Active, and Sedentary) using a pie chart. It calculates the total minutes for each activity category and displays their relative distribution as percentages.


REMEMBER TO MENTION OUTLIERS of the data o steps 2000 calories

### part3

...