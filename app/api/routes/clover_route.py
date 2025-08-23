from fastapi import APIRouter, UploadFile, File
from app.api.controllers.clover_controller import get_inventory_items
from app.api.controllers.clover_controller import update_inventory_item
from app.api.models.item_update import ItemUpdate  


router = APIRouter()

@router.post("/fetch/inventory/items")
async def getItems():
    return await get_inventory_items()

@router.post("/update/inventory/item/{item_id}")
async def updateItems(item_id: str, item_data: ItemUpdate):
    return await update_inventory_item(item_id, item_data)
