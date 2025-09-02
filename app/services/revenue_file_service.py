# import pandas as pd
# import re

# def process_revenue_files(sales_df: pd.DataFrame, master_df: pd.DataFrame, category: str) -> dict:
#     # Filter for the given category (e.g., Costco)
#     print(f"Processing revenue files for category: {category}")
#     print("Master Columns:", master_df.columns.tolist())
#     print("Sales Columns:", sales_df.columns.tolist())
#     # category_df = master_df[master_df['Printer Labels'].str.lower() == category.lower()]
   

#     # Split input category string into list and normalize to lowercase
#     Printer Labels = [c.strip().lower() for c in category.split(',')]

#     print(f"Filtering for Printer Labels: {Printer Labels}")

#     if 'Printer Labels' not in master_df.columns:
#         raise ValueError("Missing 'Printer Labels' column in master Excel file")

#     # Ensure 'Printer Labels' column is string
#     master_df['Printer Labels'] = master_df['Printer Labels'].astype(str)

#     # Filter rows where any category is found in the 'Printer Labels' string
#     category_df = master_df[master_df['Printer Labels'].str.lower().apply(
#         lambda cell: any(cat in cell for cat in Printer Labels)
#     )]

#     print(f"Filtered master data: {len(category_df)} rows matched.")
#     print(f"Processing category: {category}, found {len(category_df)} items.")

#     # Prepare lookup set of SKU and Product Codes
#     category_skus = category_df['SKU'].dropna().astype(str).unique().tolist()
#     category_codes = category_df[category_df['SKU'].isna()]['Product Code'].dropna().astype(str).unique().tolist()
#     print(f"Category SKUs: {category_skus}")
#     print(f"Category Product Codes: {category_codes}")

#     # Combine SKUs and Product Codes into one lookup column in sales_df
#     sales_df['ItemIdentifier'] = sales_df['Item SKU'].fillna(sales_df['Item Product Code']).astype(str)

#     # Match sales with master items
#     matched_sales = sales_df[sales_df['ItemIdentifier'].isin(category_skus + category_codes)]

#     # Sum revenue and discount
#     total_revenue = matched_sales['Total Revenue'].sum()
#     total_discount = matched_sales['Total Discount'].sum()

#     return {
#         "category": category,
#         "total_items_sold": len(matched_sales),
#         "total_revenue": round(total_revenue, 2),
#         "total_discount": round(total_discount, 2)
#     }


import pandas as pd
import re
import math

def process_revenue_files(sales_df: pd.DataFrame, df: pd.DataFrame, category: str) -> dict:
    print(f"Processing revenue files for category: {category}")
    
    # if "Items" not in master_excel:
    #     raise ValueError("The 'Items' sheet is missing in the master Excel file.")

    # df = master_excel["Items"]
    df = df.fillna('')  # Replace NaN with empty string

    print(f"Original 'Items' sheet shape: {df.shape}")

    # Find records with empty Clover ID
    empty_clover = df[df['Clover ID'] == '']
    print(f"\nFound {len(empty_clover)} records with empty Clover ID")

    if not empty_clover.empty:
        print("\nProcessing empty Clover ID records...")
        for idx in empty_clover.index:
            if idx > 0:
                prev_idx = idx - 1
                current_category = df.loc[idx, 'Printer Labels']
                if current_category:
                    prev_category = df.loc[prev_idx, 'Printer Labels']
                    if prev_category:
                        df.loc[prev_idx, 'Printer Labels'] = prev_category + ',' + current_category
                    else:
                        df.loc[prev_idx, 'Printer Labels'] = current_category
        print("Finished updating Printer Labels in previous records.")

    # Drop records with empty Clover ID
    final_df = df[df['Clover ID'] != '']
    print(f"Cleaned 'Items' sheet shape: {final_df.shape}")

    # Replace back the cleaned Items sheet into master_excel
    df = final_df

    # Now continue with category-based revenue matching
    Printer_Labels = [c.strip().lower() for c in category.split(',')]
    print(f"Filtering for Printer Labels: {Printer_Labels}")

    final_df['Printer Labels'] = final_df['Printer Labels'].astype(str)

    category_df = final_df[final_df['Printer Labels'].str.lower().apply(
        lambda cell: any(cat in cell for cat in Printer_Labels)
    )]

    print(f"Filtered master data: {len(category_df)} rows matched.")
    print(f"Processing category: {category}, found {len(category_df)} items.")

    category_skus = category_df['SKU'].dropna().astype(str).unique().tolist()
    category_codes = category_df[category_df['SKU'] == '']['Product Code'].dropna().astype(str).unique().tolist()

    sales_df['ItemIdentifier'] = sales_df['Item SKU'].fillna(sales_df['Item Product Code']).astype(str)

    matched_sales = sales_df[sales_df['ItemIdentifier'].isin(category_skus + category_codes)]
    matched_sales_item_from_inventory = category_df[category_df['SKU'].isin(matched_sales['ItemIdentifier'])]

    total_revenue = fix_nan(matched_sales['Total Revenue'].sum())
    total_discount = fix_nan(matched_sales['Total Discount'].sum())
    
    sold_items = []
    for _, row in matched_sales.iterrows():
        vendor_price = 0.0
        for _, item_row in matched_sales_item_from_inventory.iterrows():
            if row['ItemIdentifier'] == item_row['SKU']:
                vendor_price = item_row.get('Cost', '0')
                break
        item = {
            "item_identifier": row.get("ItemIdentifier", ""),
            "item_name": row.get("Item Name", ""),
            "price": float(row.get("Item Total with Tax/Fee Amount", 0)),
            "vendor_price": safe_float(vendor_price),
            
            # "cost": float(row.get("Cost", 0)),
            "revenue": float(row.get("Total Revenue", 0)),
            "date": row.get("Line Item Date", ""),
            # "quantity_sold": int(row.get("Qty", 0)) if pd.notnull(row.get("Qty")) else 0
        }
        sold_items.append(item)
    
    total_price = sum(item['price'] for item in sold_items)
    total_cost = sum(float(item['vendor_price']) for item in sold_items)

    return {
        "category": category,
        "total_items_sold": len(matched_sales),
        "total_revenue": round(total_revenue, 2),
        "total_discount": round(total_discount, 2),
        "total_price": round(total_price, 2),
        "total_cost": round(total_cost, 2),
        "sold_items": sold_items
    }

    # return {
    #     "category": category,
    #     "total_items_sold": len(matched_sales),
    #     "total_revenue": round(total_revenue, 2),
    #     "total_discount": round(total_discount, 2)
    # }


def analyzeRevenueOfAllPrinterLabels(sales_df: pd.DataFrame, df: pd.DataFrame) -> dict:
    print("Processing revenue files for all Printer Labels")

    df = df.fillna('')  # Replace NaN with empty string
    print(f"Original 'Items' sheet shape: {df.shape}")

    # Find records with empty Clover ID
    empty_clover = df[df['Clover ID'] == '']
    if not empty_clover.empty:
        print(f"\nFound {len(empty_clover)} records with empty Clover ID")
        for idx in empty_clover.index:
            if idx > 0:
                prev_idx = idx - 1
                current_category = df.loc[idx, 'Printer Labels']
                if current_category:
                    prev_category = df.loc[prev_idx, 'Printer Labels']
                    if prev_category:
                        df.loc[prev_idx, 'Printer Labels'] = prev_category + ',' + current_category
                    else:
                        df.loc[prev_idx, 'Printer Labels'] = current_category
        print("Finished updating Printer Labels in previous records.")

    # Drop records with empty Clover ID
    final_df = df[df['Clover ID'] != '']
    print(f"Cleaned 'Items' sheet shape: {final_df.shape}")

    final_df['Printer Labels'] = final_df['Printer Labels'].astype(str)

    # 🔹 Get all unique Printer Labels
    all_labels = set()
    for cell in final_df['Printer Labels']:
        if cell:
            for lbl in cell.split(","):
                all_labels.add(lbl.strip().lower())

    print(f"Found {len(all_labels)} unique Printer Labels")

    # 🔹 Build response for each Printer Label
    results = {}
    for label in all_labels:
        label_df = final_df[final_df['Printer Labels'].str.lower().apply(
            lambda cell: label in cell
        )]

        category_skus = label_df['SKU'].dropna().astype(str).unique().tolist()
        category_codes = label_df[label_df['SKU'] == '']['Product Code'].dropna().astype(str).unique().tolist()

        sales_df['ItemIdentifier'] = sales_df['Item SKU'].fillna(sales_df['Item Product Code']).astype(str)

        matched_sales = sales_df[sales_df['ItemIdentifier'].isin(category_skus + category_codes)]
        matched_sales_item_from_inventory = label_df[label_df['SKU'].isin(matched_sales['ItemIdentifier'])]

        total_revenue = matched_sales['Total Revenue'].sum()
        total_discount = matched_sales['Total Discount'].sum()

        sold_items = []
        for _, row in matched_sales.iterrows():
            vendor_price = 0.0
            for _, item_row in matched_sales_item_from_inventory.iterrows():
                if row['ItemIdentifier'] == item_row['SKU']:
                    print('vendor cost:',item_row.get('Cost','0'))
                    vendor_price = item_row.get('Cost', '0')
                    break
            item = {
                "item_identifier": row.get("ItemIdentifier", ""),
                "item_name": row.get("Item Name", ""),
                "price": float(row.get("Item Total with Tax/Fee Amount", 0)),
                "vendor_price": safe_float(vendor_price),
                "revenue": float(row.get("Total Revenue", 0)),
                "date": row.get("Line Item Date", "")
            }
            sold_items.append(item)

        total_price = sum(item['price'] for item in sold_items)
        total_cost = sum(float(item['vendor_price']) for item in sold_items)

        results[label] = {
            "category": label,
            "total_items_sold": len(matched_sales),
            "total_revenue": round(total_revenue, 2),
            "total_discount": round(total_discount, 2),
            "total_price": round(total_price, 2),
            "total_cost": round(total_cost, 2),
            # "sold_items": sold_items
        }

    return sanitize_json(results)


# def safe_float(val):
#     try:
#         if val is None:
#             return 0.0
#         # remove $ or other symbols
#         cleaned = re.sub(r'[^\d.\-\.]', '', str(val))
#         return float(cleaned) if cleaned else 0.0
#     except (ValueError, TypeError):
#         return 0.0

def sanitize_json(obj):
    import math
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    return obj

def safe_float(val):
    try:
        if val is None:
            return 0.0
        # handle pandas/NumPy NaN explicitly
        if str(val).lower() in ["nan", "none", "null"]:
            return 0.0
        # remove $ or other symbols
        cleaned = re.sub(r"[^\d\.\-]", "", str(val))
        return float(cleaned) if cleaned else 0.0
    except (ValueError, TypeError):
        return 0.0

def fix_nan(val):
    return 0.0 if (isinstance(val, float) and (math.isnan(val) or math.isinf(val))) else val
