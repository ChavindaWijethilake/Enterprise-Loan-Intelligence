import os
import datetime
from fpdf import FPDF

def generate_loan_agreement(applicant_name: str, loan_amount: float, decision: str) -> str:
    """
    Generates a formal PDF Loan Agreement and returns the file path.
    Only generates an agreement if the decision is APPROVED or MANUAL_APPROVED.
    """
    if "APPROVE" not in decision.upper():
        return None
        
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", style="B", size=20)
    pdf.cell(0, 15, "Official Loan Agreement", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    # Date
    pdf.set_font("Helvetica", size=12)
    today = datetime.datetime.now().strftime("%B %d, %Y")
    pdf.cell(0, 10, f"Date: {today}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Body
    pdf.set_font("Helvetica", size=12)
    content = (
        f"Dear {applicant_name},\n\n"
        f"We are pleased to inform you that your application for a loan of Rs. {loan_amount:,.2f} "
        f"has been formally APPROVED by Enterprise Loan Operations.\n\n"
        f"This document serves as the official agreement indicating the "
        f"approval of your loan request under standard banking terms and conditions. "
        f"Our representatives will contact you shortly to finalize the disbursement process.\n\n"
    )
    pdf.multi_cell(0, 8, content)
    
    pdf.ln(15)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, "Authorized Signatory", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", style="I", size=12)
    pdf.cell(0, 10, "Enterprise Loan Approval Automated Systems", new_x="LMARGIN", new_y="NEXT")
    
    # Ensure directory exists in the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "documents")
    os.makedirs(docs_dir, exist_ok=True)
    
    file_path = os.path.join(docs_dir, f"Loan_Agreement_{applicant_name.replace(' ', '_')}.pdf")
    
    pdf.output(file_path)
    return file_path
