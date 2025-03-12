import streamlit as st
import dashboardFunctions as dF
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(
    page_title = "title",
    layout = "wide",
    initial_sidebar_state = "expanded"
    )

# Streamlit date inputs
# start_date = st.date_input("Select a start date:", datetime.date(2016, 3, 12),
#                            min_value=datetime.date(2016, 3, 12),
#                            max_value=datetime.date(2016, 4, 12))

# end_date = st.date_input("Select an end date:", datetime.date(2016, 4, 12),
#                          min_value=datetime.date(2016, 3, 12),
#                          max_value=datetime.date(2016, 4, 12))


col1, col2, col3, col4, col5, col6 = st.columns(6)

# Retrieve data
steps = dF.retrieve_average("TotalSteps", ["3/25/2016", "3/26/2016", "3/27/2016", "3/28/2016", "3/29/2016"])
users = dF.retrieve_average("total_users", ["3/25/2016", "3/26/2016", "3/27/2016", "3/28/2016", "3/29/2016"]) 
distance = dF.retrieve_average("TotalDistance", ["3/25/2016", "3/26/2016", "3/27/2016", "3/28/2016", "3/29/2016"]) 
calories = dF.retrieve_average("Calories", ["3/25/2016", "3/26/2016", "3/27/2016", "3/28/2016", "3/29/2016"]) 
active_minutes = dF.retrieve_average("ActiveMinutes", ["3/25/2016", "3/26/2016", "3/27/2016", "3/28/2016", "3/29/2016"]) 
sedentary_minutes = dF.retrieve_average("SedentaryMinutes", ["3/25/2016", "3/26/2016", "3/27/2016", "3/28/2016", "3/29/2016"]) 

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

def plot_activity_pie_chart(date): 
    custom_colors = {
        "Very Active": "#005B8D",  
        "Fairly Active": "#006166", 
        "Lightly Active": "#00B3BD", 
        "Sedentary": "#CFEBEC"  
    }
    
    data = dF.activity_sum_data(date)

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
    hourly_data = dF.average_steps_per_hour(dates)

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

    heart_rate_data = dF.average_heart_rate_per_hour(dates)
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
    st.plotly_chart(plot_activity_pie_chart(["4/4/2016", "4/5/2016", "4/6/2016"]), use_container_width=True)

with col2:
    st.plotly_chart(hist_daily_average_steps(["4/4/2016", "4/5/2016", "4/6/2016"]), use_container_width=True)

with col3:
    st.plotly_chart(plot_heart_rate(["4/4/2016", "4/5/2016", "4/6/2016"]), use_container_width=True)