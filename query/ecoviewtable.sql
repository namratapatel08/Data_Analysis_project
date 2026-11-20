-- ==============================================================================
-- E-Commerce Sales Analytics: Production BI Views & Analytical Data Mart
-- Database: ecommerce
-- Project: End-to-End SQL Data Modeling & Business Intelligence
-- ==============================================================================

USE ecommerce;

-- ------------------------------------------------------------------------------
-- 1. Executive Summary KPI View
-- High-level snapshot of business performance, AOV, order lines, and revenue
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS view_executive_kpis;
CREATE VIEW view_executive_kpis AS
SELECT 
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_line_items,
    ROUND(SUM(order_amount), 2) AS total_revenue,
    ROUND(AVG(order_amount), 2) AS avg_order_value,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT order_id), 2) AS avg_items_per_order,
    COUNT(DISTINCT customer_name) AS unique_customers,
    COUNT(DISTINCT sku) AS unique_skus,
    SUM(qty) AS total_quantity_sold
FROM fact_sales_orders;


-- ------------------------------------------------------------------------------
-- 2. Category Performance & Margin Mart
-- Aggregates revenue, order volume, and category revenue share
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS view_category_performance;
CREATE VIEW view_category_performance AS
SELECT 
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(qty) AS total_units_sold,
    ROUND(SUM(order_amount), 2) AS category_revenue,
    ROUND(AVG(order_amount), 2) AS avg_order_value,
    ROUND(SUM(order_amount) * 100.0 / (SELECT SUM(order_amount) FROM fact_sales_orders), 2) AS revenue_share_pct
FROM fact_sales_orders
GROUP BY category
ORDER BY category_revenue DESC;


-- ------------------------------------------------------------------------------
-- 3. Customer Concentration & Pareto Analysis View
-- Ranks customers by cumulative revenue contribution to highlight dependency risk
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS view_customer_pareto;
CREATE VIEW view_customer_pareto AS
WITH customer_revenue AS (
    SELECT 
        customer_name,
        customer_type,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(order_amount), 2) AS total_spent
    FROM fact_sales_orders
    WHERE customer_name != 'Anonymous / Marketplace Retail'
    GROUP BY customer_name, customer_type
),
ranked_customers AS (
    SELECT 
        customer_name,
        customer_type,
        total_orders,
        total_spent,
        ROUND(total_spent * 100.0 / SUM(total_spent) OVER (), 2) AS revenue_share_pct,
        SUM(total_spent) OVER (ORDER BY total_spent DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_spent,
        ROUND(SUM(total_spent) OVER (ORDER BY total_spent DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) * 100.0 / SUM(total_spent) OVER (), 2) AS cumulative_revenue_pct,
        ROW_NUMBER() OVER (ORDER BY total_spent DESC) AS customer_rank
    FROM customer_revenue
)
SELECT 
    customer_rank,
    customer_name,
    customer_type,
    total_orders,
    total_spent,
    revenue_share_pct,
    cumulative_revenue_pct,
    CASE 
        WHEN cumulative_revenue_pct <= 50 THEN 'Top Tier (50% Dependency)'
        WHEN cumulative_revenue_pct <= 80 THEN 'Pareto Core (80% Revenue)'
        ELSE 'Long Tail (20% Revenue)'
    END AS pareto_segment
FROM ranked_customers;


-- ------------------------------------------------------------------------------
-- 4. Multi-Channel Pricing Benchmark View
-- Compares MRP across 7 major Indian retail marketplaces against Transfer Price (TP)
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS view_platform_pricing;
CREATE VIEW view_platform_pricing AS
SELECT 
    sku,
    style_id,
    catalog,
    category,
    tp_cost,
    amazon_mrp,
    ajio_mrp,
    flipkart_mrp,
    myntra_mrp,
    limeroad_mrp,
    paytm_mrp,
    snapdeal_mrp,
    ROUND((amazon_mrp + ajio_mrp + flipkart_mrp + myntra_mrp) / 4.0, 2) AS avg_major_marketplaces_mrp,
    ROUND(((amazon_mrp - tp_cost) / NULLIF(amazon_mrp, 0)) * 100, 2) AS amazon_gross_margin_pct,
    ROUND(((myntra_mrp - tp_cost) / NULLIF(myntra_mrp, 0)) * 100, 2) AS myntra_gross_margin_pct,
    ROUND(((ajio_mrp - tp_cost) / NULLIF(ajio_mrp, 0)) * 100, 2) AS ajio_gross_margin_pct
FROM dim_product_pricing;


-- ------------------------------------------------------------------------------
-- 5. Inventory Stockout Risk & Replenishment Alert View
-- Identifies critical stockout SKUs and stock distribution health
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS view_inventory_health;
CREATE VIEW view_inventory_health AS
SELECT 
    category,
    COUNT(*) AS total_skus,
    SUM(CASE WHEN stock <= 0 THEN 1 ELSE 0 END) AS out_of_stock_skus,
    ROUND(SUM(CASE WHEN stock <= 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS stockout_rate_pct,
    SUM(CASE WHEN stock BETWEEN 1 AND 10 THEN 1 ELSE 0 END) AS critical_low_skus,
    SUM(CASE WHEN stock > 10 THEN 1 ELSE 0 END) AS healthy_stock_skus,
    ROUND(AVG(stock), 2) AS avg_stock_units,
    SUM(stock) AS total_inventory_units
FROM sku_stock_clean
GROUP BY category
ORDER BY stockout_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- 6. Geographic Distribution View
-- Regional sales volume and revenue by state and city
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS view_state_sales;
CREATE VIEW view_state_sales AS
SELECT 
    ship_state,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(order_amount), 2) AS state_revenue,
    ROUND(AVG(order_amount), 2) AS avg_order_value,
    ROUND(SUM(order_amount) * 100.0 / (SELECT SUM(order_amount) FROM fact_sales_orders), 2) AS revenue_share_pct
FROM fact_sales_orders
WHERE ship_state IS NOT NULL AND ship_state != ''
GROUP BY ship_state
ORDER BY state_revenue DESC;


-- ------------------------------------------------------------------------------
-- 7. Promotional Effectiveness View
-- Measures revenue uplift and order distribution between promo and non-promo orders
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS view_promotional_impact;
CREATE VIEW view_promotional_impact AS
SELECT 
    is_promotional,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(order_amount), 2) AS total_revenue,
    ROUND(AVG(order_amount), 2) AS avg_order_value,
    ROUND(SUM(order_amount) * 100.0 / (SELECT SUM(order_amount) FROM fact_sales_orders), 2) AS revenue_share_pct
FROM fact_sales_orders
GROUP BY is_promotional;
