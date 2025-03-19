# IMPORTS
import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
import datetime
import part1
import part3
import part4
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Fitbit Dashboard",
    page_icon="../images/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "user" not in st.session_state:
    st.session_state.user = None

with st.sidebar:
    st.header("User Selection")
    user_sidebar = st.selectbox(
        "Select a user from the sidebar",
        sorted(part1.data["Id"].unique()),
        index=sorted(part1.data["Id"].unique()).index(st.session_state.user) if st.session_state.user else None,
        placeholder="Select a user",
        key="user_sidebar"
    )

    if user_sidebar != st.session_state.user:
        st.session_state.user = user_sidebar
        st.rerun()

    start_date = st.date_input(
        "Select a start date:", 
        datetime.date(2016, 3, 12), 
        min_value=datetime.date(2016, 3, 12), 
        max_value=datetime.date(2016, 4, 12)
    )
    
    end_date = st.date_input(
        "Select an end date:", 
        datetime.date(2016, 4, 12), 
        min_value=datetime.date(2016, 3, 12), 
        max_value=datetime.date(2016, 4, 12)
    )

if st.session_state.user:
    st.markdown(f"<h1 style='text-align: center; color: #005B8D;'>📊 User Analysis - {st.session_state.user}</h1>", 
                unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #005B8D;'>📊 User Analysis</h1>", unsafe_allow_html=True)

selected_user_main = st.selectbox(
    "Select a user from the dropdown",
    sorted(part1.data["Id"].unique()),
    index=sorted(part1.data["Id"].unique()).index(st.session_state.user) if st.session_state.user else None,
    key="user_dropdown_main"
)

if selected_user_main != st.session_state.user:
    st.session_state.user = selected_user_main
    st.rerun()

if st.session_state.user:
    user = st.session_state.user
    
    user_data = part1.data[part1.data["Id"] == user].copy()
    user_data.loc[:, "ActivityDate"] = pd.to_datetime(user_data["ActivityDate"], format="%Y-%m-%d")
    
    # Fetch and merge sleep data
    sleep_data = part3.compute_sleep_duration(user)
    sleep_data.rename(columns={"MinutesSlept": "TotalSleepMinutes"}, inplace=True)
    sleep_data["TotalSleepHours"] = sleep_data["TotalSleepMinutes"] / 60
    sleep_data["Date"] = pd.to_datetime(sleep_data["Date"], errors="coerce")
    
    filtered_data = user_data.merge(sleep_data, left_on="ActivityDate", right_on="Date", how="left")
    filtered_data = filtered_data[
        (filtered_data["ActivityDate"] >= pd.Timestamp(start_date)) & 
        (filtered_data["ActivityDate"] <= pd.Timestamp(end_date))
    ]
    
    if not filtered_data.empty:
        # Summary metrics
        avg_steps = int(filtered_data["TotalSteps"].mean()) 
        avg_distance = round(filtered_data["TotalDistance"].mean(), 3)
        avg_calories = int(filtered_data["Calories"].mean())
        
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Average Steps", value=avg_steps)
        col2.metric(label="Average Distance (km)", value=avg_distance)
        col3.metric(label="Average Calories Burned", value=avg_calories)
        
        # Main tabs
        tab1, tab2, tab3 = st.tabs(["Daily Steps", "Calories Burned", "Sleep Duration"])
        
        # Tab 1: Daily Steps
        with tab1:
            st.subheader("Daily Steps")
            fig_steps = px.bar(filtered_data, x="ActivityDate", y="TotalSteps", title="Daily Steps")
            st.plotly_chart(fig_steps, use_container_width=True)
        
        # Tab 2: Calories Burned
        with tab2:
            st.subheader("Calories Burned Per Day")
            fig_calories = px.bar(filtered_data, x="ActivityDate", y="Calories", 
                                title="Calories Burned Per Day")
            st.plotly_chart(fig_calories, use_container_width=True)
        
        # Tab 3: Sleep Analysis
        with tab3:
            st.subheader("Sleep Analysis")
            
            # Initialize variables
            avg_sleep = None
            sleep_efficiency = None
            bedtimes = None

            # 1. Total Sleep Duration
            if "TotalSleepHours" in filtered_data.columns and not filtered_data["TotalSleepHours"].isna().all():
                avg_sleep = filtered_data["TotalSleepHours"].mean()
                
                # Sleep Quality Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Sleep Hours", f"{avg_sleep:.1f} hrs")
                
                with col2:
                    if "TotalTimeInBed" in sleep_data.columns:
                        sleep_efficiency = (filtered_data["TotalSleepMinutes"] / 
                                          filtered_data["TotalTimeInBed"]).mean() * 100
                        st.metric("Sleep Efficiency", f"{sleep_efficiency:.1f}%")
                
                with col3:
                    try:
                        if 'intervals' in locals():
                            bedtimes = intervals.groupby('Night')['Start'].min().dt.time
                            avg_bedtime = bedtimes.mean().strftime("%H:%M")
                            st.metric("Average Bedtime", avg_bedtime)
                    except Exception as e:
                        pass
                
                # Sleep Duration Chart
                fig_sleep = px.bar(
                    filtered_data, 
                    x="ActivityDate", 
                    y="TotalSleepHours", 
                    title="Total Sleep Duration Over Time",
                    labels={"TotalSleepHours": "Hours Slept"}
                )
                st.plotly_chart(fig_sleep, use_container_width=True)

            # 2. Detailed Sleep Analysis
            conn = sqlite3.connect("../data/fitbit_database.db")
            query = f"SELECT date, value FROM minute_sleep WHERE Id = {user} ORDER BY date;"
            sleep_stage_data = pd.read_sql(query, conn)
            conn.close()

            if not sleep_stage_data.empty:
                # Data processing
                sleep_stage_data["date"] = pd.to_datetime(sleep_stage_data["date"]).dt.floor("min")
                sleep_stage_data = sleep_stage_data[
                    (sleep_stage_data["date"] >= pd.Timestamp(start_date)) &
                    (sleep_stage_data["date"] < pd.Timestamp(end_date) + pd.Timedelta(days=1))
                ]

                stage_map = {1: "Asleep", 2: "Restless", 3: "Awake"}
                sleep_stage_data["Stage"] = sleep_stage_data["value"].map(stage_map)

                # 3. Daily Sleep Breakdown
                st.subheader("Daily Sleep Stages")
                daily_agg = sleep_stage_data.groupby(
                    [pd.Grouper(key='date', freq='D'), 'Stage']
                ).size().reset_index(name='Minutes')
                daily_agg['Hours'] = daily_agg['Minutes'] / 60

                fig_stacked = px.bar(
                    daily_agg,
                    x="date",
                    y="Hours",
                    color="Stage",
                    title="Daily Sleep Stage Distribution",
                    labels={"date": "Date", "Hours": "Hours"},
                    color_discrete_map={
                        "Asleep": "#005B8D",
                        "Restless": "#0083BD", 
                        "Awake": "#CFEBEC"
                    },
                    barmode="stack"
                )
                st.plotly_chart(fig_stacked, use_container_width=True)

                # 4. Nightly Analysis
                st.subheader("Nightly Details")
                
                # Process intervals
                sleep_stage_data["time_diff"] = sleep_stage_data["date"].diff().dt.total_seconds() != 60
                sleep_stage_data["interval_group"] = sleep_stage_data.groupby("Stage")["time_diff"].cumsum()

                intervals = sleep_stage_data.groupby(["interval_group", "Stage"]).agg(
                    Start=("date", "min"),
                    End=("date", "max")
                ).reset_index()

                intervals["Duration"] = (intervals["End"] - intervals["Start"]).dt.total_seconds() / 60
                intervals["Night"] = intervals.apply(
                    lambda x: x["Start"].date() if x["Start"].hour >= 18 
                    else x["Start"].date() - pd.Timedelta(days=1), 
                    axis=1
                )

                # Night selection
                col1, col2 = st.columns([2, 1])
                with col1:
                    night_options = intervals["Night"].unique()
                    selected_night = st.selectbox(
                        "Select Night",
                        sorted(night_options, reverse=True),
                        format_func=lambda x: x.strftime("%Y-%m-%d")
                    )
                
                night_data = intervals[intervals["Night"] == selected_night]

                if not night_data.empty:
                    # Visualizations
                    viz_col1, viz_col2 = st.columns(2)
                    
                    with viz_col1:
                        fig_timeline = px.timeline(
                            night_data,
                            x_start="Start",
                            x_end="End",
                            y=[1]*len(night_data),
                            color="Stage",
                            color_discrete_map={
                                "Asleep": "#005B8D",
                                "Restless": "#0083BD",
                                "Awake": "#CFEBEC"
                            },
                            title=f"Sleep Stages for {selected_night.strftime('%b %d')}",
                            labels={"Stage": "Sleep Phase"}
                        )
                        fig_timeline.update_layout(
                            height=300,
                            xaxis_title="Time",
                            yaxis=dict(showticklabels=False),
                            xaxis=dict(tickformat="%H:%M")
                        )
                        st.plotly_chart(fig_timeline, use_container_width=True)

                    with viz_col2:
                        stage_dist = night_data.groupby("Stage")["Duration"].sum().reset_index()
                        fig_pie = px.pie(
                            stage_dist,
                            values="Duration",
                            names="Stage",
                            title="Sleep Stage Distribution",
                            color="Stage",
                            color_discrete_map={
                                "Asleep": "#005B8D",
                                "Restless": "#0083BD",
                                "Awake": "#CFEBEC"
                            }
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)

                    # Insights
                    st.subheader("Sleep Insights")
                    restless_time = stage_dist[stage_dist["Stage"] == "Restless"]["Duration"].sum()
                    
                    if restless_time > 60:
                        st.warning(f"🌙 Try reducing screen time before bed - {restless_time:.0f} mins restless")
                    
                    if avg_sleep and avg_sleep < 7:
                        st.info(f"💤 Aim for 7-9 hours - current average: {avg_sleep:.1f} hrs")
                    
                    try:
                        if sleep_efficiency:
                            sleep_score = min(100, int((avg_sleep/8)*40 + (sleep_efficiency/100)*60))
                            st.success(f"🏆 Sleep Score: {sleep_score}/100")
                    except:
                        pass

                    # Advanced Metrics
                    with st.expander("📈 Advanced Sleep Metrics"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**Sleep Patterns**")
                            try:
                                if not sleep_stage_data.empty:
                                    restless_episodes = sleep_stage_data[sleep_stage_data['Stage'] == 'Restless'].shape[0]
                                    st.metric("Daily Restless Episodes", f"{restless_episodes} times")
                            except:
                                pass
                        
                        with col2:
                            st.write("**Consistency**")
                            try:
                                if avg_sleep is not None:
                                    sleep_std = filtered_data["TotalSleepHours"].std()
                                    st.metric("Sleep Variability", f"{sleep_std:.1f} hrs")
                            except:
                                pass
                        
                        with col3:
                            st.write("**Activity Correlation**")
                            try:
                                if not filtered_data.empty:
                                    sleep_activity_corr = filtered_data[["TotalSleepHours", "TotalSteps"]].corr().iloc[0,1]
                                    st.metric("Sleep-Steps Correlation", f"{sleep_activity_corr:.2f}")
                            except:
                                pass