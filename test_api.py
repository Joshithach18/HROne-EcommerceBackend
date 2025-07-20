import requests
import json

# Base URL - change this to your deployed URL or keep localhost for local testing
BASE_URL = "http://localhost:8000"

def test_create_product():
    """Test creating a product"""
    print("Testing Create Product API...")
    url = f"{BASE_URL}/products"
    
    product_data = {
        "name": "Test Laptop",
        "price": 999.99,
        "quantity": 5
    }
    
    response = requests.post(url, json=product_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_products():
    """Test listing products"""
    print("Testing List Products API...")
    url = f"{BASE_URL}/products"
    
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)
    
    # Return products for use in order creation
    if response.status_code == 200:
        return response.json().get("products", [])
    return []

def test_create_order(product_id):
    """Test creating an order"""
    print("Testing Create Order API...")
    url = f"{BASE_URL}/orders"
    
    order_data = {
        "items": [
            {
                "product_id": product_id,
                "bought_quantity": 2
            }
        ],
        "user_address": {
            "street": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "USA"
        }
    }
    
    response = requests.post(url, json=order_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_orders():
    """Test listing orders"""
    print("Testing List Orders API...")
    user_id = "test_user_123"  # This is just a placeholder for the URL
    url = f"{BASE_URL}/orders/{user_id}"
    
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def main():
    """Run all API tests"""
    print("Starting API Tests...")
    print("=" * 50)
    
    try:
        # Test creating a product
        test_create_product()
        
        # Test listing products
        products = test_list_products()
        
        # Test creating an order (if we have products)
        if products:
            product_id = products[0].get("_id")
            if product_id:
                test_create_order(product_id)
            else:
                print("No product ID found to test order creation")
        else:
            print("No products found to test order creation")
        
        # Test listing orders
        test_list_orders()
        
        print("All tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()