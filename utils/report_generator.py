import io
from fpdf import FPDF

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
    
    # 1. Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(127, 119, 221)
    pdf.cell(0, 10, "Executive Summary", 0, 1)
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0, 0, 0)
    
    # Clean symbol for fpdf which might choke on euro/pound/rupee (fpdf struggles with unicode)
    # Actually 'latin-1' encoding for Rs / C$ / $ is fine. ₹ might crash fpdf if not unicode true.
    # To be safe, we will just use a basic replacement for unicode symbols in FPDF unless we use unicode font.
    # fpdf2 supports unicode if font is added, but default Arial does not.
    # Let's replace complex symbols for the PDF.
    try:
        clean_sal = salary_str.encode('latin-1', 'replace').decode('latin-1').replace('?', '')
    except:
        clean_sal = salary_str
        
    pdf.cell(0, 8, f"Predicted Role: {role}", 0, 1)
    pdf.cell(0, 8, f"Estimated Salary: {clean_sal}", 0, 1)
    pdf.cell(0, 8, f"Years of Experience: {years_exp}", 0, 1)
    pdf.cell(0, 8, f"Skill Alignment: {similarity:.1f}%", 0, 1)
    pdf.ln(5)

    # 2. AI Analysis
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(127, 119, 221)
    pdf.cell(0, 10, "AI Career Analysis", 0, 1)
    
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    # clean narrative for pdf (remove markdown asterisks etc if needed)
    clean_narrative = narrative.replace('**', '').replace('*', '')
    clean_narrative = clean_narrative.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, clean_narrative)
    pdf.ln(5)

    # 3. Current Skills
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(127, 119, 221)
    pdf.cell(0, 10, "Current Skills", 0, 1)
    
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    skills_text = ", ".join(selected_skills) if selected_skills else "None input"
    pdf.multi_cell(0, 6, skills_text)
    pdf.ln(5)

    # 4. Skill Gaps & Roadmap
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(127, 119, 221)
    pdf.cell(0, 10, "90-Day Learning Roadmap (Skill Gaps)", 0, 1)
    
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    
    if missing_skills:
        for i, (sk, imp) in enumerate(missing_skills):
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 6, f"{i+1}. {sk}", 0, 1)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 6, f"Priority learning area to close the gap for the {role} position. Consider short online courses or projects incorporating {sk}.")
            pdf.ln(2)
    else:
        pdf.cell(0, 6, "Excellent! You have a high match with no major skill gaps detected.", 0, 1)

    # Output to bytes
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1', 'replace')
    return io.BytesIO(pdf_bytes)
