import streamlit as st
import os
from dotenv import load_dotenv
from auth_sqlite import register_user, login_user, get_user_info
from water_tracker_sqlite import water_tracker_page
from nutrition_analyzer import nutrition_analyzer_page
from exercise_tip import exercise_tip_page
from medicine_dashboard import medicine_dashboard_page
from hospital_finder import hospital_finder_page
from ai_health_assistant import ai_health_assistant_page
from diet_planner import diet_planner_page
from ai_meal_planner import ai_meal_planner_page

# Load environment variables
load_dotenv()
PROJECT_NAME = os.getenv('PROJECT_NAME', 'nutri.ai')

# Page config
st.set_page_config(page_title=PROJECT_NAME, layout="wide")

# Custom backgrounds for each page
PAGE_BACKGROUNDS = {
    'auth': 'linear-gradient(135deg, #f8ffae 0%, #43c6ac 100%)',
    'dashboard': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'water_tracker': 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
    'nutrition_analyzer': 'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)',
    'prescription_reader': 'linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%)',
    'exercise_tip': 'linear-gradient(135deg, #f7971e 0%, #ffd200 100%)',
}

# Set background for current page
def set_background(page):
    bg = PAGE_BACKGROUNDS.get(page, '#fff')
    st.markdown(f"""
        <style>
        .stApp {{
            background: {bg} !important;
            background-attachment: fixed;
        }}
        .sidebar .sidebar-content {{
            background: rgba(255,255,255,0.7);
        }}
        </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state['page'] = 'auth'

set_background(st.session_state['page'])

# Sidebar branding and user info
# You can change the logo by replacing this URL with your preferred image
import os

image_path = os.path.join("assets", "image.png")
st.sidebar.image(image_path, width=75)
st.sidebar.title("Consistency!!!")

# Routing scaffold
PAGES = {
    "Login/Register": "auth",
    "Water Intake Tracker": "water_tracker",
    "Nutrition Analyzer": "nutrition_analyzer",
    "Exercise Tip": "exercise_tip",
    "AI Medicine Dashboard": "medicine_dashboard",
    "Nearby Hospitals": "hospital_finder",
    "AI Health Assistant": "ai_health_assistant",
    "AI Diet Planner": "diet_planner",
    "AI Meal Planner": "ai_meal_planner"
}

# Restore sidebar radio for tool selection
page = st.sidebar.radio("Go to", list(PAGES.keys()), index=0)
st.session_state['page'] = PAGES[page]

# Helper: login/register form

def auth_page():
    st.header("Login or Register")
    mode = st.radio("Select mode", ["Login", "Register"])
    username = st.text_input("Username")
    if mode == "Register":
        email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.button(mode)
    if submit:
        if mode == "Register":
            if register_user(username, email, password):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists.")
        else:
            if login_user(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

# Helper: sidebar user info

def sidebar_user_info():
    if st.session_state.get('logged_in'):
        user = get_user_info(st.session_state['username'])
        st.sidebar.markdown(f"**User:** {user['username']}")
        if user.get('email'):
            st.sidebar.markdown(f"**Email:** {user['email']}")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

# Main app logic
sidebar_user_info()

if not st.session_state.get('logged_in'):
    auth_page()
else:
    # After login, show only welcome message and user info. No tool selection buttons.
    st.header("Welcome to nutri.ai!")
    st.write("Use the sidebar to navigate between features.")
    # Do not show tool selection buttons or columns.
    # Render selected tool page
    if st.session_state['page'] == 'water_tracker':
        water_tracker_page(st.session_state['username'])
    elif st.session_state['page'] == 'nutrition_analyzer':
        nutrition_analyzer_page(st.session_state['username'])
    elif st.session_state['page'] == 'exercise_tip':
        exercise_tip_page(st.session_state['username'])
    elif st.session_state['page'] == 'medicine_dashboard':
        medicine_dashboard_page(st.session_state['username'])
    elif st.session_state['page'] == 'hospital_finder':
        hospital_finder_page(st.session_state['username'])
    elif st.session_state['page'] == 'ai_health_assistant':
        ai_health_assistant_page(st.session_state['username'])
    elif st.session_state['page'] == 'diet_planner':
        diet_planner_page(st.session_state['username'])
    elif st.session_state['page'] == 'ai_meal_planner':
        ai_meal_planner_page(st.session_state['username']) 
