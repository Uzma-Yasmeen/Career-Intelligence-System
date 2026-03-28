import io
import re
from fpdf import FPDF

# Robust helper for FPDF's limited character support
def safe_pdf_str(text):
    if not text:
        return ""
    # Map common professional symbols that latin-1 might miss or misinterpret
    replacements = {
        '₹': 'Rs. ',
        '€': 'EUR ',
        '£': 'GBP ',
        '’': "'",
        '‘': "'",
        '—': '-',
        '–': '-',
        '•': '*',
        '✅': '[PASS] ',
        '🚀': '',
        '✨': '',
        '🔥': '',
        '💡': '',
        '💎': ''
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    
    # Remove all remaining non-latin-1 characters to prevent FPDF crashes
    return text.encode('latin-1', 'replace').decode('latin-1')

class CareerReport(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 15)
        self.cell(0, 10, "AI Career Intelligence Report", 0, 1, 'C')
        self.set_draw_color(127, 119, 221)
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, 'C')

def generate_pdf_report(role, salary_str, similarity, missing_skills, selected_skills, years_exp, narrative):
    pdf = CareerReport()
    pdf.add_page()
    
    # Pre-clean all strings
    role = safe_pdf_str(role)
    salary_str = safe_pdf_str(salary_str)
    narrative = safe_pdf_str(narrative.replace('**', '').replace('*', ''))
    
    # 1. Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(127, 119, 221)
    pdf.cell(0, 10, "Executive Summary", 0, 1)
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Predicted Role: {role}", 0, 1)
    pdf.cell(0, 8, f"Estimated Salary: {salary_str}", 0, 1)
    pdf.cell(0, 8, f"Years of Experience: {years_exp}", 0, 1)
    pdf.cell(0, 8, f"Skill Alignment: {similarity:.1f}%", 0, 1)
    pdf.ln(5)

    # 2. AI Analysis
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(127, 119, 221)
    pdf.cell(0, 10, "AI Career Analysis", 0, 1)
    
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, narrative)
    pdf.ln(5)

    # 3. Current Skills
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(127, 119, 221)
    pdf.cell(0, 10, "Current Skills", 0, 1)
    
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    skills_text = ", ".join(selected_skills) if selected_skills else "None input"
    pdf.multi_cell(0, 6, safe_pdf_str(skills_text))
    pdf.ln(5)

    # 4. Roadmap & Skill Gaps
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(127, 119, 221)
    pdf.cell(0, 10, "90-Day Learning Roadmap", 0, 1)
    pdf.set_draw_color(127, 119, 221)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 50, pdf.get_y())
    pdf.ln(5)
    
    sk_map = {
        'Python': "Focus on advanced libraries like Pandas/NumPy and OOP principles. Build a data-intensive automation script.",
        'JavaScript': "Master ES6+ features, asynchronous programming (Promises/Async-Await), and DOM manipulation.",
        'TypeScript': "Implement strict typing in a project. Learn interface vs. type, generics, and configuration.",
        'Java': "Explore Spring Boot, Multithreading, and JVM internals. Build a scalable REST API.",
        'SQL': "Master Joins, CTEs, and Window functions. Optimize slow queries and understand database normalization.",
        'Docker': "Containerize a full-stack application. Learn multi-stage builds and Docker Compose orchestration.",
        'Kubernetes': "Deploy a cluster, manage pods, and understand ingress/services. Look into Helm charts.",
        'React': "Learn Hooks (useEffect, useMemo), State Management (Redux/Zustand), and component lifecycle.",
        'Node.js': "Build an Event-driven backend. Learn express middleware, filesystem, and worker threads.",
        'AWS': "Get familiar with EC2, S3, and Lambda. Aim for the AWS Cloud Practitioner concepts.",
        'Git': "Master branching strategies, rebase vs. merge, and resolving complex conflicts.",
        'Linux': "Master command-line navigation, shell scripting, and process management."
    }

    if missing_skills:
        for i, (sk, imp) in enumerate(missing_skills[:5]):
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(40, 40, 40)
            priority = "Critical" if imp > 0.5 else "High" if imp > 0.3 else "Medium"
            pdf.cell(0, 6, safe_pdf_str(f"{i+1}. {sk} - Priority: {priority}"), 0, 1)
            
            pdf.set_font("Arial", '', 10)
            pdf.set_text_color(80, 80, 80)
            desc = sk_map.get(sk, f"Essential technology for {role} professionals. Focus on building 2-3 mini-projects.")
            pdf.multi_cell(0, 5, safe_pdf_str(desc))
            pdf.ln(3)
    else:
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, "Excellent! You have a high match with no major skill gaps detected.", 0, 1)

    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1', 'replace')
    return io.BytesIO(pdf_bytes)
