import pandas as pd
import sqlite3
import os

# --- CONFIGURATION ---
# 1. Download the file from: https://world.openfoodfacts.org/data
# 2. Rename it to 'openfoodfacts.csv' and put it in the 'data/' folder.
SOURCE_FILE = 'data/en.openfoodfacts.org.products.tsv' 
DB_PATH = 'data/products.db'
CHUNK_SIZE = 50000 

def init_db():
    """Create the table structure."""
    print(f"🔧 Initializing database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # We use 'OR REPLACE' to handle duplicates gracefully
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            product_name TEXT,
            brand TEXT,
            weight_per_unit_g REAL,
            sugar_100g REAL,
            salt_100g REAL,
            sat_fat_100g REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database table created.")

def process_and_load_data():
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ ERROR: Could not find {SOURCE_FILE}")
        print("Please download 'en.openfoodfacts.org.products.csv', rename it to 'openfoodfacts.csv', and place it in the 'data' folder.")
        return

    print("🚀 Starting Import (This deals with the messy TSV format)...")
    print("This will take time depending on your computer speed.")

    # UPDATED: 'quantity' is the correct column name in modern exports (was 'product_quantity')
    use_cols = [
        'code', 
        'product_name', 
        'brands', 
        'quantity', 
        'sugars_100g', 
        'salt_100g', 
        'saturated-fat_100g'
    ]

    conn = sqlite3.connect(DB_PATH)
    total_inserted = 0
    
    # Check if the columns exist before starting the loop to give a better error message
    try:
        preview = pd.read_csv(SOURCE_FILE, sep='\t', nrows=1)
        actual_cols = preview.columns.tolist()
        # Verify if 'quantity' exists, if not try 'product_quantity' or warn user
        if 'quantity' not in actual_cols and 'product_quantity' in actual_cols:
             # Fallback if the user has an older file
             use_cols[3] = 'product_quantity'
             print("ℹ️ Detected older column name 'product_quantity'.")
    except Exception as e:
        print(f"⚠️ Warning during pre-check: {e}")

    # READ_CSV configuration for TSV files
    try:
        chunk_iterator = pd.read_csv(
            SOURCE_FILE, 
            sep='\t',              # CRITICAL: The file is tab-separated
            usecols=use_cols, 
            chunksize=CHUNK_SIZE, 
            dtype={'code': str},   # Keep barcodes as strings (preserves leading zeros)
            low_memory=False,
            on_bad_lines='skip'    # Skip broken lines (common in this dataset)
        )

        for i, chunk in enumerate(chunk_iterator):
            # --- CLEANING STEP ---
            
            # 1. Drop rows that are useless (no barcode or no name)
            chunk = chunk.dropna(subset=['code', 'product_name'])
            
            # 2. Rename columns to match our database
            # We map whichever quantity column we found to 'weight_per_unit_g'
            rename_map = {
                'code': 'barcode',
                'brands': 'brand',
                'sugars_100g': 'sugar_100g',
                'saturated-fat_100g': 'sat_fat_100g'
            }
            if 'quantity' in chunk.columns:
                rename_map['quantity'] = 'weight_per_unit_g'
            elif 'product_quantity' in chunk.columns:
                 rename_map['product_quantity'] = 'weight_per_unit_g'

            chunk = chunk.rename(columns=rename_map)
            
            # 3. Fix numeric columns (convert text to 0.0)
            numeric_cols = ['sugar_100g', 'salt_100g', 'sat_fat_100g']
            for col in numeric_cols:
                if col in chunk.columns: # Safety check
                    chunk[col] = pd.to_numeric(chunk[col], errors='coerce').fillna(0)

            # 4. Fix weight (default to 100g if missing)
            chunk['weight_per_unit_g'] = pd.to_numeric(chunk['weight_per_unit_g'], errors='coerce').fillna(100)

            # --- LOADING STEP ---
            try:
                chunk.to_sql('products', conn, if_exists='append', index=False)
                total_inserted += len(chunk)
                print(f"Processed chunk {i+1}... Total products saved: {total_inserted}")
            except sqlite3.IntegrityError:
                print(f"⚠️ Chunk {i+1} had duplicates. Skipping to keep things fast.")
            except Exception as e:
                print(f"⚠️ Error on chunk {i+1}: {e}")

    except ValueError as ve:
        print(f"❌ Column mismatch error: {ve}")
        print(f"The script expected these columns: {use_cols}")
        print("Please check the header of your csv file.")
    
    conn.close()
    print(f"\n🎉 DONE! {total_inserted} products imported into {DB_PATH}.")

if __name__ == "__main__":
    init_db()
    process_and_load_data()