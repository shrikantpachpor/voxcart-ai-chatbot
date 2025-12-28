from fastapi import APIRouter, HTTPException

router = APIRouter()

# Fake product data
FAKE_PRODUCTS = [
    {"id": 1, "name": "Apple iPhone 12", "description": "The iPhone 12 is the latest smartphone from Apple.", "price": 799.99},
    {"id": 2, "name": "Samsung Galaxy S21", "description": "The Galaxy S21 is the latest smartphone from Samsung.", "price": 699.99},
    {"id": 3, "name": "Google Pixel 5", "description": "The Pixel 5 is the latest smartphone from Google.", "price": 599.99},
]

# Fake order data
FAKE_ORDERS = {
    "12345": {"status": "Shipped", "items": [{"name": "Apple iPhone 12", "quantity": 1}]},
    "67890": {"status": "Delivered", "items": [{"name": "Samsung Galaxy S21", "quantity": 2}]},
}

@router.get("/products")
def get_products(search: str = None):
    if search:
        results = [p for p in FAKE_PRODUCTS if search.lower() in p["name"].lower()]
        return {"results": results}
    return {"results": FAKE_PRODUCTS}

@router.get("/orders/{order_id}")
def get_order_status(order_id: str):
    if order_id in FAKE_ORDERS:
        return FAKE_ORDERS[order_id]
    raise HTTPException(status_code=404, detail="Order not found")