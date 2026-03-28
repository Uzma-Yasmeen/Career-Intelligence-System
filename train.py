import pandas as pd
import numpy as np
import joblib
import os
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, r2_score, mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from xgboost import XGBRegressor

def build_models():
    print("Loading dataset...")
    df = pd.read_csv('data/survey_results_public.csv')

    # ROLE MAPPING
    role_map = {
        'Developer, full-stack': 'Full Stack Developer',
        'Developer, back-end': 'Backend Developer',
        'Developer, front-end': 'Frontend Developer',
        'Developer, mobile': 'Mobile Developer',
        'Developer, desktop or enterprise applications': 'SDE',
        'Developer, embedded applications or devices': 'SDE',
        'Architect, software or solutions': 'SDE',
        'DevOps engineer or professional': 'DevOps Engineer',
        'Data engineer': 'Data Engineer',
        'Data scientist': 'Data Scientist',
        'AI/ML engineer': 'ML Engineer',
        'Cloud infrastructure engineer': 'DevOps Engineer',
        'Engineering manager': 'SDE'
    }

    print("Cleaning data...")
    df = df.dropna(subset=['DevType'])
    df['PrimaryRole'] = df['DevType'].apply(lambda x: str(x).split(';')[0])
    df['PrimaryRole'] = df['PrimaryRole'].map(role_map)
    df = df.dropna(subset=['PrimaryRole'])

    # SKILLS TO ENCODE
    languages = ['Python', 'JavaScript', 'TypeScript', 'Java', 'SQL', 'C++', 'Go', 'Rust']
    databases = ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis']
    webframes = ['React', 'Node.js', 'Vue.js', 'Django', 'FastAPI', 'Angular']
    platforms = ['Docker', 'AWS', 'Kubernetes', 'Google Cloud', 'Azure']
    office = ['Git']
    opsys = ['Linux']

    def encode_skills(df, col, skills):
        for skill in skills:
            df[f'skill_{skill}'] = df[col].apply(lambda x: 1 if pd.notna(x) and str(skill) in str(x).split(';') else 0)

    encode_skills(df, 'LanguageHaveWorkedWith', languages)
    encode_skills(df, 'DatabaseHaveWorkedWith', databases)
    encode_skills(df, 'WebframeHaveWorkedWith', webframes)
    encode_skills(df, 'PlatformHaveWorkedWith', platforms)
    encode_skills(df, 'OfficeStackAsyncHaveWorkedWith', office)
    
    # OS has a space
    for skill in opsys:
        df[f'skill_{skill}'] = df['OpSysProfessional use'].apply(
            lambda x: 1 if pd.notna(x) and skill in str(x) else 0
        )

    # ENGINEERED FEATURES
    df['fe_signal'] = df['skill_React'] * df['skill_TypeScript']
    df['devops_signal'] = df['skill_Docker'] * df['skill_Kubernetes'] * df['skill_Linux']
    df['data_signal'] = df['skill_Python'] * df['skill_SQL']
    df['ml_signal'] = df['skill_Python'] * df['skill_FastAPI']
    df['backend_signal'] = df['skill_Java'] * df['skill_SQL']
    df['cloud_signal'] = df['skill_AWS'] * df['skill_Docker']

    skill_cols = [col for col in df.columns if col.startswith('skill_')]
    df['total_skills'] = df[skill_cols].sum(axis=1)

    web_skills = ['skill_React', 'skill_JavaScript', 'skill_TypeScript', 'skill_Node.js', 'skill_Angular', 'skill_Vue.js']
    sys_skills = ['skill_Docker', 'skill_Linux', 'skill_Kubernetes', 'skill_C++', 'skill_Go', 'skill_Rust']
    data_skills = ['skill_Python', 'skill_SQL', 'skill_PostgreSQL', 'skill_MongoDB', 'skill_FastAPI', 'skill_Django']

    df['web_ratio'] = df[web_skills].sum(axis=1) / (df['total_skills'] + 1)
    df['sys_ratio'] = df[sys_skills].sum(axis=1) / (df['total_skills'] + 1)
    df['data_ratio'] = df[data_skills].sum(axis=1) / (df['total_skills'] + 1)

    engineered = ['fe_signal', 'devops_signal', 'data_signal', 'ml_signal', 'backend_signal', 'cloud_signal', 
                  'total_skills', 'web_ratio', 'sys_ratio', 'data_ratio']

    # YearsCode
    df['YearsCode'] = pd.to_numeric(df['YearsCode'].replace('Less than 1 year', 0).replace('More than 50 years', 51), errors='coerce').fillna(0)

    # Clean missing for categorical and encode
    df['EdLevel'] = df['EdLevel'].fillna('Missing')
    df['OrgSize'] = df['OrgSize'].fillna('Missing')
    df['RemoteWork'] = df['RemoteWork'].fillna('Missing')
    df['Country'] = df['Country'].fillna('Missing')

    le_role = LabelEncoder()
    df['role_encoded'] = le_role.fit_transform(df['PrimaryRole'])

    le_country = LabelEncoder()
    df['country_encoded'] = le_country.fit_transform(df['Country'])

    le_org = LabelEncoder()
    df['org_encoded'] = le_org.fit_transform(df['OrgSize'])

    le_remote = LabelEncoder()
    df['remote_encoded'] = le_remote.fit_transform(df['RemoteWork'])

    le_ed = LabelEncoder()
    df['ed_encoded'] = le_ed.fit_transform(df['EdLevel'])

    os.makedirs('models', exist_ok=True)
    joblib.dump(le_role, 'models/le_role.pkl')
    joblib.dump(le_country, 'models/le_country.pkl')
    joblib.dump(le_org, 'models/le_org.pkl')
    joblib.dump(le_remote, 'models/le_remote.pkl')
    joblib.dump(le_ed, 'models/le_ed.pkl')

    features = skill_cols + engineered + ['YearsCode', 'ed_encoded', 'org_encoded', 'remote_encoded', 'country_encoded']

    # MODEL 1 — ROLE PREDICTOR
    print("Training Role Predictor...")
    X_role = df[features]
    y_role = df['role_encoded']

    role_model = RandomForestClassifier(
        n_estimators=50, max_depth=15, min_samples_split=5, min_samples_leaf=2,
        class_weight='balanced', random_state=42, n_jobs=-1
    )
    role_model.fit(X_role, y_role)
    joblib.dump(role_model, 'models/role_model.pkl')
    
    # Save clean samples for scatter plot
    print("Saving scatter plot data...")
    df_clean = df[['PrimaryRole', 'YearsCode', 'total_skills']].sample(min(2000, len(df)), random_state=42)
    df_clean.to_csv('data/clean_survey.csv', index=False)

    # MODEL 2 — SALARY PREDICTOR
    print("Training Salary Predictor...")
    df_salary = df.dropna(subset=['ConvertedCompYearly']).copy()
    df_salary = df_salary[(df_salary['ConvertedCompYearly'] >= 15000) & (df_salary['ConvertedCompYearly'] <= 400000)]
    
    X_sal = df_salary[features + ['role_encoded']]
    y_sal = df_salary['ConvertedCompYearly']

    salary_model = XGBRegressor(
        n_estimators=400, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, random_state=42
    )
    salary_model.fit(X_sal, y_sal)
    joblib.dump(salary_model, 'models/salary_model.pkl')

    try:
        explainer = shap.TreeExplainer(salary_model)
        with open('models/shap_explainer.pkl', 'wb') as f:
            joblib.dump(explainer, f)
    except Exception as e1:
        print(f"Normal SHAP failed: {e1}. Trying JSON reload...")
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
                temp_path = tmp.name
            salary_model.save_model(temp_path)
            temp_model = XGBRegressor()
            temp_model.load_model(temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            explainer = shap.TreeExplainer(temp_model)
            with open('models/shap_explainer.pkl', 'wb') as f:
                joblib.dump(explainer, f)
        except Exception as e2:
            print(f"JSON SHAP failed: {e2}. Saving fallback feature importances.")
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
            fallback = dict(zip(X_sal.columns, salary_model.feature_importances_))
            with open('models/shap_explainer.pkl', 'wb') as f:
                joblib.dump({'fallback_importances': fallback}, f)

    # MODEL 3 — SKILL GAP ANALYSER
    print("Building Skill Gap Profiles...")
    role_profiles = df.groupby('PrimaryRole')[skill_cols].mean()
    joblib.dump(role_profiles, 'models/role_skill_profiles.pkl')

    print("All models and encoders built successfully.")

if __name__ == "__main__":
    build_models()
