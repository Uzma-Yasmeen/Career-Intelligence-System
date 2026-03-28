import os
import sys
import traceback
import importlib.util

sys.path.append(r"c:\Users\Admin\Desktop\Projects\SRU_Projects\ai-career-intelligence")

spec = importlib.util.spec_from_file_location("6_skill_gap", r"c:\Users\Admin\Desktop\Projects\SRU_Projects\ai-career-intelligence\app\pages\6_skill_gap.py")
module = importlib.util.module_from_spec(spec)

try:
    # Mock st environment roughly to bypass is_logged_in and session_state
    import streamlit as st
    st.session_state['user'] = {'uid': 1}
    st.session_state['predicted_role'] = 'Full Stack Developer'
    st.session_state['skill_vector'] = {}
    spec.loader.exec_module(module)
    print("Successfully loaded 6_skill_gap.py")
except Exception as e:
    print("Failed on execution:")
    traceback.print_exc()
