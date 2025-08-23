# import pandas as pd
# import os
# from fastapi import UploadFile

# async def process_files(csv_file: UploadFile, excel_file: UploadFile) -> str:
#     csv_path = "uploaded_file.csv"
#     excel_path = "uploaded_file.xlsx"
#     output_excel_path = "matched_items.xlsx"

#     # Save files locally
#     with open(csv_path, "wb") as f:
#         f.write(await csv_file.read())
#     with open(excel_path, "wb") as f:
#         f.write(await excel_file.read())

#     # Read the files
#     csv_df = pd.read_csv(csv_path)
#     excel_df = pd.read_excel(excel_path, sheet_name='Items')

#     # Check SKU columns
#     if 'Item SKU' not in csv_df.columns or 'SKU' not in excel_df.columns:
#         raise ValueError("Missing 'SKU' column in one of the files")

#     # Load or create output Excel
#     if os.path.exists(output_excel_path):
#         output_df = pd.read_excel(output_excel_path)
#     else:
#         output_df = pd.DataFrame(columns=excel_df.columns)

#     # Matching logic
#     csv_skus = csv_df['Item SKU'].astype(str).str.strip().tolist()
#     matched_rows = excel_df[excel_df['SKU'].astype(str).str.strip().isin(csv_skus)]
#     existing_skus = output_df['SKU'].astype(str).str.strip().tolist()
#     new_rows = matched_rows[~matched_rows['SKU'].astype(str).str.strip().isin(existing_skus)]

#     # Append and save
#     final_df = pd.concat([output_df, new_rows], ignore_index=True)
#     final_df.to_excel(output_excel_path, index=False)

#     return output_excel_path




import pandas as pd
import os
from fastapi import UploadFile
from typing import Optional

async def process_files(csv_file: UploadFile, excel_file: UploadFile, existing_output_file: Optional[UploadFile] = None) -> str:
    csv_path = "uploaded_file.csv"
    excel_path = "uploaded_file.xlsx"
    output_excel_path = "matched_items.xlsx"

    # Save CSV and Excel (Items source)
    with open(csv_path, "wb") as f:
        f.write(await csv_file.read())
    with open(excel_path, "wb") as f:
        f.write(await excel_file.read())

    # Save the optional uploaded existing output Excel (if any)
    uploaded_output_df = None
    if existing_output_file:
        with open("uploaded_existing_output.xlsx", "wb") as f:
            f.write(await existing_output_file.read())
        uploaded_output_df = pd.read_excel("uploaded_existing_output.xlsx")

    # Read source files
    csv_df = pd.read_csv(csv_path)
    excel_df = pd.read_excel(excel_path, sheet_name='Items')

    if 'Item SKU' not in csv_df.columns or 'SKU' not in excel_df.columns:
        raise ValueError("Missing 'SKU' column in one of the files")

    # Load or create output Excel
    if os.path.exists(output_excel_path):
        existing_output_df = pd.read_excel(output_excel_path)
    else:
        existing_output_df = pd.DataFrame(columns=excel_df.columns)

    # Get SKUs from all sources to compare
    csv_skus = csv_df['Item SKU'].astype(str).str.strip().tolist()
    matched_rows = excel_df[excel_df['SKU'].astype(str).str.strip().isin(csv_skus)]

    # Avoid duplicates
    all_existing_skus = set(existing_output_df['SKU'].astype(str).str.strip().tolist())
    if uploaded_output_df is not None:
        uploaded_skus = set(uploaded_output_df['SKU'].astype(str).str.strip().tolist())
        all_existing_skus.update(uploaded_skus)

    # Filter out duplicates
    new_rows = matched_rows[~matched_rows['SKU'].astype(str).str.strip().isin(all_existing_skus)]

    # Merge and save
    final_df = pd.concat([existing_output_df, new_rows], ignore_index=True)
    final_df.to_excel(output_excel_path, index=False)

    return output_excel_path
