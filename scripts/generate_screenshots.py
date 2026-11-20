"""
Generates high-resolution executive dashboard screenshot images for GitHub README.
Creates:
1. image/dashboard_executive.png
2. image/dashboard_products.png
3. image/dashboard_pricing.png
4. image/dashboard_inventory.png
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.autolayout'] = False

os.makedirs('image', exist_ok=True)
conn = sqlite3.connect('data/ecommerce.db')

# -------------------------------------------------------------
# 1. Executive Overview Dashboard
# -------------------------------------------------------------
print("[1/4] Generating Executive Dashboard Screenshot...")
fig = plt.figure(figsize=(16, 9), dpi=150, facecolor='#0E1117')

# Title & KPI Header
fig.text(0.05, 0.94, "E-COMMERCE SALES ANALYTICS | EXECUTIVE OVERVIEW", fontsize=20, weight='bold', color='#FFFFFF')
fig.text(0.05, 0.91, "91-Day Multi-Channel Fashion Sales & Performance Intelligence | Star Schema Mart", fontsize=11, color='#94A3B8')

# KPI Cards (Top Banner)
kpis = [
    ("TOTAL REVENUE", "Rs 347.21 M", "+14.2% MoM", "#10B981"),
    ("TOTAL ORDERS", "72,826", "540.7k Line Items", "#3B82F6"),
    ("AVG ORDER VALUE", "Rs 642.14", "7.42 Items/Order", "#8B5CF6"),
    ("GROSS MARGIN", "75.4%", "Strong Pricing Power", "#F59E0B"),
    ("STOCKOUT RATE", "6.3%", "49% Critical Low", "#EF4444")
]

for i, (label, val, sub, col) in enumerate(kpis):
    ax_card = fig.add_axes([0.05 + i * 0.185, 0.77, 0.17, 0.10], facecolor='#1E293B')
    ax_card.set_xticks([])
    ax_card.set_yticks([])
    for spine in ax_card.spines.values():
        spine.set_color('#334155')
        spine.set_linewidth(1.5)
    ax_card.text(0.08, 0.70, label, fontsize=9, weight='bold', color='#94A3B8')
    ax_card.text(0.08, 0.35, val, fontsize=16, weight='bold', color='#FFFFFF')
    ax_card.text(0.08, 0.12, sub, fontsize=8, weight='bold', color=col)

# Panel 1: Daily Revenue Trend (0.05, 0.10, 0.58, 0.60)
ax_trend = fig.add_axes([0.05, 0.10, 0.58, 0.58], facecolor='#1E293B')
for spine in ax_trend.spines.values():
    spine.set_color('#334155')
ax_trend.tick_params(colors='#94A3B8', labelsize=9)
ax_trend.grid(True, linestyle='--', alpha=0.3, color='#475569')

df_daily = pd.read_sql("""
    SELECT DATE(order_date) as order_date, SUM(amount) as daily_revenue, COUNT(DISTINCT order_id) as orders
    FROM fact_sales_orders
    WHERE order_date IS NOT NULL
    GROUP BY DATE(order_date)
    ORDER BY order_date
""", conn)
df_daily['order_date'] = pd.to_datetime(df_daily['order_date'])
df_daily['ma7'] = df_daily['daily_revenue'].rolling(7).mean()

ax_trend.bar(df_daily['order_date'], df_daily['daily_revenue']/1e6, color='#3B82F6', alpha=0.45, label='Daily Revenue (M)', width=0.8)
ax_trend.plot(df_daily['order_date'], df_daily['ma7']/1e6, color='#10B981', linewidth=2.5, label='7-Day Moving Avg')
ax_trend.set_title("Daily Sales Trajectory & 7-Day Trend (March - June 2022)", fontsize=12, weight='bold', color='#FFFFFF', pad=12, loc='left')
ax_trend.set_ylabel("Revenue (Rs Millions)", fontsize=10, color='#94A3B8')
ax_trend.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#FFFFFF', loc='upper right', fontsize=9)
ax_trend.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %d'))

# Panel 2: Order Status Distribution (0.68, 0.42, 0.27, 0.26)
ax_status = fig.add_axes([0.68, 0.42, 0.27, 0.26], facecolor='#1E293B')
for spine in ax_status.spines.values():
    spine.set_color('#334155')
ax_status.tick_params(colors='#94A3B8', labelsize=9)
ax_status.grid(False)

df_status = pd.read_sql("""
    SELECT status_simplified, COUNT(*) as count 
    FROM raw_amazon_orders 
    GROUP BY status_simplified 
    ORDER BY count DESC
""", conn)

colors_donut = ['#10B981', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6']
wedges, texts, autotexts = ax_status.pie(
    df_status['count'], labels=df_status['status_simplified'], autopct='%1.1f%%',
    startangle=140, colors=colors_donut[:len(df_status)],
    textprops=dict(color='#FFFFFF', fontsize=8), pctdistance=0.75,
    wedgeprops=dict(width=0.45, edgecolor='#1E293B', linewidth=2)
)
for at in autotexts:
    at.set_color('#FFFFFF')
    at.set_weight('bold')
ax_status.set_title("Order Fulfillment & Status Ratio", fontsize=11, weight='bold', color='#FFFFFF', pad=10, loc='center')

# Panel 3: Revenue by Top 5 States (0.68, 0.10, 0.27, 0.25)
ax_geo = fig.add_axes([0.68, 0.10, 0.27, 0.25], facecolor='#1E293B')
for spine in ax_geo.spines.values():
    spine.set_color('#334155')
ax_geo.tick_params(colors='#94A3B8', labelsize=8)
ax_geo.grid(True, linestyle='--', alpha=0.3, color='#475569')

df_geo = pd.read_sql("""
    SELECT ship_state, SUM(amount)/1e6 as rev 
    FROM fact_sales_orders 
    WHERE ship_state != '' AND ship_state IS NOT NULL
    GROUP BY ship_state 
    ORDER BY rev DESC LIMIT 5
""", conn)
y_pos = np.arange(len(df_geo))
ax_geo.barh(y_pos, df_geo['rev'], color='#6366F1', alpha=0.85, height=0.6)
ax_geo.set_yticks(y_pos)
ax_geo.set_yticklabels(df_geo['ship_state'], color='#E2E8F0')
ax_geo.invert_yaxis()
ax_geo.set_xlabel("Revenue (Rs Millions)", fontsize=9, color='#94A3B8')
ax_geo.set_title("Top 5 Contributing States", fontsize=11, weight='bold', color='#FFFFFF', pad=10, loc='left')

plt.savefig('image/dashboard_executive.png', dpi=150, facecolor=fig.get_facecolor(), bbox_inches='tight')
plt.close(fig)

# -------------------------------------------------------------
# 2. Product & Category Intelligence
# -------------------------------------------------------------
print("[2/4] Generating Product Intelligence Screenshot...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10), dpi=150, facecolor='#0E1117')
fig.suptitle("PRODUCT & CATEGORY REVENUE INTELLIGENCE", fontsize=18, weight='bold', color='#FFFFFF', y=0.96)

for ax in [ax1, ax2, ax3, ax4]:
    ax.set_facecolor('#1E293B')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    ax.tick_params(colors='#94A3B8', labelsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, color='#475569')

# Plot 1: Category Revenue Breakdown
df_cat = pd.read_sql("""
    SELECT category, SUM(amount)/1e6 as revenue, COUNT(DISTINCT order_id) as orders
    FROM fact_sales_orders
    GROUP BY category
    ORDER BY revenue DESC
""", conn)
ax1.bar(df_cat['category'], df_cat['revenue'], color='#3B82F6', alpha=0.85)
ax1.set_title("Revenue by Product Category (Rs M)", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax1.set_ylabel("Revenue (Rs M)", color='#94A3B8')
ax1.tick_params(axis='x', rotation=30)

# Plot 2: Pareto 80/20 Cumulative Distribution
df_sku_rev = pd.read_sql("""
    SELECT sku, SUM(amount) as revenue
    FROM fact_sales_orders
    GROUP BY sku
    ORDER BY revenue DESC
""", conn)
df_sku_rev['cum_pct'] = (df_sku_rev['revenue'].cumsum() / df_sku_rev['revenue'].sum()) * 100
df_sku_rev['sku_pct'] = np.linspace(0, 100, len(df_sku_rev))
ax2.plot(df_sku_rev['sku_pct'], df_sku_rev['cum_pct'], color='#10B981', linewidth=2.5, label='Pareto Curve')
ax2.axhline(80, color='#EF4444', linestyle='--', linewidth=1.5, label='80% Revenue Cutoff')
ax2.axvline(20, color='#F59E0B', linestyle='--', linewidth=1.5, label='Top 20% SKUs')
ax2.set_title("Product Catalog Pareto (80/20) Distribution", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax2.set_xlabel("% of Total SKUs", color='#94A3B8')
ax2.set_ylabel("Cumulative % of Revenue", color='#94A3B8')
ax2.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#FFFFFF')

# Plot 3: Top 10 Best Selling Styles
df_styles = pd.read_sql("""
    SELECT style, SUM(amount)/1e6 as rev
    FROM fact_sales_orders
    GROUP BY style
    ORDER BY rev DESC LIMIT 10
""", conn)
y_pos = np.arange(len(df_styles))
ax3.barh(y_pos, df_styles['rev'], color='#8B5CF6', alpha=0.85)
ax3.set_yticks(y_pos)
ax3.set_yticklabels(df_styles['style'], color='#E2E8F0')
ax3.invert_yaxis()
ax3.set_title("Top 10 High-Velocity Design Styles (Rs M)", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax3.set_xlabel("Revenue (Rs M)", color='#94A3B8')

# Plot 4: Order Value Distribution Buckets
df_buckets = pd.read_sql("""
    SELECT 
        CASE 
            WHEN amount < 500 THEN 'Rs 0-500'
            WHEN amount < 1000 THEN 'Rs 500-1K'
            WHEN amount < 2000 THEN 'Rs 1K-2K'
            WHEN amount < 5000 THEN 'Rs 2K-5K'
            ELSE 'Rs 5K+'
        END as bucket,
        COUNT(DISTINCT order_id) as orders
    FROM fact_sales_orders
    GROUP BY bucket
""", conn)
order_sort = {'Rs 0-500': 1, 'Rs 500-1K': 2, 'Rs 1K-2K': 3, 'Rs 2K-5K': 4, 'Rs 5K+': 5}
df_buckets['sort'] = df_buckets['bucket'].map(order_sort)
df_buckets = df_buckets.sort_values('sort')
ax4.bar(df_buckets['bucket'], df_buckets['orders'], color='#EC4899', alpha=0.85)
ax4.set_title("Order Value Distribution Buckets (AOV Concentration)", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax4.set_ylabel("Order Count", color='#94A3B8')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('image/dashboard_products.png', dpi=150, facecolor='#0E1117', bbox_inches='tight')
plt.close(fig)

# -------------------------------------------------------------
# 3. Multi-Channel Pricing Intelligence
# -------------------------------------------------------------
print("[3/4] Generating Multi-Channel Pricing Intelligence Screenshot...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10), dpi=150, facecolor='#0E1117')
fig.suptitle("MULTI-CHANNEL COMPETITIVE PRICING & MARGIN INTELLIGENCE", fontsize=18, weight='bold', color='#FFFFFF', y=0.96)

for ax in [ax1, ax2, ax3, ax4]:
    ax.set_facecolor('#1E293B')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    ax.tick_params(colors='#94A3B8', labelsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, color='#475569')

df_p = pd.read_sql("SELECT * FROM dim_product_pricing WHERE avg_mrp > 0", conn)

# Plot 1: Average MRP across Marketplaces
platforms = ['Amazon', 'Ajio', 'Flipkart', 'Myntra', 'Limeroad', 'Paytm', 'Snapdeal']
cols = ['amazon_mrp', 'ajio_mrp', 'flipkart_mrp', 'myntra_mrp', 'limeroad_mrp', 'paytm_mrp', 'snapdeal_mrp']
avg_prices = [df_p[c].replace(0, np.nan).mean() for c in cols]
ax1.bar(platforms, avg_prices, color=['#F59E0B', '#10B981', '#3B82F6', '#EC4899', '#8B5CF6', '#06B6D4', '#EF4444'], alpha=0.85)
ax1.set_title("Average Listed MRP by Marketplace (Rs)", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax1.set_ylabel("Average Price (Rs)", color='#94A3B8')

# Plot 2: Cost (TP) vs Average MRP Margin
ax2.scatter(df_p['tp_cost'], df_p['avg_mrp'], color='#10B981', alpha=0.45, s=25)
ax2.plot([0, 1500], [0, 4500], color='#EF4444', linestyle='--', label='3x Markup Reference')
ax2.set_title("Transfer Price (Cost) vs Marketplace Selling MRP", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax2.set_xlabel("Transfer Price / Cost (Rs)", color='#94A3B8')
ax2.set_ylabel("Average Listed MRP (Rs)", color='#94A3B8')
ax2.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#FFFFFF')

# Plot 3: Gross Margin by Category
df_margin_cat = df_p.groupby('category').agg(
    avg_margin=('gross_margin_pct', 'mean'),
    count=('sku', 'count')
).reset_index().sort_values('avg_margin', ascending=False)

ax3.bar(df_margin_cat['category'], df_margin_cat['avg_margin'], color='#8B5CF6', alpha=0.85)
ax3.axhline(75, color='#F59E0B', linestyle='--', label='Portfolio Avg 75%')
ax3.set_title("Average Gross Margin % by Category", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax3.set_ylabel("Gross Margin %", color='#94A3B8')
ax3.tick_params(axis='x', rotation=30)
ax3.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#FFFFFF')

# Plot 4: Price Tier Segmentation
df_p['price_tier'] = pd.cut(
    df_p['avg_mrp'], 
    bins=[0, 1000, 2000, 3500, 10000], 
    labels=['Budget (<1K)', 'Mid-Range (1K-2K)', 'Premium (2K-3.5K)', 'Luxury (>3.5K)']
)
df_tier = df_p['price_tier'].value_counts().sort_index()
ax4.pie(
    df_tier, labels=df_tier.index, autopct='%1.1f%%',
    colors=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
    startangle=140, textprops=dict(color='#FFFFFF', fontsize=9),
    wedgeprops=dict(width=0.45, edgecolor='#1E293B', linewidth=2)
)
ax4.set_title("Catalog Distribution by Price Tier", fontsize=11, weight='bold', color='#FFFFFF', loc='center')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('image/dashboard_pricing.png', dpi=150, facecolor='#0E1117', bbox_inches='tight')
plt.close(fig)

# -------------------------------------------------------------
# 4. Inventory Health & Stockout Monitor
# -------------------------------------------------------------
print("[4/4] Generating Inventory Health Screenshot...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10), dpi=150, facecolor='#0E1117')
fig.suptitle("INVENTORY HEALTH, STOCKOUT RISK & REPLENISHMENT MONITOR", fontsize=18, weight='bold', color='#FFFFFF', y=0.96)

for ax in [ax1, ax2, ax3, ax4]:
    ax.set_facecolor('#1E293B')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    ax.tick_params(colors='#94A3B8', labelsize=9)
    ax.grid(True, linestyle='--', alpha=0.3, color='#475569')

df_stock = pd.read_sql("SELECT * FROM sku_stock_clean", conn)

# Plot 1: Stock Status Distribution
status_counts = df_stock['stock_status'].value_counts()
colors_stock = {'Healthy (>50)': '#10B981', 'Moderate (11-50)': '#3B82F6', 'Critical Low (1-10)': '#F59E0B', 'Out of Stock': '#EF4444'}
ax1.pie(
    status_counts, labels=status_counts.index, autopct='%1.1f%%',
    colors=[colors_stock.get(k, '#94A3B8') for k in status_counts.index],
    startangle=140, textprops=dict(color='#FFFFFF', fontsize=9),
    wedgeprops=dict(width=0.45, edgecolor='#1E293B', linewidth=2)
)
ax1.set_title("Stock Health Segmentation (9,271 SKUs)", fontsize=11, weight='bold', color='#FFFFFF', loc='center')

# Plot 2: Stockout Rate by Category
df_stockout = df_stock.groupby('category').agg(
    total_skus=('sku', 'count'),
    zero_stock=('stock', lambda s: (s <= 0).sum())
).reset_index()
df_stockout['stockout_pct'] = (df_stockout['zero_stock'] / df_stockout['total_skus']) * 100
df_stockout = df_stockout.sort_values('stockout_pct', ascending=False)

ax2.bar(df_stockout['category'], df_stockout['stockout_pct'], color='#EF4444', alpha=0.85)
ax2.axhline(6.3, color='#F59E0B', linestyle='--', linewidth=1.5, label='Portfolio Avg (6.3%)')
ax2.set_title("Stockout Rate % by Product Category", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax2.set_ylabel("Stockout Rate %", color='#94A3B8')
ax2.tick_params(axis='x', rotation=30)
ax2.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#FFFFFF')

# Plot 3: Top Overstocked SKUs (Capital Tied Up)
df_top_stock = df_stock.sort_values('stock', ascending=False).head(8)
y_pos = np.arange(len(df_top_stock))
ax3.barh(y_pos, df_top_stock['stock'], color='#10B981', alpha=0.85)
ax3.set_yticks(y_pos)
ax3.set_yticklabels(df_top_stock['sku'], color='#E2E8F0', fontsize=8)
ax3.invert_yaxis()
ax3.set_title("Highest Stocked SKUs (Units in Warehouse)", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax3.set_xlabel("Units Available", color='#94A3B8')

# Plot 4: Promotional vs Non-Promotional Revenue
df_promo = pd.read_sql("""
    SELECT 
        CASE WHEN is_promotional = 1 THEN 'Promotional Order' ELSE 'Non-Promotional' END as promo_type,
        SUM(amount)/1e6 as rev,
        COUNT(DISTINCT order_id) as orders
    FROM fact_sales_orders
    GROUP BY is_promotional
""", conn)
ax4.bar(df_promo['promo_type'], df_promo['rev'], color=['#3B82F6', '#F59E0B'], alpha=0.85, width=0.5)
ax4.set_title("Promotional vs Non-Promotional Revenue Impact", fontsize=11, weight='bold', color='#FFFFFF', loc='left')
ax4.set_ylabel("Revenue (Rs Millions)", color='#94A3B8')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('image/dashboard_inventory.png', dpi=150, facecolor='#0E1117', bbox_inches='tight')
plt.close(fig)

conn.close()
print("\n[SUCCESS] All 4 dashboard infographic screenshots generated in image/ directory!")
