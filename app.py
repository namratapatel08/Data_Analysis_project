"""
E-Commerce Sales Analytics & Business Intelligence Dashboard
Built with Streamlit & Plotly | Star Schema Data Warehouse
Analyzes 540,716 order lines, 72,826 orders, 1,330 SKUs across Indian Fashion Marketplaces
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Sales Analytics | Executive BI Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished C-suite appearance
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 4px 0;
    }
    .metric-sub {
        font-size: 0.8rem;
        font-weight: 500;
    }
    .sub-green { color: #10B981; }
    .sub-blue { color: #3B82F6; }
    .sub-orange { color: #F59E0B; }
    .sub-red { color: #EF4444; }
    .sub-purple { color: #8B5CF6; }
    
    .insight-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-left: 4px solid #3B82F6;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin: 15px 0;
        color: #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    # If parquet files exist, load them directly (sub-second performance)
    if os.path.exists('data/fact_sales_orders.parquet'):
        fact_df = pd.read_parquet('data/fact_sales_orders.parquet')
        fact_df['order_date'] = pd.to_datetime(fact_df['order_date'])
        raw_orders_df = pd.read_parquet('data/raw_orders.parquet')
        pricing_df = pd.read_parquet('data/dim_product_pricing.parquet')
        stock_df = pd.read_parquet('data/sku_stock_clean.parquet')
        return fact_df, raw_orders_df, pricing_df, stock_df
    
    # Fallback to database or run ETL
    if not os.path.exists('data/ecommerce.db'):
        import etl_pipeline
        etl_pipeline.run_etl()
    
    conn = sqlite3.connect('data/ecommerce.db')
    fact_df = pd.read_sql("SELECT * FROM fact_sales_orders", conn)
    fact_df['order_date'] = pd.to_datetime(fact_df['order_date'])
    raw_orders_df = pd.read_sql("SELECT * FROM raw_amazon_orders", conn)
    pricing_df = pd.read_sql("SELECT * FROM dim_product_pricing", conn)
    stock_df = pd.read_sql("SELECT * FROM sku_stock_clean", conn)
    conn.close()
    return fact_df, raw_orders_df, pricing_df, stock_df

try:
    fact_df, raw_orders_df, pricing_df, stock_df = load_data()
except Exception as e:
    st.error(f"Error loading datasets: {e}. Please ensure etl_pipeline.py has run.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. Sidebar Filters & Navigation
# -----------------------------------------------------------------------------
st.sidebar.image("image/datamodel.png", use_container_width=True)
st.sidebar.title("🛍️ E-Commerce Analytics")
st.sidebar.markdown("**Dataset:** 91-Day Multi-Channel Retail  \n**Volume:** 540k+ rows | ₹347.2M GMV")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Global Filters")

# Date Filter
min_date = fact_df['order_date'].min().date() if not fact_df['order_date'].isna().all() else None
max_date = fact_df['order_date'].max().date() if not fact_df['order_date'].isna().all() else None

if min_date and max_date:
    selected_date_range = st.sidebar.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    selected_date_range = None

# Category Filter
all_categories = sorted(fact_df['category'].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Product Category",
    options=all_categories,
    default=all_categories
)

# Channel / Customer Type Filter
customer_types = sorted(fact_df['customer_type'].dropna().unique().tolist())
selected_cust_types = st.sidebar.multiselect(
    "Customer Segment",
    options=customer_types,
    default=customer_types
)

# Promotion Filter
promo_filter = st.sidebar.radio("Promotion Filter", options=["All Orders", "Promotional Only", "Non-Promotional"], index=0)

# Filter dataframe
filtered_df = fact_df.copy()
if selected_date_range and len(selected_date_range) == 2:
    start_d, end_d = selected_date_range
    filtered_df = filtered_df[(filtered_df['order_date'].dt.date >= start_d) & (filtered_df['order_date'].dt.date <= end_d)]

if selected_categories:
    filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

if selected_cust_types:
    filtered_df = filtered_df[filtered_df['customer_type'].isin(selected_cust_types)]

if promo_filter == "Promotional Only":
    filtered_df = filtered_df[filtered_df['is_promotional'] == True]
elif promo_filter == "Non-Promotional":
    filtered_df = filtered_df[filtered_df['is_promotional'] == False]

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.info("""
**Candidate:** Final Year B.Tech Student  
**Target Roles:** Data Analyst / BI Engineer  
**Tech Stack:** SQL (MySQL/SQLite), Python (Streamlit, Plotly, Pandas), Star Schema ETL
""")

# -----------------------------------------------------------------------------
# 4. Main Navigation Tabs
# -----------------------------------------------------------------------------
st.title("📊 E-Commerce Sales & Business Intelligence Platform")
st.markdown("##### End-to-End Star Schema Data Warehouse & Multi-Channel Marketplace Analytics")

tabs = st.tabs([
    "📈 Executive Overview",
    "🛍️ Product & Categories",
    "🏷️ Multi-Channel Pricing",
    "👥 Customers & Geography",
    "📦 Inventory & Stockout Risk",
    "🎯 Promotions & ROI",
    "⚡ Interactive SQL Sandbox"
])

# =============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# =============================================================================
with tabs[0]:
    st.markdown("### 🎯 Executive Performance Metrics")
    
    # Calculate KPIs
    total_rev = filtered_df['amount'].sum()
    total_orders = filtered_df['order_id'].nunique()
    total_items = len(filtered_df)
    aov = total_rev / total_orders if total_orders > 0 else 0
    items_per_order = total_items / total_orders if total_orders > 0 else 0
    unique_skus = filtered_df['sku'].nunique()
    
    # 5 KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Gross Revenue</div>
            <div class="metric-value">₹{total_rev/1e6:.2f} M</div>
            <div class="metric-sub sub-green">● 100% Shipped GMV</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Orders</div>
            <div class="metric-value">{total_orders:,}</div>
            <div class="metric-sub sub-blue">● {total_items:,} Line Items</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Order Value</div>
            <div class="metric-value">₹{aov:.2f}</div>
            <div class="metric-sub sub-purple">● {items_per_order:.2f} Items / Basket</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Average Gross Margin</div>
            <div class="metric-value">75.4%</div>
            <div class="metric-sub sub-orange">● Strong Pricing Power</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Stockout Rate</div>
            <div class="metric-value">6.3%</div>
            <div class="metric-sub sub-red">● 49% SKUs Critical Low</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        💡 <b>Executive Insight:</b> Top 10 B2B/wholesale customers account for <b>51.65% of total revenue</b>, representing significant concentration risk. Expanding D2C customer acquisition and addressing the <b>6.3% stockout rate</b> in high-velocity Kurtas and Sets can drive an estimated <b>10–15% immediate revenue uplift</b>.
    </div>
    """, unsafe_allow_html=True)

    # Charts Row 1: Daily Revenue Trend & Fulfillment Status
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        daily_trend = filtered_df.groupby(filtered_df['order_date'].dt.date).agg(
            revenue=('amount', 'sum'),
            orders=('order_id', 'nunique')
        ).reset_index()
        daily_trend['ma7'] = daily_trend['revenue'].rolling(7).mean()

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=daily_trend['order_date'],
            y=daily_trend['revenue'],
            name="Daily Revenue",
            marker_color="#3B82F6",
            opacity=0.6
        ))
        fig_trend.add_trace(go.Scatter(
            x=daily_trend['order_date'],
            y=daily_trend['ma7'],
            name="7-Day Moving Avg",
            line=dict(color="#10B981", width=3)
        ))
        fig_trend.update_layout(
            title="<b>Daily Revenue Trajectory & 7-Day Moving Average</b>",
            xaxis_title="Date",
            yaxis_title="Revenue (₹)",
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20),
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        status_counts = raw_orders_df['status_simplified'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Orders']
        
        fig_status = px.pie(
            status_counts,
            names='Status',
            values='Orders',
            hole=0.5,
            title="<b>Order Fulfillment & Cancellation Ratio</b>",
            color_discrete_sequence=['#10B981', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6'],
            template="plotly_dark"
        )
        fig_status.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_status, use_container_width=True)

    # Charts Row 2: Day of Week & AOV Distribution
    col_dow, col_tier = st.columns(2)
    
    with col_dow:
        filtered_df['day_name'] = filtered_df['order_date'].dt.day_name()
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_df = filtered_df.groupby('day_name')['amount'].sum().reindex(dow_order).reset_index()
        
        fig_dow = px.bar(
            dow_df,
            x='day_name',
            y='amount',
            labels={'day_name': 'Day of Week', 'amount': 'Total Revenue (₹)'},
            title="<b>Revenue by Day of Week (Weekly Seasonality)</b>",
            color='amount',
            color_continuous_scale='Blues',
            template="plotly_dark"
        )
        fig_dow.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_dow, use_container_width=True)

    with col_tier:
        def get_bucket(amt):
            if amt < 500: return '₹0 - 500'
            elif amt < 1000: return '₹500 - 1,000'
            elif amt < 2000: return '₹1,000 - 2,000'
            elif amt < 5000: return '₹2,000 - 5,000'
            else: return '₹5,000+'
            
        bucket_order = ['₹0 - 500', '₹500 - 1,000', '₹1,000 - 2,000', '₹2,000 - 5,000', '₹5,000+']
        filtered_df['bucket'] = filtered_df['amount'].apply(get_bucket)
        b_df = filtered_df.groupby('bucket')['order_id'].nunique().reindex(bucket_order).reset_index()
        b_df.columns = ['Bucket', 'Orders']
        
        fig_bucket = px.bar(
            b_df,
            x='Bucket',
            y='Orders',
            labels={'Bucket': 'Order Size Tier', 'Orders': 'Order Count'},
            title="<b>Order Value Concentration (AOV Buckets)</b>",
            color='Orders',
            color_continuous_scale='Viridis',
            template="plotly_dark"
        )
        fig_bucket.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_bucket, use_container_width=True)


# =============================================================================
# TAB 2: PRODUCT & CATEGORIES
# =============================================================================
with tabs[1]:
    st.markdown("### 🛍️ Product Catalog & Category Intelligence")

    col_cat1, col_cat2 = st.columns([3, 2])
    
    with col_cat1:
        cat_agg = filtered_df.groupby('category').agg(
            revenue=('amount', 'sum'),
            orders=('order_id', 'nunique'),
            qty=('qty', 'sum')
        ).reset_index().sort_values('revenue', ascending=False)
        
        fig_cat = px.bar(
            cat_agg,
            x='category',
            y='revenue',
            text='revenue',
            labels={'category': 'Category', 'revenue': 'Revenue (₹)'},
            title="<b>Revenue by Product Category</b>",
            color='revenue',
            color_continuous_scale='Blues',
            template="plotly_dark"
        )
        fig_cat.update_traces(texttemplate='₹%{text:.2s}', textposition='outside')
        fig_cat.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_cat2:
        fig_cat_pie = px.pie(
            cat_agg,
            names='category',
            values='revenue',
            hole=0.45,
            title="<b>Category Revenue Share %</b>",
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_cat_pie.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_cat_pie, use_container_width=True)

    # Pareto 80/20 Analysis on SKUs
    st.markdown("#### 📐 Catalog Pareto 80/20 Distribution")
    sku_perf = filtered_df.groupby('sku')['amount'].sum().reset_index().sort_values('amount', ascending=False)
    sku_perf['cum_rev'] = sku_perf['amount'].cumsum()
    sku_perf['cum_pct'] = (sku_perf['cum_rev'] / sku_perf['amount'].sum()) * 100
    sku_perf['sku_pct'] = np.linspace(0, 100, len(sku_perf))

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Scatter(
        x=sku_perf['sku_pct'],
        y=sku_perf['cum_pct'],
        mode='lines',
        name='Cumulative Revenue %',
        line=dict(color='#10B981', width=3)
    ))
    fig_pareto.add_trace(go.Scatter(
        x=[0, 100], y=[80, 80],
        mode='lines',
        name='80% Revenue Benchmark',
        line=dict(color='#EF4444', dash='dash')
    ))
    fig_pareto.add_trace(go.Scatter(
        x=[20, 20], y=[0, 100],
        mode='lines',
        name='Top 20% SKUs Benchmark',
        line=dict(color='#F59E0B', dash='dash')
    ))
    fig_pareto.update_layout(
        title="<b>SKU Revenue Pareto Curve (Top ~30% SKUs generate ~80% of Sales)</b>",
        xaxis_title="% of Total SKUs in Catalog",
        yaxis_title="Cumulative % of Revenue",
        template="plotly_dark",
        height=380,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # Best-Seller Leaderboard
    st.markdown("#### 🏆 Top 15 Best-Selling Product Styles")
    top_styles = filtered_df.groupby(['style', 'category']).agg(
        total_revenue=('amount', 'sum'),
        total_orders=('order_id', 'nunique'),
        total_units=('qty', 'sum')
    ).reset_index().sort_values('total_revenue', ascending=False).head(15)
    
    top_styles['total_revenue'] = top_styles['total_revenue'].apply(lambda x: f"₹{x:,.2f}")
    top_styles.columns = ['Design Style', 'Category', 'Total Revenue', 'Orders Count', 'Units Sold']
    st.dataframe(top_styles, use_container_width=True)


# =============================================================================
# TAB 3: MULTI-CHANNEL PRICING BENCHMARK
# =============================================================================
with tabs[2]:
    st.markdown("### 🏷️ Multi-Platform Pricing Intelligence & Margin Analysis")
    st.markdown("Comparative pricing intelligence across 7 leading e-commerce platforms: **Amazon, Ajio, Flipkart, Myntra, Limeroad, Paytm, and Snapdeal**.")

    col_p1, col_p2 = st.columns(2)
    
    platforms = [
        ('Amazon MRP', 'amazon_mrp', '#F59E0B'),
        ('Ajio MRP', 'ajio_mrp', '#10B981'),
        ('Flipkart MRP', 'flipkart_mrp', '#3B82F6'),
        ('Myntra MRP', 'myntra_mrp', '#EC4899'),
        ('Limeroad MRP', 'limeroad_mrp', '#8B5CF6'),
        ('Paytm MRP', 'paytm_mrp', '#06B6D4'),
        ('Snapdeal MRP', 'snapdeal_mrp', '#EF4444')
    ]
    
    avg_platform_pricing = []
    for name, col, color in platforms:
        valid_prices = pricing_df[pricing_df[col] > 0][col]
        avg_platform_pricing.append({
            'Platform': name.replace(' MRP', ''),
            'Average Listed MRP': valid_prices.mean(),
            'Color': color
        })
    p_df = pd.DataFrame(avg_platform_pricing).sort_values('Average Listed MRP', ascending=False)

    with col_p1:
        fig_platforms = px.bar(
            p_df,
            x='Platform',
            y='Average Listed MRP',
            text='Average Listed MRP',
            color='Platform',
            title="<b>Average Listed MRP Across Marketplaces (₹)</b>",
            template="plotly_dark"
        )
        fig_platforms.update_traces(texttemplate='₹%{text:.0f}', textposition='outside')
        fig_platforms.update_layout(height=380, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_platforms, use_container_width=True)

    with col_p2:
        valid_pricing = pricing_df[(pricing_df['avg_mrp'] > 0) & (pricing_df['tp_cost'] > 0)].copy()
        
        fig_margin_scatter = px.scatter(
            valid_pricing,
            x='tp_cost',
            y='avg_mrp',
            color='category',
            hover_data=['sku', 'style_id', 'gross_margin_pct'],
            labels={'tp_cost': 'Transfer Price / Cost (₹)', 'avg_mrp': 'Average Listed MRP (₹)'},
            title="<b>Cost Price (TP) vs Listed MRP by Category</b>",
            template="plotly_dark"
        )
        fig_margin_scatter.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_margin_scatter, use_container_width=True)

    # Margins by Category & Price Tier
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        cat_margins = valid_pricing.groupby('category')['gross_margin_pct'].mean().reset_index().sort_values('gross_margin_pct', ascending=False)
        fig_cm = px.bar(
            cat_margins,
            x='category',
            y='gross_margin_pct',
            text='gross_margin_pct',
            title="<b>Average Gross Margin % by Category</b>",
            color='gross_margin_pct',
            color_continuous_scale='Teal',
            labels={'gross_margin_pct': 'Gross Margin %'},
            template="plotly_dark"
        )
        fig_cm.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_cm.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_cm, use_container_width=True)

    with col_m2:
        valid_pricing['price_tier'] = pd.cut(
            valid_pricing['avg_mrp'],
            bins=[0, 1000, 2000, 3500, 10000],
            labels=['Budget (<₹1K)', 'Mid-Range (₹1K-2K)', 'Premium (₹2K-3.5K)', 'Luxury (>₹3.5K)']
        )
        tier_counts = valid_pricing['price_tier'].value_counts().reset_index()
        tier_counts.columns = ['Price Tier', 'SKUs']
        
        fig_tier = px.pie(
            tier_counts,
            names='Price Tier',
            values='SKUs',
            hole=0.45,
            title="<b>Catalog Distribution by Price Tier</b>",
            template="plotly_dark",
            color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
        )
        fig_tier.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_tier, use_container_width=True)


# =============================================================================
# TAB 4: CUSTOMERS & GEOGRAPHY
# =============================================================================
with tabs[3]:
    st.markdown("### 👥 Customer Concentration & Regional Analytics")

    # Customer Concentration Warning & Table
    st.markdown("""
    <div class="insight-box" style="border-left-color: #EF4444;">
        ⚠️ <b>High Customer Concentration Risk:</b> The top 10 wholesale/international customers account for <b>51.65% of entire revenue</b>. Over-reliance on single-buyer accounts creates operational vulnerability if any key account churns.
    </div>
    """, unsafe_allow_html=True)

    col_cust1, col_cust2 = st.columns([3, 2])
    
    with col_cust1:
        # Top 10 Customers
        top_cust = filtered_df[filtered_df['customer_name'] != 'Anonymous / Marketplace Retail'].groupby('customer_name')['amount'].sum().reset_index()
        top_cust = top_cust.sort_values('amount', ascending=False).head(10)
        
        fig_cust = px.bar(
            top_cust,
            x='amount',
            y='customer_name',
            orientation='h',
            text='amount',
            labels={'amount': 'Revenue (₹)', 'customer_name': 'Customer Account'},
            title="<b>Top 10 Customers by Revenue (₹ Millions)</b>",
            color='amount',
            color_continuous_scale='Purples',
            template="plotly_dark"
        )
        fig_cust.update_traces(texttemplate='₹%{text:.2s}', textposition='outside')
        fig_cust.update_layout(yaxis=dict(autorange="reversed"), height=400, coloraxis_showscale=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_cust, use_container_width=True)

    with col_cust2:
        cust_type_agg = filtered_df.groupby('customer_type').agg(
            revenue=('amount', 'sum'),
            orders=('order_id', 'nunique')
        ).reset_index()
        
        fig_cust_type = px.pie(
            cust_type_agg,
            names='customer_type',
            values='revenue',
            hole=0.5,
            title="<b>Revenue by Customer Type</b>",
            template="plotly_dark",
            color_discrete_sequence=['#8B5CF6', '#3B82F6']
        )
        fig_cust_type.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_cust_type, use_container_width=True)

    # Geographic Performance
    st.markdown("#### 🗺️ Top 15 Contributing Indian States")
    state_sales = filtered_df[filtered_df['ship_state'] != ''].groupby('ship_state').agg(
        revenue=('amount', 'sum'),
        orders=('order_id', 'nunique')
    ).reset_index().sort_values('revenue', ascending=False).head(15)

    fig_state = px.bar(
        state_sales,
        x='ship_state',
        y='revenue',
        labels={'ship_state': 'State', 'revenue': 'Revenue (₹)'},
        title="<b>Geographic Revenue Distribution (Top 15 States)</b>",
        color='revenue',
        color_continuous_scale='Blues',
        template="plotly_dark"
    )
    fig_state.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20), coloraxis_showscale=False)
    st.plotly_chart(fig_state, use_container_width=True)


# =============================================================================
# TAB 5: INVENTORY & STOCKOUT RISK
# =============================================================================
with tabs[4]:
    st.markdown("### 📦 Inventory Health & Stockout Monitor")
    st.markdown("Real-time monitoring of 9,271 warehouse SKUs to minimize stockout penalties and prioritize restock schedules.")

    col_s1, col_s2, col_s3 = st.columns(3)
    
    total_skus_inv = len(stock_df)
    zero_stock_cnt = (stock_df['stock'] <= 0).sum()
    crit_stock_cnt = ((stock_df['stock'] > 0) & (stock_df['stock'] <= 10)).sum()
    healthy_stock_cnt = (stock_df['stock'] > 10).sum()
    stockout_rate = (zero_stock_cnt / total_skus_inv) * 100

    with col_s1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Stockout SKUs</div>
            <div class="metric-value">{zero_stock_cnt:,}</div>
            <div class="metric-sub sub-red">● {stockout_rate:.1f}% Out of Stock</div>
        </div>
        """, unsafe_allow_html=True)

    with col_s2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Critical Low Stock (1-10)</div>
            <div class="metric-value">{crit_stock_cnt:,}</div>
            <div class="metric-sub sub-orange">● Urgent Restock Required</div>
        </div>
        """, unsafe_allow_html=True)

    with col_s3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Healthy Stock (>10 units)</div>
            <div class="metric-value">{healthy_stock_cnt:,}</div>
            <div class="metric-sub sub-green">● Normal Velocity</div>
        </div>
        """, unsafe_allow_html=True)

    col_inv1, col_inv2 = st.columns(2)
    
    with col_inv1:
        stock_status_counts = stock_df['stock_status'].value_counts().reset_index()
        stock_status_counts.columns = ['Status', 'SKUs']
        
        fig_stock_pie = px.pie(
            stock_status_counts,
            names='Status',
            values='SKUs',
            hole=0.45,
            title="<b>Inventory Stock Level Classification</b>",
            color='Status',
            color_discrete_map={
                'Healthy (>50)': '#10B981',
                'Moderate (11-50)': '#3B82F6',
                'Critical Low (1-10)': '#F59E0B',
                'Out of Stock': '#EF4444'
            },
            template="plotly_dark"
        )
        fig_stock_pie.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_stock_pie, use_container_width=True)

    with col_inv2:
        cat_stockout = stock_df.groupby('category').agg(
            total_skus=('sku', 'count'),
            zero_stock=('stock', lambda s: (s <= 0).sum())
        ).reset_index()
        cat_stockout['stockout_pct'] = (cat_stockout['zero_stock'] / cat_stockout['total_skus']) * 100
        cat_stockout = cat_stockout.sort_values('stockout_pct', ascending=False)
        
        fig_so = px.bar(
            cat_stockout,
            x='category',
            y='stockout_pct',
            text='stockout_pct',
            labels={'category': 'Category', 'stockout_pct': 'Stockout Rate %'},
            title="<b>Stockout Rate % by Product Category</b>",
            color='stockout_pct',
            color_continuous_scale='Reds',
            template="plotly_dark"
        )
        fig_so.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_so.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_so, use_container_width=True)

    st.markdown("#### 🚨 Urgent Replenishment Alert: Out of Stock SKUs")
    zero_stock_table = stock_df[stock_df['stock'] <= 0][['sku', 'design_no', 'category', 'size', 'color']].head(15)
    st.dataframe(zero_stock_table, use_container_width=True)


# =============================================================================
# TAB 6: PROMOTIONS & CAMPAIGNS
# =============================================================================
with tabs[5]:
    st.markdown("### 🎯 Promotional Impact & ROI Analysis")

    promo_agg = filtered_df.groupby('is_promotional').agg(
        orders=('order_id', 'nunique'),
        revenue=('amount', 'sum'),
        avg_order=('amount', 'mean'),
        items_sold=('qty', 'sum')
    ).reset_index()
    promo_agg['Promo Status'] = promo_agg['is_promotional'].map({True: 'Promotional Order', False: 'Non-Promotional'})

    col_prm1, col_prm2 = st.columns(2)
    
    with col_prm1:
        fig_promo_rev = px.bar(
            promo_agg,
            x='Promo Status',
            y='revenue',
            text='revenue',
            labels={'revenue': 'Total Revenue (₹)'},
            title="<b>Revenue: Promotional vs Non-Promotional Orders</b>",
            color='Promo Status',
            color_discrete_sequence=['#3B82F6', '#F59E0B'],
            template="plotly_dark"
        )
        fig_promo_rev.update_traces(texttemplate='₹%{text:.2s}', textposition='outside')
        fig_promo_rev.update_layout(height=360, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_promo_rev, use_container_width=True)

    with col_prm2:
        fig_promo_aov = px.bar(
            promo_agg,
            x='Promo Status',
            y='avg_order',
            text='avg_order',
            labels={'avg_order': 'Average Order Value (₹)'},
            title="<b>AOV Comparison: Promo vs Full Price</b>",
            color='Promo Status',
            color_discrete_sequence=['#10B981', '#8B5CF6'],
            template="plotly_dark"
        )
        fig_promo_aov.update_traces(texttemplate='₹%{text:.1f}', textposition='outside')
        fig_promo_aov.update_layout(height=360, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_promo_aov, use_container_width=True)


# =============================================================================
# TAB 7: INTERACTIVE SQL SANDBOX
# =============================================================================
with tabs[6]:
    st.markdown("### ⚡ Interactive SQL Query Runner & Data Mart Explorer")
    st.markdown("Run live SQL queries directly against the normalized Star Schema database (`data/ecommerce.db`).")

    PRESET_QUERIES = {
        "1. Executive KPI Summary View": "SELECT * FROM view_executive_kpis;",
        "2. Category Performance & Revenue Share": "SELECT * FROM view_category_performance;",
        "3. Inventory Stockout Risk by Category": "SELECT * FROM view_inventory_health;",
        "4. Top 10 States by Order Revenue": "SELECT * FROM view_state_sales LIMIT 10;",
        "5. Platform Price Benchmark (First 10 SKUs)": "SELECT sku, catalog, category, tp_cost, amazon_mrp, myntra_mrp, ajio_mrp FROM dim_product_pricing LIMIT 10;",
        "6. Fulfillment Rate by Sales Channel": """
SELECT 
    sales_channel,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(CASE WHEN status_simplified = 'Shipped' THEN 1 ELSE 0 END) AS shipped_orders,
    ROUND(SUM(CASE WHEN status_simplified = 'Shipped' THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT order_id), 2) AS fulfillment_rate_pct,
    SUM(CASE WHEN status_simplified = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    ROUND(SUM(CASE WHEN status_simplified = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT order_id), 2) AS cancellation_rate_pct
FROM raw_amazon_orders
GROUP BY sales_channel;
        """,
        "7. Custom Query (Type your own below)": ""
    }

    selected_query_label = st.selectbox("Choose a Pre-Configured Project SQL Query", list(PRESET_QUERIES.keys()))
    default_sql = PRESET_QUERIES[selected_query_label]

    user_query = st.text_area("SQL Query Editor (SQLite / MySQL syntax):", value=default_sql, height=140)

    if st.button("▶️ Execute Query", type="primary"):
        if user_query.strip():
            try:
                conn = sqlite3.connect('data/ecommerce.db')
                query_res = pd.read_sql_query(user_query, conn)
                conn.close()
                st.success(f"Query returned {len(query_res):,} rows successfully.")
                st.dataframe(query_res, use_container_width=True)
                
                # Download button
                csv = query_res.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Export Results to CSV",
                    csv,
                    "query_results.csv",
                    "text/csv",
                    key='download-csv'
                )
            except Exception as e:
                st.error(f"SQL Execution Error: {e}")
        else:
            st.warning("Please enter a SQL query to execute.")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94A3B8; font-size: 0.85rem;">
    <b>E-Commerce Sales Analytics & BI Platform</b> | Star Schema Data Modeling & Interactive Analytics | Final Year B.Tech Project
</div>
""", unsafe_allow_html=True)
