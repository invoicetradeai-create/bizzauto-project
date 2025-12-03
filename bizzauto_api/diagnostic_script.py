from database import SessionLocal
from crud import get_products, get_product_by_name

COLUMN_TO_CHECK = "name" 
SEARCH_TERM = "Chips"

db = SessionLocal()

print("--- DIAGNOSTIC START ---")

# TEST 1: Can we see ANYTHING in the 'products' table?
all_data = get_products(db, limit=3)
print(f"1. Raw Table Data (First 3 rows): {all_data}")

if len(all_data) > 0:
    # TEST 2: Check exact column name
    first_row = all_data[0]
    if not hasattr(first_row, COLUMN_TO_CHECK):
        print(f"❌ ERROR: Column '{COLUMN_TO_CHECK}' not found in table!")
        # This part is a bit different since we have ORM objects, not dicts
        # We can inspect the object's attributes
        print(f"   Available columns are: {list(first_row.__dict__.keys())}")
    else:
        # TEST 3: Try the search
        print(f"   Searching for '{SEARCH_TERM}' in column '{COLUMN_TO_CHECK}'...")
        
        # Try specific search (Case Insensitive)
        search_res = get_product_by_name(db, name=SEARCH_TERM)
        print(f"2. Search Results: {search_res}")
else:
    print("❌ Table 'products' appears empty or does not exist.")

print("--- DIAGNOSTIC END ---")

db.close()
