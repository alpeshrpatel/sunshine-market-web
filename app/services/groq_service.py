# import os
# import openai

# # Set your GROQ API key
# openai.api_key = os.getenv("GROQ_API_KEY")
# openai.base_url = "https://api.groq.com/openai/v1"  # Use Groq endpoint

# def extract_sku_data(pdf_text: str) -> dict:
#     prompt = f"""
# You are a data extraction assistant. Given this invoice text, extract all unique SKU codes (from the UPC column) and their corresponding quantities.

# Return the result in JSON format like:
# {{ "SKU1": quantity1, "SKU2": quantity2, ... }}

# Invoice Text:
# \"\"\"
# {pdf_text}
# \"\"\"
#     """
#     response = openai.ChatCompletion.create(
#         model="llama3-70b-8192",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.2
#     )

#     content = response.choices[0].message.content
#     try:
#         return eval(content.strip())  # safer: use `json.loads` with validation
#     except Exception:
#         return {}


import os
import re
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key='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'
)

def extract_sku_data(pdf_text: str, vendor: str) -> dict:
    
    if vendor.lower() == "vendor_a":
        prompt = f"""
                You are a data extraction assistant.

                From the following invoice text, extract all **UPC codes** (usually 10-digit numbers in the "UPC" column) and their corresponding **unit quantities** from the "EACH" column.

                Format your output strictly as a JSON dictionary with:
                - keys as UPC codes (strings),
                - values as integer quantities.

                ✅ Example format:
                {{
                "7756700284": 20,
                "7684007657": 8
                }}

                💡 ONLY return UPCs and quantities. Ignore prices, totals, or other information.

                --- INVOICE TEXT ---
                {pdf_text}
                """
    elif vendor.lower() == "vendor_b":
        prompt = f"""
                You are a precise data extraction assistant.

                From the following invoice text, extract all **UPC codes** and their corresponding quantities.

                🔍 Extract rules:
                - **UPC codes** are located after the keyword `UPC:` and may include hyphens (e.g., `0-80480-01540-4`). Remove all hyphens from them.
                - **Quantity** is given next to `BPC:` (e.g., `BPC: 12`). This is the quantity ordered.
                - Match each `UPC` with the **nearest preceding** `BPC` value in the same block of text.
                - If either `UPC` or `BPC` is missing in a block, skip that entry.

                📦 Output:
                Return only a **JSON dictionary** with:
                - Keys as UPCs (as strings, hyphens removed)
                - Values as integer quantities

                ✅ Example output format:
                {{
                "080480015404": 12,
                "080680835318": 6
                }}

                🚫 Do not include extra text, prices, totals, notes, or explanations.
                Only return the valid JSON object as described.

                --- INVOICE TEXT BELOW ---
                {pdf_text}
                """
        
    #2 prompt = f"""
    #     You are a precise data extraction assistant.

    #     From the following invoice text, extract all **UPC codes** and their corresponding quantities.

    #     🔍 Extract rules:
    #     - **UPC codes** are located after the keyword `UPC:` and may include hyphens (e.g., `0-80480-01540-4`). Remove all hyphens from them.
    #     - **Quantity** is given next to `BPC:` (e.g., `BPC: 12`). This is the quantity ordered.
    #     - Match each `UPC` with the **nearest preceding** `BPC` value in the same block of text.
    #     - If either `UPC` or `BPC` is missing in a block, skip that entry.

    #     📦 Output:
    #     Return only a **JSON dictionary** with:
    #     - Keys as UPCs (as strings, hyphens removed)
    #     - Values as integer quantities

    #     ✅ Example output format:
    #     {{
    #     "080480015404": 12,
    #     "080680835318": 6
    #     }}

    #     🚫 Do not include extra text, prices, totals, notes, or explanations.
    #     Only return the valid JSON object as described.

    #     --- INVOICE TEXT BELOW ---
    #     {pdf_text}
    #     """
    
#     prompt = f"""
# You are a precise data extraction assistant.

# From the following invoice text, extract all **UPC codes** and their corresponding quantities.

# 🔍 Extraction Rules:
# - **UPC codes** appear after the keyword `UPC:` and may contain hyphens (e.g., `0-80480-01540-4`). Remove all hyphens.
# - **Quantity** is located next to `BPC:` (e.g., `BPC: 12`). This is the quantity ordered.
# - For each block of item data, link the **nearest preceding `BPC:`** value to the following `UPC:` value.
# - Skip any blocks that are missing either a valid `UPC:` or a valid `BPC:`.

# 📦 Output Format:
# Return only a **JSON dictionary** with:
# - Keys as UPCs (as strings with no hyphens)
# - Values as integers representing quantities

# ✅ Example:
# {{
#   "080480015404": 12,
#   "080680835318": 6
# }}

# 🚫 Strict Output Rules:
# - Do not include explanations, text outside the JSON, or unrelated information.
# - Output only the final JSON object.

# --- INVOICE TEXT BELOW ---
# {pdf_text}
# """


    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()
    print(f"Raw response content: {content}")  # Debugging output

    # try:
    #     return json.loads(content)  # consider using json.loads(content) for safety
    # except Exception:
    #     return {}
    try:
       
        cleaned = (
            content.replace("“", '"')
                   .replace("”", '"')
                   .replace("’", "'")
                   .replace("`", "'")
                   .strip()
        )
        # print(f"Cleaned response content: {cleaned}")  # Debugging output
        
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            cleaned_json_str = match.group(0)
            parsed = json.loads(cleaned_json_str)
            print(f"✅ Parsed SKU data:\n{parsed}\n")
            return parsed
        else:
            print("⚠️ JSON object not found in response.")
            return cleaned
    except Exception as e:
        print(f"❌ JSON parsing error: {e}")
        return {}