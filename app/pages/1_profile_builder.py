import streamlit as st
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.firebase_auth import is_logged_in
from utils.pdf_parser import parse_resume
from utils.github_analyser import analyse_github_profile, SKILLS_LIST

# if not is_logged_in():
#     st.switch_page("pages/2_login.py")

st.progress(0.14, text="Step 1 of 7 — Profile Builder")
st.title("Profile Builder")

if 'selected_skills' not in st.session_state:
    st.session_state['selected_skills'] = []
if 'detected_skills' not in st.session_state:
    st.session_state['detected_skills'] = []
if 'input_method' not in st.session_state:
    st.session_state['input_method'] = 'manual'
if 'years_exp' not in st.session_state:
    st.session_state['years_exp'] = 0

def toggle_skill(s):
    if s in st.session_state['selected_skills']:
        st.session_state['selected_skills'].remove(s)
    else:
        st.session_state['selected_skills'].append(s)

tab1, tab2, tab3, tab4 = st.tabs(["Manual", "Upload Resume", "GitHub", "Job Description"])

with tab1:
    st.header("Manual Selection")
    colA, colB, colC, colD = st.columns(4)
    
    languages = ['Python', 'JavaScript', 'TypeScript', 'Java', 'SQL', 'C++', 'Go', 'Rust']
    databases = ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis']
    frameworks = ['React', 'Node.js', 'Vue.js', 'Django', 'FastAPI', 'Angular']
    tools = ['Docker', 'AWS', 'Kubernetes', 'Google Cloud', 'Azure', 'Git', 'Linux']
    
    with colA:
        st.subheader("Languages")
        for s in languages:
            checked = s in st.session_state['selected_skills']
            if st.checkbox(s, value=checked, key=f"cb_{s}"):
                if s not in st.session_state['selected_skills']:
                    st.session_state['selected_skills'].append(s)
            else:
                if s in st.session_state['selected_skills']:
                    st.session_state['selected_skills'].remove(s)
                    
    with colB:
        st.subheader("Databases")
        for s in databases:
             checked = s in st.session_state['selected_skills']
             if st.checkbox(s, value=checked, key=f"cb_{s}"):
                 if s not in st.session_state['selected_skills']:
                     st.session_state['selected_skills'].append(s)
             else:
                 if s in st.session_state['selected_skills']:
                     st.session_state['selected_skills'].remove(s)
                    
    with colC:
        st.subheader("Frameworks")
        for s in frameworks:
             checked = s in st.session_state['selected_skills']
             if st.checkbox(s, value=checked, key=f"cb_{s}"):
                 if s not in st.session_state['selected_skills']:
                     st.session_state['selected_skills'].append(s)
             else:
                 if s in st.session_state['selected_skills']:
                     st.session_state['selected_skills'].remove(s)
                    
    with colD:
        st.subheader("Tools")
        for s in tools:
             checked = s in st.session_state['selected_skills']
             if st.checkbox(s, value=checked, key=f"cb_{s}"):
                 if s not in st.session_state['selected_skills']:
                     st.session_state['selected_skills'].append(s)
             else:
                 if s in st.session_state['selected_skills']:
                     st.session_state['selected_skills'].remove(s)

with tab2:
    st.header("Upload Resume")
    pdf_file = st.file_uploader("Upload PDF Resume", type=['pdf'])
    if pdf_file:
        res = parse_resume(pdf_file)
        st.write("Detected Skills:", res['skills'])
        st.write("Detected Experience Levels (Years):", res['years'])
        if st.button("Use these skills", key="btn_pdf"):
            st.session_state['selected_skills'] = res['skills']
            st.session_state['detected_skills'] = res['skills']
            st.session_state['years_exp'] = res['years']
            st.session_state['input_method'] = 'pdf'
            st.success("Skills updated from Resume!")

with tab3:
    st.header("GitHub Profiler")
    gh_user = st.text_input("GitHub Username")
    if st.button("Analyze GitHub"):
        if gh_user:
            with st.spinner("Analyzing..."):
                res = analyse_github_profile(gh_user)
                if 'error' in res:
                    st.error(res['error'])
                else:
                    st.write(f"Found {res['public_repos']} repos.")
                    st.write("Detected Skills:", res['detected_skills'])
                    st.session_state['temp_gh_skills'] = res['detected_skills']
        
    if 'temp_gh_skills' in st.session_state:
        if st.button("Use GitHub skills"):
            st.session_state['selected_skills'] = st.session_state['temp_gh_skills']
            st.session_state['input_method'] = 'github'
            st.success("Skills updated from GitHub!")

with tab4:
    st.header("Job Description Match")
    jd_text = st.text_area("Paste Job Description")
    if st.button("Extract Skills"):
        found = []
        for s in SKILLS_LIST:
            pattern = r'\b' + re.escape(s.lower()) + r'\b'
            if s == 'C++':
                if 'c++' in jd_text.lower():
                    found.append(s)
                continue
            if re.search(pattern, jd_text.lower()):
                found.append(s)
        st.write("Extracted Skills:", found)
        st.session_state['temp_jd_skills'] = found
        
    if 'temp_jd_skills' in st.session_state:
         if st.button("Use as target skills"):
            st.session_state['selected_skills'] = st.session_state['temp_jd_skills']
            st.session_state['input_method'] = 'job_description'
            st.success("Skills updated!")

st.markdown("---")
st.subheader("General Info")

yoe = st.slider("Years of experience", 0, 20, value=st.session_state.get('years_exp', 0))
st.session_state['years_exp'] = yoe

edu = st.selectbox("Education level", [
    "Bachelor’s degree",
    "Master’s degree",
    "Some college/university study without earning a degree",
    "Secondary school (e.g. American high school)",
    "Professional degree",
    "Other doctoral degree",
    "Primary/elementary school",
    "Associate degree",
    "Missing"
])
st.session_state['education'] = edu

country = st.selectbox("Country", ["United States", "India", "United Kingdom", "Germany", "Canada", "France", "Pakistan", "Nigeria", "Brazil", "Indonesia", "Missing"])
from utils.currency import get_currency_info
c_info = get_currency_info(country)
st.caption(f"Salary will be shown in {c_info['code']} ({c_info['sym']})")
st.session_state['country'] = country

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    if st.button("← Back"):
        st.switch_page("main.py")
with c2:
    if st.button("Continue →", type="primary"):
        # Build skill vector
        vector = {}
        for s in SKILLS_LIST:
            vector[f'skill_{s}'] = 1 if s in st.session_state['selected_skills'] else 0
        st.session_state['skill_vector'] = vector
        st.switch_page("pages/2_role_predictor.py")
