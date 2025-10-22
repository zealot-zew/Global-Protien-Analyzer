# 🌍 Global Food & Nutrition Analyzer

This project is a **Python-based data analysis tool** that processes the [Open Food Facts](https://world.openfoodfacts.org/) dataset to analyze the **protein content of food products** across various countries and categories.

It demonstrates a complete, miniature **data pipeline**:

- **Extract:** Reading a massive, raw TSV (or CSV) file.  
- **Transform:** Cleaning, filtering, and standardizing the data using Pandas.  
- **Load:** Storing the clean, processed data into an SQLite database.  
- **Analyze:** Running queries on the database using Pandas and performing statistical calculations with NumPy.

---

## 🚀 Features

- Analyzes **average protein content** for all food categories in a specific country.  
- Analyzes **average protein content for a specific food category**, broken down by country.  
- Provides detailed **statistical analysis** (mean, median, standard deviation) for any given food category using NumPy.  
- Includes a simple, **interactive Command-Line Interface (CLI)** to access all analysis.

---

## 💻 Technologies Used

- **Python 3.10+**  
- **Pandas:** For data loading, cleaning, and analysis.  
- **NumPy:** For high-performance statistical calculations.  
- **SQLite3:** (Python's built-in module) For storing and querying the cleaned data.

---

## 📂 Project Structure

```
food-analyzer/
├── .venv/                   # Virtual environment
├── data/
│   └── en.openfoodfacts.org.products.tsv  # The (very large) raw data file
├── cleaner.py               # Script to clean raw data and build the DB
├── analysis.py              # Module with all analysis functions
├── main.py                  # Main script to run the application
├── food.db                  # The generated SQLite database (after running cleaner.py)
├── requirements.txt         # List of Python dependencies
└── README.md                # This file
```

---

## 🛠️ How to Use

### 1. Prerequisites

- Python 3  
- Git (optional, for cloning)  
- The Open Food Facts dataset (TSV or CSV)

---

### 2. Installation & Setup

#### Step A: Clone and set up the environment

```bash
# 1. Clone the repository (or download the files)
git clone https://github.com/zealot-zew/Global-Protien-Analyzer.git
cd Global-Protien-Analyzer

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the environment
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install the required packages
pip install pandas numpy

#### Step B: Get the Data

1. Download the dataset from [Kaggle: Open Food Facts Dataset](https://www.kaggle.com/openfoodfacts/open-food-facts).  
2. Find the file named `en.openfoodfacts.org.products.tsv` (or `.csv`).  
3. Create a folder named `data` in your project directory.  
4. Place the downloaded file inside the `data/` folder.

---

### 3. Running the Project

This is a **two-step process**. You must build the database first, then run the app.

#### Step 1: Build the Database (Run ONCE)

```bash
python cleaner.py
```

**Output:**
```
Loading raw TSV...
Cleaning data...
Cleaned data has XXXXX rows.
Saving to database 'food.db'...
Done! Database 'food.db' is ready.
```

You will now see a `food.db` file in your directory.  
You only need to run this script again if your raw data changes.

#### Step 2: Run the Application

```bash
python main.py
```

This will start the **interactive CLI menu**, and you can begin your analysis.

---

## 🔬 How the Code Works

### 1. `cleaner.py` – *The Data Janitor*

This script’s job is to convert the raw, messy `en.openfoodfacts.org.products.tsv` file into a clean, fast, and small SQLite database (`food.db`).

**Workflow:**
- **Load:**  
  Uses `pd.read_csv()` to load the TSV file with `sep='\t'` and specific columns (`usecols=[...]`).
- **Define Scope:**  
  Filters by `TARGET_COUNTRIES` and `TARGET_CATEGORIES` to reduce noise.
- **Clean:**  
  - Renames columns (e.g., `proteins_100g` → `protein`)  
  - Drops rows with missing key values using `.dropna()`  
  - Standardizes strings with custom `clean_country` and `clean_category` functions.  
- **Store:**  
  Saves the final DataFrame to SQLite with:
  ```python
  df.to_sql('products', conn, if_exists='replace', index=False)
  ```

---

### 2. `analysis.py` – *The Brain*

This module holds all the logic for performing analysis on `food.db`.

**Functions:**

- `get_mean_protein_by_country(country_name)`  
  - Runs SQL query: `SELECT category, protein FROM products WHERE country = ?`  
  - Groups by category using `df.groupby('category')['protein'].mean()`  
  - Returns mean protein by category for that country.

- `get_mean_protein_by_category(category_name)`  
  - Reverse of the above.  
  - Groups by country using `df.groupby('country')['protein'].mean()`  
  - Returns average protein per country for a category.

- `get_overall_stats_for_category(category_name)`  
  - Fetches all protein values for a given category.  
  - Converts to NumPy array using `df['protein'].to_numpy()`.  
  - Calculates and returns mean, median, and standard deviation using NumPy.

---

### 3. `main.py` – *The User Interface*

This is the entry point for users.

**Responsibilities:**
- Imports functions from `analysis.py`.  
- Runs a menu loop (`while True:`) to show options.  
- Takes user input for country or category.  
- Calls the correct function and displays results neatly.

This structure cleanly separates:
- **Data prep** → `cleaner.py`  
- **Analysis logic** → `analysis.py`  
- **User interaction** → `main.py`