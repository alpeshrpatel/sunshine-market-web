

from fastapi import APIRouter, UploadFile, File, Form
from app.api.controllers.revenue_analyzer_controller import analyzeRevenue

router = APIRouter()

@router.post("/revenue-analyze")
async def analyze_revenue_and_discount(
    # sales_csv: UploadFile = File(...),
    # master_excel: UploadFile = File(...),
    # category: str = "Vendor_Costco"
    csv_file: UploadFile = File(...),
    excel_file: UploadFile = File(None),
    category: str = Form(...),
    
):
    return await analyzeRevenue(csv_file, excel_file, category)

