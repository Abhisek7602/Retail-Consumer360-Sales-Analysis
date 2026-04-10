# Consumer360 — Retail Customer Segmentation & Maket Basket Analysis
![Retail Analytics](https://github.com/Abhisek7602/Retail_Sales_Data_Analysis/blob/main/Retail_image.jpg)

## Overview
This project involves a comprehensive analysis of a national retail chain's transactional data using SQL, Python, and Power BI. The goal is to identify high-value customers ("Whales") versus churn risks by building an industry-standard **RFM (Recency, Frequency, Monetary)** segmentation model. The following README provides a detailed account of the project's objectives, business problems, solutions, findings, and conclusions.

## Objectives

- Build a Star Schema data warehouse from raw transactional logs for downstream analytics.
- Implement RFM scoring (1–5 scale) to segment customers into actionable tiers.
- Execute Market Basket Analysis to uncover non-obvious product affinity patterns.
- Visualize insights in Power BI with Row Level Security for regional access control.
- Automate the ETL pipeline, validate end-to-end flow, build a Churn Risk deck, and document architecture for final handoff.

## Dataset

The data for this project is sourced from a retail transaction log containing invoice-level records:

## Project Steps

### 1. Set Up the Environment
   - **Tools Used**: Visual Studio Code (VS Code), Python, SQL (PostgreSQL)
   - **Goal**: Create a structured workspace within VS Code and organize project folders for smooth development and data handling.
    
### 3. Download Retail Sales Data
   - **Data Source**: Use the Kaggle API to download the Retail Sales datasets from Kaggle.
   - **Dataset Link**: [Retail Sales Data](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci)
   - **Storage**: Save the data in the `data/` folder for easy reference and access.
     
### 4. Load Data into PostgreSQL

   - **Set Up Connections:** Connect to PostgreSQL using sqlalchemy and load the cleaned data into the database.
   - **Table Creation:** Build the full Star Schema — dim_customer, dim_product, dim_date, dim_country, and fact_sales — using Python SQLAlchemy to automate table      creation and data insertion.
   - **Verification:** Run initial SQL queries to confirm data has been loaded accurately and all foreign key relationships are intact.


### 5. Install Required Libraries and Load Data
   - **Libraries**: Install necessary Python libraries using:
     ```bash
     pip install pandas numpy mlxtend
     ```
   - **Loading Data**: Read the data into a Pandas DataFrame for initial analysis and transformations.

### 6. Explore the Data
   - **Goal**: Conduct an initial data exploration to understand data distribution, check column names, types, and identify potential issues.
   - **Analysis**: Use functions like `.info()`, `.describe()`, and `.head()` to get a quick overview of the data structure and statistics.

### 7. Data Cleaning
   - **Remove Duplicates**: Identify and remove duplicate entries to avoid skewed results.
   - **Handle Missing Values**: Drop rows or columns with missing values if they are insignificant; fill values where essential.
   - **Fix Data Types**: Ensure all columns have consistent data types (e.g., dates as `datetime`, prices as `float`).
   - **Currency Formatting**: Use `.replace()` to handle and format currency values for analysis.
   - **Validation**: Check for any remaining inconsistencies and verify the cleaned data.
   - **Remove Cancelled Orders:** Filter out rows where Quantity is negative or zero — these represent returns and cancellations.
   - **Handle Missing Values:** Drop rows with missing Customer ID as they cannot be used in RFM segmentation.
   - **Fix Data Types:** Ensure InvoiceDate is parsed as datetime and Price and Revenue are stored as float.
   - **Remove Invalid Prices:** Filter out rows where Price is zero or negative to avoid skewing monetary calculations.
   - **Validation:** Verify the cleaned dataset for consistency before loading into PostgreSQL.

### 8. Feature Engineering
   - **Create Revenue Column:** Calculate Revenue for each transaction by multiplying Quantity by Price and adding it as a new column.
   - **RFM Metrics:** Derive Recency, Frequency, and Monetary values per customer using grouped aggregations on the cleaned dataset.
   - **RFM Scoring:** Apply quantile-based scoring (1–5 scale) to each RFM dimension and concatenate into a combined RFM_Score.
   - **Customer Segmentation:** Classify each customer into Champion, Loyal, Potential Loyalist, or Hibernating based on R and F score thresholds.

 ### 9.Power BI Dashboard
 - **Data Import:** Load Data.csv, rfm_segments.csv, Rules.csv, and the PostgreSQL fact table into Power BI Desktop.
 - **Dashboard 1:** Sales Analysis: Build KPI cards, revenue trend charts, segment distribution visuals, and the customer-level RFM score table.
 - **Dashboard 2:** Rules Analysis: Visualise association rules, lift vs. confidence scatter plots, and confidence band distributions.
 - **Slicers:** Add Country, Description, Segment, and RFM_Score slicers for dynamic self-service filtering.

### 9. Project Publishing and Documentation
   - **Documentation**: Maintain well-structured documentation of the entire process in this README.md.
   - **Project Publishing**: Publish the completed project on GitHub or any other version control platform, including:
     - The `README.md` file (this document).
     - SQL query scripts.
     - Python ETL and analysis scripts (ETL.py).
     - Power BI .pbix file.
     - Data files (if possible) or steps to access them.

## Requirements

- **Python:3.13**
- **SQL Databases**:PostgreSQL
- **Python Libraries**:
  - `pandas`, `numpy`, `mlxtend`
  - **Kaggle Website** (for data downloading)

## Tech Stack

```
SQL (PostgreSQL)  →  Python (Pandas, mlxtend)  →  Power BI →  Automation
```

## SQL — Creating Dimension Table

### 1. Create the Raw Sales Staging Table.
```sql
CREATE TABLE sales (
    invoice        BIGINT,
    invoice_date   TIMESTAMP,
    customer_id    INTEGER,
    stock_code     VARCHAR(20),
    description    TEXT,
    quantity       INTEGER,
    price          NUMERIC(10,2),
    revenue        NUMERIC(12,2),
    country        VARCHAR(50)
);
```
**Objective:** Define the raw staging table to ingest transactional data as the single source of truth for all downstream dimension and fact table loads.

---

### 2. Build the Customer Dimension Table.
```sql
DROP TABLE IF EXISTS dim_customer;
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY,
    country      VARCHAR(50)
);

INSERT INTO dim_customer
SELECT DISTINCT
    customer_id,
    country
FROM sales
WHERE customer_id IS NOT NULL;
```
**Objective:** Extract unique customers with their associated country into a dedicated dimension table to support regional segmentation.

---

### 3. Build the Product Dimension Table.
```sql
DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product (
    product_key  VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(255)
);

INSERT INTO dim_product
SELECT
    stock_code,
    MAX(description)
FROM sales
GROUP BY stock_code;
```
**Objective:** Normalise product data into a dimension table, using MAX(description) to resolve multiple description variants per stock code into a single canonical product name.

---

### 4. Build the Date Dimension Table.
```sql
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date_key DATE PRIMARY KEY,
    year     INT,
    month    INT,
    day      INT,
    quarter  INT
);

INSERT INTO dim_date (date_key, year, month, day, quarter)
SELECT DISTINCT
    invoice_date::DATE,
    EXTRACT(YEAR    FROM invoice_date)::INT,
    EXTRACT(MONTH   FROM invoice_date)::INT,
    EXTRACT(DAY     FROM invoice_date)::INT,
    EXTRACT(QUARTER FROM invoice_date)::INT
FROM sales
WHERE invoice_date IS NOT NULL;
```
**Objective:** Create a date dimension to enable time-intelligence analysis — monthly sales trends, cohort tracking, and quarter-over-quarter comparisons in Power BI.

---

### 5. Build the Country Dimension Table.
```sql
DROP TABLE IF EXISTS dim_country;
CREATE TABLE dim_country (
    country_key  SERIAL PRIMARY KEY,
    country_name VARCHAR(50)
);

INSERT INTO dim_country (country_name)
SELECT DISTINCT country
FROM sales
WHERE country IS NOT NULL;
```
**Objective:** Isolate country data into a standalone lookup dimension to support geographical revenue analysis and regional filtering across the dashboard.

---

### 6. Build the Central Fact Table.
```sql
DROP TABLE IF EXISTS fact_sales;
CREATE TABLE fact_sales (
    sales_id     SERIAL PRIMARY KEY,
    invoice_no   VARCHAR(20),
    customer_key INT,
    product_key  VARCHAR(20),
    date_key     DATE,
    quantity     INT,
    price        DECIMAL(10,2),
    revenue      DECIMAL(12,2),

    CONSTRAINT fk_customer FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_product  FOREIGN KEY (product_key)  REFERENCES dim_product(product_key),
    CONSTRAINT fk_date     FOREIGN KEY (date_key)     REFERENCES dim_date(date_key)
);

INSERT INTO fact_sales (invoice_no, customer_key, product_key, date_key, quantity, price, revenue)
SELECT
    invoice,
    customer_id,
    stock_code,
    invoice_date::DATE,
    quantity,
    price,
    revenue
FROM sales
WHERE quantity    > 0
  AND customer_id    IS NOT NULL
  AND invoice_date   IS NOT NULL;
```
**Objective:** Load clean, validated transactional records into the central fact table with enforced foreign key relationships to all dimension tables, forming the core of the Star Schema.

---

### 7. Build the RFM Aggregation Table.
```sql
DROP TABLE IF EXISTS clean_sales_customer;
CREATE TABLE clean_sales_customer (
    customer_id        INT PRIMARY KEY,
    last_purchase_date DATE,
    frequency          INT,
    monetary           DECIMAL(12,2)
);

INSERT INTO clean_sales_customer
SELECT
    customer_id,
    MAX(invoice_date)       AS last_purchase_date,
    COUNT(DISTINCT invoice) AS frequency,
    SUM(quantity * price)   AS monetary
FROM sales
GROUP BY customer_id;
```
**Objective:** Pre-aggregate the three core RFM dimensions — recency anchor date, purchase frequency, and total monetary value — per customer as the direct input to the Python scoring pipeline.

---

## Python — RFM Analysis and Market basket Analysis

## RFM Analysis

```python
rfm = df.groupby('Customer ID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,  # Recency
    'Invoice':     'nunique',                                  # Frequency
    'Revenue':     'sum'                                       # Monetary
}).reset_index()

rfm['R_Score'] = pd.qcut(rfm['Recency'].rank(method='first'),  5, labels=[5,4,3,2,1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'),  5, labels=[1,2,3,4,5])

rfm.to_csv("rfm_customer_segments.csv", index=False)

def segment(row):
    if row['R_Score'] >= '4' and row['F_Score'] >= '4':
        return 'Champion'
    elif row['F_Score'] >= '4':
        return 'Loyal'
    elif row['R_Score'] <= '2' and row['F_Score'] <= '2':
        return 'Hibernating'
    else:
        return 'Potential Loyalist'

rfm['Segment'] = rfm.apply(segment, axis=1)

rfm.groupby('Segment')['Monetary'].mean().sort_values(ascending=False)

rfm.to_csv("rfm_segments.csv", index=False

```

## Market Basket Analysis

```python

from mlxtend.frequent_patterns import apriori, association_rules

basket = df.groupby(['InvoiceNo', 'StockCode'])['Quantity'] \
            .sum().unstack().fillna(0)

basket = basket.applymap(lambda x: 1 if x > 0 else 0)

frequent_items = apriori(basket, min_support=0.02, use_colnames=True)
rules = association_rules(
     frequent_items,
     metric='lift',
     min_threshold=1.2 )
rules.sort_values('confidence', ascending=False).head()

rules.to_csv("Rules.csv", index=False)
```

---

## Power BI — Sales Analysis & Rules Analysis Dashboard

## Dashboard 1 — Sales Analysis

**Page:** Sales Analysis  
**KPI Cards:** Sum of Revenue (998.14K) | Count of Customers (283) | Distinct Invoices (336) | AOV (2.97K) | Avg Spending by Segment (3.53K)

### Visual 1. Revenue by Day (Line Chart).
```dax
Revenue by Day = SUM(Data[Revenue])
```
**Objective:** Track daily revenue fluctuations to identify peak and low-performing days across the sales period.

---

### Visual 2. Revenue by Day and Segment (Stacked Bar Chart).
```dax
Revenue by Segment = 
CALCULATE(
    SUM(Data[Revenue]),
    ALLEXCEPT(Rfm_Segment, Rfm_Segment[Segment])
)
```
**Objective:** Compare daily revenue contribution across all four customer segments — Champion, Loyal, Potential Loyalist, and Hibernating — to identify which tiers drive peak-day performance.

---

### Visual 3. Revenue by Country (Donut Chart).
```dax
Revenue by Country = 
CALCULATE(
    SUM(Data[Revenue]),
    ALLEXCEPT(Data, Data[Country])
)
```
**Objective:** Visualise geographical revenue distribution to identify dominant markets — United Kingdom, Netherlands, Portugal, EIRE, and France.

---

### Visual 4. Revenue by Description (Horizontal Bar Chart).
```dax
Top Products by Revenue = 
CALCULATE(
    SUM(Data[Revenue]),
    TOPN(10, ALL(Data[Description]), SUM(Data[Revenue]))
)
```
**Objective:** Surface the Top 10 best-selling products by revenue to guide inventory prioritisation and promotional strategy.

---

### Visual 5. RFM Score Table (Customer-Level Detail Table).

Columns Displayed: CustomerID | R_Score | F_Score | M_Score | RFM_Score | Segment

**Objective:** Provide a granular, customer-level view of all RFM scores and assigned segments — enabling the sales team to directly action the Hibernating churn-risk list.

---

### Visual 6. Count of Customers by Segment (Pie Chart).
```dax
Customer Count by Segment = 
CALCULATE(
    DISTINCTCOUNT(Rfm_Segment[CustomerID]),
    ALLEXCEPT(Rfm_Segment, Rfm_Segment[Segment])
)
```
**Objective:** Show the proportional distribution of customers across all four segments — Hibernating (47%), Champion (22.97%), Potential Loyalist (16.96%), and Loyal — to quantify churn exposure at a glance.

---

## Dashboard 2 — Rules Analysis (Market Basket)

**Page:** Rules Analysis  
**KPI Cards:** Total Association Rules (234) | Max Lift Score (27.15) | Avg Confidence (0.43) | High Confidence Rules (26)

---

### Visual 7. Association Rules Table (Antecedents → Consequents).

Columns Displayed: antecedents | consequents | Sum of Lift | Sum of Confidence

**Objective:** Display all generated association rules ranked by lift score to identify the strongest product affinity pairs for cross-sell and bundle campaign targeting.

---

### Visual 8. Sum of Lift and Confidence by Antecedents (Bar Chart).
```dax
Lift by Antecedent = 
CALCULATE(
    SUM(Rules[lift]),
    ALLEXCEPT(Rules, Rules[antecedents])
)
```
**Objective:** Rank antecedent products by their combined lift and confidence scores to identify which trigger products most reliably predict a secondary purchase.

---

### Visual 9. Sum of Lift and Confidence by Consequents (Bar Chart).
```dax
Confidence by Consequent = 
CALCULATE(
    SUM(Rules[confidence]),
    ALLEXCEPT(Rules, Rules[consequents])
)
```
**Objective:** Identify which consequent products are most frequently recommended across all rules — highlighting the highest-affinity cross-sell targets for marketing campaigns.

---

### Visual 10. Avg Confidence by Confidence Band (Donut Chart).
```sql
Confidence Band Categories:
Very Strong  →  Confidence >= 0.70   (47.39%)
Strong       →  Confidence >= 0.50   (35.66%)
Moderate     →  Confidence >= 0.30   (16.95%)
```

**Objective:** Segment all 234 association rules into confidence bands to help the marketing team prioritise only the highest-reliability product recommendations for bundle promotions.

---

### Visual 11. Lift vs. Confidence Scatter Plot (Antecedent × Consequent).
```dax
Avg Confidence = AVERAGE(Rules[confidence])
Max Lift Score = MAX(Rules[lift])
```
**Objective:** Plot every association rule on a Lift vs. Confidence axis to visually identify the ideal sweet-spot rules — high confidence and high lift — that deliver both reliability and impact for targeted cross-selling.

## Filters Applied Across Both Pages
```sql
Slicer 1 — Country     : Filter all visuals by market geography
Slicer 2 — Description : Filter by specific product
Slicer 3 — Segment     : Isolate Champion / Loyal / Hibernating / Potential Loyalist
Slicer 4 — RFM_Score   : Drill into specific RFM score combinations
```

**Objective:** Enable dynamic, self-service filtering so regional managers and business stakeholders can independently explore the data without modifying the underlying model.

---

## Python — Automation (ETL.py)
```python

# -------------------------------
#Importing Necessary Library
# -------------------------------
import pandas as pd
import numpy as np
import datetime as dt

# -------------------------------
#Read the file
# -------------------------------
df=pd.read_csv(r'"C:\Users\nayak\Desktop\Projects\Retail_Sales_Data_Analysis\Clean_Sales.csv"')
print(df)

# -------------------------------
#To Datatime Formate
# -------------------------------
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# -------------------------------
# Remove cancelled orders & invalid rows
# -------------------------------
df = df[df['Quantity'] > 0]
df = df[df['Price'] > 0]
df.dropna(subset=['Customer ID'], inplace=True)

# -------------------------------
# Create Total Price
# -------------------------------
df['Revenue'] = df['Quantity'] * df['Price']

# -------------------------------
# 2. Snapshot Date (for Recency)
# -------------------------------
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%d-%m-%Y %H:%M')
snapshot_date = df['InvoiceDate'].max() + dt.timedelta(days=1)

# -------------------------------
# 3. Calculate RFM Metrics
# -------------------------------

df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%d-%m-%Y %H:%M')
snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
rfm = df.groupby('Customer ID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'Invoice':     'nunique',
    'Revenue':     'sum'
}).reset_index()
rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
rfm

# -------------------------------
# 4. RFM Scoring (1-5 scale)
# -------------------------------
# RECENCY SCORE (R_Score)
rfm['R_Score'] = pd.qcut(rfm['Recency'].rank(method='first'), 5, labels=[5,4,3,2,1])

# FREQUENCY SCORE (F_Score)
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])

# MONETARY SCORE (M_Score)
rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])

# COMBINED RFM SCORE
rfm['RFM_Score'] = rfm['R_Score'].astype(str) + \
                   rfm['F_Score'].astype(str) + \
                   rfm['M_Score'].astype(str)

rfm

# -------------------------------
# 5. Customer Segmentation
# -------------------------------

def segment(row):
    if row['R_Score'] >= '4' and row['F_Score'] >= '4':
        return 'Champion'
    elif row['F_Score'] >= '4':
        return 'Loyal'
    elif row['R_Score'] <= '2' and row['F_Score'] <= '2':
        return 'Hibernating'
    else:
        return 'Potential Loyalist'
rfm['Segment'] = rfm.apply(segment, axis=1)
rfm.groupby('Segment')['Monetary'].mean().sort_values(ascending=False)

# -------------------------------
# 6. Export Processed Data
# -------------------------------

rfm.to_csv("rfm_customer_segments.csv", index=False)
print("RFM pipeline completed successfully")

# -------------------------------
# 6. Market Basket Analysis
# -------------------------------

from mlxtend.frequent_patterns import apriori, association_rules
basket = df.groupby(['InvoiceNo', 'StockCode'])['Quantity'] \
             .sum().unstack().fillna(0)

basket = basket.applymap(lambda x: 1 if x > 0 else 0)
frequent_items = apriori(basket, min_support=0.02, use_colnames=True)

rules = association_rules(
      frequent_items,
      metric='lift',
      min_threshold=1.2)

rules.sort_values('confidence', ascending=False).head()

rules.to_csv("Rules.csv", index=False)

```

## Findings and Conclusion

- **Revenue Overview:** The dataset contains 10,000 transactions generating 998.14K in total revenue across 283 unique customers and 336 distinct invoices, with an Average Order Value of 2.97K.
- **Revenue Overview:**  The dataset contains 10,000 transactions generating 998.14K in total revenue across 283 unique customers and 336 distinct invoices, with an Average Order Value of 2.97K.
- **Geographical Dominance:** The United Kingdom is the overwhelmingly dominant market, followed by Netherlands, Portugal, EIRE, and France — confirming the need for UK-focused retention strategy.
- **RFM Segmentation:** Champions (22.97%) represent the highest average spend tier at 3.53K and were statistically validated — satisfying the core project audit requirement that Champions demonstrably lead in Lifetime Value.
- **Churn Exposure:** Hibernating customers account for 47% of the entire customer base — the largest single segment — representing the most critical and immediate priority for win-back campaigns.
- **Loyal & Potential Loyalist Gap:** Loyal (13.07%) and Potential Loyalist (16.96%) segments together hold significant untapped revenue potential and should be targeted with frequency-driving promotions to accelerate their upgrade to Champion status.
- **Market Basket Analysis:** The Apriori algorithm generated 234 association rules with a Max Lift Score of 27.15, identifying 26 high-confidence rules — confirming strong, non-obvious product affinity patterns actionable for cross-sell bundle campaigns.
- **Rule Confidence Distribution:** Nearly half of all rules (47.39%) fall in the Very Strong confidence band (≥0.70), providing the marketing team a reliable, high-precision set of product recommendations to act on immediately.
- **Pipeline Automation:** The end-to-end ETL pipeline — from raw CSV ingestion through RFM scoring to Power BI dashboard — was successfully automated, ensuring zero-touch scheduled execution for future reporting cycles.

---

## 4-Week Project Timeline

| Week | Focus Area | Key Deliverables |
|------|-----------|-----------------|
| Week 1 | Data Engineering & Schema | Star Schema (Fact + Dims), Single Customer View SQL |
| Week 2 | Analytical Core (Python) | RFM Scores, Segment Tiers, Market Basket Rules |
| Week 3 | Dashboard Construction | Power BI Dashboard Preparation|
| Week 4 | Automation & Handoff | Airflow/Cron ETL, Executive Presentation Deck |

---

