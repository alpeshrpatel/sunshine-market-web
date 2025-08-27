from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.revenue_file_service import process_revenue_files, analyzeRevenueOfAllPrinterLabels
import pandas as pd

router = APIRouter()

async def analyzeRevenue(
    sales_csv: UploadFile = File(...),
    master_excel: UploadFile = File(...),
    category: str = "Costco"
):
    try:
        sales_df = pd.read_csv(sales_csv.file)
        master_df = pd.read_excel(master_excel. file, sheet_name='Items')
        # master_df = pd.read_excel(master_excel.file)

        result = process_revenue_files(sales_df, master_df, category)
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def analyzeRevenueOfAllLabels(
    sales_csv: UploadFile = File(...),
    master_excel: UploadFile = File(...)
    
):
    try:
        sales_df = pd.read_csv(sales_csv.file)
        master_df = pd.read_excel(master_excel. file, sheet_name='Items')
        # master_df = pd.read_excel(master_excel.file)

        result = analyzeRevenueOfAllPrinterLabels(sales_df, master_df)
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
