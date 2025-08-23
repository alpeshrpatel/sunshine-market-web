from fastapi import FastAPI, HTTPException
import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from app.api.models.item_update import ItemUpdate

load_dotenv()

app = FastAPI()

CLOVER_BASE_URL = "https://api.clover.com/v3/merchants"
MERCHANT_ID = '243204911883'
API_TOKEN = '0a408026-9900-36f4-3398-fdf394c9d954'

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}



async def get_inventory_items():
    url = f"{CLOVER_BASE_URL}/{MERCHANT_ID}/items"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching items: {response}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
        

async def update_inventory_item(item_id: str, item_data: ItemUpdate):
    url = f"{CLOVER_BASE_URL}/{MERCHANT_ID}/items/{item_id}"

    payload = item_data.dict(exclude_none=True)

    if not payload:
        raise HTTPException(status_code=400, detail="No fields to update.")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=HEADERS, json=payload)
        if response.status_code in [200, 201]:
            return {"message": "Item updated successfully", "item": response.json()}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)


# @app.post("/inventory/item")
# async def create_inventory_item(name: str, price: int):
#     url = f"{CLOVER_BASE_URL}/{MERCHANT_ID}/items"
#     payload = {
#         "name": name,
#         "price": price
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=HEADERS, json=payload)
#         if response.status_code in [200, 201]:
#             return response.json()
#         else:
#             raise HTTPException(status_code=response.status_code, detail=response.text)


# @app.delete("/inventory/item/{item_id}")
# async def delete_inventory_item(item_id: str):
#     url = f"{CLOVER_BASE_URL}/{MERCHANT_ID}/items/{item_id}"
#     async with httpx.AsyncClient() as client:
#         response = await client.delete(url, headers=HEADERS)
#         if response.status_code in [200, 204]:
#             return {"message": "Item deleted successfully"}
#         else:
#             raise HTTPException(status_code=response.status_code, detail=response.text)
