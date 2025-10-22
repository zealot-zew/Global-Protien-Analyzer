# In analysis.py
#This file will contain all the functions that query the database and perform calculations.

import sqlite3
import pandas as pd
import numpy as np

DB_NAME = 'food.db'

def get_mean_protein_by_country(country_name):
    """
    Finds the average protein for all categories in a given country.
    """
    conn = sqlite3.connect(DB_NAME)
    
    # Use pandas to directly query the SQL database
    query = "SELECT category, protein FROM products WHERE country = ?"
    df = pd.read_sql_query(query, conn, params=(country_name,))
    
    conn.close()
    
    if df.empty:
        return f"No data found for {country_name}."
    
    # Use pandas groupby to get the mean
    result = df.groupby('category')['protein'].mean().sort_values(ascending=False)
    return result

def get_mean_protein_by_category(category_name):
    """
    Finds the average protein for a category, broken down by country.
    """
    conn = sqlite3.connect(DB_NAME)
    
    query = "SELECT country, protein FROM products WHERE category = ?"
    df = pd.read_sql_query(query, conn, params=(category_name,))
    
    conn.close()
    
    if df.empty:
        return f"No data found for {category_name}."
        
    result = df.groupby('country')['protein'].mean().sort_values(ascending=False)
    return result

def get_overall_stats_for_category(category_name):
    """
    Gets detailed NumPy stats (mean, median, std) for a category.
    """
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT protein FROM products WHERE category = ?"
    # Load just the protein column into a DataFrame
    df = pd.read_sql_query(query, conn, params=(category_name,))
    conn.close()
    
    if df.empty:
        return f"No data found for {category_name}."

    # --- NumPy Usage ---
    # Convert the pandas column to a NumPy array for calculations
    protein_array = df['protein'].to_numpy()
    
    stats = {
        'mean': np.mean(protein_array),
        'median': np.median(protein_array),
        'std_dev': np.std(protein_array),
        'count': len(protein_array)
    }
    return stats