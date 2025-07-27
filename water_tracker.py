import streamlit as st
import datetime
import plotly.graph_objects as go
from pymongo.collection import Collection
import pandas as pd

# Helper to get water logs collection
def get_water_collection(db) -> Collection:
    return db['water_logs']

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

def water_tracker_page(db, username):
    st.header("💧 Water Intake Tracker")
    today = datetime.date.today()
    users = db['users']
    user = users.find_one({'username': username})

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
        get_water_collection(db).insert_one({
            'username': username,
            'date': today.isoformat(),
            'amount': amount,
            'timestamp': datetime.datetime.now()
        })
        st.success(f"Added {amount} ml to your log!")
        st.rerun()

    # Fetch today's logs
    logs = list(get_water_collection(db).find({'username': username, 'date': today.isoformat()}))
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
        log_df = pd.DataFrame([{ 'Time': log['timestamp'].strftime('%H:%M'), 'Amount (ml)': log['amount']} for log in logs])
        st.table(log_df)
        csv = log_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Today's Log as CSV", csv, file_name="water_log_today.csv", mime="text/csv")
    else:
        st.info("No water logged yet today.")

    # --- Streak Visualizations ---
    st.subheader("Water Intake Streaks")
    # Weekly streak: how many days in the last 7 did user meet their goal?
    last_7_days = [(today - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    streak_data = []
    for d in last_7_days:
        logs_day = list(get_water_collection(db).find({'username': username, 'date': d}))
        total_day = sum(log['amount'] for log in logs_day)
        streak_data.append(1 if total_day >= goal_ml else 0)
    streak_df = pd.DataFrame({"Date": last_7_days, "Goal Met": streak_data})
    fig_streak = go.Figure([go.Bar(x=streak_df['Date'], y=streak_df['Goal Met'], marker_color=["#4bb543" if v else "#ff4b4b" for v in streak_df['Goal Met']])])
    fig_streak.update_layout(title="Weekly Water Goal Streak", yaxis=dict(dtick=1, title="Goal Met (1=Yes, 0=No)"), xaxis_title="Date", margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_streak, use_container_width=True)

    # Per-day streak: show a colorful progress bar for today
    st.subheader("Today's Streak Progress")
    streak_color = "#4bb543" if total_ml >= goal_ml else ("#ffa500" if total_ml > 0 else "#e0e0e0")
    st.markdown(f'<div style="background-color:{streak_color};padding:1em;border-radius:8px;color:white;font-weight:bold;">{int(total_ml/goal_ml*100) if goal_ml else 0}% of your goal today</div>', unsafe_allow_html=True) 