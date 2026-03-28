import streamlit as st
import joblib
import os
import shap

@st.cache_resource
def load_models():
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    
    if not os.path.exists(os.path.join(models_dir, 'role_model.pkl')):
        # Avoid crashing if models don't exist yet, return None or dummies
        return None
        
    models = {
        'role_model': joblib.load(os.path.join(models_dir, 'role_model.pkl')),
        'salary_model': joblib.load(os.path.join(models_dir, 'salary_model.pkl')),
        'shap_explainer': joblib.load(os.path.join(models_dir, 'shap_explainer.pkl')),
        'role_profiles': joblib.load(os.path.join(models_dir, 'role_skill_profiles.pkl')),
        'le_role': joblib.load(os.path.join(models_dir, 'le_role.pkl')),
        'le_country': joblib.load(os.path.join(models_dir, 'le_country.pkl')),
        'le_org': joblib.load(os.path.join(models_dir, 'le_org.pkl')),
        'le_remote': joblib.load(os.path.join(models_dir, 'le_remote.pkl')),
        'le_ed': joblib.load(os.path.join(models_dir, 'le_ed.pkl'))
    }
    return models
