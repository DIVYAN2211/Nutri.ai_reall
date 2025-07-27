import streamlit as st
import os
import requests
import plotly.graph_objects as go

GROQ_API_KEY = "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"
# Helper: Use GROQ Llama3 to analyze a meal

def groq_analyze_meal(meal_desc):
    # Check if API key is available
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Provide fallback meal analysis
        meal_desc_lower = meal_desc.lower()
        
        # Basic meal analysis data
        fallback_meals = {
            "egg": {"calories": 140, "protein": 12, "carbs": 2, "fat": 10, "fiber": 0, "health_score": 80, "suggestions": ["Add vegetables for more nutrients", "Use whole grain bread"]},
            "toast": {"calories": 80, "protein": 3, "carbs": 15, "fat": 1, "fiber": 2, "health_score": 70, "suggestions": ["Use whole grain bread", "Add healthy fats like avocado"]},
            "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0, "health_score": 85, "suggestions": ["Grill instead of fry", "Add vegetables"]},
            "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4, "health_score": 70, "suggestions": ["Use brown rice for more fiber", "Add vegetables"]},
            "salad": {"calories": 20, "protein": 2, "carbs": 4, "fat": 0.2, "fiber": 1.5, "health_score": 95, "suggestions": ["Add protein like chicken or beans", "Use olive oil dressing"]},
            "fish": {"calories": 100, "protein": 20, "carbs": 0, "fat": 2.5, "fiber": 0, "health_score": 90, "suggestions": ["Bake or grill instead of fry", "Add vegetables"]},
            "milk": {"calories": 42, "protein": 3.4, "carbs": 5, "fat": 1, "fiber": 0, "health_score": 75, "suggestions": ["Choose low-fat options", "Add to smoothies"]},
            "bread": {"calories": 79, "protein": 3.1, "carbs": 15, "fat": 1, "fiber": 1.2, "health_score": 65, "suggestions": ["Use whole grain bread", "Limit portion size"]}
        }
        
        # Try to match meal description with fallback data
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        suggestions = []
        
        for food_name, nutrition in fallback_meals.items():
            if food_name in meal_desc_lower:
                total_calories += nutrition["calories"]
                total_protein += nutrition["protein"]
                total_carbs += nutrition["carbs"]
                total_fat += nutrition["fat"]
                total_fiber += nutrition["fiber"]
                suggestions.extend(nutrition["suggestions"])
        
        if total_calories > 0:
            avg_health_score = min(95, 70 + (total_protein * 0.5) + (total_fiber * 2))
            return {
                "calories": total_calories,
                "protein": total_protein,
                "carbs": total_carbs,
                "fat": total_fat,
                "fiber": total_fiber,
                "health_score": int(avg_health_score),
                "suggestions": suggestions[:3]  # Limit to 3 suggestions
            }, f"Basic analysis for {meal_desc} (get GROQ API key for detailed analysis)"
        
        # Generic fallback for unknown meals
        return {
            "calories": 200,
            "protein": 10,
            "carbs": 25,
            "fat": 8,
            "fiber": 3,
            "health_score": 70,
            "suggestions": ["Add more vegetables", "Include lean protein", "Choose whole grains"]
        }, f"Generic analysis for {meal_desc} (get GROQ API key for accurate analysis)"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"Analyze this meal: {meal_desc}. Return a JSON with keys: food, calories, protein, carbs, fat, fiber, health_score, suggestions (list of improvements)."
    )
    data = {"model": "llama3-70b-8192", "messages": [{"role": "system", "content": prompt}], "max_tokens": 512}
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:
            return {}, "API key invalid or expired. Please check your GROQ_API_KEY."
        elif resp.status_code != 200:
            return {}, f"API Error: {resp.status_code} - {resp.text}"
        
        result = resp.json()
        if 'choices' not in result or not result['choices']:
            return {}, f"API Error: No choices in response"
        
        import re, json as pyjson
        text = result['choices'][0]['message']['content']
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return pyjson.loads(match.group(0)), text
            except:
                pass
        # Fallback: try to extract numbers from text
        fallback = {}
        for k in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'health_score']:
            m = re.search(rf'{k}[^\d]*(\d+)', text, re.IGNORECASE)
            if m:
                fallback[k] = int(m.group(1))
        return fallback, text
    except Exception as e:
        return {}, str(e)

def diet_planner_page(username):
    st.markdown("""
        <style>
        .diet-header { color: #1a1a1a !important; font-size: 2em; font-weight: bold; margin-bottom: 0.2em; }
        .diet-desc { color: #222 !important; font-size: 1.1em; margin-bottom: 1em; }
        .diet-section { color: #3a6ea5 !important; font-size: 1.2em; font-weight: bold; margin-top: 1em; }
        .diet-suggestion { color: #1a4d2e; font-size: 1em; margin-bottom: 0.5em; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="diet-header">🥗 AI Diet Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="diet-desc">Plan your meals for the day and get AI-powered nutrition analysis, suggestions, and visualizations.</div>', unsafe_allow_html=True)
    with st.form("diet_form"):
        breakfast = st.text_area("Breakfast (e.g. 2 eggs, toast, orange juice)")
        lunch = st.text_area("Lunch (e.g. grilled chicken, rice, salad)")
        dinner = st.text_area("Dinner (e.g. fish curry, brown rice, veggies)")
        submit = st.form_submit_button("Analyze My Diet")
    if submit:
        meals = {"Breakfast": breakfast, "Lunch": lunch, "Dinner": dinner}
        meal_results = {}
        total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0, "health_score": 0}
        all_suggestions = []
        for meal, desc in meals.items():
            if desc.strip():
                with st.spinner(f"Analyzing {meal}..."):
                    result, raw = groq_analyze_meal(desc)
                meal_results[meal] = result
                for k in total:
                    if k in result and isinstance(result[k], (int, float)):
                        total[k] += result[k]
                if 'suggestions' in result and isinstance(result['suggestions'], list):
                    all_suggestions.extend(result['suggestions'])
        # Visualize each meal
        for meal, result in meal_results.items():
            st.markdown(f'<div class="diet-section">{meal} Analysis</div>', unsafe_allow_html=True)
            if result and any(result.values()):
                st.markdown(f"**Calories:** {result.get('calories', 'N/A')} kcal")
                st.markdown(f"**Protein:** {result.get('protein', 'N/A')} g")
                st.markdown(f"**Carbs:** {result.get('carbs', 'N/A')} g")
                st.markdown(f"**Fat:** {result.get('fat', 'N/A')} g")
                st.markdown(f"**Fiber:** {result.get('fiber', 'N/A')} g")
                if all(k in result for k in ['protein', 'carbs', 'fat', 'fiber']):
                    fig = go.Figure(data=[
                        go.Pie(labels=['Protein', 'Carbs', 'Fat', 'Fiber'],
                               values=[result['protein'], result['carbs'], result['fat'], result['fiber']],
                               hole=0.4)
                    ])
                    fig.update_layout(title=f"{meal} Macronutrient Breakdown", margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)
                if 'health_score' in result:
                    st.markdown(f"**Health Score:** {result['health_score']} / 100")
                if 'suggestions' in result and result['suggestions']:
                    st.markdown("**AI Suggestions:**")
                    for s in result['suggestions']:
                        st.markdown(f'<div class="diet-suggestion">- {s}</div>', unsafe_allow_html=True)
            else:
                st.info("No analysis available for this meal. Try rephrasing or using more common foods.")
        # Daily summary
        st.markdown('<div class="diet-section">Daily Nutrition Summary</div>', unsafe_allow_html=True)
        st.markdown(f"**Total Calories:** {total['calories']} kcal")
        st.markdown(f"**Total Protein:** {total['protein']} g")
        st.markdown(f"**Total Carbs:** {total['carbs']} g")
        st.markdown(f"**Total Fat:** {total['fat']} g")
        st.markdown(f"**Total Fiber:** {total['fiber']} g")
        st.markdown(f"**Average Health Score:** {round(total['health_score']/max(1,len([r for r in meal_results.values() if r and any(r.values())])),1)} / 100")
        # Daily macronutrient pie
        if all(k in total for k in ['protein', 'carbs', 'fat', 'fiber']) and sum([total[k] for k in ['protein', 'carbs', 'fat', 'fiber']]) > 0:
            fig = go.Figure(data=[
                go.Pie(labels=['Protein', 'Carbs', 'Fat', 'Fiber'],
                       values=[total['protein'], total['carbs'], total['fat'], total['fiber']],
                       hole=0.4)
            ])
            fig.update_layout(title="Daily Macronutrient Breakdown", margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        # All suggestions
        if all_suggestions:
            st.markdown('<div class="diet-section">AI Suggestions for Your Day</div>', unsafe_allow_html=True)
            for s in all_suggestions:
                st.markdown(f'<div class="diet-suggestion">- {s}</div>', unsafe_allow_html=True) 
