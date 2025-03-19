# IMPORTS
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3
import datetime
import part1
import part3
import General_insights as gi
import user_graphing_function as ugf

st.set_page_config(
    page_title="Fitbit Dashboard",
    page_icon="../images/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_latest_weight_data(user):
    conn = sqlite3.connect('../data/fitbit_database.db')
    
    query = f"""
    SELECT WeightKg, BMI, Date
    FROM weight_log
    WHERE Id = '{user}'
    """
    
    cur = conn.cursor()
    cur.execute(query)
    result_rows = cur.fetchall()
    conn.close()
    
    if result_rows:
        result_df = pd.DataFrame(result_rows, columns=['WeightKg', 'BMI', 'Date'])
        result_df['Date'] = pd.to_datetime(result_df['Date'], errors='coerce')
        
        result_df = result_df.sort_values(by='Date', ascending=False)
        
        if not result_df.empty:
            latest_date = result_df['Date'].iloc[0]
            formatted_date = latest_date.strftime("%m/%d/%y")
            return result_df['WeightKg'].iloc[0], result_df['BMI'].iloc[0], formatted_date
    
    return None, None, None

with st.sidebar:
    if "start_date" not in st.session_state or "end_date" not in st.session_state:
        st.session_state.start_date = datetime.date(2016, 3, 12)
        st.session_state.end_date = datetime.date(2016, 4, 12)
    if "user" not in st.session_state:
        st.session_state.user = None
        
    user_sidebar = st.selectbox(
        "Select a user",
        sorted(part1.data["Id"].unique()),
        index=sorted(part1.data["Id"].unique()).index(st.session_state.user) if st.session_state.user else None,
        placeholder="Select a user",
        key="user_sidebar"
    )

    if user_sidebar != st.session_state.user:
        st.session_state.user = user_sidebar
        st.rerun()
        
    if st.session_state.user:
        # Get user category
        user_category_df = part3.create_new_dataframe()
        user_category = user_category_df.loc[user_category_df["Id"] == st.session_state.user, "Class"].iloc[0] if st.session_state.user in user_category_df["Id"].values else "Unknown"
        
        # Get latest weight data
        latest_weight, latest_bmi, latest_date = get_latest_weight_data(st.session_state.user)
        
        st.markdown(
            """
            <style>
            .sidebar-metric {
                background-color: #CFEBEC;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
                text-align: center;
            }
            .metric-label {
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 3px;
            }
            .metric-value {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
            .metric-date {
                font-size: 11px;
                color: #555;
                margin-top: 2px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Display User Category
        st.markdown(
            f"""
            <div class="sidebar-metric">
                <div class="metric-label">User Category</div>
                <div class="metric-value">{user_category}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if latest_weight:
            st.markdown(
                f"""
                <div class="sidebar-metric">
                    <div class="metric-label">Weight</div>
                    <div class="metric-value">{round(latest_weight, 1)} kg</div>
                    <div class="metric-date">{latest_date}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="sidebar-metric">
                    <div class="metric-label">Weight</div>
                    <div class="metric-value">Not Available</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        if latest_bmi:
            st.markdown(
                f"""
                <div class="sidebar-metric">
                    <div class="metric-label">BMI</div>
                    <div class="metric-value">{round(latest_bmi, 1)}</div>
                    <div class="metric-date">{latest_date}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="sidebar-metric">
                    <div class="metric-label">BMI</div>
                    <div class="metric-value">Not Available</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("<br>", unsafe_allow_html=True)

    start_date = st.date_input(
        "Select a start date:", 
        value=datetime.date(2016, 3, 12),
        min_value=datetime.date(2016, 3, 12), 
        max_value=datetime.date(2016, 4, 12),
        key = "start_date"
    )
    
    end_date = st.date_input(
        "Select an end date:", 
        value=datetime.date(2016, 4, 12),
        min_value=datetime.date(2016, 3, 12), 
        max_value=datetime.date(2016, 4, 12),
        key = "end_date"
    )
    
    if start_date > end_date:
        st.error("Please ensure that the end date is later than the start date.")
    else:
        dates = pd.date_range(start_date, end_date, freq='d').strftime("%m/%d/%Y")


if not st.session_state.user:
    st.markdown(
        """
        <div style="background-color: #CFEBEC; 
        padding: 10px; 
        border-radius: 5px; 
        text-align: center;">
            <span style="color: #333; font-size: 16pt; font-weight: bold;">
                Please select a user ID from the sidebar.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()


if st.session_state.user and start_date < end_date:
    user = st.session_state.user
    
    user_data = part1.data[part1.data["Id"] == user].copy()
    user_data.loc[:, "ActivityDate"] = pd.to_datetime(user_data["ActivityDate"], format="%Y-%m-%d")
    
    user_category_df = part3.create_new_dataframe()
    
    sleep_data = part3.compute_sleep_duration(user)
    sleep_data.rename(columns={"MinutesSlept": "TotalSleepMinutes"}, inplace=True)
    sleep_data["TotalSleepHours"] = sleep_data["TotalSleepMinutes"] / 60
    sleep_data["Date"] = pd.to_datetime(sleep_data["Date"], errors="coerce")
    
    # Merge sleep duration into user_data based on date
    filtered_data = user_data.merge(sleep_data, left_on="ActivityDate", right_on="Date", how="left")
    
    # Filter data based on selected date range
    filtered_data = filtered_data[(filtered_data["ActivityDate"] >= pd.Timestamp(start_date)) & (filtered_data["ActivityDate"] <= pd.Timestamp(end_date))]
    
    if not filtered_data.empty:
        # Summary
        avg_steps = int(filtered_data["TotalSteps"].mean()) 
        avg_distance = round(filtered_data["TotalDistance"].mean(), 3)
        avg_calories = int(filtered_data["Calories"].mean())
        avg_active_min = int((filtered_data["VeryActiveMinutes"] + filtered_data["FairlyActiveMinutes"] + filtered_data["LightlyActiveMinutes"]).mean())
        avg_sedentary_min = int(filtered_data["SedentaryMinutes"].mean())
        avg_sleep_duration = round(filtered_data["TotalSleepHours"].mean(), 2)
        
        columns = [st.columns(5) if np.isnan(avg_sleep_duration) else st.columns(6)][0]
        
        gi.create_metric_block(columns[0], "Avr. Steps", avg_steps, "")
        gi.create_metric_block(columns[1], "Avr. Distance", avg_distance, "km")
        gi.create_metric_block(columns[2], "Avr. Calories", avg_calories, "kcal")
        gi.create_metric_block(columns[3], "Avr. Active Min", avg_active_min, "")
        gi.create_metric_block(columns[4], "Avr. Sedentary Min", avg_sedentary_min, "")
        if not np.isnan(avg_sleep_duration):
            gi.create_metric_block(columns[5], "Avr. Sleep Duration", avg_sleep_duration, "h")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(
            """
            <style>
            /* Change the default red line to turquoise */
            .stTabs [data-baseweb="tab-list"] [data-baseweb="tab-highlight"] {
                background-color: #00B3BD !important;
            }
            
            /* Style for the active tab button - just the text color */
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                color: #00B3BD;
                font-weight: bold;
            }
            
            /* Style for the inactive tab buttons */
            .stTabs [data-baseweb="tab-list"] button[aria-selected="false"] {
                color: #333;
                font-weight: normal;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overviews", "Heart Rate", "Sleep Duration", "Calories", "Steps", "Intensity"])

        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_combined = ugf.plot_steps_calories_combined(user, start_date, end_date)
                if fig_combined:
                    st.plotly_chart(fig_combined, use_container_width=True)
                else:
                    st.warning("No data available for the selected date range.")

            with col2:
                # # Display daily calories chart
                # fig_calories = ugf.plot_daily_calories(user, start_date, end_date)
                # if fig_calories:
                #     st.plotly_chart(fig_calories, use_container_width=True)
                # else:
                #     st.warning("No calorie data available for the selected date range.")
                fig_activity = ugf.plot_activity_breakdown(user, start_date, end_date)
                if fig_activity:
                    st.plotly_chart(fig_activity, use_container_width=True)
                else:
                    st.warning("No activity data available for the selected date range.")
            
        # Tab 2: Heart Rate
        with tab2:
            # First check if heart rate data is available
            hr_data = ugf.get_heart_rate_data(user, start_date, end_date)
            hr_data_available = len(hr_data) > 0
            
            if hr_data_available:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_hr_trends = ugf.plot_heart_rate_trends(user, start_date, end_date)
                    st.plotly_chart(fig_hr_trends, use_container_width=True)
                
                with col2:
                    fig_hr_zones = ugf.plot_heart_rate_zones(user, start_date, end_date)
                    st.plotly_chart(fig_hr_zones, use_container_width=True)
                
                st.markdown("<hr>", unsafe_allow_html=True)
                
                st.markdown("""
                    <h4 style="color: #333; margin-bottom: 10px;">
                        Heart Rate for Selected Day
                    </h4>
                """, unsafe_allow_html=True)
                
                with st.container():
                    available_dates = sorted(hr_data['Date'].unique())
                    
                    if available_dates:
                        select_col, metrics_col1, metrics_col2, metrics_col3 = st.columns([2, 1, 1, 1])
                        
                        with select_col:
                            min_date = min(available_dates) if available_dates else pd.Timestamp("2016-03-12").date()
                            max_date = max(available_dates) if available_dates else pd.Timestamp("2016-04-12").date()
                            default_date = min_date
                            selected_date = st.date_input(
                                "Select a date to view detailed heart rate data:",
                                value=default_date,
                                min_value=min_date,
                                max_value=max_date,
                                key="heart_rate_date"
                            )
                        
                        daily_hr_data = ugf.get_heart_rate_for_day(user, selected_date)
                        
                        if not daily_hr_data.empty:
                            avg_hr = int(daily_hr_data['Value'].mean())
                            max_hr = int(daily_hr_data['Value'].max())
                            resting_hr = int(daily_hr_data['Value'].quantile(0.05))
                            
                            with metrics_col1:
                                st.metric("Average HR", f"{avg_hr} bpm")
                            
                            with metrics_col2:
                                st.metric("Max HR", f"{max_hr} bpm")
                            
                            with metrics_col3:
                                st.metric("Resting HR", f"{resting_hr} bpm")
                            
                            fig_daily_hr = ugf.plot_daily_heart_rate(user, selected_date)
                            st.plotly_chart(fig_daily_hr, use_container_width=True)
                            
                            st.markdown("""
                            <div style="background-color: #CFEBEC; padding: 10px; border-radius: 5px;">
                                <p style="margin: 0; color: #333;">
                                    <b>Notes:</b> The line shows your heart rate throughout the day. 
                                    Blue shaded areas indicate periods of elevated heart rate.
                                    Dashed lines show your resting, average, and peak heart rates for the day.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(f"No heart rate data available for {selected_date}.")
                    else:
                        st.warning("No heart rate data available for any specific day in the selected date range.")
            else:
                # Single styled warning message
                st.markdown(
                    """
                    <div style="background-color: #CFEBEC; 
                    padding: 20px; 
                    border-radius: 5px; 
                    text-align: center;
                    margin: 50px 0;">
                        <span style="color: #333; font-size: 16pt; font-weight: bold;">
                            No heart rate data available for the selected date range.
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Tab 3: Sleep Duration
        with tab3:
            fig_sleep = ugf.plot_sleep_duration(user, start_date, end_date)
            if fig_sleep:
                st.plotly_chart(fig_sleep, use_container_width=True)
            else:
                st.warning("No sleep data available for the selected date range.")
        
        # Tab 4: Calories
        with tab4:
            calories_data = ugf.get_hourly_calories_data(user, start_date, end_date)
            calories_data_available = not calories_data.empty
            
            if calories_data_available:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_calories_trends = ugf.plot_hourly_calories(user, start_date, end_date)
                    st.plotly_chart(fig_calories_trends, use_container_width=True)
                
                with col2:
                    fig_calories_pie = ugf.plot_daily_calories_pie(user, start_date, end_date)
                    st.plotly_chart(fig_calories_pie, use_container_width=True)
                
                st.markdown("<hr>", unsafe_allow_html=True)
                
                st.markdown("""
                    <h4 style="color: #333; margin-bottom: 10px;">
                        Calories Burned for Selected Day
                    </h4>
                """, unsafe_allow_html=True)
                
                with st.container():
                    available_dates = sorted(calories_data['Date'].unique())
                    
                    if available_dates:
                        select_col, metrics_col1, metrics_col2, metrics_col3 = st.columns([2, 1, 1, 1])
                        
                        with select_col:
                            min_date = min(available_dates) if available_dates else pd.Timestamp("2016-03-12").date()
                            max_date = max(available_dates) if available_dates else pd.Timestamp("2016-04-12").date()
                            default_date = min_date
                            
                            selected_date = st.date_input(
                                "Select a date to view detailed calories data:",
                                value=default_date,
                                min_value=min_date,
                                max_value=max_date,
                                key="calories_date"
                            )
                        
                        fig_daily_calories, total_calories, max_calories, max_hour = ugf.plot_daily_calories_chart(user, selected_date)
                        
                        if fig_daily_calories:
                            with metrics_col1:
                                st.metric("Total Calories", f"{int(total_calories)}")
                            
                            with metrics_col2:
                                st.metric("Max Calories (Hour)", f"{int(max_calories)}")
                            
                            with metrics_col3:
                                st.metric("Peak Hour", f"{max_hour}")
                            
                            st.plotly_chart(fig_daily_calories, use_container_width=True)
                            
                            st.markdown("""
                            <div style="background-color: #CFEBEC; padding: 10px; border-radius: 5px;">
                                <p style="margin: 0; color: #333;">
                                    <b>Notes:</b> The line shows your calorie burn throughout the day. 
                                    Blue shaded areas indicate periods of elevated calorie burn.
                                    Dashed lines show your average and peak calorie burn for the day.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(f"No calories data available for {selected_date}.")
                    else:
                        st.warning("No calories data available for any specific day in the selected date range.")
            else:
                # Single styled warning message
                st.markdown(
                    """
                    <div style="background-color: #CFEBEC; 
                    padding: 20px; 
                    border-radius: 5px; 
                    text-align: center;
                    margin: 50px 0;">
                        <span style="color: #333; font-size: 16pt; font-weight: bold;">
                            No calories data available for the selected date range.
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        # Tab 5: Steps
        with tab5:
            steps_data = ugf.get_hourly_steps_data(user, start_date, end_date)
            steps_data_available = not steps_data.empty
            
            if steps_data_available:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_steps_trends = ugf.plot_hourly_steps(user, start_date, end_date)
                    st.plotly_chart(fig_steps_trends, use_container_width=True)
                
                with col2:
                    fig_steps_pie = ugf.plot_daily_steps_pie(user, start_date, end_date)
                    st.plotly_chart(fig_steps_pie, use_container_width=True)
                
                st.markdown("<hr>", unsafe_allow_html=True)
                
                st.markdown("""
                    <h4 style="color: #333; margin-bottom: 10px;">
                        Steps for Selected Day
                    </h4>
                """, unsafe_allow_html=True)
                
                with st.container():
                    available_dates = sorted(steps_data['Date'].unique())
                    
                    if available_dates:
                        select_col, metrics_col1, metrics_col2, metrics_col3 = st.columns([2, 1, 1, 1])
                        
                        with select_col:
                            min_date = min(available_dates) if available_dates else pd.Timestamp("2016-03-12").date()
                            max_date = max(available_dates) if available_dates else pd.Timestamp("2016-04-12").date()
                            default_date = min_date
                            
                            selected_date = st.date_input(
                                "Select a date to view detailed steps data:",
                                value=default_date,
                                min_value=min_date,
                                max_value=max_date,
                                key="steps_date"
                            )
                        
                        fig_daily_steps, total_steps, max_steps, max_hour = ugf.plot_daily_steps_chart(user, selected_date)
                        
                        if fig_daily_steps:
                            with metrics_col1:
                                st.metric("Total Steps", f"{int(total_steps):,}")
                            
                            with metrics_col2:
                                st.metric("Max Steps (Hour)", f"{int(max_steps):,}")
                            
                            with metrics_col3:
                                st.metric("Most Active Hour", f"{max_hour}")
                            
                            st.plotly_chart(fig_daily_steps, use_container_width=True)
                            
                            st.markdown("""
                            <div style="background-color: #CFEBEC; padding: 10px; border-radius: 5px;">
                                <p style="margin: 0; color: #333;">
                                    <b>Notes:</b> The line shows your steps throughout the day. 
                                    Blue shaded areas indicate periods of higher activity.
                                    Dashed lines show your average and peak step counts for the day.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(f"No steps data available for {selected_date}.")
                    else:
                        st.warning("No steps data available for any specific day in the selected date range.")
            else:
                # Single styled warning message
                st.markdown(
                    """
                    <div style="background-color: #CFEBEC; 
                    padding: 20px; 
                    border-radius: 5px; 
                    text-align: center;
                    margin: 50px 0;">
                        <span style="color: #333; font-size: 16pt; font-weight: bold;">
                            No steps data available for the selected date range.
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        # Tab 6: Intensity
        with tab6:
            intensity_data = ugf.get_hourly_intensity_data(user, start_date, end_date)
            intensity_data_available = not intensity_data.empty
            
            if intensity_data_available:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_intensity_trends = ugf.plot_hourly_intensity(user, start_date, end_date)
                    st.plotly_chart(fig_intensity_trends, use_container_width=True)
                
                with col2:
                    fig_intensity_pie = ugf.plot_daily_intensity_pie(user, start_date, end_date)
                    st.plotly_chart(fig_intensity_pie, use_container_width=True)
                
                st.markdown("<hr>", unsafe_allow_html=True)
                
                st.markdown("""
                    <h4 style="color: #333; margin-bottom: 10px;">
                        Activity Intensity for Selected Day
                    </h4>
                """, unsafe_allow_html=True)
                
                with st.container():
                    available_dates = sorted(intensity_data['Date'].unique())
                    
                    if available_dates:
                        select_col, metrics_col1, metrics_col2, metrics_col3 = st.columns([2, 1, 1, 1])
                        
                        with select_col:
                            min_date = min(available_dates) if available_dates else pd.Timestamp("2016-03-12").date()
                            max_date = max(available_dates) if available_dates else pd.Timestamp("2016-04-12").date()
                            default_date = min_date
                            
                            selected_date = st.date_input(
                                "Select a date to view detailed intensity data:",
                                value=default_date,
                                min_value=min_date,
                                max_value=max_date,
                                key="intensity_date"
                            )
                        
                        fig_daily_intensity, avg_intensity, max_intensity, max_hour = ugf.plot_daily_intensity_chart(user, selected_date)
                        
                        if fig_daily_intensity:
                            with metrics_col1:
                                st.metric("Avg Intensity", f"{avg_intensity:.3f}")
                            
                            with metrics_col2:
                                st.metric("Max Intensity", f"{max_intensity:.3f}")
                            
                            with metrics_col3:
                                st.metric("Peak Hour", f"{max_hour}")
                            
                            st.plotly_chart(fig_daily_intensity, use_container_width=True)
                    
                    st.markdown("""
                    <div style="background-color: #CFEBEC; padding: 10px; border-radius: 5px;">
                        <p style="margin: 0; color: #333;">
                            <b>Notes:</b> The line shows your activity intensity throughout the day. 
                            Blue shaded areas indicate periods of higher intensity activity.
                            Dashed lines show your average and peak intensity levels for the day.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)