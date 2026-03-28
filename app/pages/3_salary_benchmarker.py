import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.firebase_auth import is_logged_in
from utils.model_loader import load_models
from utils.currency import format_salary, format_currency_amount, get_currency_info
from utils.feature_names import get_plain_english_shap, get_plain_english_feature
from utils.salary_calibration import calibrate_salary, get_calibrated_salary_range

# if not is_logged_in():
#     st.switch_page("pages/2_login.py")

st.progress(0.42, text="Step 3 of 7 — Salary Prediction")
st.title("Salary Benchmarker")

try:
    models = load_models()
except Exception as e:
    st.warning("Models failed to load! Please run train.py first to generate the models.")
    st.stop()
    
if models is None or models.get('salary_model') is None:
    st.warning("Models not found! Please run train.py first to generate the models.")
    st.stop()

st.subheader("Fine-tune your details")
colA, colB = st.columns(2)
with colA:
    org_size = st.selectbox("Company Size", ["20 to 99 employees", "100 to 499 employees", "10,000 or more employees", "1,000 to 4,999 employees", "2 to 9 employees", "10 to 19 employees", "500 to 999 employees", "Just me - I am a freelancer, sole proprietor, etc.", "5,000 to 9,999 employees", "I don’t know", "Missing"])
with colB:
    remote = st.selectbox("Work Style", ["Remote", "Hybrid (some remote, some in-person)", "In-person", "Missing"])

def get_full_input_df():
    sv = st.session_state.get('skill_vector', {})
    df = pd.DataFrame([sv])
    
    df['fe_signal'] = df.get('skill_React', 0) * df.get('skill_TypeScript', 0)
    df['devops_signal'] = df.get('skill_Docker', 0) * df.get('skill_Kubernetes', 0) * df.get('skill_Linux', 0)
    df['data_signal'] = df.get('skill_Python', 0) * df.get('skill_SQL', 0)
    df['ml_signal'] = df.get('skill_Python', 0) * df.get('skill_FastAPI', 0)
    df['backend_signal'] = df.get('skill_Java', 0) * df.get('skill_SQL', 0)
    df['cloud_signal'] = df.get('skill_AWS', 0) * df.get('skill_Docker', 0)

    skill_cols = [c for c in df.columns if c.startswith('skill_')]
    df['total_skills'] = df.get(skill_cols, pd.DataFrame()).sum(axis=1)

    web_skills = ['skill_React', 'skill_JavaScript', 'skill_TypeScript', 'skill_Node.js', 'skill_Angular', 'skill_Vue.js']
    sys_skills = ['skill_Docker', 'skill_Linux', 'skill_Kubernetes', 'skill_C++', 'skill_Go', 'skill_Rust']
    data_skills = ['skill_Python', 'skill_SQL', 'skill_PostgreSQL', 'skill_MongoDB', 'skill_FastAPI', 'skill_Django']

    df['web_ratio'] = df[[c for c in web_skills if c in df.columns]].sum(axis=1) / (df['total_skills'] + 1)
    df['sys_ratio'] = df[[c for c in sys_skills if c in df.columns]].sum(axis=1) / (df['total_skills'] + 1)
    df['data_ratio'] = df[[c for c in data_skills if c in df.columns]].sum(axis=1) / (df['total_skills'] + 1)

    df['YearsCode'] = st.session_state.get('years_exp', 0)
    
    le_ed = models['le_ed']
    ed_val = st.session_state.get('education', 'Missing')
    if ed_val not in le_ed.classes_: ed_val = 'Missing' if 'Missing' in le_ed.classes_ else le_ed.classes_[0]
    df['ed_encoded'] = le_ed.transform([ed_val])[0]
    
    le_org = models['le_org']
    org_val = org_size if org_size in le_org.classes_ else ('Missing' if 'Missing' in le_org.classes_ else le_org.classes_[0])
    df['org_encoded'] = le_org.transform([org_val])[0]
    
    le_rem = models['le_remote']
    rem_val = remote if remote in le_rem.classes_ else ('Missing' if 'Missing' in le_rem.classes_ else le_rem.classes_[0])
    df['remote_encoded'] = le_rem.transform([rem_val])[0]
    
    le_country = models['le_country']
    c_val = st.session_state.get('country', 'Missing')
    if c_val not in le_country.classes_: c_val = 'Missing' if 'Missing' in le_country.classes_ else le_country.classes_[0]
    df['country_encoded'] = le_country.transform([c_val])[0]
    
    le_role = models['le_role']
    r_val = st.session_state.get('predicted_role', le_role.classes_[0])
    if r_val not in le_role.classes_: r_val = le_role.classes_[0]
    df['role_encoded'] = le_role.transform([r_val])[0]
    
    return df

if st.button("Predict Salary"):
    try:
        df_in = get_full_input_df()
        
        # KEY CORRECTION: Use United States as the benchmark country for prediction.
        # The scale factor (ratio) handles the conversion to the local market.
        # Predicting directly for India AND applying a ratio causes double-adjustment.
        le_country = models['le_country']
        if 'United States' in le_country.classes_:
            df_in['country_encoded'] = le_country.transform(['United States'])[0]
        elif 'United States of America' in le_country.classes_:
            df_in['country_encoded'] = le_country.transform(['United States of America'])[0]

        sal_model = models['salary_model']
        
        features = sal_model.feature_names_in_
        for c in features:
            if c not in df_in.columns:
                df_in[c] = 0
                
        X = df_in[features]
        raw_usd = float(sal_model.predict(X)[0])
    except Exception as e:
        # print(e) # for debug
        st.error("There was a problem making the salary prediction. Please ensure your inputs are complete.")
        st.stop()
        
    user_country = st.session_state.get('country', 'United States')
    years_exp = st.session_state.get('years_exp', 0)
    role = st.session_state.get('predicted_role', 'Unknown')
    
    # Core Country Calibration Logic
    calibrated_usd, c_ratio, exp_mult = calibrate_salary(raw_usd, user_country, years_exp)
    
    curr_info = get_currency_info(user_country)
    sal_str, local_salary, sym = format_salary(calibrated_usd, user_country)
    
    st.session_state['salary'] = local_salary
    st.session_state['currency_sym'] = sym
    st.session_state['salary_usd'] = calibrated_usd # Now save the correctly calibrated USD!
    
    # 3 Things the user requested to see
    # 1. Calibrated salary
    # 2. Market Range
    # 3. Note explaining calibration
    sal_range_str = get_calibrated_salary_range(user_country, years_exp, role, curr_info)
    
    c1, c2, c3, c4 = st.columns(4)
    # The formatted string usually has (approx usd) attached, split it for metric
    c1.metric("Annual Salary", sal_str.split(" (")[0])
    
    # Monthly metric logic specifically for India vs elsewhere
    if user_country == "India":
       monthly = local_salary / 12
       c2.metric("Monthly Salary", f"₹{(monthly):,.0f}")
    else:
       c2.metric("Monthly Salary", f"{sym}{(local_salary/12):,.0f}")
       
    c3.metric("Role", role)
    c4.metric("Experience", f"{years_exp} Years")
    
    if " (" in sal_str:
        st.caption(f"USD Equivalent: approximately ${calibrated_usd:,.0f} USD")
        
    if user_country != "United States" and user_country != "Missing":
        st.info(f"**Note:** Salary calibrated for {user_country} market based on local developer compensation data (Ratio: {c_ratio}). The Stack Overflow survey is US-dominated, so raw predictions are adjusted for your country and experience level. Exchange rates are approximate 2025 averages and actual rates vary.")
    
    # Distribution curve 
    try:
        x_vals = np.linspace(max(0, local_salary - (20000 * c_ratio * exp_mult * curr_info['rate'] * 2)), 
                             local_salary + (20000 * c_ratio * exp_mult * curr_info['rate'] * 2), 100)
        std_dev = 20000 * c_ratio * exp_mult * curr_info['rate']
        y_vals = np.exp(-0.5 * ((x_vals - local_salary) / std_dev)**2)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, fill='tozeroy', name='Market Range', line=dict(color='#7F77DD')))
        fig.add_vline(x=local_salary, line_dash="dash", line_color="#E24B4A", annotation_text="Your Salary")
        fig.update_layout(title=f"Estimated Salary Distribution for {user_country}", xaxis_title=f"Annual Salary ({sym})", yaxis_title="Density", yaxis_visible=False)
        st.plotly_chart(fig)
        st.caption(sal_range_str) # Plotly caption now contains the exact market range logic
    except Exception as e:
        st.warning("Could not render the distribution chart.")
        st.write(sal_range_str)
        
    # SHAP logic
    try:
        explainer = models.get('shap_explainer')
        if explainer is not None:
            st.subheader("What drives your salary?")
            
            # Calibration multiplier applied globally to SHAP values
            scale_factor = c_ratio * exp_mult
            
            if isinstance(explainer, dict) and 'fallback_importances' in explainer:
                importances = explainer['fallback_importances']
                feat_imp = pd.Series(importances).sort_values(ascending=False).head(10)
                
                pe_index = [get_plain_english_feature(f) for f in feat_imp.index]
                pe_index_rev = list(reversed(pe_index))
                feat_vals_rev = list(reversed(feat_imp.values))
                
                fig_shap = go.Figure(go.Bar(
                    x=feat_vals_rev, y=pe_index_rev, orientation='h', marker_color='#1D9E75'
                ))
                fig_shap.update_layout(title="Top Salary Drivers (Feature Importance)", xaxis_title="Impact Level")
                st.plotly_chart(fig_shap)
                st.caption("These are the most impactful skills determining your salary potential.")
            else:
                # Normal SHAP - Handle different versions of SHAP output
                shap_data = explainer(X)
                
                # Check if it's an Explanation object (new API) or array (old API)
                if hasattr(shap_data, 'values'):
                    shap_vals = shap_data.values[0] if len(shap_data.values.shape) > 1 else shap_data.values
                    base_value = shap_data.base_values[0] if hasattr(shap_data.base_values, '__len__') else shap_data.base_values
                else:
                    shap_vals = shap_data[0] if len(shap_data.shape) > 1 else shap_data
                    base_value = explainer.expected_value
                
                # Apply calibration scaling
                shap_vals = shap_vals * scale_factor
                base_value = base_value * scale_factor
                diff = sum(shap_vals)
                
                # Combine features with small impacts
                imp_df = pd.DataFrame({'feature': features, 'val': shap_vals})
                imp_df['abs_val'] = imp_df['val'].abs()
                imp_df = imp_df.sort_values(by='abs_val', ascending=False)
                
                top_features = imp_df.head(10)
                
                # Display values in English
                pe_labels = [get_plain_english_shap(f, X.iloc[0][f]) for f in top_features['feature']]
                vals = top_features['val'].values
                # Format text
                text_vals = [("+" if v > 0 else "") + format_currency_amount(v, user_country) for v in vals]
                colors = ['#1D9E75' if v > 0 else '#E24B4A' for v in vals]
                
                # ADD "Other Factors" bar to balance the math
                top_10_sum = sum(vals)
                other_sum = diff - top_10_sum
                
                if abs(other_sum) > 500: # Only add if significant
                    pe_labels = list(pe_labels) + ["Miscellaneous Factors"]
                    vals = np.append(vals, other_sum)
                    text_vals = list(text_vals) + [("+" if other_sum > 0 else "") + format_currency_amount(other_sum, user_country)]
                    colors = list(colors) + ["#777777"]

                pe_labels_rev = list(reversed(pe_labels))
                vals_rev = list(reversed(vals))
                text_vals_rev = list(reversed(text_vals))
                colors_rev = list(reversed(colors))
                
                fig_shap = go.Figure(go.Bar(
                    x=vals_rev, y=pe_labels_rev, orientation='h', text=text_vals_rev, textposition='outside',
                    marker_color=colors_rev
                ))
                fig_shap.update_layout(
                    title="Salary Profile Adjustments", 
                    xaxis_title=f"Impact amount ({sym})", 
                    yaxis_title="Profile Factor",
                    margin=dict(l=200, r=100), # Add space for labels
                    height=max(400, 40 * len(pe_labels_rev))
                )
                st.plotly_chart(fig_shap)
                
                with st.expander("Why are some traits negative?"):
                    st.write("""
                    **The Experience Paradox:** The model compares your profile to the 'Market Average'. If the baseline is based on a global average of 12+ years of seniority, having 5 years will appear as a 'reducer' relative to that benchmark, even though it's positive in real-world terms.
                    
                    **Skill Specialization:** Sometimes knowing a generic skill (like MySQL) is viewed by the model as less specialized than the requirements for high-paying roles (like Kubernetes), leading to a 'reduction' compared to a hyper-specialized profile.
                    """)
                
                st.subheader("Salary Drivers Summary")
                card1, card2, card3 = st.columns(3)
                card1.metric("Market Average", format_currency_amount(base_value, user_country, always_full=True))
                
                card2.metric("Your Profile Impact", ("+" if diff>0 else "") + format_currency_amount(diff, user_country, always_full=True))
                card3.metric("Estimated Salary", format_currency_amount(calibrated_usd, user_country, always_full=True))
                
                # FIXED LOGIC: Find the actual highest booster and reducer
                boosters = imp_df[imp_df['val'] > 0]
                reducers = imp_df[imp_df['val'] < 0]
                
                if not boosters.empty:
                    max_feat = boosters.iloc[0]['feature']
                    st.write(f"Your biggest salary booster is **{get_plain_english_shap(max_feat, X.iloc[0][max_feat])}**.")
                else:
                    st.write("Your profile is currently tracking exactly at or below the market average for your role.")
                    
                if not reducers.empty:
                    min_feat = reducers.iloc[-1]['feature'] if not reducers.empty else None # Sort order check
                    # Actually imp_df is sorted by abs value. Let's find real min.
                    real_min_idx = np.argmin(shap_vals)
                    st.write(f"Your biggest salary reducer is **{get_plain_english_shap(features[real_min_idx], X.iloc[0][features[real_min_idx]])}**.")
                
                if user_country in ["India", "Pakistan", "Nigeria", "Brazil", "Indonesia"]:
                    st.info("Note: Your country is classified as a developing nation. While the USD-converted salary may appear lower globally, your local purchasing power is likely much higher.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        st.warning("Could not render the detailed salary drivers analysis.")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("← Back"):
        st.switch_page("pages/2_role_predictor.py")
with col2:
    if st.button("Continue →", type="primary"):
        st.switch_page("pages/4_skill_gap.py")
