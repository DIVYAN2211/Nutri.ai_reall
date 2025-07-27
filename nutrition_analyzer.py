import streamlit as st
import requests
import os
import plotly.graph_objects as go
import base64
import mimetypes

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

from PIL import Image
from io import BytesIO
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

def load_blip():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

def blip_caption(image_bytes):
    try:
        processor, model = load_blip()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        with torch.no_grad():
            out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        return f"Error in BLIP processing: {str(e)}"

def groq_llava_caption(image_bytes, mime_type):
    # Check if API key is available
    if not GROQ_API_KEY:
        return "API key not configured. Please set GROQ_API_KEY environment variable."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    img_b64 = base64.b64encode(image_bytes).decode()
    data = {
        "model": "llava-1.5-7b",
        "messages": [
            {"role": "system", "content": "You are a food recognition expert. Describe the food in this image as clearly as possible. Include the main ingredients and cooking method if visible. If you can't recognize the food clearly, say 'Unknown'."},
            {"role": "user", "content": [
                {"type": "text", "text": "What food is in this image? Describe it in detail."},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{img_b64}"}}
            ]}
        ],
        "max_tokens": 300
    }
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 404:
            return "Vision model not available. Please check if LLaVA model is supported by your GROQ API plan."
        elif resp.status_code == 401:
            return "API key invalid or expired. Please check your GROQ_API_KEY."
        elif resp.status_code != 200:
            return f"API Error: {resp.status_code} - {resp.text}"
        
        result = resp.json()
        if 'choices' not in result or not result['choices']:
            return "API Error: No choices in response"
        
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def groq_llama3_nutrition(food_desc):
    # Check if API key is available
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Provide basic fallback nutrition data for common foods
        food_desc_lower = food_desc.lower()
        
        # Simple food recognition and nutrition data
        basic_foods = {
            "chicken": {"food": "Chicken", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0, "health_score": 85},
            "rice": {"food": "Rice", "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4, "health_score": 70},
            "egg": {"food": "Egg", "calories": 70, "protein": 6, "carbs": 0.6, "fat": 5, "fiber": 0, "health_score": 80},
            "bread": {"food": "Bread", "calories": 79, "protein": 3.1, "carbs": 15, "fat": 1, "fiber": 1.2, "health_score": 65},
            "milk": {"food": "Milk", "calories": 42, "protein": 3.4, "carbs": 5, "fat": 1, "fiber": 0, "health_score": 75},
            "apple": {"food": "Apple", "calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4, "health_score": 90},
            "banana": {"food": "Banana", "calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "fiber": 2.6, "health_score": 85},
            "salad": {"food": "Salad", "calories": 20, "protein": 2, "carbs": 4, "fat": 0.2, "fiber": 1.5, "health_score": 95},
            "fish": {"food": "Fish", "calories": 100, "protein": 20, "carbs": 0, "fat": 2.5, "fiber": 0, "health_score": 90},
            "potato": {"food": "Potato", "calories": 77, "protein": 2, "carbs": 17, "fat": 0.1, "fiber": 2.2, "health_score": 75}
        }
        
        # Try to match food description with basic foods
        for food_name, nutrition in basic_foods.items():
            if food_name in food_desc_lower:
                nutrition["suggested_pairings"] = ["Vegetables", "Whole grains", "Healthy fats"]
                return nutrition, f"Basic nutrition data for {food_name}"
        
        # If no match found, return generic data
        return {
            "food": "Generic Food", 
            "calories": 100, 
            "protein": 5, 
            "carbs": 15, 
            "fat": 3, 
            "fiber": 2, 
            "health_score": 70,
            "suggested_pairings": ["Vegetables", "Whole grains", "Healthy fats"]
        }, "Basic nutrition estimate (get GROQ API key for accurate analysis)"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        "You are a nutrition expert. Given the following food description, return a JSON object with keys: "
        "food (name of the food), calories (number), protein (number in grams), carbs (number in grams), "
        "fat (number in grams), fiber (number in grams), health_score (number 0-100), "
        "suggested_pairings (array of 3-5 foods that pair well with this meal). "
        "Provide realistic nutritional values. If you can't recognize the food, return 'Unknown' for food.\n"
        f"Food description: {food_desc}"
    )
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": prompt}
        ],
        "max_tokens": 600
    }
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:
            return {"food": "API key invalid or expired. Please check your GROQ_API_KEY."}, "Authentication failed"
        elif resp.status_code != 200:
            return {"food": f"API Error: {resp.status_code} - {resp.text}"}, resp.text
        
        result = resp.json()
        if 'choices' not in result or not result['choices']:
            return {"food": "API Error: No choices in response"}, str(result)
        
        import re, json as pyjson
        text = result['choices'][0]['message']['content']
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                nutrition_data = pyjson.loads(match.group(0))
                # Ensure all required fields are present
                required_fields = ['food', 'calories', 'protein', 'carbs', 'fat', 'fiber', 'health_score']
                for field in required_fields:
                    if field not in nutrition_data:
                        nutrition_data[field] = 0 if field in ['calories', 'protein', 'carbs', 'fat', 'fiber'] else 'Unknown'
                return nutrition_data, text
            except:
                return {"food": "Unknown", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0, "health_score": 0}, text
        else:
            return {"food": "Unknown", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0, "health_score": 0}, text
    except Exception as e:
        return {"food": "Error", "error": str(e), "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0, "health_score": 0}, str(e)

def show_nutrition_result(result):
    st.markdown(f"**Calories:** {result.get('calories', 'N/A')} kcal")
    st.markdown(f"**Protein:** {result.get('protein', 'N/A')} g")
    st.markdown(f"**Carbs:** {result.get('carbs', 'N/A')} g")
    st.markdown(f"**Fat:** {result.get('fat', 'N/A')} g")
    st.markdown(f"**Fiber:** {result.get('fiber', 'N/A')} g")
    # Macronutrient pie chart
    if all(k in result for k in ['protein', 'carbs', 'fat', 'fiber']):
        fig = go.Figure(data=[
            go.Pie(labels=['Protein', 'Carbs', 'Fat', 'Fiber'],
                   values=[result['protein'], result['carbs'], result['fat'], result['fiber']],
                   hole=0.4)
        ])
        fig.update_layout(title="Macronutrient Breakdown", margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    # Health score graph
    if 'health_score' in result:
        st.subheader("Health Score")
        st.progress(result['health_score'] / 100)
        st.markdown(f"**Score:** {result['health_score']} / 100")
    # Suggested pairings
    if 'suggested_pairings' in result and result['suggested_pairings']:
        st.subheader("Suggested Pairings")
        if isinstance(result['suggested_pairings'], list):
            st.markdown(", ".join(result['suggested_pairings']))
        else:
            st.markdown(str(result['suggested_pairings']))

def nutrition_analyzer_page(username):
    st.header("🍽️ Nutrition Analyzer")
    st.write("Upload a meal image or enter your meal details to analyze nutrition.")
    tab1, tab2 = st.tabs(["Image Upload", "Manual Input"])

    with tab1:
        uploaded = st.file_uploader("Upload meal image", type=["jpg", "jpeg", "png"])
        if uploaded:
            image_bytes = uploaded.read()
            mime_type = uploaded.type or f"image/{mimetypes.guess_type(uploaded.name)[0] or 'jpeg'}"
            st.image(image_bytes, caption="Uploaded Meal", use_container_width=True)

            
            # Use BLIP for image recognition first
            with st.spinner("Analyzing image with BLIP..."):
                blip_caption_text = blip_caption(image_bytes)
            st.info(f"BLIP recognition: {blip_caption_text}")
            
            # Then provide nutrition info based on BLIP caption
            with st.spinner("Extracting nutrition facts from BLIP recognition..."):
                result, raw_response = groq_llama3_nutrition(blip_caption_text)
            
            if result.get("error") or result.get("food") in ["Unknown", "Error"]:
                st.warning("Could not recognize the meal or analyze the image. Please try a clearer image or describe it manually.")
                st.expander("Show LLM response").write(raw_response)
            else:
                st.success(f"Food: {result['food']}")
                show_nutrition_result(result)
        else:
            st.info("Please upload a meal image.")

    with tab2:
        food_desc = st.text_area("Describe your meal (e.g. 2 eggs, 1 toast, 1 cup milk)")
        if st.button("Analyze Nutrition") and food_desc:
            with st.spinner("Analyzing input..."):
                result, raw_response = groq_llama3_nutrition(food_desc)
            if result.get("error") or result.get("food") in ["Unknown", "Error"]:
                st.warning("Could not analyze the input. Please try again.")
                st.expander("Show LLM response").write(raw_response)
            else:
                st.success(f"Food: {result['food']}")
                show_nutrition_result(result) 
