import streamlit as st
import os
import requests
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

GROQ_API_KEY = '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'

def groq_health_answer(question):
    # Check if API key is available
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Provide basic fallback health tips
        question_lower = question.lower()
        
        # Basic health tips for common questions
        health_tips = {
            "weight": "Maintain a balanced diet with regular exercise. Focus on whole foods and portion control.",
            "diet": "Eat a variety of fruits, vegetables, lean proteins, and whole grains. Stay hydrated.",
            "exercise": "Aim for 150 minutes of moderate exercise per week. Include both cardio and strength training.",
            "sleep": "Get 7-9 hours of sleep per night. Maintain a consistent sleep schedule.",
            "stress": "Practice mindfulness, deep breathing, and regular physical activity to manage stress.",
            "water": "Drink 8-10 glasses of water daily. More if you're active or in hot weather.",
            "nutrition": "Focus on whole, unprocessed foods. Include protein, healthy fats, and complex carbohydrates.",
            "fitness": "Start with 30 minutes of daily activity. Gradually increase intensity and duration.",
            "health": "Regular check-ups, balanced diet, exercise, and adequate sleep are key to good health."
        }
        
        # Find matching tips
        answer = "Here are some general health tips:"
        tips = []
        
        for keyword, tip in health_tips.items():
            if keyword in question_lower:
                answer = tip
                tips = [
                    "Consult with a healthcare professional for personalized advice",
                    "Make gradual changes to your lifestyle",
                    "Track your progress to stay motivated"
                ]
                break
        
        if not tips:
            answer = "For personalized health advice, please consult with a healthcare professional."
            tips = [
                "Get regular check-ups",
                "Maintain a balanced diet",
                "Exercise regularly",
                "Get adequate sleep",
                "Manage stress effectively"
            ]
        
        return answer, tips, "Basic health advice (get GROQ API key for personalized AI responses)"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"Answer this health/nutrition/fitness question in a friendly, practical way. "
        f"Also provide 3-5 actionable tips as a JSON list.\nQuestion: {question}"
    )
    data = {"model": "llama3-70b-8192", "messages": [{"role": "system", "content": prompt}], "max_tokens": 512}
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:
            return "API key invalid or expired. Please check your GROQ_API_KEY.", [], "Authentication failed"
        elif resp.status_code != 200:
            return f"API Error: {resp.status_code} - {resp.text}", [], resp.text
        
        result = resp.json()
        if 'choices' not in result or not result['choices']:
            return f"API Error: No choices in response", [], str(result)
        
        text = result['choices'][0]['message']['content']
        # Extract tips JSON
        tips_match = re.search(r'\[.*\]', text, re.DOTALL)
        tips = []
        if tips_match:
            try:
                import json as pyjson
                tips = pyjson.loads(tips_match.group(0))
            except:
                tips = []
        
        # Remove tips from answer
        answer = text.split('\n[')[0].strip()
        return answer, tips, text
    except Exception as e:
        return f"Error: {str(e)}", [], str(e)

def ai_health_assistant_page(username):
    st.markdown("""
        <style>
        .ai-header { color: #1a1a1a !important; font-size: 2em; font-weight: bold; margin-bottom: 0.2em; }
        .ai-desc { color: #222 !important; font-size: 1.1em; margin-bottom: 1em; }
        .ai-answer-card { background: #f6f8fa; color: #1a4d2e; border-radius: 10px; padding: 1em; margin-bottom: 1em; font-size: 1.1em; }
        .ai-tips-card { background: #e0f7fa; color: #222; border-radius: 10px; padding: 1em; margin-bottom: 1em; font-size: 1.05em; }
        .ai-tip-item { color: #3a6ea5; font-weight: bold; margin-bottom: 0.5em; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="ai-header">🤖 AI Health Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="ai-desc">Ask any health, nutrition, or fitness question and get AI-powered answers and tips.</div>', unsafe_allow_html=True)
    question = st.text_input("Your question", key="ai_health_question_input")
    if st.button("Ask AI") and question:
        with st.spinner("Thinking..."):
            answer, tips, raw = groq_health_answer(question)
        st.success("AI Answer:")
        st.markdown(f'<div class="ai-answer-card">{answer}</div>', unsafe_allow_html=True)
        # Only show tips if they are valid strings
        tips_list = []
        if tips and isinstance(tips, list):
            for tip in tips:
                if isinstance(tip, dict):
                    tip_text = tip.get('tip') or next(iter(tip.values()), None)
                else:
                    tip_text = tip
                if isinstance(tip_text, str) and tip_text.strip().lower() != 'undefined' and tip_text.strip():
                    tips_list.append(tip_text.strip())
        if tips_list:
            st.subheader("Actionable Tips")
            st.markdown('<div class="ai-tips-card">', unsafe_allow_html=True)
            for tip_text in tips_list:
                st.markdown(f'<div class="ai-tip-item">- {tip_text}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            # Word cloud of tips
            tips_text = ' '.join(tips_list)
            wc = WordCloud(width=800, height=300, background_color='white').generate(tips_text)
            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("No actionable tips found. Try rephrasing your question for more specific advice.")
        st.expander("Show LLM response").write(raw) 
