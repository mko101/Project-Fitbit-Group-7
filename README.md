# Data Engineering Project: Analysing Fitbit Data

This project studies a dataset obtained from fitbits of 35 different respondence from amazon survey in 2016 that submited censored usage data. This library will provide tools to study various statistical analysis of the users.

Data file is csv and it contains information about ID of the user and Activity date, Total steps, Total distance, Step size, Tracker distance, Logged activities distance, Very active distance, Fairly active, Moderate active distance, Light active distance, Sedentary active distance, Very active minutes, Fairly active minutes, Lightly active minutes, Sedentary Minutes, Calories. 

Functions: 
`calc_unique_graph_total_distance()` - prints the number of unique users and graphs the total distance over all active dates per user

`visualise_calories_burned(user_id, dates)` - displays a line graph that shows the calories burnt on each day based on a user_id and a list of dates

`frequency_day_barplot()` - display a bar plot that shows the frequency at which all individuals work out on each day of the week

`linear_regression_visualization(user_id)` - follows a linear regression model to investigate and display the relationship between the amount of steps taken and the amount of calories burnt based on input user_id

plot_activity_pie_chart() - visualizes the proportion of time spent in different activity levels (Very Active, Fairly Active, Lightly Active, and Sedentary) using a pie chart. It calculates the total minutes for each activity category and displays their relative distribution as percentages.


REMEMBER TO MENTION OUTLIERS of the data o steps 2000 calories