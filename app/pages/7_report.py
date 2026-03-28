import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.firebase_auth import is_logged_in
from utils.report_generator import generate_pdf_report
from utils.currency import format_salary

# if not is_logged_in():
#     st.switch_page("pages/2_login.py")

st.progress(1.0, text="Complete! Step 7 of 7 — Download Report 🎉")
st.title("📄 Download PDF Report")

role = st.session_state.get('predicted_role')
if not role:
    st.error("No valid analysis found. Please run the predictors first.")
    if st.button("← Go Back"):
        st.switch_page("pages/6_roadmap.py")
    st.stop()

salary_usd = st.session_state.get('salary_usd', 0.0)
user_country = st.session_state.get('country', 'United States')
sal_str, _, _ = format_salary(salary_usd, user_country)

similarity = st.session_state.get('similarity', 0.0)
missing_skills = st.session_state.get('missing_skills', [])
selected_skills = st.session_state.get('selected_skills', [])
years_exp = st.session_state.get('years_exp', 0)
narrative = st.session_state.get('narrative', 'No narrative generated.')

try:
    pdf_buf = generate_pdf_report(
        role=role, 
        salary_str=sal_str, 
        similarity=similarity, 
        missing_skills=missing_skills, 
        selected_skills=selected_skills, 
        years_exp=years_exp, 
        narrative=narrative
    )

    st.success("Your report is ready!")

    col_mid1, col_mid2 = st.columns(2)
    with col_mid1:
        st.download_button(
            label="Download Report as PDF",
            data=pdf_buf,
            file_name="AI_Career_Intelligence_Report.pdf",
            mime="application/pdf",
            type="primary"
        )
except Exception as e:
    st.error("There was a problem generating the PDF report. Data may contain incompatible characters.")
    st.info("You can still take screenshots of the previous pages to save your analysis.")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("← Back to Roadmap"):
        st.switch_page("pages/6_roadmap.py")

with col2:
    if st.button("Start New Analysis"):
        for key in ['selected_skills', 'skill_vector', 'predicted_role', 'salary', 'salary_usd', 'similarity', 'missing_skills', 'narrative', 'balloons_shown']:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("pages/1_profile_builder.py")
