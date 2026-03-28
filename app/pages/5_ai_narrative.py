import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.firebase_auth import is_logged_in, get_current_user
from utils.gemini_narrative import generate_career_narrative
from utils.firestore_db import save_analysis
from utils.currency import format_salary

# if not is_logged_in():
#     st.switch_page("pages/2_login.py")

st.progress(0.71, text="Step 5 of 7 — AI Career Narrative")
st.title("AI Career Narrative")

# Session state checks
role = st.session_state.get('predicted_role')
if not role:
    st.error("Missing prediction details. Please go back and complete the earlier steps.")
    st.stop()
    
salary_usd = st.session_state.get('salary_usd', 0.0)
user_country = st.session_state.get('country', 'United States')
sal_str, _, _ = format_salary(salary_usd, user_country)

similarity = st.session_state.get('similarity', 0.0)
missing_skills = st.session_state.get('missing_skills', [])
selected_skills = st.session_state.get('selected_skills', [])
years_exp = st.session_state.get('years_exp', 0)

if st.button("✨ Generate My Career Summary"):
    with st.spinner("Gemini is analyzing your profile..."):
        try:
            narrative = generate_career_narrative(role, sal_str, user_country, similarity, missing_skills, selected_skills, years_exp)
            
            if narrative.startswith("Error") or "Technical Details" in narrative:
                st.error(narrative)
            else:
                st.session_state['narrative'] = narrative
                st.info(narrative) # Display the successful narrative
            
            # Save to Firebase
            user = get_current_user()
            if user:
                # missing_skills is a list of tuples (skill_name, importance) or just strings
                missing_skills_list = [s[0] if isinstance(s, (list, tuple)) else str(s) for s in missing_skills]
                
                data = {
                    'predicted_role': role,
                    'salary_estimate': salary_usd, # Save USD internally
                    'skill_alignment': similarity,
                    'missing_skills': missing_skills_list,
                    'selected_skills': selected_skills,
                    'years_experience': years_exp,
                    'gemini_summary': narrative,
                    'input_method': st.session_state.get('input_method', 'manual')
                }
                try:
                    save_analysis(user['uid'], data)
                    st.success("✅ Analysis saved to your profile")
                except Exception as db_e:
                    st.warning(f"Note: Could not save to cloud: {str(db_e)}")
        except Exception as e:
            st.error(f"There was a problem generating your AI narrative: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

if st.session_state.get('narrative'):
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.switch_page("pages/4_skill_gap.py")
    with col2:
        if st.button("Continue to Roadmap →", type="primary"):
            st.switch_page("pages/6_roadmap.py")

else:
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.switch_page("pages/4_skill_gap.py")

