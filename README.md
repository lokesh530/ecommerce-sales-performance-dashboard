# E-Commerce Sales Performance Dashboard

## Project Overview
A complete, industry-level data analytics project that demonstrates the end-to-end data pipeline from raw data generation to SQL database design, advanced data analysis, and an interactive Streamlit web dashboard.

## 🚀 Features
- **Synthetic Data Generation:** Python script (`generate_data.py`) utilizing the `Faker` library to generate a realistic Indian-market E-commerce dataset (16,500+ records).
- **Relational Database Design:** Normalized schema design (Customers, Products, Orders, Order Items) with primary/foreign key constraints.
- **Advanced SQL Analysis:** Over 15 comprehensive business queries including Window Functions (`RANK`, `ROW_NUMBER`), Common Table Expressions (CTEs), Subqueries, and multi-table Joins.
- **Interactive Web Dashboard:** A multi-page Streamlit application with Plotly visualizations analyzing Sales, Products, Customers, Profit margins, and Inventory levels.

## 🛠️ Technology Stack
- **Database:** MySQL / SQLite
- **Languages:** SQL, Python
- **Libraries:** Pandas, SQLAlchemy, Streamlit, Plotly, Faker

## 📂 Project Structure
```
├── app.py                      # Streamlit Web Dashboard
├── data/                       # Raw CSV dataset files
├── scripts/
│   ├── generate_data.py        # Python script to generate synthetic data
│   └── db_setup.py             # Python script for initial database loading
└── sql/
    ├── 00_master_setup.sql     # Master SQL script to create tables and load data
    └── analysis_queries.sql    # Advanced SQL business queries
```

## 📊 Dashboard Previews
The dashboard contains 5 main pages:
1. **Home:** High-level KPIs and business overview.
2. **Sales:** Revenue trends over time and payment method analysis.
3. **Products:** Top selling products and category distribution.
4. **Customers:** Customer acquisition trends and top spenders.
5. **Profit & Inventory:** Profit margins and low-stock alerts.

## 💡 How to Run Locally

### 1. Database Setup
Execute the `00_master_setup.sql` script inside MySQL Workbench or any SQL client to instantly build the database schema and insert all 16,500 rows.

### 2. Streamlit Dashboard
Install the required python packages and run the dashboard:
```bash
pip install streamlit pandas plotly sqlalchemy
streamlit run app.py
```
