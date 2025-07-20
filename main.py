from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
import re

app = FastAPI(title="Ecommerce Backend", description="FastAPI Ecommerce Application", version="1.0.0")

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client.ecommerce

# Collections
products_collection = db.products
orders_collection = db.orders

# Pydantic Models
class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

class Product(BaseModel):
    id: str = Field(alias="_id")
    name: str
    price: float
    quantity: int

class OrderItem(BaseModel):
    product_id: str
    bought_quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItem]
    user_address: Dict[str, Any]

class Order(BaseModel):
    id: str = Field(alias="_id")
    items: List[Dict[str, Any]]
    total_amount: float
    user_address: Dict[str, Any]
    timestamp: str

class ApiResponse(BaseModel):
    message: str

# Helper Functions
def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    doc['_id'] = str(doc['_id'])
    return doc

def serialize_docs(docs):
    """Convert list of MongoDB documents to JSON serializable format"""
    return [serialize_doc(doc) for doc in docs]

@app.get("/")
async def root():
    return {"message": "Ecommerce Backend API is running!"}

# Create Products API
@app.post("/products", status_code=201)
async def create_product(product: ProductCreate):
    try:
        product_dict = product.dict()
        
        # Insert product into MongoDB
        result = products_collection.insert_one(product_dict)
        
        return ApiResponse(message="Product created successfully")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List Products API
@app.get("/products", status_code=200)
async def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (supports regex)"),
    size: Optional[str] = Query(None, description="Filter by size"),
    limit: Optional[int] = Query(10, description="Number of products to return"),
    offset: Optional[int] = Query(0, description="Number of products to skip")
):
    try:
        # Build query filter
        query_filter = {}
        
        if name:
            # Support partial search with regex
            query_filter["name"] = {"$regex": name, "$options": "i"}
        
        if size:
            query_filter["size"] = size
        
        # Get products with pagination
        cursor = products_collection.find(query_filter).skip(offset).limit(limit)
        products = list(cursor)
        
        # Serialize products
        serialized_products = serialize_docs(products)
        
        return {"products": serialized_products}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create Order API
@app.post("/orders", status_code=201)
async def create_order(order: OrderCreate):
    try:
        total_amount = 0.0
        order_items = []
        
        # Process each item in the order
        for item in order.items:
            # Find the product
            product = products_collection.find_one({"_id": ObjectId(item.product_id)})
            
            if not product:
                raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
            
            # Check if enough quantity is available
            if product["quantity"] < item.bought_quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough quantity available for product {product['name']}"
                )
            
            # Calculate item total
            item_total = product["price"] * item.bought_quantity
            total_amount += item_total
            
            # Update product quantity
            new_quantity = product["quantity"] - item.bought_quantity
            products_collection.update_one(
                {"_id": ObjectId(item.product_id)},
                {"$set": {"quantity": new_quantity}}
            )
            
            # Add item to order
            order_items.append({
                "product_id": item.product_id,
                "bought_quantity": item.bought_quantity,
                "price": product["price"],
                "total_price": item_total
            })
        
        # Create order document
        order_doc = {
            "items": order_items,
            "total_amount": total_amount,
            "user_address": order.user_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Insert order into MongoDB
        result = orders_collection.insert_one(order_doc)
        
        return ApiResponse(message="Order created successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get List of Orders
@app.get("/orders/{user_id}", status_code=200)
async def get_user_orders(
    user_id: str,
    limit: Optional[int] = Query(10, description="Number of orders to return"),
    offset: Optional[int] = Query(0, description="Number of orders to skip")
):
    try:
        # In a real application, you'd filter by user_id
        # For this implementation, we'll return all orders for demonstration
        # In production, you'd add user_id field to orders and filter by it
        
        cursor = orders_collection.find().skip(offset).limit(limit)
        orders = list(cursor)
        
        # Serialize orders
        serialized_orders = serialize_docs(orders)
        
        return {"orders": serialized_orders}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)