print("Script starting...")
import joblib
import pandas as pd
import numpy as np
import os

def test_prediction_consistency():
    models_dir = 'models'
    if not os.path.exists(os.path.join(models_dir, 'role_model.pkl')):
        print("Models not found.")
        return

    role_model = joblib.load(os.path.join(models_dir, 'role_model.pkl'))
    le_role = joblib.load(os.path.join(models_dir, 'le_role.pkl'))
    le_ed = joblib.load(os.path.join(models_dir, 'le_ed.pkl'))
    le_org = joblib.load(os.path.join(models_dir, 'le_org.pkl'))
    le_remote = joblib.load(os.path.join(models_dir, 'le_remote.pkl'))
    le_country = joblib.load(os.path.join(models_dir, 'le_country.pkl'))

    features = role_model.feature_names_in_
    
    # Mock skill vector (same skills)
    sv = {f'skill_{s}': 1 if s in ['Python', 'SQL'] else 0 for s in [
        'Python', 'JavaScript', 'TypeScript', 'Java', 'SQL', 'C++', 'Go', 'Rust',
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
        'React', 'Node.js', 'Vue.js', 'Django', 'FastAPI', 'Angular',
        'Docker', 'AWS', 'Kubernetes', 'Google Cloud', 'Azure',
        'Git', 'Linux'
    ]}

    def get_pred(sv, years, edu, country):
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

        df['YearsCode'] = years
        df['ed_encoded'] = le_ed.transform([edu if edu in le_ed.classes_ else le_ed.classes_[0]])[0]
        df['org_encoded'] = le_org.transform([le_org.classes_[0]])[0]
        df['remote_encoded'] = le_remote.transform([le_remote.classes_[0]])[0]
        df['country_encoded'] = le_country.transform([country if country in le_country.classes_ else le_country.classes_[0]])[0]

        for c in features:
            if c not in df.columns:
                df[c] = 0
        
        X = df[features]
        probs = role_model.predict_proba(X)[0]
        pred_idx = np.argmax(probs)
        return le_role.inverse_transform([role_model.classes_[pred_idx]])[0], probs[pred_idx]

    p1, c1 = get_pred(sv, 5, "Bachelor’s degree", "United States")
    p2, c2 = get_pred(sv, 5, "Bachelor’s degree", "United States")
    
    print(f"Run 1: {p1} ({c1})")
    print(f"Run 2: {p2} ({c2})")
    
    if p1 == p2 and c1 == c2:
        print("Consistency check: PASSED (same inputs, same outputs)")
    else:
        print("Consistency check: FAILED (same inputs, different outputs!)")

    p3, c3 = get_pred(sv, 5, "Master’s degree", "United States")
    print(f"Run 3 (Changed Edu): {p3} ({c3})")

if __name__ == "__main__":
    test_prediction_consistency()
