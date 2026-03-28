import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.firebase_auth import is_logged_in
from utils.model_loader import load_models

# if not is_logged_in():
#     st.switch_page("pages/2_login.py")

st.progress(0.57, text="Step 4 of 7 — Skill Gap Analysis")
st.title("Skill Gap Analysis")

try:
    models = load_models()
except Exception as e:
    st.error("Failed to load models. Please run train.py first.")
    st.stop()
    
if models is None or models.get('role_profiles') is None:
    st.warning("Models not found! Please run train.py first.")
    st.stop()

role_profiles = models['role_profiles']
if role_profiles.empty:
    st.warning("Role profiles are empty. Please re-run train.py.")
    st.stop()

predicted_role = st.session_state.get('predicted_role', None)

if predicted_role is None or predicted_role not in role_profiles.index:
    st.error("No valid predicted role found in session. Go back and re-run predictors.")
    if st.button("← Go Back"):
        st.switch_page("pages/2_role_predictor.py")
    st.stop()

# --- CALCULATION LOGIC (BEFORE UI) ---
# Build user vector matching the exact columns of role_profiles
target_profile = role_profiles.loc[predicted_role].values
skill_cols = role_profiles.columns

sv = st.session_state.get('skill_vector', {})
user_vector = np.array([sv.get(c, 0) for c in skill_cols])

# 1. Total Alignment (Cosine)
try:
    sim = cosine_similarity([user_vector], [target_profile])[0][0]
    st.session_state['similarity'] = float(sim * 100)
except:
    sim = 0

# 2. Missing Skills (Top 5)
missing = []
for i, col in enumerate(skill_cols):
    if user_vector[i] == 0:
        if target_profile[i] >= 0.15:
            missing.append((col.replace('skill_', ''), target_profile[i]))
missing.sort(key=lambda x: x[1], reverse=True)
top_missing = missing[:5]
st.session_state['missing_skills'] = top_missing

# 3. Core Competency Score (weighted match on Top 5 skills used in the role)
top_5_indices = target_profile.argsort()[-5:][::-1]
user_has_count = sum([user_vector[i] for i in top_5_indices])
core_comp_score = (user_has_count / 5.0) * 100
st.session_state['core_comp_score'] = core_comp_score

# --- UI SECTION ---
colA, colB = st.columns(2)
with colA:
    st.metric("Overall Profile Match", f"{sim*100:.1f}%")
with colB:
    st.metric("Core Competency Score", f"{core_comp_score:.1f}%", help="Out of the top 5 foundational skills for this role, how many do you have?")
    
with st.expander("ℹ️ Understanding these scores (Specialization vs. Breadth)"):
    st.write(f"""
    **Overall Profile Match ({sim*100:.1f}%)**: This measures your profile's 'orientation' against the complete industry standard. It's often lower for specialists because it accounts for every secondary tool (like Docker, Linux, or SQL) that pros in this role typically know.
                
    **Core Competency Score ({core_comp_score:.1f}%)**: This specifically highlights that you have mastered **{user_has_count} out of the Top 5 foundational skills** required for a {predicted_role}. 
                
    *Conclusion:* You are a strong candidate on fundamentals, but building 'breadth' in the missing areas below will significantly increase your market value.
    """)

# Radar Chart
try:
    # get top 8 skills for this role
    top_8_indices = target_profile.argsort()[-8:][::-1]
    top_8_skills = [skill_cols[i].replace('skill_', '') for i in top_8_indices]
    role_top_8_vals = target_profile[top_8_indices]
    user_top_8_vals = user_vector[top_8_indices]

    # close polygon by repeating first val
    theta = top_8_skills + [top_8_skills[0]]
    r_role = list(role_top_8_vals) + [role_top_8_vals[0]]
    r_user = list(user_top_8_vals) + [user_top_8_vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
          r=r_role,
          theta=theta,
          fill='toself',
          name=f'{predicted_role} Average',
          line_color='#7F77DD'
    ))
    fig.add_trace(go.Scatterpolar(
          r=r_user,
          theta=theta,
          fill='toself',
          name='Your Profile',
          line_color='#1D9E75'
    ))

    fig.update_layout(
      polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
      showlegend=True,
      title="Your Profile vs Role Benchmark"
    )

    st.plotly_chart(fig)
    st.caption("This radar chart visualizes how your current skillset aligns with the typical requirements for this role.")
except Exception as e:
    st.warning("Could not render the radar chart.")

st.subheader(f"Top 5 Skills to Learn for {predicted_role}")
if top_missing:
    for skill, imp in top_missing:
        st.write(f"**{skill}** (Usage in role: {imp*100:.0f}%)")
        st.progress(float(min(max(imp, 0.0), 1.0)))
else:
    st.success("You have no major missing skills for this role!")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("← Back"):
        st.switch_page("pages/3_salary_benchmarker.py")
with col2:
    if st.button("Continue →", type="primary"):
        st.switch_page("pages/5_ai_narrative.py")
