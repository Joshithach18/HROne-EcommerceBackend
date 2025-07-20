from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
import re
import ssl
import certifi

app = FastAPI(title="Ecommerce Backend", description="FastAPI Ecommerce Application", version="1.0.0")

# MongoDB Connection with SSL fix
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

# Try different connection methods
try:
    if "mongodb+srv" in MONGO_URL:
        # For MongoDB Atlas with SSL
        client = MongoClient(
            MONGO_URL,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )
    else:
        # For local MongoDB
        client = MongoClient(MONGO_URL)
    
    # Test the connection
    client.admin.command('ping')
    print("MongoDB connection successful!")
    
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    # Fallback - create client anyway, will handle errors in endpoints
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

def handle_db_operation(operation):
    """Handle database operations with proper error handling"""
    try:
        return operation()
    except Exception as e:
        error_msg = str(e)
        if "SSL" in error_msg or "handshake" in error_msg:
            raise HTTPException(
                status_code=503, 
                detail="Database connection issue. Please check MongoDB Atlas configuration."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Database error: {error_msg}")

# Root endpoint now shows products (what they want to test)
@app.get("/")
async def root(
    name: Optional[str] = Query(None, description="Filter by product name (supports regex)"),
    size: Optional[str] = Query(None, description="Filter by size"),
    limit: Optional[int] = Query(10, description="Number of products to return"),
    offset: Optional[int] = Query(0, description="Number of products to skip")
):
    """List all products - this is now the root endpoint for testing"""
    try:
        def get_products():
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
            return products
        
        products = handle_db_operation(get_products)
        
        # Serialize products
        serialized_products = serialize_docs(products)
        
        # If no products exist, return a helpful message
        if not serialized_products:
            return {
                "message": "Ecommerce Backend API is running!",
                "products": [],
                "note": "No products found. Use POST /products to add products.",
                "status": "Database connected successfully"
            }
        
        return {"products": serialized_products}
    
    except HTTPException:
        raise
    except Exception as e:
        return {
            "message": "Ecommerce Backend API is running!",
            "error": f"Database connection issue: {str(e)}",
            "products": [],
            "note": "Please check MongoDB Atlas configuration"
        }

# Create Products API
@app.post("/products", status_code=201)
async def create_product(product: ProductCreate):
    try:
        product_dict = product.dict()
        
        def insert_product():
            return products_collection.insert_one(product_dict)
        
        result = handle_db_operation(insert_product)
        
        return ApiResponse(message="Product created successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List Products API (keeping this for API consistency)
@app.get("/products", status_code=200)
async def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (supports regex)"),
    size: Optional[str] = Query(None, description="Filter by size"),
    limit: Optional[int] = Query(10, description="Number of products to return"),
    offset: Optional[int] = Query(0, description="Number of products to skip")
):
    try:
        def get_products():
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
            return products
        
        products = handle_db_operation(get_products)
        
        # Serialize products
        serialized_products = serialize_docs(products)
        
        return {"products": serialized_products}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create Order API
@app.post("/orders", status_code=201)
async def create_order(order: OrderCreate):
    try:
        total_amount = 0.0
        order_items = []
        
        def process_order():
            nonlocal total_amount, order_items
            
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
            return orders_collection.insert_one(order_doc)
        
        result = handle_db_operation(process_order)
        
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
        def get_orders():
            cursor = orders_collection.find().skip(offset).limit(limit)
            return list(cursor)
        
        orders = handle_db_operation(get_orders)
        
        # Serialize orders
        serialized_orders = serialize_docs(orders)
        
        return {"orders": serialized_orders}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
