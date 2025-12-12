from analyzer import NutritionAnalyzer
from tabulate import tabulate # For pretty tables
import pandas as pd

def main():
    print("🛒 --- Grocery Trip Risk Report --- 🛒\n")

    # Initialize
    analyzer = NutritionAnalyzer(
        db_path='data/products.db',
        shopping_list_path='data/shopping_list1.csv'
    )

    # Process
    raw_data = analyzer.load_data()

    if raw_data is None:
        print("Error: Could not load data.")
        return

    processed_data = analyzer.analyze(raw_data)
    totals = analyzer.get_weekly_totals(processed_data)

    # --- 1. OVERALL HEALTH SUMMARY ---
    print("📊 DAILY INTAKE ESTIMATES (Avg over 7 days):")

    limits = analyzer.LIMITS

    # Sugar Check
    sugar_flag = "🚨 HIGH" if totals['sugar'] > limits['sugar'] else "✅ OK"
    print(f"  - Sugar:       {totals['sugar']:.1f}g / {limits['sugar']}g  [{sugar_flag}]")

    # Salt Check
    salt_flag = "🚨 HIGH" if totals['salt'] > limits['salt'] else "✅ OK"
    print(f"  - Salt:        {totals['salt']:.1f}g / {limits['salt']}g   [{salt_flag}]")

    # Fat Check
    fat_flag = "🚨 HIGH" if totals['sat_fat'] > limits['sat_fat'] else "✅ OK"
    print(f"  - Sat. Fat:    {totals['sat_fat']:.1f}g / {limits['sat_fat']}g  [{fat_flag}]")
    print("-" * 50)

    # --- 2. RISKY PRODUCT IDENTIFICATION ---
    print("\n🔍 TOP RISKY PRODUCTS (Contributing most to daily excess):")

    # Sort by risk score descending
    risky_df = processed_data.sort_values(by='risk_score', ascending=False)

    # Select columns to display
    display_cols = ['product_name', 'quantity', 'daily_sugar', 'daily_salt', 'risk_score']

    # Rename for cleaner output
    output_table = risky_df[display_cols].copy()
    output_table.columns = ['Product', 'Qty', 'Daily Sugar(g)', 'Daily Salt(g)', 'Risk Index']

    print(tabulate(output_table, headers='keys', tablefmt='simple', showindex=False, floatfmt=".2f"))

    # --- 3. EXPORT ---
    processed_data.to_html("data/risk_report.html")
    print("\n📄 Detailed HTML report saved to 'data/risk_report.html'")

if __name__ == "__main__":
    main()