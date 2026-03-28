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

# Build user vector matching the exact columns of role_profiles
target_profile = role_profiles.loc[predicted_role].values
skill_cols = role_profiles.columns

sv = st.session_state.get('skill_vector', {})
user_vector = np.array([sv.get(c, 0) for c in skill_cols])

try:
    sim = cosine_similarity([user_vector], [target_profile])[0][0]
    st.session_state['similarity'] = float(sim * 100)
    
    colA, colB = st.columns(2)
    with colA:
        st.metric("Total Skill Alignment", f"{sim*100:.1f}%")
    with colB:
        core_match_pct = st.session_state.get('core_match_pct', 0)
        st.metric("Core Role Match", f"{core_match_pct:.1f}%", help="This measures how well your specific skills match the high-priority requirements for this role.")
        
    with st.expander("ℹ️ Understanding these scores (Specialization vs. Breadth)"):
        st.write(f"""
        **Total Skill Alignment ({sim*100:.1f}%)**: This measures your profile's 'orientation' against the complete industry standard. It's often lower for specialists because it accounts for every secondary tool (like Docker, Linux, or SQL) that pros in this role typically know.
                 
        **Core Role Match ({core_match_pct:.1f}%)**: This is more encouraging! It specifically highlights that you have mastered the **foundational skills** required for a {predicted_role}. 
                 
        *Conclusion:* You are a strong candidate on fundamentals, but building 'breadth' in the missing areas below will significantly increase your market value.
        """)
except Exception as e:
    st.error("Failed to calculate skill alignment.")
    st.stop()

# Find missing skills (user = 0, role average >= threshold)
missing = []
for i, col in enumerate(skill_cols):
    if user_vector[i] == 0:
        # Lowered threshold to 15% to provide more comprehensive suggestions for niche roles
        if target_profile[i] >= 0.15:
            missing.append((col.replace('skill_', ''), target_profile[i]))

# rank by importance
missing.sort(key=lambda x: x[1], reverse=True)
top_missing = missing[:5]
st.session_state['missing_skills'] = top_missing

# Calculate Core Match (specifically for skills the user DOES have that are important)
core_matches = []
for i, col in enumerate(skill_cols):
    if user_vector[i] == 1 and target_profile[i] >= 0.1:
        core_matches.append(target_profile[i])

core_match_pct = (sum(core_matches) / sum(target_profile)) * 100 if sum(target_profile) > 0 else 0
st.session_state['core_match_pct'] = core_match_pct

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
        st.write(f"**{skill}** (Current usage in role: {imp*100:.0f}%)")
        # Ensure progress bar value is between 0 and 1
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
