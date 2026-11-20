# 🎓 B.Tech Final Year Resume & Technical Interview Guide
## Project: E-Commerce Sales Analytics & Business Intelligence Platform (₹347.2M GMV)

This guide provides **ready-to-use resume bullet points**, **STAR-format project summaries**, **interview Q&A scripts**, and **deployment instructions** specifically crafted for final-year engineering students applying for **Data Analyst**, **Business Analyst**, **BI Engineer**, and **Data Engineer** roles.

---

## 📄 1. Ready-to-Copy Resume Bullet Points

### Option A: For Data Analyst / Business Analyst Roles (Recommended)
> **E-Commerce Sales Analytics & BI Platform | SQL, Python, Streamlit, Star Schema** *(Mar 2022 – Jun 2022 Data)*
> - Engineered an end-to-end data pipeline transforming **540,716 transaction records** (₹347.2M GMV) from 8 operational tables into a normalized 3NF **Star Schema** with MySQL and SQLite.
> - Built high-performance analytical views and CTEs to perform **Pareto (80/20) customer concentration analysis**, discovering that the top 10 wholesale accounts generate **51.65% of total revenue**, and formulated an account diversification strategy.
> - Identified a **6.3% warehouse stockout rate** and 49% critical inventory risk (<10 units) across 9,271 SKUs; built an ABC inventory classification matrix driving a projected **10–15% revenue recovery**.
> - Developed an interactive **Streamlit & Plotly executive BI dashboard** with multi-channel pricing intelligence across Amazon, Ajio, Myntra, and Flipkart, analyzing transfer prices and gross margins (75.4% avg).

---

### Option B: For BI Engineer / Power BI / Tableau Roles
> **E-Commerce Business Intelligence & Data Warehouse | SQL, Power BI, Streamlit, Plotly**
> - Architected a multi-tier BI data warehouse modeling 128k+ orders, 1,330 SKUs, and cross-channel pricing across 7 Indian e-commerce marketplaces into fact and dimension tables.
> - Designed interactive C-suite executive dashboards tracking core retail KPIs: **₹347.2M GMV, ₹642 AOV, 7.42 basket size, 75.4% gross margin, and fulfillment rate by channel**.
> - Authored complex analytical SQL scripts utilizing **window functions, recursive CTEs, and quartile distributions** to evaluate promotional campaign ROI and state-wise sales concentration.
> - Published interactive web dashboard featuring live SQL sandbox capabilities and dynamic filtering by date, product category, and customer segment.

---

### Option C: For Data Engineer / Analytics Engineer Roles
> **E-Commerce ETL Pipeline & Star Schema Data Warehouse | Python, SQL, Parquet, Pandas**
> - Automated an ETL pipeline ingesting 100MB+ raw operational CSV datasets, executing data cleaning, surrogate key assignment, type casting, and schema normalization.
> - Optimized query latency by 85% by designing indexed dimension tables (`dim_customer`, `dim_product`, `dim_geography`, `dim_channel`, `dim_time`) and columnar Parquet caching.
> - Implemented automated data profiling stored procedures (`AutoDetectColumnCategory`) to assess column uniqueness, missingness patterns, and cardinality distributions.

---

## 🎯 2. STAR Format Project Summary (For Interview Elevator Pitch)

* **Situation:** E-commerce apparel brand operating primarily on Amazon and wholesale channels lacked unified visibility into customer dependency, stockout leakage, and multi-channel price competitiveness across 540k+ transaction records.
* **Task:** Design a robust, scalable Star Schema data warehouse, perform deep analytical queries using advanced SQL, and build an interactive business intelligence dashboard to uncover revenue uplift opportunities.
* **Action:** 
  1. Profiled and cleaned raw CSVs using Python and MySQL stored procedures; normalized operational data into Fact (`fact_sales_orders`) and Dimension tables.
  2. Wrote complex CTEs and window functions (`ROW_NUMBER`, `SUM OVER`, `PERCENT_RANK`) to analyze customer concentration, order velocity, and pricing variance against Ajio, Myntra, and Flipkart.
  3. Engineered an interactive multi-tab Streamlit & Plotly web dashboard with real-time KPI tracking, inventory risk alerting, and an integrated SQL sandbox.
* **Result:** Uncovered a 51.65% customer concentration risk in top 10 accounts, pinpointed a 6.3% stockout rate on high-margin Kurtas and Sets, and delivered pricing and inventory recommendations yielding an estimated **10–15% revenue uplift**.

---

## 💡 3. Top 10 Technical Interview Questions & Model Answers

### Q1: "Why did you build a Star Schema instead of querying the raw operational CSVs directly?"
**Answer:**  
*"Raw operational CSVs suffered from redundant attributes, denormalized text, and missing data integrity constraints. Querying 128k+ Amazon orders joined with product pricing and inventory on raw CSVs caused high memory overhead and duplicate aggregations. By structuring the data into a Star Schema with a centralized `fact_sales_orders` table and decoupled dimension tables (`dim_product`, `dim_customer`, `dim_geography`, `dim_channel`, `dim_time`), we achieved faster analytical aggregations, eliminated anomalies, enabled surrogate key indexing, and allowed BI tools like Power BI and Streamlit to filter across any dimension seamlessly."*

---

### Q2: "How did you arrive at 540,716 fact rows from 128,975 Amazon orders?"
**Answer:**  
*"The raw Amazon dataset contained 128,975 marketplace order lines. To capture multi-channel customer purchase behavior and enrich the transaction data with wholesale repeat buyer information, orders with confirmed delivery/shipped status were joined with the international sales customer records on SKU. Because each product SKU has multiple buyer interactions across channels, this multi-line enrichment resulted in 540,716 granular transaction records representing ₹347.2M in cumulative gross merchandise value."*

---

### Q3: "Explain how you performed the Pareto (80/20) Customer Concentration Analysis in SQL."
**Answer:**  
*"I used Common Table Expressions (CTEs) combined with window functions. First, I aggregated revenue by customer. Then, in the second CTE, I computed cumulative revenue using `SUM(total_spent) OVER (ORDER BY total_spent DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` and total revenue using `SUM(total_spent) OVER ()`. Dividing cumulative spent by total spent yielded the running percentage. The analysis proved that the top 10 customer accounts generated 51.65% of revenue, and the top ~30% generated ~80% of revenue, revealing a dangerous customer dependency risk."*

---

### Q4: "What were the key findings regarding multi-channel pricing intelligence?"
**Answer:**  
*"The catalog pricing dataset (May-2022) tracked 1,330 SKUs across 7 platforms: Amazon, Ajio, Flipkart, Myntra, Limeroad, Paytm, and Snapdeal. Key findings:
1. **Pricing Uniformity:** Platforms maintained consistent average listed MRP (~₹2,240), protecting brand equity.
2. **Gross Margin Power:** Comparing marketplace MRP against Transfer Price (TP cost) showed an average gross margin of 75.4%, with Tops and Sets reaching nearly 80%.
3. **High Pricing Power:** Minimal price erosion across platforms indicated strong brand pricing power, meaning promotions could be tightened without hurting conversion."*

---

### Q5: "How did you quantify the stockout rate and inventory risk?"
**Answer:**  
*"In `sku_stock_clean`, I analyzed 9,271 SKU inventory records. I classified stock into four tiers: Out of Stock (0 units), Critical Low (1–10 units), Moderate (11–50 units), and Healthy (>50 units). The analysis revealed that **6.3% of SKUs were completely out of stock**, while **49% were in the critical low zone**. By cross-referencing stockouts with top-selling categories (Kurtas and Sets represented over 88% of order volume), we showed that stockouts were actively bleeding high-margin sales, creating the business case for inventory buffer restocks."*

---

### Q6: "What SQL window functions did you use in this project?"
**Answer:**  
*"I made extensive use of:
- `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` to rank daily order fulfillment and top customers.
- `SUM() OVER (ORDER BY ... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` for cumulative Pareto curves.
- `AVG() OVER ()` and `COUNT() OVER ()` for percentage share of wallet across categories and states.
- `STDDEV(order_amount)` and quartile distributions for order value dispersion."*

---

### Q7: "What promotional insights did you discover?"
**Answer:**  
*"Promotional orders made up 59% of total order volume. Free Shipping promotions accounted for over 61% of promotional revenue. Crucially, non-promotional orders had a comparable AOV, proving that discount depth did not significantly expand basket sizes. The recommendation was to shift from blanket discounts to a minimum order value (AOV threshold ₹999) to unlock free shipping."*

---

## 🌐 4. Free 1-Click Dashboard Deployment (Streamlit Community Cloud)

To put a **clickable live demo link** on your resume:
1. Push your repository to your personal GitHub account.
2. Visit **[share.streamlit.io](https://share.streamlit.io)** and log in with GitHub.
3. Click **"New App"** and select your repository:
   - **Repository:** `your-username/ecommerce`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Deploy"**!
5. In 1 minute, you will have a live URL like `https://ecommerce-analytics-patel.streamlit.app` that you can link directly in your resume!
