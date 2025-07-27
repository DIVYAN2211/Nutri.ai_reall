import streamlit as st
import os
import requests
import datetime
import plotly.graph_objects as go

GROQ_API_KEY ="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"
YOUTUBE_API_KEY = "AIzaSyCeH61WIIL85tMA5PrpeNKgIneHt5BA15o"

# Helper: Get workout videos using YouTube API
def get_youtube_workout_videos(workout_type, duration):
    """Get workout videos using YouTube API search"""
    
    # Search queries for each workout type
    search_queries = {
        "Full Body": f"full body workout {duration} minutes",
        "Cardio": f"cardio workout {duration} minutes",
        "Yoga": f"yoga workout {duration} minutes",
        "Strength": f"strength training workout {duration} minutes"
    }
    
    query = search_queries.get(workout_type, search_queries["Full Body"])
    
    # YouTube API search endpoint
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': 3,
        'key': YOUTUBE_API_KEY,
        'videoDuration': 'medium',  # 4-20 minutes
        'videoCategoryId': '17'  # Sports category
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                videos.append({
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })
            
            return videos
        else:
            st.error(f"YouTube API Error: {response.status_code}")
            return get_fallback_videos(workout_type, duration)
            
    except Exception as e:
        st.error(f"Error fetching YouTube videos: {str(e)}")
        return get_fallback_videos(workout_type, duration)

def get_fallback_videos(workout_type, duration):
    """Fallback videos if YouTube API fails"""
    workout_videos = {
        "Full Body": [
            {"title": f"Full Body Workout - {duration} Min", "url": "https://youtu.be/4iy4yEKa7W8?si=I4ualKc1cs5OgDhM"},
            {"title": f"Complete Full Body Routine - {duration} Min", "url": "https://youtu.be/Y08OkdVO4Co?si=IgaIOZPisww75GGw"},
            {"title": f"Full Body Training Session - {duration} Min", "url": "https://youtu.be/cbKkB3POqaY?si=NglNAb1bk5lcAvbW"}
        ],
        "Cardio": [
            {"title": f"Cardio Workout - {duration} Min", "url": "https://youtu.be/kZDvg92tTMc?si=C7z3s8Z9p80zLtQR"},
            {"title": f"High Intensity Cardio - {duration} Min", "url": "https://youtu.be/9psH-BsJ_IM?si=dFBQzu3BA5knYgQ_"},
            {"title": f"Cardio Training Session - {duration} Min", "url": "https://youtu.be/cZyHgKtK75A?si=wt-bN3sH5azoogGb"}
        ],
        "Yoga": [
            {"title": f"Yoga Flow - {duration} Min", "url": "https://youtu.be/CM43AZaRXNw?si=RBa7hWytCh3qbQwP"},
            {"title": f"Morning Yoga Routine - {duration} Min", "url": "https://youtu.be/NJU8dcCacRY?si=smH_evd5sFEf-ULC"},
            {"title": f"Yoga for Beginners - {duration} Min", "url": "https://youtu.be/Vu_NnDWxKY4?si=_tjb5Wul1Xsehufb"}
        ],
        "Strength": [
            {"title": f"Strength Training - {duration} Min", "url": "https://youtu.be/4iy4yEKa7W8?si=I4ualKc1cs5OgDhM"},
            {"title": f"Weight Training Session - {duration} Min", "url": "https://youtu.be/Y08OkdVO4Co?si=IgaIOZPisww75GGw"},
            {"title": f"Strength Building Workout - {duration} Min", "url": "https://youtu.be/cbKkB3POqaY?si=NglNAb1bk5lcAvbW"}
        ]
    }
    
    return workout_videos.get(workout_type, workout_videos["Full Body"])

# Legacy function for GROQ API (kept for compatibility)
def get_workout_videos(workout_type, duration):
    """Get workout videos using YouTube API"""
    return get_youtube_workout_videos(workout_type, duration)

def groq_workout_recommendations(workout_type, duration):
    # Check if API key is available
    if not GROQ_API_KEY:
        return [{"title": "API key not configured. Please set GROQ_API_KEY environment variable.", "url": "#"}]
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        f"Generate 3 popular {workout_type} workout videos for {duration} minutes. "
        "For each video, provide a title and a valid YouTube video ID (11 characters). "
        "Use this real workout video ID that is guaranteed to work: 'ml6cTmdAZ2Y'. "
        "Return as JSON array with 'title' and 'video_id' keys."
    )
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 512
    }
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:
            return [{"title": "API key invalid or expired. Please check your GROQ_API_KEY.", "url": "#"}]
        elif resp.status_code != 200:
            return [{"title": f"API Error: {resp.status_code} - {resp.text}", "url": "#"}]
        
        result = resp.json()
        if 'choices' not in result or not result['choices']:
            return [{"title": "API Error: No choices in response", "url": "#"}]
        
        import re, json as pyjson
        text = result['choices'][0]['message']['content']
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                videos = pyjson.loads(match.group(0))
                if isinstance(videos, list) and len(videos) > 0:
                    # Convert video_id to full URL
                    for video in videos:
                        if 'video_id' in video:
                            video['url'] = f"https://www.youtube.com/watch?v={video['video_id']}"
                            del video['video_id']
                    return videos
            except:
                pass
        
        # Fallback: use YouTube API
        return get_youtube_workout_videos(workout_type, duration)
    except Exception as e:
        # Fallback: use YouTube API
        return get_youtube_workout_videos(workout_type, duration)

def extract_youtube_id(url):
    import re
    match = re.search(r"(?:v=|be/|embed/)([\w-]{11})", url)
    return match.group(1) if match else None

def exercise_tip_page(username):
    st.header("🏋️ Exercise Tip")
    st.write("Get personalized workout tips and track your streak!")
    workout_type = st.selectbox("Workout type", ["Full Body", "Cardio", "Yoga", "Strength"])
    duration = st.slider("Duration (minutes)", 5, 90, 20, 5)
    if st.button("Get Video Recommendations"):
        with st.spinner("Searching for workout videos..."):
            videos = get_youtube_workout_videos(workout_type, duration)
        st.markdown("<h2 style='color:white;'>Recommended Videos:</h2>", unsafe_allow_html=True)
        for v in videos:
            vid_id = extract_youtube_id(v['url'])
            if vid_id:
                st.video(f"https://www.youtube.com/watch?v={vid_id}")
                st.markdown(f"<div style='margin-bottom:1em;'><b>{v['title']}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"[{v['title']}]({v['url']})")
        st.info("After you complete a workout, mark it below to track your streak!")

    # Daily streak tracking
    today = datetime.date.today().isoformat()
    streak_col = db['exercise_streaks']
    streak = streak_col.find_one({'username': username})
    if not streak:
        streak = {'username': username, 'dates': []}
    if st.button("I completed my workout today!"):
        if today not in streak['dates']:
            streak['dates'].append(today)
            streak_col.update_one({'username': username}, {'$set': {'dates': streak['dates']}}, upsert=True)
            st.success("Streak updated!")
        else:
            st.info("You already marked today!")
    st.subheader("Your Daily Streak:")
    st.markdown(f"**{len(streak['dates'])} days**")
    st.progress(min(len(streak['dates']) % 7 / 7, 1.0))
    if streak['dates']:
        st.write("Dates:", ', '.join(streak['dates']))

    # Weekly streak visualization (trend analysis)
    st.subheader("Weekly Workout Trend")
    import pandas as pd
    last_7_days = [(datetime.date.today() - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    streak_set = set(streak['dates'])
    streak_counts = [1 if d in streak_set else 0 for d in last_7_days]
    df = pd.DataFrame({"Date": last_7_days, "Completed": streak_counts})
    fig = go.Figure([go.Scatter(x=df['Date'], y=df['Completed'], mode='lines+markers', line=dict(color='green'))])
    fig.update_layout(title="Workouts Completed in Last 7 Days", xaxis_title="Date", yaxis_title="Completed (1=Yes, 0=No)", yaxis=dict(dtick=1))
    st.plotly_chart(fig, use_container_width=True) 
