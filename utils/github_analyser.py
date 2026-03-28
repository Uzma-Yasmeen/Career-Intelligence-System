from github import Github
from github import Auth
import re

SKILLS_LIST = [
    'Python', 'JavaScript', 'TypeScript', 'Java', 'SQL', 'C++', 'Go', 'Rust',
    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
    'React', 'Node.js', 'Vue.js', 'Django', 'FastAPI', 'Angular',
    'Docker', 'AWS', 'Kubernetes', 'Google Cloud', 'Azure',
    'Git', 'Linux'
]

def analyse_github_profile(username):
    try:
        # Unauthenticated use, rate limit applies (60/hour)
        g = Github()
        user = g.get_user(username)
        
        repos = user.get_repos(sort='updated')[:20]
        
        languages_detected = set()
        tools_detected = set()
        
        # Git is implied if they are on GitHub
        tools_detected.add('Git')
        
        for repo in repos:
            if repo.fork:
                continue
                
            try:
                # Languages
                languages = repo.get_languages()
                for lang in languages.keys():
                    if lang in SKILLS_LIST:
                        languages_detected.add(lang)
                        
                # Tools mapping from files (heuristic)
                contents = repo.get_contents("")
                for file_content in contents:
                    file_name = file_content.name.lower()
                    if file_name == 'dockerfile':
                        tools_detected.add('Docker')
                        tools_detected.add('Linux')
                    elif file_name == 'serverless.yml' or 'aws' in file_name:
                        tools_detected.add('AWS')
                    elif 'kube' in file_name or file_name.endswith('.yaml'):
                        pass # could be kubernetes, but too loose
                    elif 'package.json' in file_name:
                        tools_detected.add('Node.js')
            except Exception as e:
                # Empty repo or other issue
                continue

        all_detected = list(languages_detected.union(tools_detected))
        
        return {
            'username': user.login,
            'name': user.name or user.login,
            'public_repos': user.public_repos,
            'followers': user.followers,
            'detected_skills': all_detected,
            'languages': list(languages_detected),
            'tools': list(tools_detected)
        }
    except Exception as e:
        return {"error": str(e)}
