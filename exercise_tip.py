import streamlit as st
import os
import requests
import datetime
import plotly.graph_objects as go
import pandas as pd
import re

GROQ_API_KEY ="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"
YOUTUBE_API_KEY = "AIzaSyCeH61WIIL85tMA5PrpeNKgIneHt5BA15o"

# -----------------------------
# YouTube Workout Video Fetcher
# -----------------------------
def get_youtube_workout_videos(workout_type, duration):
    search_queries = {
        "Full Body": f"full body workout {duration} minutes",
        "Cardio": f"cardio workout {duration} minutes",
        "Yoga": f"yoga workout {duration} minutes",
        "Strength": f"strength training workout {duration} minutes"
    }

    query = search_queries.get(workout_type, search_queries["Full Body"])
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': 3,
        'key': YOUTUBE_API_KEY,
        'videoDuration': 'medium',
        'videoCategoryId': '17'
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "title": item['snippet']['title'],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                }
                for item in data.get('items', [])
            ]
        else:
            st.error(f"YouTube API Error: {response.status_code}")
            return get_fallback_videos(workout_type, duration)
    except Exception as e:
        st.error(f"Error fetching YouTube videos: {str(e)}")
        return get_fallback_videos(workout_type, duration)

def get_fallback_videos(workout_type, duration):
    fallback = {
        "Full Body": [
            {"title": "Full Body Workout", "url": "https://youtu.be/4iy4yEKa7W8"},
            {"title": "Complete Full Body Routine", "url": "https://youtu.be/Y08OkdVO4Co"},
            {"title": "Total Body Burn", "url": "https://youtu.be/cbKkB3POqaY"}
        ],
        "Cardio": [
            {"title": "Cardio Blast", "url": "https://youtu.be/kZDvg92tTMc"},
            {"title": "High Intensity Cardio", "url": "https://youtu.be/9psH-BsJ_IM"},
            {"title": "Cardio Routine", "url": "https://youtu.be/cZyHgKtK75A"}
        ],
        "Yoga": [
            {"title": "Yoga Flow", "url": "https://youtu.be/CM43AZaRXNw"},
            {"title": "Morning Yoga", "url": "https://youtu.be/NJU8dcCacRY"},
            {"title": "Yoga for Beginners", "url": "https://youtu.be/Vu_NnDWxKY4"}
        ],
        "Strength": [
            {"title": "Strength Training", "url": "https://youtu.be/4iy4yEKa7W8"},
            {"title": "Weight Training", "url": "https://youtu.be/Y08OkdVO4Co"},
            {"title": "Strength Workout", "url": "https://youtu.be/cbKkB3POqaY"}
        ]
    }
    return fallback.get(workout_type, fallback["Full Body"])

def extract_youtube_id(url):
    match = re.search(r"(?:v=|be/|embed/)([\w-]{11})", url)
    return match.group(1) if match else None

# -----------------------------
# GROQ: Motivational Message
# -----------------------------
def get_motivational_quote(workout_type):
    if not GROQ_API_KEY:
        return "Set the GROQ_API_KEY environment variable to generate quotes."

    prompt = (
        f"Provide a short, powerful motivational quote for someone doing a {workout_type} workout. "
        f"It should be uplifting, around 20-30 words, and fitness-focused."
    )
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 80
    }

    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content']
            return content.strip()
        else:
            return f"Error: {resp.status_code} from GROQ API"
    except Exception as e:
        return f"Error: {str(e)}"

# -----------------------------
# Streamlit Page
# -----------------------------
def exercise_tip_page(username):
    st.header("🏋️ Exercise Tip")
    st.write("Get personalized workout tips powered by AI!")

    workout_type = st.selectbox("Workout type", ["Full Body", "Cardio", "Yoga", "Strength"])
    duration = st.slider("Duration (minutes)", 5, 90, 20, 5)

    if st.button("🎥 Get Video Recommendations"):
        with st.spinner("Searching for workout videos..."):
            videos = get_youtube_workout_videos(workout_type, duration)

        st.markdown("### 🔗 Recommended Videos")
        for video in videos:
            vid_id = extract_youtube_id(video['url'])
            if vid_id:
                st.video(f"https://www.youtube.com/watch?v={vid_id}")
                st.markdown(f"**{video['title']}**", unsafe_allow_html=True)
            else:
                st.markdown(f"[{video['title']}]({video['url']})")

    if st.button("💬 Inspire Me"):
        with st.spinner("Fetching motivational quote..."):
            quote = get_motivational_quote(workout_type)
        st.success("Here’s your motivational quote:")
        st.info(f"“{quote}”")

    # Optional Trend Display: Static Example for Visual Appeal
    st.subheader("📊 Sample Weekly Activity Chart")
    last_7_days = [(datetime.date.today() - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    sample_data = [1, 0, 1, 1, 0, 1, 1]
    df = pd.DataFrame({"Date": last_7_days, "Workout": sample_data})
    fig = go.Figure([go.Scatter(x=df['Date'], y=df['Workout'], mode='lines+markers', line=dict(color='green'))])
    fig.update_layout(title="Sample Workout Pattern", xaxis_title="Date", yaxis=dict(dtick=1, title="Workout Done"))
    st.plotly_chart(fig, use_container_width=True)
