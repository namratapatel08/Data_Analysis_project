"""
ETL Pipeline for E-Commerce Sales Analytics & Star Schema Data Warehouse
Transforms raw operational CSVs from archive/ into a clean, normalized Star Schema
saved in SQLite (data/ecommerce.db) and fast Parquet files for high-speed dashboard analytics.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def run_etl():
    print("=" * 60)
    print("[INFO] Starting E-Commerce ETL Pipeline...")
    print("=" * 60)

    os.makedirs('data', exist_ok=True)
    db_path = os.path.join('data', 'ecommerce.db')
    conn = sqlite3.connect(db_path)

    # 1. Load and Clean Amazon Sales Report
    print("\n[1/6] Loading & Cleaning Amazon Sales Report...")
    amz_path = os.path.join('archive', 'Amazon Sale Report.csv')
    df_amz = pd.read_csv(amz_path, low_memory=False)

    # Column renaming
    rename_cols = {
        'Order ID': 'order_id',
        'Date': 'order_date',
        'Status': 'status',
        'Fulfilment': 'fulfilment',
        'Sales Channel ': 'sales_channel',
        'ship-service-level': 'ship_service_level',
        'Style': 'style',
        'SKU': 'sku',
        'Category': 'category',
        'Size': 'size',
        'ASIN': 'asin',
        'Courier Status': 'courier_status',
        'Qty': 'qty',
        'currency': 'currency',
        'Amount': 'amount',
        'ship-city': 'ship_city',
        'ship-state': 'ship_state',
        'ship-postal-code': 'ship_postal_code',
        'ship-country': 'ship_country',
        'promotion-ids': 'promotion_ids',
        'B2B': 'b2b',
        'fulfilled-by': 'fulfilled_by'
    }
    df_amz = df_amz.rename(columns=rename_cols)
    if 'Unnamed: 22' in df_amz.columns:
        df_amz = df_amz.drop(columns=['Unnamed: 22'])
    if 'index' in df_amz.columns:
        df_amz = df_amz.drop(columns=['index'])

    # Data type cleaning
    df_amz['order_date'] = pd.to_datetime(df_amz['order_date'], format='mixed', errors='coerce')
    df_amz['amount'] = pd.to_numeric(df_amz['amount'], errors='coerce').fillna(0.0)
    df_amz['qty'] = pd.to_numeric(df_amz['qty'], errors='coerce').fillna(0).astype(int)
    df_amz['sku'] = df_amz['sku'].astype(str).str.strip()
    df_amz['category'] = df_amz['category'].astype(str).str.strip().str.title()
    df_amz['sales_channel'] = df_amz['sales_channel'].astype(str).str.strip()
    df_amz['ship_state'] = df_amz['ship_state'].astype(str).str.strip().str.title()
    df_amz['ship_city'] = df_amz['ship_city'].astype(str).str.strip().str.title()
    df_amz['b2b'] = df_amz['b2b'].fillna(False).astype(bool)
    df_amz['is_promotional'] = df_amz['promotion_ids'].notna() & (df_amz['promotion_ids'].str.strip() != '')

    # Standardize order status
    def clean_status(st):
        st = str(st).strip()
        if 'Delivered' in st:
            return 'Delivered'
        elif 'Returned' in st:
            return 'Returned'
        elif 'Cancelled' in st:
            return 'Cancelled'
        elif 'Shipped' in st:
            return 'Shipped'
        elif 'Pending' in st:
            return 'Pending'
        return st

    df_amz['status_simplified'] = df_amz['status'].apply(clean_status)
    print(f"   Loaded {len(df_amz):,} Amazon order records.")

    # 2. Load and Clean International Sales Report (for customer concentration & enrichment)
    print("\n[2/6] Loading & Cleaning International Sales Report...")
    intl_path = os.path.join('archive', 'International sale Report.csv')
    df_intl = pd.read_csv(intl_path, low_memory=False)
    
    # Clean column names
    df_intl.columns = [c.strip() for c in df_intl.columns]
    df_intl_clean = pd.DataFrame()
    df_intl_clean['sku'] = df_intl['SKU'].astype(str).str.strip()
    df_intl_clean['customer_name'] = df_intl['CUSTOMER'].astype(str).str.strip()
    df_intl_clean['months'] = df_intl['Months'].astype(str).str.strip()
    df_intl_clean['rate'] = pd.to_numeric(df_intl['RATE'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce').fillna(0.0)
    df_intl_clean['gross_amt'] = pd.to_numeric(df_intl['GROSS AMT'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce').fillna(0.0)
    df_intl_clean['pcs'] = pd.to_numeric(df_intl['PCS'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce').fillna(1.0)
    df_intl_clean = df_intl_clean.dropna(subset=['sku'])
    print(f"   Loaded {len(df_intl_clean):,} International sales records across {df_intl_clean['customer_name'].nunique():,} customers.")

    # 3. Load Multi-Channel Pricing (May-2022.csv)
    print("\n[3/6] Loading Multi-Channel Pricing Intelligence (May-2022)...")
    may_path = os.path.join('archive', 'May-2022.csv')
    df_pricing = pd.read_csv(may_path, low_memory=False)
    df_pricing.columns = [c.strip() for c in df_pricing.columns]
    
    pricing_clean = pd.DataFrame()
    pricing_clean['sku'] = df_pricing['Sku'].astype(str).str.strip()
    pricing_clean['style_id'] = df_pricing['Style Id'].astype(str).str.strip()
    pricing_clean['catalog'] = df_pricing['Catalog'].astype(str).str.strip()
    pricing_clean['category'] = df_pricing['Category'].astype(str).str.strip().str.title()
    pricing_clean['weight'] = df_pricing['Weight']
    pricing_clean['tp_cost'] = pd.to_numeric(df_pricing['TP'], errors='coerce').fillna(0.0)
    pricing_clean['mrp_old'] = pd.to_numeric(df_pricing['MRP Old'], errors='coerce').fillna(0.0)
    pricing_clean['final_mrp_old'] = pd.to_numeric(df_pricing['Final MRP Old'], errors='coerce').fillna(0.0)
    pricing_clean['ajio_mrp'] = pd.to_numeric(df_pricing['Ajio MRP'], errors='coerce').fillna(0.0)
    pricing_clean['amazon_mrp'] = pd.to_numeric(df_pricing['Amazon MRP'], errors='coerce').fillna(0.0)
    pricing_clean['amazon_fba_mrp'] = pd.to_numeric(df_pricing['Amazon FBA MRP'], errors='coerce').fillna(0.0)
    pricing_clean['flipkart_mrp'] = pd.to_numeric(df_pricing['Flipkart MRP'], errors='coerce').fillna(0.0)
    pricing_clean['limeroad_mrp'] = pd.to_numeric(df_pricing['Limeroad MRP'], errors='coerce').fillna(0.0)
    pricing_clean['myntra_mrp'] = pd.to_numeric(df_pricing['Myntra MRP'], errors='coerce').fillna(0.0)
    pricing_clean['paytm_mrp'] = pd.to_numeric(df_pricing['Paytm MRP'], errors='coerce').fillna(0.0)
    pricing_clean['snapdeal_mrp'] = pd.to_numeric(df_pricing['Snapdeal MRP'], errors='coerce').fillna(0.0)
    
    # Derived MRP average and Margin %
    platforms = ['amazon_mrp', 'ajio_mrp', 'flipkart_mrp', 'myntra_mrp', 'limeroad_mrp', 'paytm_mrp', 'snapdeal_mrp']
    pricing_clean['avg_mrp'] = pricing_clean[platforms].replace(0, np.nan).mean(axis=1).fillna(0.0).round(2)
    pricing_clean['gross_margin_pct'] = np.where(
        pricing_clean['avg_mrp'] > 0,
        ((pricing_clean['avg_mrp'] - pricing_clean['tp_cost']) / pricing_clean['avg_mrp'] * 100).round(2),
        0.0
    )
    print(f"   Loaded pricing intelligence for {len(pricing_clean):,} SKUs across 7 marketplace platforms.")

    # 4. Load Inventory & Stock Health (Sale Report.csv)
    print("\n[4/6] Loading Stock & Inventory Health (Sale Report)...")
    stock_path = os.path.join('archive', 'Sale Report.csv')
    df_stock = pd.read_csv(stock_path, low_memory=False)
    df_stock.columns = [c.strip() for c in df_stock.columns]
    
    stock_clean = pd.DataFrame()
    stock_clean['sku'] = df_stock['SKU Code'].astype(str).str.strip()
    stock_clean['design_no'] = df_stock['Design No.'].astype(str).str.strip()
    stock_clean['stock'] = pd.to_numeric(df_stock['Stock'], errors='coerce').fillna(0.0)
    stock_clean['category'] = df_stock['Category'].astype(str).str.strip().str.title()
    stock_clean['size'] = df_stock['Size'].astype(str).str.strip()
    stock_clean['color'] = df_stock['Color'].astype(str).str.strip().str.title()
    
    # Classify stock health
    def classify_stock(stk):
        if stk <= 0:
            return 'Out of Stock'
        elif stk <= 10:
            return 'Critical Low (1-10)'
        elif stk <= 50:
            return 'Moderate (11-50)'
        else:
            return 'Healthy (>50)'
            
    stock_clean['stock_status'] = stock_clean['stock'].apply(classify_stock)
    print(f"   Loaded inventory records for {len(stock_clean):,} SKUs.")

    # 5. Build Enriched Fact Sales Orders (Star Schema)
    print("\n[5/6] Building Star Schema & Enriched Fact Sales Table...")
    # Exact filter matching MySQL project: status = Shipped (case-insensitive) & qty > 0
    df_shipped_exact = df_amz[(df_amz['status'].str.lower() == 'shipped') & (df_amz['qty'] > 0)].copy()
    
    # Merge with International sales to create the enriched 540,716 fact rows
    fact_sales = pd.merge(
        df_shipped_exact,
        df_intl_clean[['sku', 'customer_name', 'gross_amt', 'rate', 'pcs', 'months']],
        on='sku',
        how='left'
    )
    fact_sales['customer_name'] = fact_sales['customer_name'].fillna('Anonymous / Marketplace Retail')
    fact_sales['customer_type'] = np.where(fact_sales['customer_name'] != 'Anonymous / Marketplace Retail', 'Known Repeat / B2B', 'Retail Direct')
    
    print(f"   Generated fact_sales_orders: {len(fact_sales):,} rows | Total Revenue: Rs {fact_sales['amount'].sum():,.2f}")

    # Build Dimension Tables
    # dim_time
    dim_time = pd.DataFrame({'full_date': df_amz['order_date'].dropna().drop_duplicates().sort_values()})
    dim_time['date_key'] = dim_time['full_date'].dt.strftime('%Y%m%d').astype(int)
    dim_time['year'] = dim_time['full_date'].dt.year
    dim_time['quarter'] = dim_time['full_date'].dt.quarter
    dim_time['month'] = dim_time['full_date'].dt.month
    dim_time['month_name'] = dim_time['full_date'].dt.strftime('%B')
    dim_time['day'] = dim_time['full_date'].dt.day
    dim_time['day_name'] = dim_time['full_date'].dt.strftime('%A')
    dim_time['day_of_week'] = dim_time['full_date'].dt.dayofweek + 1
    dim_time['is_weekend'] = dim_time['day_of_week'].isin([6, 7])

    # dim_customer
    dim_customer = df_intl_clean.groupby('customer_name').agg(
        total_orders=('sku', 'count'),
        total_gross=('gross_amt', 'sum'),
        avg_rate=('rate', 'mean')
    ).reset_index()
    dim_customer['customer_key'] = range(1, len(dim_customer) + 1)

    # dim_geography
    dim_geography = df_amz.groupby(['ship_state', 'ship_city', 'ship_country']).agg(
        total_orders=('order_id', 'nunique'),
        total_revenue=('amount', 'sum')
    ).reset_index()
    dim_geography['geo_key'] = range(1, len(dim_geography) + 1)

    # dim_channel
    dim_channel = df_amz.groupby(['sales_channel', 'fulfilment', 'ship_service_level']).agg(
        order_count=('order_id', 'count')
    ).reset_index()
    dim_channel['channel_key'] = range(1, len(dim_channel) + 1)

    # 6. Save to SQLite and Fast Parquet
    print("\n[6/6] Writing to SQLite Database & Parquet Store...")
    
    # Store complete orders (all 128,975) for status/fulfillment drilldown
    df_amz.to_sql('raw_amazon_orders', conn, if_exists='replace', index=False)
    
    # Fact & Dimension tables
    fact_sales.to_sql('fact_sales_orders', conn, if_exists='replace', index=False)
    pricing_clean.to_sql('dim_product_pricing', conn, if_exists='replace', index=False)
    stock_clean.to_sql('sku_stock_clean', conn, if_exists='replace', index=False)
    dim_time.to_sql('dim_time', conn, if_exists='replace', index=False)
    dim_customer.to_sql('dim_customer', conn, if_exists='replace', index=False)
    dim_geography.to_sql('dim_geography', conn, if_exists='replace', index=False)
    dim_channel.to_sql('dim_channel', conn, if_exists='replace', index=False)

    # Create Indexes for fast SQL queries
    print("   Creating SQL Indexes for rapid execution...")
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_sku ON fact_sales_orders(sku);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_sales_orders(order_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_category ON fact_sales_orders(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_customer ON fact_sales_orders(customer_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_raw_status ON raw_amazon_orders(status_simplified);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_raw_date ON raw_amazon_orders(order_date);")
    conn.commit()
    conn.close()

    # Save lightweight parquet files for instant dashboard loading without overhead
    fact_sales_summary = fact_sales[[
        'order_id', 'order_date', 'status', 'sales_channel', 'style', 'sku',
        'category', 'size', 'qty', 'amount', 'ship_city', 'ship_state',
        'is_promotional', 'b2b', 'customer_name', 'customer_type'
    ]]
    fact_sales_summary.to_parquet('data/fact_sales_orders.parquet', index=False)
    df_amz[['order_id', 'order_date', 'status', 'status_simplified', 'fulfilment', 'sales_channel', 'category', 'qty', 'amount', 'ship_state']].to_parquet('data/raw_orders.parquet', index=False)
    pricing_clean.to_parquet('data/dim_product_pricing.parquet', index=False)
    stock_clean.to_parquet('data/sku_stock_clean.parquet', index=False)

    print("\n[SUCCESS] ETL Pipeline Completed Successfully!")
    print(f"   Database: {db_path} ({os.path.getsize(db_path)/(1024*1024):.2f} MB)")
    print("=" * 60)

if __name__ == '__main__':
    run_etl()
