import streamlit as st
import joblib
import os


def _safe_load(path):
    # Load one saved file. If it fails, return None instead of crashing the page.
    try:
        return joblib.load(path)
    except Exception as e:
        print(f"Could not load {os.path.basename(path)}: {e}")
        return None


def _load_shap_explainer(models_dir, salary_model):
    # 1. Try the saved explainer file first.
    explainer = _safe_load(os.path.join(models_dir, 'shap_explainer.pkl'))
    if explainer is not None:
        return explainer

    # 2. The saved file was made with a different SHAP version.
    #    Build a fresh explainer from the salary model instead.
    if salary_model is None:
        return None
    try:
        import shap
        return shap.TreeExplainer(salary_model)
    except Exception as e:
        print(f"Could not rebuild SHAP explainer: {e}")

    # 3. Last option: use the model's own feature importances.
    try:
        names = list(salary_model.feature_names_in_)
        values = salary_model.feature_importances_
        return {'fallback_importances': dict(zip(names, values))}
    except Exception:
        return None


@st.cache_resource
def load_models():
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')

    if not os.path.exists(os.path.join(models_dir, 'role_model.pkl')):
        return None

    files = {
        'role_model': 'role_model.pkl',
        'salary_model': 'salary_model.pkl',
        'role_profiles': 'role_skill_profiles.pkl',
        'le_role': 'le_role.pkl',
        'le_country': 'le_country.pkl',
        'le_org': 'le_org.pkl',
        'le_remote': 'le_remote.pkl',
        'le_ed': 'le_ed.pkl',
    }

    models = {}
    for key, filename in files.items():
        models[key] = _safe_load(os.path.join(models_dir, filename))

    models['shap_explainer'] = _load_shap_explainer(models_dir, models['salary_model'])
    return models


def match_education(le_ed, ed_val):
    # The dropdown shows short names like "Bachelor’s degree", but the model
    # was trained on full survey names like "Bachelor’s degree (B.A., B.S., ...)".
    # Find the full name that starts with the short name.
    if ed_val in le_ed.classes_:
        return ed_val
    short = str(ed_val).split(' (')[0]
    for full_name in le_ed.classes_:
        if full_name.startswith(short):
            return full_name
    if 'Missing' in le_ed.classes_:
        return 'Missing'
    return le_ed.classes_[0]
