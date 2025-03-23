# IMPORTS 
import streamlit as st
import pandas as pd
import datetime
import part1
import part5
import plots_general_insights as plots

st.set_page_config(
    page_title="Fitbit Dashboard",
    page_icon="images/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.image("images/logo_title.png")
st.sidebar.markdown("<div style='margin: 25px 0px;'></div>", unsafe_allow_html=True)

st.sidebar.page_link("General_insights.py", label="General Analysis", icon=":material/analytics:")
st.sidebar.page_link("pages/1_User-specific_data.py", label="User-specific Analysis", icon=":material/person:")
st.sidebar.markdown("---")


with st.sidebar:
    user = st.selectbox(
        "Select a user",
        sorted(part1.data["Id"].unique()),
        index=None,
        placeholder="Select a user",
    )

    if user:
        st.session_state.user = user
        st.switch_page("pages/1_User-specific_data.py")

    start_date = st.date_input("Select a start date:", datetime.date(2016, 3, 12), min_value=datetime.date(year=2016, month=3, day=12), max_value=datetime.date(year=2016, month=4, day=12), format="MM/DD/YYYY")
    end_date = st.date_input("Select an end date:", datetime.date(2016, 4, 12), min_value=datetime.date(year=2016, month=3, day=12), max_value=datetime.date(year=2016, month=4, day=12), format="MM/DD/YYYY")

    if start_date and end_date:
        if start_date > end_date:
            st.error("Please ensure that the end date is later than the start date.")
        else:
            dates = pd.date_range(start_date, end_date, freq='d').strftime("%m/%d/%Y")
            
if start_date <= end_date:
    st.markdown("<h3 style='text-align: left; margin-top: -40px;'>Fitbit Data Analysis</h3>", unsafe_allow_html=True)
    # Row of average metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # Retrieve data
    steps = part5.retrieve_average("TotalSteps", dates)
    users = part5.retrieve_average("total_users", dates) 
    distance = part5.retrieve_average("TotalDistance", dates) 
    calories = part5.retrieve_average("Calories", dates) 
    active_minutes = part5.retrieve_average("ActiveMinutes", dates) 
    sedentary_minutes = part5.retrieve_average("SedentaryMinutes", dates) 

    # Display each metric
    plots.create_metric_block(col1, "Total Users", users, "")
    plots.create_metric_block(col2, "Average Steps", steps, "")
    plots.create_metric_block(col3, "Average Distance", distance, "km")
    plots.create_metric_block(col4, "Average Calories", calories, "kcal")
    plots.create_metric_block(col5, "Avr. Active Min", active_minutes, "")
    plots.create_metric_block(col6, "Avr. Sedentary Min", sedentary_minutes, "")

    st.markdown("</br>", unsafe_allow_html=True)
    tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Period", "Daily", "Weekly", "Sleep insights", "Weather insights", "Statistics", "Correlations", "Other"])

    # Period graphs
    with tab0:
        st.plotly_chart(plots.plot_steps_calories_combined_general(dates), use_container_width=True)

    # Daily graphs
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(plots.bar_chart_hourly_average_steps(dates), use_container_width=True)
        
        with col2:
            st.plotly_chart(plots.plot_heart_rate(dates), use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(plots.bar_chart_hourly_average_calories(dates), use_container_width=True)

        with col2:
            st.plotly_chart(plots.bar_chart_daily_intensity(dates), use_container_width=True)

        st.plotly_chart(plots.bar_chart_daily_sleep(dates), use_container_width=True)
    
    # Weekly graphs
    with tab2:
        col1, col2 = st.columns(2) 

        with col1:
            st.plotly_chart(plots.bar_chart_average_distance_per_week(dates), use_container_width=True)
        with col2:
            st.plotly_chart(plots.bar_chart_average_steps_per_week(dates), use_container_width=True)

        col1, col2 = st.columns(2)  

        with col1:
            st.plotly_chart(plots.bar_chart_average_calories_per_day_for_week(dates), use_container_width=True)
        
        with col2:
            st.plotly_chart(plots.bar_chart_weekly_sleep(dates), use_container_width=True)
            
        st.plotly_chart(plots.plot_active_minutes_bar_chart_per_day(dates), use_container_width=True)

    # Sleep insights
    with tab3:
        with st.popover("Correlation explained"):
                st.write("Correlation is a measure of how two variables are related to each other, with values ranging from -1 to 1. If the correlation is 1, it means the two variables move together perfectly in the same direction. If the correlation is -1, the variables move in exactly opposite directions. A correlation of 0 means there's no clear connection between them.")

        col1, col2 = st.columns(2)

        with col1:
            fig, corr = plots.plot_correlation_sleep_sedentary_minutes(dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.create_correlation_block("Correlation coefficient:", corr, "")

        with col2:
            fig, corr = plots.plot_correlation_sleep_active_minutes(dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.create_correlation_block("Correlation coefficient:", corr, "")
        
        col1, col2 = st.columns(2)

        with col1:
            fig, corr = plots.plot_correlation_sleep_steps(dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.create_correlation_block("Correlation coefficient:", corr, "")

        with col2:
            fig, corr = plots.plot_correlation_sleep_calories(dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.create_correlation_block("Correlation coefficient:", corr, "")
    
    # Weather insights
    with tab4:
        with st.popover("Correlation explained"):
            st.write("Correlation is a measure of how two variables are related to each other, with values ranging from -1 to 1. If the correlation is 1, it means the two variables move together perfectly in the same direction. If the correlation is -1, the variables move in exactly opposite directions. A correlation of 0 means there's no clear connection between them.")
          
        col1, col2 = st.columns(2)
        hour_selection = ["0-4", "4-8", "8-12", "12-16", "16-20", "20-24"]
        days_selection = ["Weekdays", "Weekend"]

        with col1:
            st.markdown("</br>", unsafe_allow_html=True)
            hours = st.segmented_control("Hours", hour_selection, key="Hours", default=["4-8", "8-12", "12-16", "16-20"], selection_mode="multi")
            days = st.pills("Time of the week", days_selection, key="Days", default=["Weekend"], selection_mode="multi")

            fig, corr = plots.plot_correlation_weather_steps(hours, days, dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.create_correlation_block("Correlation coefficient:", corr, "")

        with col2:
            st.markdown("</br>", unsafe_allow_html=True)
            hours2 = st.segmented_control("Hours", hour_selection, key="Hours2", default=["4-8", "8-12", "12-16", "16-20"], selection_mode="multi")
            days2 = st.pills("Time of the week", days_selection, key="Days2", default=["Weekend"], selection_mode="multi")

            fig, corr = plots.plot_correlation_weather_intensity(hours2, days2, dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.create_correlation_block("Correlation coefficient:", corr, "")

    # Statistics
    with tab5:
        col1, col2, col3 = st.columns([4, 5, 12])
        with col1:
            with st.popover("Median explained"):
                st.write("The median is the middle value of a dataset when it is ordered from smallest to largest.")
        with col2: 
            with st.popover("Upper quartile explained"):
                st.write("The upper quartile represents the value below which 75% of the data points fall. It is also known as the third quartile or 75th percentile.")
        
        with col3:
            with st.popover("Lower quartile explained"):
                st.write("The lower quartile represents the value below which 25% of the data points fall, and it is also called the first quartile or 25th percentile.")
        
        col1, col2, col3 = st.columns([2, 0.25, 2])

        with col1:
            fig, data = plots.plot_boxplot("TotalSteps", "Total Steps", dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.get_stats(data, "TotalSteps", 0, "steps")

        with col3:
            fig, data = plots.plot_boxplot("Calories", "Calories", dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.get_stats(data, "Calories", 0, "kcal")

        col1, col2, col3 = st.columns([2, 0.25, 2])

        with col1:
            fig, data = plots.plot_boxplot("TotalDistance", "Total Distance", dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.get_stats(data, "TotalDistance", 2, "km")

        with col3:
            fig, data = plots.plot_boxplot("TotalActiveMinutes", "Total Active Minutes", dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.get_stats(data, "TotalActiveMinutes", 0, "min")

        fig, data = plots.plot_boxplot("SedentaryMinutes", "Sedentary Minutes", dates)
        st.plotly_chart(fig, use_container_width=True)
        plots.get_stats(data, "SedentaryMinutes", 0, "min")
    
    # Correlations
    with tab6:
        with st.popover("Correlation explained"):
            st.write("Correlation is a measure of how two variables are related to each other, with values ranging from -1 to 1. If the correlation is 1, it means the two variables move together perfectly in the same direction. If the correlation is -1, the variables move in exactly opposite directions. A correlation of 0 means there's no clear connection between them.")
          
        col1, col2 = st.columns(2)
        with col1:
            fig, corr = plots.scatterplot_heart_rate_intensityvity(dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.create_correlation_block("Correlation coefficient:", corr, "")
        
        with col2:
            fig, corr = plots.scatterplot_calories_and_active_minutes(dates)
            st.plotly_chart(fig, use_container_width=True)
            plots.create_correlation_block("Correlation coefficient:", corr, "")

        st.plotly_chart(plots.plot_active_minutes_active_distance(dates), use_container_width=True)

    # Other insights
    with tab7:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(plots.plot_activity_pie_chart(dates), use_container_width=True)

        with col2:
            st.plotly_chart(plots.plot_weight_pie_chart(), use_container_width=True)
            plots.create_correlation_block("Note:<br>This graph is not affected by the specified date range.", "", "")

        col1, col2, = st.columns(2)

        with col1:
            st.plotly_chart(plots.plot_user_pie_chart(), use_container_width=True)
            plots.create_correlation_block("Note:<br>This graph is not affected by the specified date range.", "", "")

        with col2: 
            st.plotly_chart(plots.bar_chart_total_workout_frequency_for_period(dates), use_container_width=True)
            plots.create_correlation_block("Note:<br>This graph is not affected by the specified date range.", "", "")


