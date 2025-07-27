import streamlit as st
import datetime
import plotly.graph_objects as go
import sqlite3
import pandas as pd

# Database file path
DB_PATH = 'nutri_app.db'

def init_water_table():
    """Initialize water_logs table in SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create water_logs table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS water_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            amount INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get SQLite database connection"""
    return sqlite3.connect(DB_PATH)

# Hydration goal recommender based on user input
def recommend_goal(weight_kg, height_cm, activity, goal_type):
    # Base: 35ml per kg
    base = weight_kg * 35
    # Adjust for activity
    if activity == 'Low':
        base *= 1.0
    elif activity == 'Moderate':
        base *= 1.15
    elif activity == 'High':
        base *= 1.3
    # Adjust for weight loss
    if goal_type == 'Weight Loss':
        base *= 1.1
    elif goal_type == 'Maintenance':
        base *= 1.0
    elif goal_type == 'Muscle Gain':
        base *= 1.05
    # Height can be a minor factor
    if height_cm > 180:
        base += 200
    elif height_cm < 160:
        base -= 100
    return int(base)

# Hydration advisor
def hydration_advice(total_ml, goal_ml):
    percent = total_ml / goal_ml * 100
    if percent < 50:
        return "You need to drink more water! Aim for at least half your goal by now.", "#ff4b4b"
    elif percent < 100:
        return "Good progress! Keep sipping to reach your goal.", "#ffa500"
    else:
        return "Great job! You've met your hydration goal.", "#4bb543"

def add_water_log(username, amount):
    """Add water log to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        today = datetime.date.today().isoformat()
        cursor.execute(
            'INSERT INTO water_logs (username, date, amount) VALUES (?, ?, ?)',
            (username, today, amount)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding water log: {e}")
        return False

def get_today_logs(username):
    """Get today's water logs for user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        today = datetime.date.today().isoformat()
        cursor.execute(
            'SELECT amount, timestamp FROM water_logs WHERE username = ? AND date = ? ORDER BY timestamp',
            (username, today)
        )
        
        logs = cursor.fetchall()
        conn.close()
        
        return [{'amount': log[0], 'timestamp': log[1]} for log in logs]
    except Exception as e:
        print(f"Error getting water logs: {e}")
        return []

def get_weekly_logs(username):
    """Get weekly water logs for user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get logs for the last 7 days
        week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        cursor.execute(
            'SELECT date, SUM(amount) as total FROM water_logs WHERE username = ? AND date >= ? GROUP BY date ORDER BY date',
            (username, week_ago)
        )
        
        logs = cursor.fetchall()
        conn.close()
        
        return [{'date': log[0], 'total': log[1]} for log in logs]
    except Exception as e:
        print(f"Error getting weekly logs: {e}")
        return []

def water_tracker_page(username):
    st.header("💧 Water Intake Tracker")
    
    # Initialize water table
    init_water_table()
    
    st.subheader("Hydration Recommender")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        weight_kg = st.number_input("Weight (kg)", min_value=20, max_value=200, value=70, step=1)
    with col2:
        height_cm = st.number_input("Height (cm)", min_value=120, max_value=220, value=170, step=1)
    with col3:
        activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
    with col4:
        goal_type = st.selectbox("Goal", ["Maintenance", "Weight Loss", "Muscle Gain"])
    
    goal_ml = recommend_goal(weight_kg, height_cm, activity, goal_type)
    st.markdown(f"**Your personalized daily water goal:** {goal_ml} ml")

    # Log water intake
    st.subheader("Log your water intake")
    amount = st.number_input("Amount (ml)", min_value=50, max_value=2000, value=250, step=50)
    if st.button("Add Water Log"):
        if add_water_log(username, amount):
            st.success(f"Added {amount} ml to your log!")
            st.rerun()
        else:
            st.error("Failed to add water log. Please try again.")

    # Fetch today's logs
    logs = get_today_logs(username)
    total_ml = sum(log['amount'] for log in logs)
    st.markdown(f"### Total today: **{total_ml} ml**")

    # Donut chart
    fig = go.Figure(data=[
        go.Pie(
            labels=["Drank", "Remaining"],
            values=[total_ml, max(goal_ml - total_ml, 0)],
            hole=0.6,
            marker_colors=["#4bb543", "#e0e0e0"]
        )
    ])
    fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

    # Hydration advisor
    advice, color = hydration_advice(total_ml, goal_ml)
    st.markdown(f'<div style="background-color:{color};padding:1em;border-radius:8px;color:white;font-weight:bold;">{advice}</div>', unsafe_allow_html=True)

    # Show log history
    st.subheader("Today's Water Log")
    if logs:
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['time'] = df['timestamp'].dt.strftime('%H:%M')
        st.dataframe(df[['time', 'amount']].rename(columns={'time': 'Time', 'amount': 'Amount (ml)'}), use_container_width=True)
    else:
        st.info("No water logs for today yet. Start drinking water!")

    # Weekly progress
    st.subheader("Weekly Progress")
    weekly_logs = get_weekly_logs(username)
    if weekly_logs:
        weekly_df = pd.DataFrame(weekly_logs)
        weekly_df['date'] = pd.to_datetime(weekly_df['date'])
        weekly_df['day'] = weekly_df['date'].dt.strftime('%a')
        
        fig_weekly = go.Figure(data=[
            go.Bar(
                x=weekly_df['day'],
                y=weekly_df['total'],
                marker_color='#4bb543'
            )
        ])
        fig_weekly.update_layout(
            title="Water Intake This Week",
            xaxis_title="Day",
            yaxis_title="Total (ml)",
            showlegend=False
        )
        st.plotly_chart(fig_weekly, use_container_width=True)
    else:
        st.info("No weekly data available yet.") 