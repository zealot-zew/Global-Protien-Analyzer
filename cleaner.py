# In cleaner.py
#This script's only job is to read the massive, messy CSV and create a small, clean food.db file.

import pandas as pd
import sqlite3

# --- 1. Define Columns and Filters ---

# These are the only columns we care about
COLUMNS_TO_KEEP = [
    'product_name', 
    'countries_en', 
    'categories', 
    'proteins_100g'
]

# We must filter to a small list, or the data is too messy
TARGET_COUNTRIES = ['France', 'United States', 'Germany', 'Spain', 'United Kingdom']
TARGET_CATEGORIES = ['Beverages', 'Meats', 'Snacks', 'Breads', 'Desserts', 'Pizzas', 'Fruits']

# --- 2. Define Cleaning Functions ---

def clean_country(cell):
    """Takes a messy country string and returns the first, clean country."""
    if not isinstance(cell, str):
        return None
    # 'France, Germany, UK' -> 'France'
    first_country = cell.split(',')[0].strip().title()
    return first_country

def clean_category(cell):
    """Takes a messy category string and returns the first, clean category."""
    if not isinstance(cell, str):
        return None
    # 'Snacks, Sweet snacks, Biscuits' -> 'Snacks'
    first_category = cell.split(',')[0].strip().title()
    return first_category

# --- 3. Main Cleaning Process ---
def build_database():
    print("Loading raw TSV... (This may take a minute)")
    # Load *only* the columns we need to save memory
    df = pd.read_csv('en.openfoodfacts.org.products.tsv', sep = '\t' ,usecols=COLUMNS_TO_KEEP)

    print("Cleaning data...")
    # Rename columns for ease of use
    df.rename(columns={
        'countries_en': 'country',
        'proteins_100g': 'protein'
    }, inplace=True)

    # Drop any row that's missing our key data
    df.dropna(subset=['product_name', 'country', 'categories', 'protein'], inplace=True)

    # Apply the cleaning functions
    df['country'] = df['country'].apply(clean_country)
    df['category'] = df['categories'].apply(clean_category)
    
    # Drop the original 'categories' column
    df.drop(columns=['categories'], inplace=True)

    # Filter the DataFrame to *only* our target lists
    df = df[df['country'].isin(TARGET_COUNTRIES)]
    df = df[df['category'].isin(TARGET_CATEGORIES)]
    
    # We must drop duplicates *after* cleaning
    df.dropna(subset=['country', 'category'], inplace=True)

    print(f"Cleaned data has {len(df)} rows.")
    print(df.head())

    # --- 4. Save to Database ---
    print("Saving to database 'food.db'...")
    # Connect to the database (it will be created if it doesn't exist)
    conn = sqlite3.connect('food.db')
    
    # Save the clean DataFrame to a table named 'products'
    df.to_sql('products', conn, if_exists='replace', index=False)
    
    conn.close()
    print("Done! Database 'food.db' is ready.")


# --- Run the function ---
if __name__ == "__main__":
    build_database()