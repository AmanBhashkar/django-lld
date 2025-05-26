# Dummy Data Population

This project includes comprehensive dummy data generation to help you test the e-commerce API with realistic data.

## Quick Start

### Method 1: Using the Simple Script

```bash
python populate_dummy_data.py
```

### Method 2: Using Django Management Command

```bash
python manage.py populate_db
```

## Command Options

The `populate_db` management command supports several options:

```bash
# Basic usage with default values
python manage.py populate_db

# Custom quantities
python manage.py populate_db --users=20 --products=100 --orders=50

# Clear existing data and populate fresh
python manage.py populate_db --clear

# Full custom setup
python manage.py populate_db --clear --users=25 --products=80 --orders=40
```

### Available Options

- `--users`: Number of users to create (default: 10)
- `--products`: Number of products to create (default: 50)
- `--orders`: Number of orders to create (default: 25)
- `--clear`: Clear existing data before populating

## What Data Gets Created

### 1. Users 👥

- **Quantity**: 10-25 realistic users
- **Details**:  
  - Usernames like `johnsmith1`, `janedoe2`
  - Email addresses: `username@example.com`
  - Password: `testpass123` (for all test users)
  - First and last names from common name lists
  - Mix of realistic user profiles

### 2. Products 📦

- **Quantity**: 50-100 diverse products
- **Categories**:
  - **Electronics**: iPhones, MacBooks, Gaming Consoles ($99-$2999)
  - **Clothing**: Nike shoes, Levi's jeans, Designer shirts ($19-$299)
  - **Home & Garden**: Kitchen appliances, Smart home devices ($29-$899)
  - **Books**: Classic literature, Popular novels ($9-$49)
  - **Sports**: Equipment, Outdoor gear ($24-$599)
- **Features**:
  - Realistic pricing based on category
  - Stock quantities (5-100 items)
  - Availability status (75% available, 25% out of stock)
  - Detailed descriptions

### 3. Orders 🛒

- **Quantity**: 25-50 realistic orders
- **Details**:
  - Random users as customers
  - 1-5 products per order
  - Realistic shipping addresses across US cities
  - Order statuses: pending, confirmed, shipped, delivered, cancelled
  - Payment statuses: pending, completed, failed
  - Created dates spread over last 30 days
  - Automatic stock quantity updates
  - Calculated total amounts

### 4. Order Items 📋

- **Automatically created** with each order
- Links products to orders with quantities
- Stores price at time of purchase
- Updates product stock levels realistically

## Sample Data Examples

### Sample Users

``` text
Username: johnsmith1
Email: johnsmith1@example.com
Password: testpass123
Name: John Smith
```

### Sample Products

``` text
iPhone 15 Pro - $1,299.99 (Electronics)
Nike Air Max 270 - $129.99 (Clothing)
Instant Pot Duo 7-in-1 - $89.99 (Home & Garden)
The Great Gatsby - $12.99 (Books)
Wilson Tennis Racket - $149.99 (Sports)
```

### Sample Orders

``` text
Order #1:
- Customer: johnsmith1
- Items: iPhone 15 Pro (1x), AirPods Pro (1x)
- Total: $1,549.98
- Status: delivered
- Address: 123 Main St, New York, NY 10001
```

## Testing the API

After populating data, you can test various API endpoints:

### Products API

```bash
# Get all products
curl http://127.0.0.1:8000/api/products/

# Filter by price range
curl "http://127.0.0.1:8000/api/products/?min_price=100&max_price=500"

# Search by name
curl "http://127.0.0.1:8000/api/products/?name=iphone"
```

### Orders API

```bash
# Get all orders
curl http://127.0.0.1:8000/api/orders/

# Get specific order
curl http://127.0.0.1:8000/api/orders/1/
```

### Authentication

Use any of the created users to test authenticated endpoints:

- Username: Any generated username (e.g., `johnsmith1`)
- Password: `testpass123`

## Data Relationships

The dummy data maintains proper relationships:

- **Users** → **Orders** (One user can have multiple orders)
- **Orders** → **OrderItems** → **Products** (Many-to-many through OrderItems)
- **Stock Management**: Product quantities decrease when orders are created
- **Realistic Pricing**: Order totals calculated from actual product prices

## Clearing Data

To start fresh:

```bash
# Clear all dummy data and repopulate
python manage.py populate_db --clear

# Or manually clear specific data
python manage.py shell
>>> from store_products.models import *
>>> OrderItem.objects.all().delete()
>>> Order.objects.all().delete()
>>> Products.objects.all().delete()
>>> from django.contrib.auth.models import User
>>> User.objects.filter(is_superuser=False).delete()
```

## Tips for Testing

1. **Start Small**: Use default quantities first to understand the data structure
2. **Check Admin Panel**: Visit `/admin/` to see the created data visually
3. **Use Swagger UI**: Visit `/api/docs/swagger/` to test API endpoints interactively
4. **Monitor Logs**: Check the log files to see API interactions
5. **Test Filters**: Try different filter combinations on products and orders

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the project root directory
2. **Database Errors**: Ensure migrations are applied: `python manage.py migrate`
3. **Permission Errors**: Check that the database file is writable
4. **Memory Issues**: Reduce quantities if creating too much data

### Verification

```bash
# Check created data counts
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from store_products.models import Products, Order, OrderItem
>>> print(f"Users: {User.objects.count()}")
>>> print(f"Products: {Products.objects.count()}")
>>> print(f"Orders: {Order.objects.count()}")
>>> print(f"Order Items: {OrderItem.objects.count()}")
```

This dummy data system provides a comprehensive foundation for testing all aspects of your e-commerce API! 🚀
