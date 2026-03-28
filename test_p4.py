import joblib
import pandas as pd
import numpy as np
import os

models_dir = os.path.join(r"c:\Users\Admin\Desktop\Projects\SRU_Projects\ai-career-intelligence", 'models')
print("Loading models...")
role_model = joblib.load(os.path.join(models_dir, 'role_model.pkl'))
le_role = joblib.load(os.path.join(models_dir, 'le_role.pkl'))

df = pd.DataFrame([{'YearsCode': 5}])
features = role_model.feature_names_in_
print("Features expected:", len(features))

for c in features:
    if c not in df.columns:
        df[c] = 0

X = df[features]
try:
    probs = role_model.predict_proba(X)[0]
    print("Predict_proba successful, probs shape:", probs.shape)
    
    classes = role_model.classes_
    print("Role model classes:", classes)
    
    role_classes = le_role.inverse_transform(classes)
    print("Inverse transform successful:", role_classes[:5])
    
    # Feature importances
    importances = role_model.feature_importances_
    print("Feature importances successful, len:", len(importances))
except Exception as e:
    import traceback
    traceback.print_exc()

