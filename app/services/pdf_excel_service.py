import fitz  # PyMuPDF
import pandas as pd
from app.utils.extractor import extract_invoice_data

def extract_pdf_data_and_update_excel(pdf_path, excel_path):
    doc = fitz.open(pdf_path)
    full_text = "".join([page.get_text() for page in doc])
    
    extracted_data = extract_invoice_data(full_text)

    df = pd.read_excel(excel_path)

    for row in extracted_data:
        df = df.append(row, ignore_index=True)

    output_path = excel_path.replace(".xlsx", "_updated.xlsx")
    df.to_excel(output_path, index=False)

    return extracted_data
