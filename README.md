# Data Engineering Project: Analysing Fitbit Data

This project studies a dataset obtained from fitbits of 35 different respondence from amazon survey in 2016 that submited censored usage data. This library will provide tools to study various statistical analysis of the users.

Data file "daily_activity.csv" is csv and it contains information about ID of the user and Activity date, Total steps, Total distance, Step size, Tracker distance, Logged activities distance, Very active distance, Fairly active, Moderate active distance, Light active distance, Sedentary active distance, Very active minutes, Fairly active minutes, Lightly active minutes, Sedentary Minutes, Calories. 

Functions in part1: 
`calc_unique_graph_total_distance()` - prints the number of unique users and graphs the total distance over all active dates per user

`visualise_calories_burned(user_id, dates)` - displays a line graph that shows the calories burnt on each day based on a user_id and a list of dates

`frequency_day_barplot()` - display a bar plot that shows the frequency at which all individuals work out on each day of the week

`linear_regression_visualization(user_id)` - follows a linear regression model to investigate and display the relationship between the amount of steps taken and the amount of calories burnt based on input user_id

`plot_activity_pie_chart()` - visualizes the proportion of time spent in different activity levels (Very Active, Fairly Active, Lightly Active, and Sedentary) using a pie chart. It calculates the total minutes for each activity category and displays their relative distribution as percentages.

For the second part the "fitbit_database.db" is used. SHOULD ADD SOME DESCRIBTION

Functions in part2:
`create_new_dataframe()` - creates, displays, and returns a new DataFrame with two columns: "Id" (unique user IDs) and "Class" (user category: Heavy, Moderate, or Light). The classification is based on how frequently each user appears in the original CSV file "daily_activity.csv". The resulting DataFrame is sorted in descending order, from Heavy to Light users.

REMEMBER TO MENTION OUTLIERS of the data o steps 2000 calories