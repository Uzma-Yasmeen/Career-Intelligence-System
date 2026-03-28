import pdfplumber
import PyPDF2
import re

# Skills from the requirements
SKILLS_LIST = [
    'Python', 'JavaScript', 'TypeScript', 'Java', 'SQL', 'C++', 'Go', 'Rust',
    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
    'React', 'Node.js', 'Vue.js', 'Django', 'FastAPI', 'Angular',
    'Docker', 'AWS', 'Kubernetes', 'Google Cloud', 'Azure',
    'Git', 'Linux'
]

def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber failed: {e}. Falling back to PyPDF2")
        try:
            file.seek(0)
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e2:
            print(f"PyPDF2 failed: {e2}")
    
    return text

def extract_skills_from_text(text):
    text_lower = text.lower()
    found_skills = []
    
    for skill in SKILLS_LIST:
        skill_lower = skill.lower()
        # Create a word boundary regex to avoid partial matches
        # E.g., 'Go' shouldn't match 'Google' or 'good'
        # Treat . like in Node.js or Vue.js specially
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        
        # Special case: C++ (not word boundary compliant easily)
        if skill == 'C++':
            if 'c++' in text_lower:
                found_skills.append(skill)
            continue
            
        if re.search(pattern, text_lower):
            found_skills.append(skill)
            
    return found_skills

def extract_experience_years(text):
    # Regex heuristic for looking for "X years" or "X+ years"
    pattern = r'(\d+)(?:\+)?\s*(?:years?|yrs?)(?:\s+of\s+experience)?'
    matches = re.findall(pattern, text.lower())
    
    if matches:
        try:
            # take max
            return max([int(m) for m in matches if int(m) <= 50])
        except:
            return 0
    return 0

def parse_resume(file):
    text = extract_text_from_pdf(file)
    skills = extract_skills_from_text(text)
    years = extract_experience_years(text)
    
    return {
        'skills': skills,
        'years': years,
        'raw_text': text
    }
