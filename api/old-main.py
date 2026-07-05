from fastapi import FastAPI  # type: ignore[import]
from pydantic import BaseModel # type: ignore[import]

app = FastAPI()

items = {1: {"name": "Item 1", "price": 10.0, "description": "This is item 1", "tax": 1.0}, 2: {"name": "Item 2", "price": 20.0, "description": "This is item 2", "tax": 2.0}}

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.get("/")
async def read_root():
    return {"Message": "Hello World"}

@app.get("/ping")
async def ping():
    return {"Message": "OK"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    if item_id in items:
        return items[item_id]
    if q:
        items["q"] = q
        return items
    return {"Message": "Item not found"}

@app.post("/items/{item_id}")
async def create_item(item_id: int, item: dict):
    if item_id in items:
        return {"Message": "Item already exists"}
    items[item_id] = item
    return {"Message": "Item created", "item": item}

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    if item_id in items:
        items[item_id] = item.model_dump()
    if q:
        items["q"] = q
    
    return {"Message": "Item updated", "item": item}