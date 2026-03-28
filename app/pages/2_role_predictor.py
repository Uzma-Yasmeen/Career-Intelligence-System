import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.firebase_auth import is_logged_in
from utils.model_loader import load_models

# if not is_logged_in():
#     st.switch_page("pages/2_login.py")

st.progress(0.28, text="Step 2 of 7 — Role Prediction")
st.title("Role Predictor")

models = load_models()
if models is None or models.get('role_model') is None:
    st.warning("Models not found! Please run train.py first to generate the models.")
    st.stop()

def get_input_df():
    sv = st.session_state.get('skill_vector', {})
    df = pd.DataFrame([sv])

    df['fe_signal'] = df.get('skill_React', 0) * df.get('skill_TypeScript', 0)
    df['devops_signal'] = df.get('skill_Docker', 0) * df.get('skill_Kubernetes', 0) * df.get('skill_Linux', 0)
    df['data_signal'] = df.get('skill_Python', 0) * df.get('skill_SQL', 0)
    df['ml_signal'] = df.get('skill_Python', 0) * df.get('skill_FastAPI', 0)
    df['backend_signal'] = df.get('skill_Java', 0) * df.get('skill_SQL', 0)
    df['cloud_signal'] = df.get('skill_AWS', 0) * df.get('skill_Docker', 0)

    skill_cols = [c for c in df.columns if c.startswith('skill_')]
    df['total_skills'] = df[skill_cols].sum(axis=1)

    web_skills = ['skill_React', 'skill_JavaScript', 'skill_TypeScript', 'skill_Node.js', 'skill_Angular', 'skill_Vue.js']
    sys_skills = ['skill_Docker', 'skill_Linux', 'skill_Kubernetes', 'skill_C++', 'skill_Go', 'skill_Rust']
    data_skills = ['skill_Python', 'skill_SQL', 'skill_PostgreSQL', 'skill_MongoDB', 'skill_FastAPI', 'skill_Django']

    df['web_ratio'] = df[[c for c in web_skills if c in df.columns]].sum(axis=1) / (df['total_skills'] + 1)
    df['sys_ratio'] = df[[c for c in sys_skills if c in df.columns]].sum(axis=1) / (df['total_skills'] + 1)
    df['data_ratio'] = df[[c for c in data_skills if c in df.columns]].sum(axis=1) / (df['total_skills'] + 1)

    df['YearsCode'] = st.session_state.get('years_exp', 0)

    le_ed = models['le_ed']
    ed_val = st.session_state.get('education', 'Missing')
    if ed_val not in le_ed.classes_:
        ed_val = le_ed.classes_[0]
    df['ed_encoded'] = le_ed.transform([ed_val])[0]

    le_org = models['le_org']
    df['org_encoded'] = le_org.transform([le_org.classes_[0]])[0]

    le_rem = models['le_remote']
    df['remote_encoded'] = le_rem.transform([le_rem.classes_[0]])[0]

    le_country = models['le_country']
    c_val = st.session_state.get('country', 'Missing')
    if c_val not in le_country.classes_:
        c_val = le_country.classes_[0]
    df['country_encoded'] = le_country.transform([c_val])[0]

    return df, skill_cols

df_in, skill_cols = get_input_df()

role_model = models['role_model']
le_role = models['le_role']

features = role_model.feature_names_in_
missing_cols = [c for c in features if c not in df_in.columns]
for c in missing_cols:
    df_in[c] = 0

try:
    X = df_in[features]
    probs = role_model.predict_proba(X)[0]
    role_classes = le_role.inverse_transform(role_model.classes_)
except Exception as e:
    st.error("Prediction failed. Please go back and ensure your profile is complete.")
    if st.button("← Go Back"):
        st.switch_page("pages/1_profile_builder.py")
    st.stop()

# Sort roles by probability descending
role_probs = list(zip(role_classes, probs))
role_probs.sort(key=lambda x: x[1], reverse=True)

predicted_role = role_probs[0][0]
confidence = role_probs[0][1] * 100

st.session_state['predicted_role'] = predicted_role
st.session_state['role_probs'] = role_probs

# ── Prediction heading ────────────────────────────────────
st.success(f"### Best Match: **{predicted_role}** — AI Confidence: {confidence:.1f}%")

# ── Confidence bar chart ──────────────────────────────────
try:
    # Reverse so highest probability appears at top visually
    rp_reversed = list(reversed(role_probs))

    # Verify sync
    if rp_reversed[-1][0] != predicted_role:
        st.error("Chart sorting mismatch detected.")

    bar_colors = [
        '#7F77DD' if r[0] == predicted_role else '#CECBF6'
        for r in rp_reversed
    ]

    fig = go.Figure(go.Bar(
        x=[r[1] * 100 for r in rp_reversed],
        y=[r[0] for r in rp_reversed],
        orientation='h',
        marker_color=bar_colors,
        text=[f"{r[1]*100:.1f}%" for r in rp_reversed],
        textposition='outside',
        textfont=dict(size=12)
    ))
    fig.add_annotation(
        x=confidence + 2,
        y=predicted_role,
        text="⭐ Best Match",
        showarrow=False,
        font=dict(size=12, color='#3C3489'),
        xanchor='left'
    )
    fig.update_layout(
        title=f"Role confidence — {predicted_role} is your top match",
        xaxis=dict(
            title="Confidence %",
            range=[0, 130],
            ticksuffix='%',
            showgrid=False
        ),
        yaxis=dict(showgrid=False),
        height=350,
        margin=dict(l=200, r=120, t=60, b=40),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"The model analysed your skills and experience "
        f"to predict your best-fit role. "
        f"Purple = your top match."
    )
except Exception as e:
    st.warning("Could not render the role chart.")
    st.dataframe(pd.DataFrame(role_probs, columns=["Role", "Probability"]))

# ── Why you match this role ───────────────────────────────
st.markdown("---")
st.subheader(f"Why you match {predicted_role}")

try:
    role_profiles = models.get('role_profiles', None)
    skill_vector = st.session_state.get('skill_vector', {})

    if role_profiles is not None and not role_profiles.empty:
        if predicted_role in role_profiles.index:
            role_profile = role_profiles.loc[predicted_role]
            profile_skill_cols = [
                c for c in role_profiles.columns
                if c.startswith('skill_')
            ]

            # Skills user HAS that match the role
            matching = []
            for col in profile_skill_cols:
                user_has = float(skill_vector.get(col, 0))
                role_avg = float(role_profile.get(col, 0))
                if user_has == 1 and role_avg >= 0.25:
                    skill_name = col.replace('skill_', '')
                    pct = round(role_avg * 100)
                    matching.append((skill_name, pct))

            # Sort by role average descending
            matching.sort(key=lambda x: x[1], reverse=True)
            top_matching = matching[:5]

            if top_matching:
                st.markdown(
                    f"These skills you already have are "
                    f"highly valued by {predicted_role}s:"
                )
                for skill, pct in top_matching:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"✅ **{skill}**")
                        st.progress(pct / 100)
                    with col2:
                        st.markdown(
                            f"<div style='padding-top:8px;"
                            f"color:#1D9E75;font-weight:500'>"
                            f"{pct}% of {predicted_role}s "
                            f"have this</div>",
                            unsafe_allow_html=True
                        )
            else:
                st.info(
                    f"Add more skills to see what matches "
                    f"the {predicted_role} role."
                )
except Exception as e:
    pass

# ── Scatter plot ──────────────────────────────────────────
st.markdown("---")

@st.cache_data
def load_scatter_data():
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data', 'clean_survey.csv'
    )
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

df_clean = load_scatter_data()

if not df_clean.empty:
    try:
        colors = [
            '#7F77DD', '#1D9E75', '#D85A30', '#378ADD',
            '#639922', '#D4537E', '#EF9F27', '#E24B4A',
            '#888780'
        ]
        fig2 = go.Figure()
        roles_in_data = df_clean['PrimaryRole'].unique()
        for i, r in enumerate(roles_in_data):
            sub = df_clean[df_clean['PrimaryRole'] == r]
            fig2.add_trace(go.Scatter(
                x=sub['YearsCode'],
                y=sub['total_skills'],
                mode='markers',
                name=r,
                marker=dict(
                    size=5,
                    opacity=0.35,
                    color=colors[i % len(colors)]
                ),
                hovertemplate=(
                    f"<b>{r}</b><br>"
                    "Experience: %{x} yrs<br>"
                    "Skills: %{y}<extra></extra>"
                )
            ))

        # User star
        user_skills_count = int(
            df_in['total_skills'].values[0])
        user_years = st.session_state.get('years_exp', 0)

        fig2.add_trace(go.Scatter(
            x=[user_years],
            y=[user_skills_count],
            mode='markers',
            name='⭐ You',
            marker=dict(
                size=20,
                color='gold',
                symbol='star',
                line=dict(width=2, color='#3C3489')
            ),
            hovertemplate=(
                "<b>You</b><br>"
                f"Experience: {user_years} yrs<br>"
                f"Skills: {user_skills_count}"
                "<extra></extra>"
            )
        ))

        fig2.update_layout(
            title="You (⭐) among real developers",
            xaxis_title="Years of Coding Experience",
            yaxis_title="Number of Skills Known",
            height=450,
            legend=dict(
                orientation='h',
                y=-0.25,
                font=dict(size=10)
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(
            "Each dot is a real developer from the "
            "Stack Overflow 2025 survey. "
            "The gold star shows where your profile sits."
        )
    except Exception as e:
        st.warning("Could not render the scatter plot.")
else:
    st.info("Scatter plot data not found. Run train.py first.")

# ── Navigation ────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("← Back"):
        st.switch_page("pages/1_profile_builder.py")
with col2:
    if st.button("Continue →", type="primary"):
        st.switch_page("pages/3_salary_benchmarker.py")