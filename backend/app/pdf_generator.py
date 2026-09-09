import os
from fpdf import FPDF
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "worksheets")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize(text: str) -> str:
    """Converts unicode symbols like arrows to ASCII safe representations for FPDF 1.7"""
    if not text:
        return ""
    replacements = {
        '↔': '<->',
        '→': '->',
        '←': '<-',
        '–': '-',
        '—': '-',
        '’': "'",
        '‘': "'",
        '”': '"',
        '“': '"',
        '•': '*',
        '≤': '<='
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

class WorksheetPDF(FPDF):
    def header(self):
        # Header banner
        self.set_fill_color(33, 150, 243)
        self.rect(0, 0, 210, 24, 'F')
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'VaaniSetu - Vernacular Pedagogy', 0, 1, 'C')
        
        self.set_font('Arial', '', 10)
        self.cell(0, 6, 'Jharkhand PALASH MTB-MLE & NIPUN Bharat FLN Classroom Worksheet', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'VaaniSetu Edge AI | Jharkhand PALASH MTB-MLE Primary Classroom Tool', 0, 0, 'C')

def create_worksheet_pdf(worksheet_data: Dict[str, Any], filename: str = "fln_worksheet.pdf") -> str:
    pdf = WorksheetPDF()
    pdf.add_page()
    
    # Title section
    pdf.set_text_color(20, 20, 20)
    pdf.set_font('Arial', 'B', 14)
    title = sanitize(worksheet_data.get('title', 'FLN Bilingual Worksheet'))
    pdf.cell(0, 8, title, 0, 1, 'L')
    
    pdf.set_font('Arial', 'I', 11)
    pdf.set_text_color(70, 70, 70)
    sub = sanitize(f"Topic: {worksheet_data.get('sub_title', 'Numeracy & Vocabulary')} | Grade: {worksheet_data.get('grade', 'Grade 1-2')}")
    pdf.cell(0, 6, sub, 0, 1, 'L')
    pdf.ln(3)

    # Student metadata box
    pdf.set_draw_color(200, 200, 200)
    pdf.set_fill_color(245, 247, 250)
    pdf.rect(10, 48, 190, 16, 'DF')
    pdf.set_xy(14, 52)
    pdf.set_font('Arial', '', 10)
    pdf.cell(55, 8, "Student Name: __________________", 0, 0)
    pdf.cell(40, 8, "Roll No: ______", 0, 0)
    pdf.cell(45, 8, "Date: ____________", 0, 0)
    pdf.cell(40, 8, "Score: ___ / 10", 0, 1)
    
    pdf.ln(12)

    # Instructions
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(30, 80, 160)
    pdf.cell(0, 6, "Classroom Instructions:", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(40, 40, 40)
    instructions = sanitize(worksheet_data.get('instructions', 'Read the questions carefully and select the correct vernacular answer.'))
    pdf.multi_cell(0, 6, instructions)
    pdf.ln(4)

    # Questions section
    questions = worksheet_data.get('questions', [])
    for q in questions:
        q_num = q.get('q_num', 1)
        q_text = sanitize(q.get('question', ''))
        
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(0, 6, f"Q{q_num}. {q_text}", 0, 1)
        
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(50, 50, 50)
        options = q.get('options', [])
        opt_str = "    ".join([f"({chr(65+i)}) {sanitize(opt)}" for i, opt in enumerate(options)])
        pdf.cell(0, 6, f"   Options: {opt_str}", 0, 1)
        
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "   Student Answer: [   ]               Teacher Remarks: ________________________", 0, 1)
        pdf.ln(3)

    # Activity table
    pdf.ln(4)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(30, 80, 160)
    pdf.cell(0, 6, "FLN Quick Reference Table (Hindi <-> Santhali <-> English)", 0, 1)
    
    # Table Header
    pdf.set_fill_color(230, 238, 250)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(30, 7, "Hindi Word", 1, 0, 'C', True)
    pdf.cell(50, 7, "Santhali (Phonetic)", 1, 0, 'C', True)
    pdf.cell(45, 7, "Ol Chiki Script Ref", 1, 0, 'C', True)
    pdf.cell(55, 7, "Classroom Context", 1, 1, 'C', True)

    # Table rows
    sample_rows = [
        ("Ek (1)", "Mid", "U+1C50 - 1C7F", "Numeracy (Count)"),
        ("Bar (2)", "Bar", "Ol Chiki Ol", "Numeracy (Count)"),
        ("Pe (3)", "Pe", "Ol Chiki Ol", "Numeracy (Count)"),
        ("Kitab", "Puthi", "Language Reader", "Reading FLN"),
        ("Namaste", "Johar", "Universal Greeting", "Discipline & Greeting"),
        ("Doodh", "Toa", "Health & Nutrition", "Hygiene & Life Science")
    ]
    
    pdf.set_font('Arial', '', 9)
    for row in sample_rows:
        pdf.cell(30, 6, row[0], 1, 0, 'C')
        pdf.cell(50, 6, row[1], 1, 0, 'C')
        pdf.cell(45, 6, row[2], 1, 0, 'C')
        pdf.cell(55, 6, row[3], 1, 1, 'L')

    output_path = os.path.join(OUTPUT_DIR, filename)
    pdf.output(output_path, 'F')
    return output_path
