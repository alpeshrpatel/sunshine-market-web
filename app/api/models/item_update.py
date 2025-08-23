from pydantic import BaseModel

class ItemUpdate(BaseModel):
    name: str | None = None
    price: int | None = None