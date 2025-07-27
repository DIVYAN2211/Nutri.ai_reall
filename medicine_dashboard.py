import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
import requests
import json
from collections import Counter
from datetime import timedelta, date

GROQ_API_KEY ="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"

# --- LLM Helper ---
def get_medicine_info_llm(medicine, dosage=None, frequency=None, duration=None):
    # Check if API key is available
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Provide fallback medicine data
        medicine_lower = medicine.lower()
        
        # Basic medicine information
        fallback_medicines = {
            "paracetamol": {
                "uses": "Pain relief and fever reduction",
                "type": "Analgesic and antipyretic",
                "side_effects": "Generally safe, rare liver issues with overdose",
                "warnings": "Do not exceed recommended dosage",
                "summary": "Common pain reliever and fever reducer"
            },
            "dolo": {
                "uses": "Pain relief and fever reduction",
                "type": "Analgesic and antipyretic",
                "side_effects": "Generally safe, rare allergic reactions",
                "warnings": "Consult doctor for long-term use",
                "summary": "Brand name for paracetamol, used for pain and fever"
            },
            "aspirin": {
                "uses": "Pain relief, fever reduction, blood thinning",
                "type": "NSAID and antiplatelet",
                "side_effects": "Stomach irritation, bleeding risk",
                "warnings": "Avoid if allergic, consult doctor before use",
                "summary": "Pain reliever with blood thinning properties"
            },
            "ibuprofen": {
                "uses": "Pain relief, inflammation reduction, fever",
                "type": "NSAID",
                "side_effects": "Stomach upset, kidney issues with long use",
                "warnings": "Take with food, avoid if stomach sensitive",
                "summary": "Anti-inflammatory pain reliever"
            },
            "amoxicillin": {
                "uses": "Bacterial infections",
                "type": "Antibiotic",
                "side_effects": "Diarrhea, nausea, allergic reactions",
                "warnings": "Complete full course, avoid alcohol",
                "summary": "Common antibiotic for bacterial infections"
            }
        }
        
        # Try to match medicine with fallback data
        for med_name, info in fallback_medicines.items():
            if med_name in medicine_lower:
                return info
        
        # Generic fallback for unknown medicines
        return {
            "uses": "Consult your doctor for specific uses",
            "type": "Consult your doctor for medicine type",
            "side_effects": "Consult your doctor for side effects",
            "warnings": "Always follow doctor's instructions",
            "summary": f"Basic information for {medicine} (get GROQ API key for detailed analysis)"
        }
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"Give a JSON summary for the medicine '{medicine}'"
        + (f", dosage: {dosage}, frequency: {frequency}, duration: {duration}" if dosage or frequency or duration else "")
        + ". Include: uses, type (e.g. antibiotic, painkiller), common side effects, warnings, and a one-sentence summary."
    )
    data = {"model": "llama3-70b-8192", "messages": [{"role": "system", "content": prompt}], "max_tokens": 512}
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:
            return {"summary": "API key invalid or expired. Please check your GROQ_API_KEY."}
        elif resp.status_code != 200:
            return {"summary": f"API Error: {resp.status_code} - {resp.text}"}
        
        result = resp.json()
        if 'choices' not in result or not result['choices']:
            return {"summary": f"API Error: No choices in response"}
        
        text = result['choices'][0]['message']['content']
        match = __import__('re').search(r'\{.*\}', text, __import__('re').DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return {"summary": text}
        else:
            return {"summary": text}
    except Exception as e:
        return {"summary": f"Error: {str(e)}"}

def get_combination_info_llm(meds):
    # Check if API key is available
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Provide fallback combination data
        if len(meds) == 0:
            return {"interactions": "No medicines to analyze", "summary": "Add medicines to get interaction analysis"}
        
        medicine_names = [m.get('name', '').lower() for m in meds]
        
        # Basic interaction warnings
        interactions = []
        if any('paracetamol' in name or 'dolo' in name for name in medicine_names):
            interactions.append("Paracetamol: Generally safe, avoid alcohol")
        if any('aspirin' in name for name in medicine_names):
            interactions.append("Aspirin: May interact with blood thinners")
        if any('ibuprofen' in name for name in medicine_names):
            interactions.append("Ibuprofen: May cause stomach irritation")
        if any('amoxicillin' in name for name in medicine_names):
            interactions.append("Amoxicillin: Avoid alcohol, complete full course")
        
        if not interactions:
            interactions = ["Consult your doctor for specific interactions"]
        
        return {
            "interactions": interactions,
            "summary": f"Basic interaction analysis for {len(meds)} medicines (get GROQ API key for detailed analysis)"
        }
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"Given this list of medicines: {', '.join([m['name'] for m in meds])}, "
        "describe any important interactions, precautions, and give a one-sentence summary. Return as JSON with keys: interactions, summary."
    )
    data = {"model": "llama3-70b-8192", "messages": [{"role": "system", "content": prompt}], "max_tokens": 512}
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 401:
            return {"summary": "API key invalid or expired. Please check your GROQ_API_KEY."}
        elif resp.status_code != 200:
            return {"summary": f"API Error: {resp.status_code} - {resp.text}"}
        
        result = resp.json()
        if 'choices' not in result or not result['choices']:
            return {"summary": f"API Error: No choices in response"}
        
        text = result['choices'][0]['message']['content']
        match = __import__('re').search(r'\{.*\}', text, __import__('re').DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return {"summary": text}
        else:
            return {"summary": text}
    except Exception as e:
        return {"summary": f"Error: {str(e)}"}

# --- Streamlit App ---
def medicine_dashboard_page(username):
    st.markdown("""
        <style>
        .dashboard-title { font-size: 2.2em; font-weight: bold; color: #2d3a4a; margin-bottom: 0.2em; }
        .section-title { font-size: 1.2em; font-weight: bold; color: #3a6ea5; margin-top: 1em; margin-bottom: 0.5em; }
        .ai-text { color: #222; background: #f6f8fa; padding: 0.5em 1em; border-radius: 8px; font-size: 1.1em; }
        .med-list { color: #1a4d2e; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="dashboard-title">💊 AI Medicine Dashboard</div>', unsafe_allow_html=True)
    st.write("Add your medicines and get AI-powered insights and visualizations.")

    if 'medicines' not in st.session_state:
        st.session_state['medicines'] = []

    # Dynamic input
    with st.form("add_medicine_form"):
        cols = st.columns([2, 2, 2, 2])
        name = cols[0].text_input("Medicine Name", key="med_name")
        dosage = cols[1].text_input("Dosage (e.g. 500mg)", key="med_dosage")
        frequency = cols[2].text_input("Frequency (e.g. 2x/day)", key="med_freq")
        duration = cols[3].text_input("Duration (e.g. 5 days)", key="med_dur")
        add_btn = st.form_submit_button("Add Medicine")
        if add_btn and name:
            st.session_state['medicines'].append({
                'name': name, 'dosage': dosage, 'frequency': frequency, 'duration': duration
            })
            st.rerun()

    # Show current medicines
    if st.session_state['medicines']:
        st.markdown('<div class="section-title">Your Medicines</div>', unsafe_allow_html=True)
        st.markdown('<ul class="med-list">' + ''.join([f'<li>{i+1}. {med["name"]} {med["dosage"]} {med["frequency"]} {med["duration"]}</li>' for i, med in enumerate(st.session_state['medicines'])]) + '</ul>', unsafe_allow_html=True)
        if st.button("Clear All Medicines"):
            st.session_state['medicines'] = []
            st.rerun()
    else:
        st.info("Add medicines above to get started.")
        return

    # LLM info for each medicine
    med_infos = []
    for med in st.session_state['medicines']:
        with st.spinner(f"Getting info for {med['name']}..."):
            info = get_medicine_info_llm(med['name'], med['dosage'], med['frequency'], med['duration'])
        med_infos.append(info)

    # Combination info
    with st.spinner("Analyzing medicine combination..."):
        combo_info = get_combination_info_llm(st.session_state['medicines'])

    # --- Dashboard Layout ---
    st.markdown('<div class="section-title">AI Insights & Visualizations</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # 1. Pie chart: Distribution of medicine types
    with col1:
        st.markdown('<div class="section-title">Medicine Types Distribution</div>', unsafe_allow_html=True)
        types = [info.get('type', 'Unknown') for info in med_infos]
        type_counts = Counter(types)
        fig1 = go.Figure(data=[go.Pie(labels=list(type_counts.keys()), values=list(type_counts.values()), hole=0.4)])
        fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig1, use_container_width=True)

    # 2. Timeline: Dosage/frequency schedule
    with col2:
        st.markdown('<div class="section-title">Dosage Timeline (Simulated)</div>', unsafe_allow_html=True)
        timeline_data = []
        today = date.today()
        for med in st.session_state['medicines']:
            try:
                days = int(''.join(filter(str.isdigit, med['duration']))) if med['duration'] else 5
            except:
                days = 5
            for d in range(days):
                timeline_data.append({
                    'Medicine': med['name'],
                    'Day': today + timedelta(days=d),
                    'Dosage': med['dosage']
                })
        if timeline_data:
            import pandas as pd
            df = pd.DataFrame(timeline_data)
            fig2 = go.Figure()
            for med in df['Medicine'].unique():
                fig2.add_trace(go.Scatter(x=df[df['Medicine']==med]['Day'], y=[1]*len(df[df['Medicine']==med]), mode='markers', name=med, marker=dict(size=12)))
            fig2.update_layout(yaxis=dict(showticklabels=False), margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)

    # 3. Bar chart: Duration of each medicine
    with col3:
        st.markdown('<div class="section-title">Medicine Duration (Days)</div>', unsafe_allow_html=True)
        durations = [int(''.join(filter(str.isdigit, m['duration']))) if m['duration'] else 5 for m in st.session_state['medicines']]
        fig3 = go.Figure([go.Bar(x=[m['name'] for m in st.session_state['medicines']], y=durations)])
        fig3.update_layout(xaxis_title="Medicine", yaxis_title="Days", margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig3, use_container_width=True)

    # 4. Network graph: Interactions (simulated from LLM)
    with col4:
        st.markdown('<div class="section-title">Medicine Interaction Network</div>', unsafe_allow_html=True)
        G = nx.Graph()
        for med in st.session_state['medicines']:
            G.add_node(med['name'])
        interactions = combo_info.get('interactions', '')
        if isinstance(interactions, str) and interactions and interactions != 'None found':
            for med in st.session_state['medicines']:
                for other in st.session_state['medicines']:
                    if med != other and med['name'].lower() in interactions.lower() and other['name'].lower() in interactions.lower():
                        G.add_edge(med['name'], other['name'])
        fig4, ax = plt.subplots()
        nx.draw(G, with_labels=True, node_color='skyblue', node_size=2000, font_size=12, ax=ax)
        st.pyplot(fig4)

    # 5. Word cloud: Side effects
    st.markdown('<div class="section-title">Common Side Effects Word Cloud</div>', unsafe_allow_html=True)
    side_effects = ' '.join([str(info.get('common side effects', '')) for info in med_infos])
    if side_effects.strip():
        wc = WordCloud(width=800, height=300, background_color='white').generate(side_effects)
        fig5, ax5 = plt.subplots()
        ax5.imshow(wc, interpolation='bilinear')
        ax5.axis('off')
        st.pyplot(fig5)
    else:
        st.info("No side effects data available for word cloud.")

    # AI Insights (Summary)
    st.markdown('<div class="section-title">AI Insights for Each Medicine</div>', unsafe_allow_html=True)
    for med, info in zip(st.session_state['medicines'], med_infos):
        st.markdown(f'<div class="ai-text"><b>{med["name"]}</b>: {info.get("summary", "")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-text">- Uses: {info.get("uses", "N/A")}<br>- Type: {info.get("type", "N/A")}<br>- Side Effects: {info.get("common side effects", "N/A")}<br>- Warnings: {info.get("warnings", "N/A")}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">AI Combination Insights</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-text"><b>Summary:</b> {combo_info.get("summary", "")}<br><b>Interactions:</b> {combo_info.get("interactions", "None found")}</div>', unsafe_allow_html=True)

    # Download summary
    st.markdown('<div class="section-title">Download/Export</div>', unsafe_allow_html=True)
    if st.button("Download AI Summary as Text"):
        summary = f"AI Medicine Dashboard Summary\n\n"
        for med, info in zip(st.session_state['medicines'], med_infos):
            summary += f"{med['name']} ({med['dosage']} {med['frequency']} {med['duration']}): {info.get('summary', '')}\n"
        summary += f"\nCombination Summary: {combo_info.get('summary', '')}\nInteractions: {combo_info.get('interactions', 'None found')}\n"
        st.download_button("Download", summary, file_name="medicine_dashboard_summary.txt") 
