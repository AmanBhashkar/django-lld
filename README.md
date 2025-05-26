# Django E-commerce API

A comprehensive Django REST API for an e-commerce platform with product management, order processing, and payment integration.

## Features Implemented

### ✅ 1. Filter-based Product API

- Filter products by name (case-insensitive partial match)
- Filter by price range (min_price, max_price)
- Filter by availability status
- Comprehensive query parameter validation

### ✅ 2. Many-to-Many Relationship (Products & Orders)

- **Order Model**: Manages customer orders with status tracking
- **OrderItem Model**: Junction table linking products to orders with quantity and pricing
- Automatic stock management during order creation and cancellation

### ✅ 3. Complete CRUD APIs

#### Product Management

- `GET /api/products/` - List all products with filters
- `GET /api/products/{id}/` - Get specific product
- `POST /api/products/add/` - Create new product
- `PUT/PATCH /api/products/{id}/update/` - Update product
- `DELETE /api/products/{id}/delete/` - Delete product

#### Order Management

- `GET /api/orders/` - List all orders with filters
- `GET /api/orders/{id}/` - Get specific order
- `POST /api/orders/create/` - Create new order
- `PUT/PATCH /api/orders/{id}/update/` - Update order
- `DELETE /api/orders/{id}/cancel/` - Cancel order (restores stock)

### ✅ 4. Razorpay Payment Integration

- `POST /api/payments/razorpay/create/` - Create Razorpay order
- `POST /api/payments/razorpay/verify/` - Verify payment signature
- Automatic order status updates on successful payment

### ✅ 5. Comprehensive Logging

- **API Logger**: Tracks all API requests and responses
- **Payment Logger**: Dedicated logging for payment operations
- **Error Tracking**: Detailed error logging with context
- **Log Files**: Separate log files for different components

### ✅ 6. Dummy Data Population

- **Management Command**: `populate_db` for creating test data
- **Realistic Data**: Users, products, orders with proper relationships
- **Configurable**: Customizable quantities and data clearing options
- **Categories**: Electronics, Clothing, Books, Sports, Home & Garden

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd django-lld
```

### 2. Create Virtual Environment

```bash
python -m venv .lld
source .lld/bin/activate  # On Windows: .lld\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Razorpay (Optional)

Update `ecommerce/settings.py` with your Razorpay credentials:

```python
RAZORPAY_KEY_ID = 'your_actual_razorpay_key_id'
RAZORPAY_KEY_SECRET = 'your_actual_razorpay_key_secret'
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Populate Database with Dummy Data 🎯

Choose one of these methods to add test data:

#### Method 1: Simple Script (Recommended)

```bash
python populate_dummy_data.py
```

#### Method 2: Django Management Command

```bash
# Basic usage (10 users, 50 products, 25 orders)
python manage.py populate_db

# Custom quantities
python manage.py populate_db --users=20 --products=100 --orders=50

# Clear existing data and populate fresh
python manage.py populate_db --clear --users=15 --products=60 --orders=30
```

**What gets created:**

- **Users**: Realistic test users with username/password: `testpass123`
- **Products**: 5 categories (Electronics, Clothing, Books, Sports, Home & Garden)
- **Orders**: Complete orders with multiple items and realistic data
- **Relationships**: Proper user-order-product relationships with stock management

### 8. Start Development Server

```bash
python manage.py runserver
```

## Dummy Data Details

The dummy data system creates comprehensive test data for all models:

### 📊 Data Overview

- **Users**: 10-25 realistic users with common names
- **Products**: 50-100 products across 5 categories with realistic pricing
- **Orders**: 25-50 orders with 1-5 items each
- **Stock Management**: Automatic stock updates when orders are created

### 🏷️ Product Categories

- **Electronics**: $99-$2,999 (iPhones, MacBooks, Gaming consoles)
- **Clothing**: $19-$299 (Nike, Adidas, Designer brands)
- **Home & Garden**: $29-$899 (Kitchen appliances, Smart home)
- **Books**: $9-$49 (Classic literature, Popular novels)
- **Sports**: $24-$599 (Equipment, Outdoor gear)

### 👥 Test Users

All test users have the password: `testpass123`

- Usernames: `johnsmith1`, `janedoe2`, etc.
- Emails: `username@example.com`
- Realistic first/last names

### 📋 Sample Commands

```bash
# Quick start with default data
python manage.py populate_db

# Large dataset for performance testing
python manage.py populate_db --users=50 --products=200 --orders=100

# Fresh start (clears existing data)
python manage.py populate_db --clear

# Check what was created
python manage.py shell -c "
from django.contrib.auth.models import User
from store_products.models import Products, Order, OrderItem
print(f'Users: {User.objects.count()}')
print(f'Products: {Products.objects.count()}')
print(f'Orders: {Order.objects.count()}')
print(f'Order Items: {OrderItem.objects.count()}')
"
```

For detailed information, see [DUMMY_DATA_README.md](DUMMY_DATA_README.md)

## API Documentation

### Swagger UI

Access the interactive API documentation at:

- **Swagger UI**: `http://127.0.0.1:8000/api/docs/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/api/docs/redoc/`
- **Schema**: `http://127.0.0.1:8000/api/schema/`

### Example API Calls

#### Create a Product

```bash
curl -X POST http://127.0.0.1:8000/api/products/add/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock_quantity": 10,
    "is_available": true
  }'
```

#### Filter Products

```bash
# Filter by name and price range
curl "http://127.0.0.1:8000/api/products/?name=laptop&min_price=500&max_price=1500"
```

#### Create an Order

```bash
curl -X POST http://127.0.0.1:8000/api/orders/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "shipping_address": "123 Main St, City, Country",
    "order_items": [
      {
        "product_id": "1",
        "quantity": "2"
      }
    ]
  }'
```

## Models

### Products

- `name`: Product name
- `description`: Product description
- `price`: Product price (decimal)
- `stock_quantity`: Available stock
- `is_available`: Availability status
- `created_at`, `updated_at`: Timestamps

### Order

- `user`: Foreign key to User
- `status`: Order status (pending, confirmed, shipped, delivered, cancelled)
- `total_amount`: Total order amount
- `shipping_address`: Delivery address
- `payment_status`: Payment status
- `payment_id`: Razorpay payment ID

### OrderItem

- `order`: Foreign key to Order
- `product`: Foreign key to Product
- `quantity`: Quantity ordered
- `price_at_time`: Product price when ordered

## Logging

Logs are stored in the `logs/` directory:

- `django.log`: General Django logs
- `api.log`: API-specific logs
- `payments.log`: Payment operation logs

## Admin Interface

Access the Django admin at `http://127.0.0.1:8000/admin/` to:

- Manage products, orders, and order items
- View detailed order information
- Monitor system data

## Payment Flow

1. Create an order using `/api/orders/create/`
2. Create Razorpay order using `/api/payments/razorpay/create/`
3. Process payment on frontend using Razorpay
4. Verify payment using `/api/payments/razorpay/verify/`
5. Order status automatically updates to 'confirmed'

## Error Handling

The API includes comprehensive error handling:

- Input validation errors
- Stock availability checks
- Payment verification failures
- Detailed error messages with appropriate HTTP status codes

## Security Features

- CSRF protection
- Input validation and sanitization
- Payment signature verification
- Proper error handling without sensitive data exposure

## Development Notes

- All endpoints are documented with OpenAPI/Swagger
- Comprehensive logging for debugging and monitoring
- Stock management with automatic updates
- Transaction safety for critical operations
- Proper HTTP status codes and error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
