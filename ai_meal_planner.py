import streamlit as st
import os
import requests
import plotly.graph_objects as go
# from fpdf import FPDF  # No longer needed
import io

GROQ_API_KEY ="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"

# Helper: Use GROQ Llama3 to generate a meal plan
def groq_generate_meal_plan(profile, period='daily'):
    # Check if API key is available
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        fallback = {
            "meals": [
                {"meal": "breakfast", "foods": "Oatmeal with fruit, 1 boiled egg", "calories": 350, "protein": 15, "carbs": 50, "fat": 8, "fiber": 6, "health_score": 85},
                {"meal": "lunch", "foods": "Grilled chicken, brown rice, steamed veggies", "calories": 500, "protein": 35, "carbs": 60, "fat": 10, "fiber": 8, "health_score": 90},
                {"meal": "dinner", "foods": "Fish curry, chapathi, salad", "calories": 450, "protein": 30, "carbs": 55, "fat": 9, "fiber": 7, "health_score": 88}
            ],
            "shopping_list": ["Oatmeal", "Eggs", "Fruit", "Chicken", "Brown rice", "Vegetables", "Fish", "Chapathi", "Salad ingredients"],
            "ai_tips": ["API key not configured. Please set GROQ_API_KEY environment variable. This is a generic healthy meal plan."]
        }
        return fallback, "No API key"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"Given this user profile: {profile}, generate a {period} meal plan (breakfast, lunch, dinner, snacks) with food items, calories, macros, and a health score for each meal. "
        "If you cannot generate a fully customized plan due to medical conditions or missing info, return a safe, generic healthy meal plan and include a warning in ai_tips. "
        "Always return a valid JSON object with keys: meals (list of dicts with meal, foods, calories, protein, carbs, fat, fiber, health_score), shopping_list (list), ai_tips (list)."
    )
    data = {"model": "llama3-70b-8192", "messages": [{"role": "system", "content": prompt}], "max_tokens": 1024}
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:
            # Return fallback plan with error
            fallback = {
                "meals": [
                    {"meal": "breakfast", "foods": "Oatmeal with fruit, 1 boiled egg", "calories": 350, "protein": 15, "carbs": 50, "fat": 8, "fiber": 6, "health_score": 85},
                    {"meal": "lunch", "foods": "Grilled chicken, brown rice, steamed veggies", "calories": 500, "protein": 35, "carbs": 60, "fat": 10, "fiber": 8, "health_score": 90},
                    {"meal": "dinner", "foods": "Fish curry, chapathi, salad", "calories": 450, "protein": 30, "carbs": 55, "fat": 9, "fiber": 7, "health_score": 88}
                ],
                "shopping_list": ["Oatmeal", "Eggs", "Fruit", "Chicken", "Brown rice", "Vegetables", "Fish", "Chapathi", "Salad ingredients"],
                "ai_tips": ["API key invalid or expired. Please check your GROQ_API_KEY. This is a generic healthy meal plan."]
            }
            return fallback, "Authentication failed"
        elif resp.status_code != 200:
            # Return fallback plan with error
            fallback = {
                "meals": [
                    {"meal": "breakfast", "foods": "Oatmeal with fruit, 1 boiled egg", "calories": 350, "protein": 15, "carbs": 50, "fat": 8, "fiber": 6, "health_score": 85},
                    {"meal": "lunch", "foods": "Grilled chicken, brown rice, steamed veggies", "calories": 500, "protein": 35, "carbs": 60, "fat": 10, "fiber": 8, "health_score": 90},
                    {"meal": "dinner", "foods": "Fish curry, chapathi, salad", "calories": 450, "protein": 30, "carbs": 55, "fat": 9, "fiber": 7, "health_score": 88}
                ],
                "shopping_list": ["Oatmeal", "Eggs", "Fruit", "Chicken", "Brown rice", "Vegetables", "Fish", "Chapathi", "Salad ingredients"],
                "ai_tips": [f"API Error: {resp.status_code}. This is a generic healthy meal plan. For specific medical conditions, consult your doctor."]
            }
            return fallback, f"API Error: {resp.status_code} - {resp.text}"
        
        result = resp.json()
        if 'choices' not in result or not result['choices']:
            # Return fallback plan with error
            fallback = {
                "meals": [
                    {"meal": "breakfast", "foods": "Oatmeal with fruit, 1 boiled egg", "calories": 350, "protein": 15, "carbs": 50, "fat": 8, "fiber": 6, "health_score": 85},
                    {"meal": "lunch", "foods": "Grilled chicken, brown rice, steamed veggies", "calories": 500, "protein": 35, "carbs": 60, "fat": 10, "fiber": 8, "health_score": 90},
                    {"meal": "dinner", "foods": "Fish curry, chapathi, salad", "calories": 450, "protein": 30, "carbs": 55, "fat": 9, "fiber": 7, "health_score": 88}
                ],
                "shopping_list": ["Oatmeal", "Eggs", "Fruit", "Chicken", "Brown rice", "Vegetables", "Fish", "Chapathi", "Salad ingredients"],
                "ai_tips": ["API Error: No choices in response. This is a generic healthy meal plan. For specific medical conditions, consult your doctor."]
            }
            return fallback, f"API Error: No choices in response"
        
        import re, json as pyjson
        text = result['choices'][0]['message']['content']
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return pyjson.loads(match.group(0)), text
            except:
                pass
        # Fallback: generic plan
        fallback = {
            "meals": [
                {"meal": "breakfast", "foods": "Oatmeal with fruit, 1 boiled egg", "calories": 350, "protein": 15, "carbs": 50, "fat": 8, "fiber": 6, "health_score": 85},
                {"meal": "lunch", "foods": "Grilled chicken, brown rice, steamed veggies", "calories": 500, "protein": 35, "carbs": 60, "fat": 10, "fiber": 8, "health_score": 90},
                {"meal": "dinner", "foods": "Fish curry, chapathi, salad", "calories": 450, "protein": 30, "carbs": 55, "fat": 9, "fiber": 7, "health_score": 88}
            ],
            "shopping_list": ["Oatmeal", "Eggs", "Fruit", "Chicken", "Brown rice", "Vegetables", "Fish", "Chapathi", "Salad ingredients"],
            "ai_tips": ["This is a generic healthy meal plan. For specific medical conditions, consult your doctor."]
        }
        return fallback, text
    except Exception as e:
        # Fallback: generic plan with error
        fallback = {
            "meals": [
                {"meal": "breakfast", "foods": "Oatmeal with fruit, 1 boiled egg", "calories": 350, "protein": 15, "carbs": 50, "fat": 8, "fiber": 6, "health_score": 85},
                {"meal": "lunch", "foods": "Grilled chicken, brown rice, steamed veggies", "calories": 500, "protein": 35, "carbs": 60, "fat": 10, "fiber": 8, "health_score": 90},
                {"meal": "dinner", "foods": "Fish curry, chapathi, salad", "calories": 450, "protein": 30, "carbs": 55, "fat": 9, "fiber": 7, "health_score": 88}
            ],
            "shopping_list": ["Oatmeal", "Eggs", "Fruit", "Chicken", "Brown rice", "Vegetables", "Fish", "Chapathi", "Salad ingredients"],
            "ai_tips": [f"Error: {str(e)}. This is a generic healthy meal plan. For specific medical conditions, consult your doctor."]
        }
        return fallback, str(e)

def generate_txt_summary(meal_plan, profile):
    lines = []
    lines.append("AI Personalized Meal Plan\n")
    lines.append(f"Profile: {profile}\n")
    lines.append("\nMeal Plan:")
    for meal in meal_plan.get('meals', []):
        lines.append(f"{meal.get('meal','').capitalize()}: {meal.get('foods','')}")
        lines.append(f"Calories: {meal.get('calories','N/A')} | Protein: {meal.get('protein','N/A')}g | Carbs: {meal.get('carbs','N/A')}g | Fat: {meal.get('fat','N/A')}g | Fiber: {meal.get('fiber','N/A')}g | Health Score: {meal.get('health_score','N/A')}")
        lines.append("")
    lines.append("Shopping List:")
    for item in meal_plan.get('shopping_list', []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("AI Tips:")
    for tip in meal_plan.get('ai_tips', []):
        if 'error' not in tip.lower():
            lines.append(f"- {tip}")
    return '\n'.join(lines)

def ai_meal_planner_page(username):
    st.markdown("""
        <style>
        .meal-header { color: #1a1a1a !important; font-size: 2em; font-weight: bold; margin-bottom: 0.2em; }
        .meal-desc { color: #222 !important; font-size: 1.1em; margin-bottom: 1em; }
        .meal-section { color: #3a6ea5 !important; font-size: 1.2em; font-weight: bold; margin-top: 1em; }
        .meal-tip { color: #1a4d2e; font-size: 1em; margin-bottom: 0.5em; }
        .meal-food { color: #222; font-size: 1.1em; font-weight: bold; }
        .meal-macros { color: #3a6ea5; font-size: 1em; }
        .meal-shopping { color: #1a4d2e; font-size: 1em; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="meal-header">🍽️ AI Personalized Meal Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="meal-desc">Enter your health data and get a daily or weekly meal plan, shopping list, and AI tips. Download as TXT!</div>', unsafe_allow_html=True)
    with st.form("profile_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=5, max_value=100, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with col2:
            weight = st.number_input("Weight (kg)", min_value=20, max_value=200, value=70)
            height = st.number_input("Height (cm)", min_value=120, max_value=220, value=170)
        with col3:
            goal = st.selectbox("Goal", ["Weight Loss", "Maintenance", "Muscle Gain"])
            period = st.selectbox("Plan For", ["daily", "weekly"])
        allergies = st.text_input("Allergies (comma separated)")
        med_cond = st.text_area("Medical Conditions (comma separated or free text)")
        submit = st.form_submit_button("Generate Meal Plan")
    if submit:
        profile = {
            "age": age, "gender": gender, "weight": weight, "height": height, "goal": goal,
            "allergies": allergies, "medical_conditions": med_cond
        }
        with st.spinner("Generating your personalized meal plan..."):
            meal_plan, raw = groq_generate_meal_plan(profile, period)
        if meal_plan.get('meals'):
            st.markdown('<div class="meal-section">Meal Plan</div>', unsafe_allow_html=True)
            for meal in meal_plan['meals']:
                st.markdown(f'<div class="meal-food">{meal.get("meal","").capitalize()}: {meal.get("foods","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meal-macros">Calories: {meal.get("calories","N/A")} | Protein: {meal.get("protein","N/A")}g | Carbs: {meal.get("carbs","N/A")}g | Fat: {meal.get("fat","N/A")}g | Fiber: {meal.get("fiber","N/A")}g | Health Score: {meal.get("health_score","N/A")}</div>', unsafe_allow_html=True)
                if all(k in meal for k in ['protein', 'carbs', 'fat', 'fiber']):
                    fig = go.Figure(data=[
                        go.Pie(labels=['Protein', 'Carbs', 'Fat', 'Fiber'],
                               values=[meal['protein'], meal['carbs'], meal['fat'], meal['fiber']],
                               hole=0.4)
                    ])
                    fig.update_layout(title=f"{meal.get('meal','').capitalize()} Macronutrient Breakdown", margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)
            # Shopping list
            if meal_plan.get('shopping_list'):
                st.markdown('<div class="meal-section">Shopping List</div>', unsafe_allow_html=True)
                for item in meal_plan['shopping_list']:
                    st.markdown(f'<div class="meal-shopping">- {item}</div>', unsafe_allow_html=True)
            # AI tips
            if meal_plan.get('ai_tips'):
                st.markdown('<div class="meal-section">AI Tips</div>', unsafe_allow_html=True)
                for tip in meal_plan['ai_tips']:
                    if 'error' not in tip.lower():
                        st.markdown(f'<div class="meal-tip">- {tip}</div>', unsafe_allow_html=True)
            # Download as TXT
            st.markdown('<div class="meal-section">Download Meal Plan</div>', unsafe_allow_html=True)
            txt_summary = generate_txt_summary(meal_plan, profile)
            st.download_button("Download TXT", data=txt_summary, file_name="ai_meal_plan.txt", mime="text/plain")
        else:
            st.warning("Could not generate a meal plan. Try changing your profile or try again later.")
            st.expander("Show LLM response").write(raw) 
