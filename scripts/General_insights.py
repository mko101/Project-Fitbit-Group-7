# IMPORTS 
import streamlit as st
import pandas as pd
import datetime
import part1
import plotly.express as px
import Part5 as part5

st.set_page_config(
    page_title="Fitbit Dashboard",
    page_icon="../images/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

col1, col2, col3, col4, col5, col6 = st.columns(6)

# Retrieve data
steps = part5.retrieve_average("TotalSteps", dates)
users = part5.retrieve_average("total_users", dates) 
distance = part5.retrieve_average("TotalDistance", dates) 
calories = part5.retrieve_average("Calories", dates) 
active_minutes = part5.retrieve_average("ActiveMinutes", dates) 
sedentary_minutes = part5.retrieve_average("SedentaryMinutes", dates) 

# Define a function for styled containers
def create_metric_block(col, title, value, unit="", bg_color="#CFEBEC"):
    with col:
        container = st.container()
        container.markdown(
            f"""
            <style>
            .metric-box {{
                background-color: {bg_color};
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            }}
            .metric-title {{
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .metric-value {{
                font-size: 22px;
                font-weight: bold;
                color: #333;
            }}
            </style>
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value} {unit}</div>
            </div>
            """,
            unsafe_allow_html=True  # This is needed for styling
        )

# Display each metric
create_metric_block(col1, "Total Users", users, "")
create_metric_block(col2, "Average Steps", steps, "")
create_metric_block(col3, "Average Distance", distance, "km")
create_metric_block(col4, "Average Calories", calories, "kcal")
create_metric_block(col5, "Avr. Active Min", active_minutes, "")
create_metric_block(col6, "Avr. Sedentary Min", sedentary_minutes, "")

def plot_activity_pie_chart(dates): 
    custom_colors = {
        "Very Active": "#005B8D",  
        "Fairly Active": "#006166", 
        "Lightly Active": "#00B3BD", 
        "Sedentary": "#CFEBEC"  
    }
    
    data = part5.activity_sum_data(dates)

    fig = px.pie(
        data, values='Minutes', names='Activity', 
        title="Average Activity Breakdown Per Day",
        hole=0.5, color='Activity', 
        color_discrete_map=custom_colors  
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal layout

        )   
    )
    
    fig.update_traces(
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Minutes: %{value:.0f}<extra></extra>"  
    )
    
    return fig

def hist_daily_average_steps(dates):
    hourly_data = part5.average_steps_per_hour(dates)

    # Identify top 3 most intensive hours
    top_hours = hourly_data.nlargest(3, "StepTotal")["Hour"].tolist()

    hourly_data["Color"] = hourly_data["Hour"].apply(lambda x: "#00B3BD" if x in top_hours else "#CFEBEC")
    hourly_data["HourFormatted"] = hourly_data["Hour"].astype(str) + ":00"

    # Plot histogram using Plotly
    fig = px.bar(
        hourly_data, 
        x="HourFormatted",
        y="StepTotal",
        title="Average Steps Per Hour",
        color="Color",
        color_discrete_map="identity",
        category_orders={"HourFormatted": [f"{h}:00" for h in sorted(hourly_data['Hour'].unique())]}  # Ensure correct order
    )

    # Customize layout
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            title = None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False,  
        bargap=0.2
    )

    fig.update_traces(
        hovertemplate="<b>Hour:</b> %{x}<br><b>Avg Steps:</b> %{y:.0f}<extra></extra>"
    )

    return fig

def plot_heart_rate(dates):

    heart_rate_data = part5.average_heart_rate_per_hour(dates)
    heart_rate_data['Hour'] = heart_rate_data['Hour'].astype(str) + ":00"

    fig = px.line(
        heart_rate_data, 
        x="Hour", 
        y="Value",
        title="Heart Rate Per Hour",
        labels={"Hour": "Hour of Day", "Value": "Avg Heart Rate (bpm)"},
        line_shape="spline",  # Smooth curve
        markers=True
    )

    # Format x-axis for better readability
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 6, 12, 18, 23],
            title = None
        ),
        yaxis=dict(
            title=None
        ),
        showlegend=False
    )

    fig.update_traces(line=dict(color="#00B3BD"))
    fig.update_traces(
        hovertemplate="<b>Hour:</b> %{x}<br><b>Avg Heart Rate:</b> %{y:.0f} bmp<extra></extra>"
    )

    return fig

col1, col2, col3 = st.columns([1, 1.5, 1.5])  

with col1:
    st.plotly_chart(plot_activity_pie_chart(dates), use_container_width=True)

with col2:
    st.plotly_chart(hist_daily_average_steps(dates), use_container_width=True)

with col3:
    st.plotly_chart(plot_heart_rate(dates), use_container_width=True)