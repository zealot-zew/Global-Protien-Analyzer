# In main.py
#This file is the user-facing menu. It just calls the functions from analysis.py

import analysis  # Import your other file
import os

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    """Displays the main menu and gets user input."""
    print("\n--- 🍞 Global Protein Analyzer 🥩 ---")
    print("1. See protein stats by Country")
    print("2. See protein stats by Category")
    print("3. Get detailed stats for one Category")
    print("4. Exit")
    return input("Enter your choice: ")

def run_stats_by_country():
    country = input("Enter country (e.g., France, United States): ").title()
    print(f"\nCalculating stats for {country}...")
    results = analysis.get_mean_protein_by_country(country)
    print("--- Average Protein (g) per Category ---")
    print(results)

def run_stats_by_category():
    category = input("Enter category (e.g., Meats, Snacks, Beverages): ").title()
    print(f"\nCalculating stats for {category}...")
    results = analysis.get_mean_protein_by_category(category)
    print("--- Average Protein (g) by Country ---")
    print(results)

def run_detailed_stats():
    category = input("Enter category (e.g., Meats, Snacks, Beverages): ").title()
    print(f"\nCalculating stats for {category}...")
    stats = analysis.get_overall_stats_for_category(category)
    
    if isinstance(stats, str):
        print(stats)
        return

    print(f"\n--- Detailed NumPy Stats for {category} ---")
    print(f"Total Products Analyzed: {stats['count']}")
    print(f"Mean Protein:   {stats['mean']:.2f}g")
    print(f"Median Protein: {stats['median']:.2f}g")
    print(f"Std. Deviation: {stats['std_dev']:.2f}g")

# --- Main Application Loop ---
if __name__ == "__main__":
    while True:
        clear_screen()
        choice = main_menu()
        
        if choice == '1':
            run_stats_by_country()
        elif choice == '2':
            run_stats_by_category()
        elif choice == '3':
            run_detailed_stats()
        elif choice == '4':
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            
        input("\nPress Enter to return to the menu...")