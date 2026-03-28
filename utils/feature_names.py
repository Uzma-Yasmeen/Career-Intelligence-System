def get_plain_english_feature(feat):
    mapping = {
        'country_encoded': 'Your country',
        'YearsCode': 'Years of experience',
        'ed_encoded': 'Education level',
        'remote_encoded': 'Work style',
        'org_encoded': 'Company size',
        'role_encoded': 'Your developer role',
        'web_ratio': 'Web skills depth',
        'sys_ratio': 'Systems skills depth',
        'data_ratio': 'Data skills depth',
        'total_skills': 'Total skills known',
        'fe_signal': 'React and TypeScript combo',
        'devops_signal': 'Docker and Kubernetes and Linux combo',
        'data_signal': 'Python and SQL combo',
        'ml_signal': 'Python and FastAPI combo',
        'backend_signal': 'Java and SQL combo',
        'cloud_signal': 'AWS and Docker combo'
    }
    if feat in mapping:
        return mapping[feat]
    if feat.startswith('skill_'):
        return f"Knows {feat.replace('skill_', '')}"
    return feat

def get_plain_english_shap(feat, val):
    mapping = {
        'country_encoded': 'Your country',
        'YearsCode': 'Years of experience',
        'ed_encoded': 'Education level',
        'remote_encoded': 'Work style',
        'org_encoded': 'Company size',
        'role_encoded': 'Your developer role',
        'web_ratio': 'Web skills depth',
        'sys_ratio': 'Systems skills depth',
        'data_ratio': 'Data skills depth',
        'total_skills': 'Total skills known',
        'fe_signal': 'React and TypeScript combo',
        'devops_signal': 'Docker and Kubernetes and Linux combo',
        'data_signal': 'Python and SQL combo',
        'ml_signal': 'Python and FastAPI combo',
        'backend_signal': 'Java and SQL combo',
        'cloud_signal': 'AWS and Docker combo'
    }
    if feat in mapping:
        return mapping[feat]
        
    if feat.startswith('skill_'):
        skill_name = feat.replace('skill_', '')
        if float(val) > 0.5:
            return f"Knows {skill_name}"
        else:
            return f"Missing {skill_name}"
    return feat
