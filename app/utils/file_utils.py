import pandas as pd
from PyPDF2 import PdfReader
from fastapi import UploadFile
import tempfile
import os

async def read_pdf_text(pdf_file: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await pdf_file.read())
        tmp_path = tmp.name

    reader = PdfReader(tmp_path)
    text = "\n".join([page.extract_text() or "" for page in reader.pages])
    os.remove(tmp_path)
    print(f"Extracted text from PDF: {text}...")  # Log first 100 characters for debugging
    return text

def save_excel(df: pd.DataFrame) -> str:
    output_path = "updated_invoice.xlsx"
    df.to_excel(output_path, index=False)
    return output_path
