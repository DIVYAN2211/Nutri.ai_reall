import streamlit as st
import os
import requests
import pandas as pd

GROQ_API_KEY = "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"

# Helper: Use GROQ Llama3 to simulate/augment hospital search
def groq_find_hospitals(location):
    # Check if API key is available
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Provide fallback hospital data for common locations
        location_lower = location.lower()
        
        # Basic hospital data for common cities
        fallback_hospitals = {
            "mumbai": [
                {"name": "Lilavati Hospital", "address": "A-791, Bandra Reclamation, Bandra (W), Mumbai", "description": "Multi-specialty hospital with advanced medical facilities"},
                {"name": "Kokilaben Dhirubhai Ambani Hospital", "address": "Rao Saheb Achutrao Patwardhan Marg, Four Bungalows, Andheri (W), Mumbai", "description": "State-of-the-art medical center with comprehensive healthcare services"},
                {"name": "Tata Memorial Hospital", "address": "Dr Ernest Borges Road, Parel, Mumbai", "description": "Specialized cancer treatment and research center"}
            ],
            "delhi": [
                {"name": "AIIMS Delhi", "address": "Sri Aurobindo Marg, Ansari Nagar, New Delhi", "description": "Premier medical institute with comprehensive healthcare services"},
                {"name": "Safdarjung Hospital", "address": "Ansari Nagar West, New Delhi", "description": "Large government hospital with multiple specialties"},
                {"name": "Max Super Speciality Hospital", "address": "Saket, New Delhi", "description": "Advanced medical care with modern facilities"}
            ],
            "bangalore": [
                {"name": "Manipal Hospital", "address": "98, HAL Airport Road, Bangalore", "description": "Multi-specialty hospital with international standards"},
                {"name": "Fortis Hospital", "address": "154, Bannerghatta Road, Bangalore", "description": "Advanced healthcare with cutting-edge technology"},
                {"name": "Apollo Hospital", "address": "154/11, Bannerghatta Road, Bangalore", "description": "Comprehensive medical care and emergency services"}
            ],
            "chennai": [
                {"name": "Apollo Hospitals", "address": "Greams Road, Chennai", "description": "Leading healthcare provider with world-class facilities"},
                {"name": "Fortis Malar Hospital", "address": "Adyar, Chennai", "description": "Specialized medical care with modern infrastructure"},
                {"name": "MIOT International", "address": "Mount Poonamallee Road, Chennai", "description": "Advanced medical technology and patient care"}
            ],
            "vellore": [
                {"name": "Christian Medical College", "address": "Vellore, Tamil Nadu", "description": "Premier medical institution with comprehensive healthcare"},
                {"name": "Vellore Government Hospital", "address": "Vellore, Tamil Nadu", "description": "Government hospital providing essential medical services"},
                {"name": "Apollo Speciality Hospital", "address": "Vellore, Tamil Nadu", "description": "Specialized medical care with modern facilities"}
            ]
        }
        
        # Try to match location with fallback data
        for city, hospitals in fallback_hospitals.items():
            if city in location_lower:
                return hospitals, f"Basic hospital data for {city} (get GROQ API key for real-time data)"
        
        # Generic fallback for unknown locations
        generic_hospitals = [
            {"name": "City General Hospital", "address": f"{location}, Main Street", "description": "General hospital providing essential medical services"},
            {"name": "Community Medical Center", "address": f"{location}, Healthcare District", "description": "Multi-specialty medical center with emergency services"},
            {"name": "Regional Hospital", "address": f"{location}, Medical Complex", "description": "Comprehensive healthcare facility with modern amenities"}
        ]
        return generic_hospitals, f"Generic hospital data for {location} (get GROQ API key for accurate information)"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"List 5 well-known hospitals near {location}. For each, provide a short description (services, specialties, reputation). "
        "Return as a JSON list of objects with 'name', 'address', and 'description'."
    )
    data = {"model": "llama3-70b-8192", "messages": [{"role": "system", "content": prompt}], "max_tokens": 512}
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:
            return [], "API key invalid or expired. Please check your GROQ_API_KEY."
        elif resp.status_code != 200:
            return [], f"API Error: {resp.status_code} - {resp.text}"
        
        result = resp.json()
        if 'choices' not in result or not result['choices']:
            return [], f"API Error: No choices in response"
        
        text = result['choices'][0]['message']['content']
        import re, json as pyjson
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                return pyjson.loads(match.group(0)), text
            except:
                return [], text
        else:
            return [], text
    except Exception as e:
        return [], str(e)

# Geocode address to lat/lon using Nominatim API
def geocode_address(address):
    try:
        url = f"https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        resp = requests.get(url, params=params, headers={"User-Agent": "nutri.ai/1.0"})
        data = resp.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None, None

def hospital_finder_page(username):
    st.markdown("""
        <style>
        .hospital-header { color: #1a1a1a !important; font-size: 2em; font-weight: bold; margin-bottom: 0.2em; }
        .hospital-desc-text { color: #222 !important; font-size: 1.1em; margin-bottom: 1em; }
        .hospital-label { color: #1a1a1a !important; font-size: 1em; font-weight: bold; }
        .hospital-card {
            background: #f6f8fa;
            border-radius: 10px;
            padding: 1em;
            margin-bottom: 1em;
            box-shadow: 0 2px 8px rgba(44,62,80,0.07);
        }
        .hospital-name { color: #1a4d2e; font-size: 1.2em; font-weight: bold; }
        .hospital-address { color: #3a6ea5; font-size: 1em; }
        .hospital-desc { color: #222; font-size: 1em; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="hospital-header">🏥 Nearby Hospitals Finder</div>', unsafe_allow_html=True)
    st.markdown('<div class="hospital-desc-text">Enter your city or location to find hospitals near you, with AI-generated descriptions.</div>', unsafe_allow_html=True)
    location = st.text_input("Enter your city or location", key="hospital_location_input")
    if st.button("Find Hospitals") and location:
        with st.spinner("Searching for hospitals..."):
            hospitals, raw = groq_find_hospitals(location)
        if hospitals:
            st.success(f"Hospitals near {location}:")
            # Table visualization
            df = pd.DataFrame(hospitals)
            st.dataframe(df[['name', 'address', 'description']])
            # Map visualization
            st.markdown('<div class="hospital-label">Map of Hospitals</div>', unsafe_allow_html=True)
            map_data = []
            for h in hospitals:
                lat, lon = geocode_address(h.get('address', ''))
                if lat and lon:
                    map_data.append({'lat': lat, 'lon': lon, 'name': h.get('name', '')})
            if map_data:
                map_df = pd.DataFrame(map_data)
                st.map(map_df[['lat', 'lon']])
            else:
                st.info("Map not available for these addresses.")
            # Card visualization
            for h in hospitals:
                st.markdown(f'''<div class="hospital-card">
                    <div class="hospital-name">{h.get('name','')}</div>
                    <div class="hospital-address">{h.get('address','')}</div>
                    <div class="hospital-desc">{h.get('description','')}</div>
                </div>''', unsafe_allow_html=True)
        else:
            st.warning("Could not find hospitals. Try a different location.")
            st.expander("Show LLM response").write(raw) 
