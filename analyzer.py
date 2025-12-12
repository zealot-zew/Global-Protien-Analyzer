import pandas as pd
import numpy as np
import sqlite3

class NutritionAnalyzer:
    def __init__(self, db_path, shopping_list_path):
        self.db_path = db_path
        self.list_path = shopping_list_path

        # Recommended Daily Limits (Adult)
        self.LIMITS = {
            'sugar': 50.0,   # grams
            'salt': 5.0,     # grams
            'sat_fat': 20.0  # grams
        }

    def load_data(self):
        """Loads shopping list and merges with database."""
        # 1. Load User List
        try:
            # We read the CSV.
            user_df = pd.read_csv(self.list_path, dtype={'barcode': str})
        except FileNotFoundError:
            return None

        # 2. Load Product Database
        conn = sqlite3.connect(self.db_path)
        # Read all products (in a real app, you'd filter by barcode here)
        db_df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()

        # 3. Merge (Left Join)
        merged_df = pd.merge(user_df, db_df, on='barcode', how='left')

        # Handle unknown products (fill NaNs with 0)
        merged_df.fillna(0, inplace=True)

        return merged_df

    def analyze(self, df):
        """Performs calculation using NumPy vectorization."""
        if df is None or df.empty:
            return None

        days_in_period = 7.0

        # --- 🛡️ SAFETY FIX: FORCE NUMERIC TYPES ---
        # This block prevents the "can't multiply sequence" error.
        # It forces columns to be numbers, turning bad strings (like "300g") into clean numbers or NaNs.

        # 1. Clean Quantity and Weight
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1.0)
        df['weight_per_unit_g'] = pd.to_numeric(df['weight_per_unit_g'], errors='coerce').fillna(100.0)

        # 2. Clean Nutrients
        for col in ['sugar_100g', 'salt_100g', 'sat_fat_100g']:
             df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # --- NUMPY CALCULATIONS (Now safe) ---

        # 1. Calculate Total Weight Consumed per item
        total_weight_g = df['quantity'].values * df['weight_per_unit_g'].values

        # 2. Calculate Total Nutrient Content
        # Formula: Total Weight * (Nutrient per 100g / 100)
        df['total_sugar'] = total_weight_g * (df['sugar_100g'].values / 100)
        df['total_salt'] = total_weight_g * (df['salt_100g'].values / 100)
        df['total_sat_fat'] = total_weight_g * (df['sat_fat_100g'].values / 100)

        # 3. Daily Contribution
        df['daily_sugar'] = df['total_sugar'] / days_in_period
        df['daily_salt'] = df['total_salt'] / days_in_period
        df['daily_sat_fat'] = df['total_sat_fat'] / days_in_period

        # 4. Risk Score
        sugar_risk = df['daily_sugar'] / self.LIMITS['sugar']
        salt_risk = df['daily_salt'] / self.LIMITS['salt']
        fat_risk = df['daily_sat_fat'] / self.LIMITS['sat_fat']

        # $$ Risk = 0.5 * SugarRisk + 0.3 * SaltRisk + 0.2 * FatRisk $$
        df['risk_score'] = (0.5 * sugar_risk) + (0.3 * salt_risk) + (0.2 * fat_risk)

        return df

    def get_weekly_totals(self, df):
        """Aggregates data for the final report."""
        return {
            'sugar': df['daily_sugar'].sum(),
            'salt': df['daily_salt'].sum(),
            'sat_fat': df['daily_sat_fat'].sum()
        }