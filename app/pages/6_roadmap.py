import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.firebase_auth import is_logged_in
from utils.currency import format_salary

# if not is_logged_in():
#     st.switch_page("pages/2_login.py")

st.progress(0.85, text="Step 6 of 7 — Learning Roadmap")
st.title("90-Day Learning Roadmap")

role = st.session_state.get('predicted_role')
if not role:
    st.error("Missing prediction details. Please go back and complete the earlier steps.")
    if st.button("← Go Back"):
        st.switch_page("pages/5_ai_narrative.py")
    st.stop()

salary_usd = st.session_state.get('salary_usd', 0.0)
user_country = st.session_state.get('country', 'United States')
sal_str, _, _ = format_salary(salary_usd, user_country)

similarity = st.session_state.get('similarity', 0.0)
missing_skills = st.session_state.get('missing_skills', [])
narrative = st.session_state.get('narrative', '')

try:
    st.success(f"### Goal: {role} | Est. Salary: {sal_str} | Alignment: {similarity:.1f}%")

    if narrative:
        with st.expander("Your AI Career Narrative", expanded=False):
            st.write(narrative)

    st.subheader("Action Plan to Close Skill Gaps")

    for idx, (skill, imp) in enumerate(missing_skills):
        with st.expander(f"Week {idx*2 + 1}-{idx*2 + 2}: Master {skill}"):
            st.markdown(f"**Timeline:** Weeks {idx*2 + 1}–{idx*2 + 2}")
            if imp >= 0.5:
                st.markdown("**Priority:** Critical")
            elif imp >= 0.3:
                st.markdown("**Priority:** Important")
            else:
                st.markdown("**Priority:** Optional")
                
            st.markdown(f"**Best Resource:** [Search {skill} courses on Coursera](https://www.coursera.org/search?query={skill})")
            st.markdown(f"*Usage in the {role} role:*")
            st.progress(float(min(max(imp, 0.0), 1.0)))
            
    if 'balloons_shown' not in st.session_state:
        st.balloons()
        st.session_state['balloons_shown'] = True
except Exception as e:
    st.error("There was a problem rendering the roadmap.")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("← Back"):
        st.switch_page("pages/5_ai_narrative.py")
with col2:
    if st.button("📄 Download PDF Report", type="primary"):
        st.switch_page("pages/7_report.py")
