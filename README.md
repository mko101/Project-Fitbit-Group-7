# Data Engineering Project: Analysing Fitbit Data

This project studies a dataset obtained from fitbits of 35 different respondence from amazon survey in 2016 that submited censored usage data. This library will provide tools to study various statistical analysis of the users.

Data file "daily_activity.csv" is csv and it contains information about ID of the user and Activity date, Total steps, Total distance, Step size, Tracker distance, Logged activities distance, Very active distance, Fairly active, Moderate active distance, Light active distance, Sedentary active distance, Very active minutes, Fairly active minutes, Lightly active minutes, Sedentary Minutes, Calories. 

## Part 1: Getting acquinted with the data
Functions: `calc_unique_graph_total_distance()` - prints the number of unique users and graphs the total distance over all active dates per user

`visualise_calories_burned(user_id, dates)` - displays a line graph that shows the calories burnt on each day based on a user_id and a list of dates

`frequency_day_barplot()` - displays a bar plot that shows the frequency at which all individuals work out on each day of the week

`linear_regression_visualization(user_id)` - follows a linear regression model to investigate and display the relationship between the amount of steps taken and the amount of calories burnt based on input user_id

`plot_activity_pie_chart()` - visualizes the proportion of time spent in different activity levels (Very Active, Fairly Active, Lightly Active, and Sedentary) using a pie chart. It calculates the total minutes for each activity category and displays their relative distribution as percentages.

`make_correlation_heatmap()` - visualizes the correlation between all numerical columns of the dataset in a heatmap

`describe_columns(user_id)` - describes the count, mean, standard deviation, minimum, 25% quantile, 50% quantile, 75% quantile and maximum of each column based on a user_id. Pass None as an argument to get the description of all users.

REMEMBER TO MENTION OUTLIERS of the data o steps 2000 calories

For the second part the "fitbit_database.db" is used. SHOULD ADD SOME DESCRIPTION

## Part 3: Interacting with the database
Functions: `create_new_dataframe()` - creates, displays, and returns a new DataFrame with two columns: "Id" (unique user IDs) and "Class" (user category: Heavy, Moderate, or Light). The classification is based on how frequently each user appears in the original CSV file "daily_activity.csv". The resulting DataFrame is sorted in descending order, from Heavy to Light users.

`run_analysis(data_type)` - This function takes paramater "steps" or "calories" and verifies its data by retrieving daily and hourly records, merging them, and comparing total daily values with summed hourly values (in `get_verified_data(data_type)`). It identifies matches and mismatches, calculates statistics like match percentage and absolute differences (in `calculate_statistics(merged_df, label, total_column, value_column)`), and visualizes the results through pie, bar, and line charts (in `plot_graphs(merged_df, label)`).

`compute_sleep_duration(user_id)` - computes the duration of each moment of sleep of a specific user, where the total sleep duration is calculated as the time the user wakes up minus the time the user goes to sleep

`compare_activity_and_sleep(user_id)` - calculates the total active minutes as the sum of the very active, fairly active and light active minutes on a day and then preforms a regression based on the minutes the user is asleep on that day.