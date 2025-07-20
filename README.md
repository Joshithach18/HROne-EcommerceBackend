# Ecommerce Backend API

A FastAPI-based ecommerce backend application with MongoDB integration for managing products and orders.

## Features

- Create and list products with filtering capabilities
- Create orders with automatic inventory management
- Retrieve user orders with pagination
- MongoDB integration for data persistence
- Input validation using Pydantic models
- RESTful API design

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.10+** - Programming language
- **MongoDB** - NoSQL database for data storage
- **Pymongo** - MongoDB driver for Python
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server for running the application

## API Endpoints

### Products

#### Create Product
- **POST** `/products`
- Creates a new product
- **Request Body:**
  ```json
  {
    "name": "Product Name",
    "price": 99.99,
    "quantity": 10
  }
  ```
- **Response:** `201 Created`

#### List Products
- **GET** `/products`
- Retrieves products with optional filtering and pagination
- **Query Parameters:**
  - `name` (optional): Filter by product name (supports regex)
  - `size` (optional): Filter by size
  - `limit` (optional): Number of products to return (default: 10)
  - `offset` (optional): Number of products to skip (default: 0)
- **Response:** `200 OK`

### Orders

#### Create Order
- **POST** `/orders`
- Creates a new order and updates product inventory
- **Request Body:**
  ```json
  {
    "items": [
      {
        "product_id": "product_id_here",
        "bought_quantity": 2
      }
    ],
    "user_address": {
      "street": "123 Main St",
      "city": "City Name",
      "state": "State",
      "zip": "12345"
    }
  }
  ```
- **Response:** `201 Created`

#### Get User Orders
- **GET** `/orders/{user_id}`
- Retrieves orders for a specific user with pagination
- **Query Parameters:**
  - `limit` (optional): Number of orders to return (default: 10)
  - `offset` (optional): Number of orders to skip (default: 0)
- **Response:** `200 OK`

## Database Schema

### Products Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "price": "float",
  "quantity": "integer"
}
```

### Orders Collection
```json
{
  "_id": "ObjectId",
  "items": [
    {
      "product_id": "string",
      "bought_quantity": "integer",
      "price": "float",
      "total_price": "float"
    }
  ],
  "total_amount": "float",
  "user_address": "object",
  "timestamp": "string (ISO format)"
}
```

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- MongoDB instance (local or MongoDB Atlas)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**
   - Option 1: Local MongoDB
     ```bash
     # Install MongoDB locally and start the service
     # Default connection: mongodb://localhost:27017/
     ```
   
   - Option 2: MongoDB Atlas (Recommended for deployment)
     ```bash
     # Create a free M0 cluster on MongoDB Atlas
     # Get the connection string and set it as environment variable
     export MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/ecommerce?retryWrites=true&w=majority"
     ```

5. **Run the application**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Interactive API Documentation: `http://localhost:8000/docs`
   - Alternative API Documentation: `http://localhost:8000/redoc`

## Environment Variables

- `MONGO_URL`: MongoDB connection string (default: `mongodb://localhost:27017/`)

## Deployment

### Using Render.com (Free Plan)

1. **Prepare for deployment**
   - Ensure your code is in a public GitHub repository
   - Make sure `requirements.txt` is in the root directory
   - Set up MongoDB Atlas for production database

2. **Deploy to Render**
   - Connect your GitHub repository to Render
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `python main.py`
   - Add environment variable: `MONGO_URL` with your MongoDB Atlas connection string

### Using Railway (Free Plan)

1. **Deploy to Railway**
   - Connect your GitHub repository to Railway
   - Railway will auto-detect the Python application
   - Add environment variable: `MONGO_URL` with your MongoDB Atlas connection string

## Testing

You can test the API endpoints using:

1. **FastAPI Interactive Documentation**
   - Visit `http://localhost:8000/docs`
   - Test all endpoints directly from the browser

2. **cURL Examples**
   ```bash
   # Create a product
   curl -X POST "http://localhost:8000/products" \
        -H "Content-Type: application/json" \
        -d '{"name":"Test Product","price":99.99,"quantity":10}'
   
   # List products
   curl "http://localhost:8000/products"
   
   # Create an order (replace product_id with actual ID)
   curl -X POST "http://localhost:8000/orders" \
        -H "Content-Type: application/json" \
        -d '{"items":[{"product_id":"product_id_here","bought_quantity":1}],"user_address":{"street":"123 Main St","city":"Test City"}}'
   ```

3. **Postman**
   - Import the API endpoints into Postman for comprehensive testing

## Project Structure

```
ecommerce-backend/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── .gitignore          # Git ignore file (recommended)
```

## Code Quality Features

- **Input Validation**: Pydantic models ensure data integrity
- **Error Handling**: Comprehensive exception handling with appropriate HTTP status codes
- **Documentation**: Detailed API documentation with FastAPI's automatic OpenAPI generation
- **Type Hints**: Full type annotations for better code clarity
- **Database Operations**: Optimized MongoDB queries with proper indexing considerations
- **Pagination**: Implemented for large dataset handling
- **Inventory Management**: Automatic stock updates during order creation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is created as part of a hiring task and follows the specifications provided.