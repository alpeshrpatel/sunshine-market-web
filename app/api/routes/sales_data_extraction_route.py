from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from app.api.controllers.sales_data_extraction_controller import process_files

router = APIRouter()

@router.post("/upload/")
async def upload_files(
    csv_file: UploadFile = File(...),
    excel_file: UploadFile = File(...),
    existing_output_file: UploadFile = File(None)  # Optional third file
):
    result_file_path = await process_files(csv_file, excel_file, existing_output_file)
    return FileResponse(
        path=result_file_path,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename="matched_items.xlsx"
    )

