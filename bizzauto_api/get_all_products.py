from database import SessionLocal
from crud import get_products

db = SessionLocal()

print("--- FETCHING ALL PRODUCTS ---")

# Fetch all products from the database
all_products = get_products(db, limit=100) # Limit to 100 to avoid too much output

if all_products:
    print(f"✅ Found {len(all_products)} product(s):")
    for product in all_products:
        print(f" - ID: {product.id}, Name: {product.name}, Price: {product.sale_price}, Stock: {product.stock_quantity}")
else:
    print("❌ No products found in the database.")

print("--- FINISHED ---")

db.close()
