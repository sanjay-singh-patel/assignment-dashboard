import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Kessebohmer Sales Dashboard", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .metric-card { background: #1e1e2e; border-radius: 10px; padding: 16px; text-align: center; }
    .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Load ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_excel("data/Test Data 22 Intern (1).xlsx")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Sales value'] = pd.to_numeric(df['Sales value'], errors='coerce').fillna(0)
    df['Product Category 1'] = df['Product Category 1'].fillna("Uncategorised")
    df['Customer Category'] = df['Customer Category'].fillna("Unknown")
    return df

df = load()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔍 Filters")
    zone_filter = st.multiselect("Zone", sorted(df['Zone'].dropna().unique()), default=sorted(df['Zone'].dropna().unique()))
    quarter_filter = st.multiselect("Quarter", sorted(df['Quarter'].dropna().unique()), default=sorted(df['Quarter'].dropna().unique()))
    cat_filter = st.multiselect("Customer Category", sorted(df['Customer Category'].dropna().unique()), default=sorted(df['Customer Category'].dropna().unique()))
    rep_filter = st.multiselect("External Sales Rep", sorted(df['External Sales Representative'].dropna().unique()), default=sorted(df['External Sales Representative'].dropna().unique()))

fdf = df[
    df['Zone'].isin(zone_filter) &
    df['Quarter'].isin(quarter_filter) &
    df['Customer Category'].isin(cat_filter) &
    df['External Sales Representative'].isin(rep_filter)
]

pos = fdf[fdf['Sales value'] > 0]

# ── KPIs ──────────────────────────────────────────────────────────────────────
TARGET = 650_000_000
total_sales = pos['Sales value'].sum()
credit_notes = fdf[fdf['Sales value'] < 0]['Sales value'].sum()
net_sales = fdf['Sales value'].sum()
num_customers = fdf['Customer Name'].nunique()
num_invoices = fdf['Invoice No.'].nunique()
achievement = (total_sales / TARGET) * 100

st.title("📊 Kessebohmer Sales Dashboard — 2022")
st.caption(f"Showing **{len(fdf):,}** transactions · **{num_customers}** customers · **{num_invoices}** invoices")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Gross Sales", f"₹{total_sales/1e6:.1f}M")
k2.metric("Net Sales", f"₹{net_sales/1e6:.1f}M")
k3.metric("Credit Notes", f"₹{credit_notes/1e6:.1f}M")
k4.metric("Target", f"₹{TARGET/1e6:.0f}M")
k5.metric("Achievement", f"{achievement:.1f}%", delta=f"{achievement-100:.1f}%")

st.divider()

# ── Row 1: Monthly Trend + Quarterly Split ────────────────────────────────────
c1, c2 = st.columns([3, 1])

with c1:
    monthly = fdf.groupby(fdf['Date'].dt.to_period('M'))['Sales value'].sum().reset_index()
    monthly['Month'] = monthly['Date'].astype(str)
    fig = px.area(monthly, x='Month', y='Sales value',
                  title="📈 Monthly Sales Trend",
                  color_discrete_sequence=['#636EFA'])
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10), xaxis_title="", yaxis_title="Sales (₹)")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    q_sales = fdf.groupby('Quarter')['Sales value'].sum().reset_index()
    fig = px.pie(q_sales, names='Quarter', values='Sales value',
                 title="🗓 Quarterly Split", hole=0.45,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Zone Sales + Customer Category ─────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    zone_sales = fdf.groupby('Zone')['Sales value'].sum().reset_index().sort_values('Sales value', ascending=True)
    fig = px.bar(zone_sales, x='Sales value', y='Zone', orientation='h',
                 title="🗺 Sales by Zone", color='Zone',
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10), showlegend=False, xaxis_title="Sales (₹)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    cust_cat = fdf.groupby('Customer Category')['Sales value'].sum().reset_index()
    fig = px.pie(cust_cat, names='Customer Category', values='Sales value',
                 title="🏷 Revenue by Customer Category", hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Product Category + Product Main ────────────────────────────────────
c5, c6 = st.columns(2)

with c5:
    prod1 = fdf.groupby('Product Category 1')['Sales value'].sum().reset_index().sort_values('Sales value', ascending=True)
    fig = px.bar(prod1, x='Sales value', y='Product Category 1', orientation='h',
                 title="📦 Sales by Product Category",
                 color='Sales value', color_continuous_scale='Blues')
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10), yaxis_title="", xaxis_title="Sales (₹)", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c6:
    prod_main = fdf[fdf['Product Main'] != '-'].groupby('Product Main')['Sales value'].sum().reset_index()
    prod_main = prod_main.sort_values('Sales value', ascending=False).head(15)
    fig = px.bar(prod_main, x='Sales value', y='Product Main', orientation='h',
                 title="🔩 Top 15 Product Lines",
                 color='Sales value', color_continuous_scale='Teal')
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10), yaxis_title="", xaxis_title="Sales (₹)", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 4: Zone × Product Heatmap ─────────────────────────────────────────────
st.subheader("🔥 Zone × Product Category Heatmap")
pivot = pd.pivot_table(fdf, values='Sales value', index='Product Category 1',
                       columns='Zone', aggfunc='sum', fill_value=0)
fig = px.imshow(pivot, text_auto='.2s', aspect='auto',
                color_continuous_scale='RdYlGn',
                title="Sales Value (₹) — Product vs Zone")
fig.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig, use_container_width=True)

# ── Row 5: Top Sales Reps + Rep Efficiency ────────────────────────────────────
c7, c8 = st.columns(2)

with c7:
    rep_sales = fdf.groupby('External Sales Representative')['Sales value'].sum().reset_index()
    top10 = rep_sales.sort_values('Sales value', ascending=True).tail(10)
    fig = px.bar(top10, x='Sales value', y='External Sales Representative', orientation='h',
                 title="🏆 Top 10 Sales Representatives",
                 color='Sales value', color_continuous_scale='Viridis')
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10), yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c8:
    rep_eff = fdf.groupby('External Sales Representative').agg(
        Sales=('Sales value', 'sum'),
        Invoices=('Invoice No.', 'nunique')
    ).reset_index()
    rep_eff['Avg per Invoice'] = rep_eff['Sales'] / rep_eff['Invoices'].replace(0, 1)
    fig = px.scatter(rep_eff, x='Invoices', y='Sales', size='Avg per Invoice',
                     hover_name='External Sales Representative',
                     title="🎯 Rep Efficiency (Sales vs Invoice Volume)",
                     color='Sales', color_continuous_scale='Plasma')
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 6: Pareto (Customer Revenue Concentration) ───────────────────────────
st.subheader("📊 Customer Revenue Concentration (Pareto)")
cust_sales = fdf.groupby('Customer Name')['Sales value'].sum().sort_values(ascending=False).reset_index()
cust_sales['Cumulative %'] = cust_sales['Sales value'].cumsum() / cust_sales['Sales value'].sum() * 100

fig = go.Figure()
fig.add_bar(x=cust_sales['Customer Name'], y=cust_sales['Sales value'],
            name='Sales', marker_color='#636EFA')
fig.add_scatter(x=cust_sales['Customer Name'], y=cust_sales['Cumulative %'],
                mode='lines', name='Cumulative %', yaxis='y2',
                line=dict(color='#EF553B', width=2))
fig.update_layout(
    height=380, margin=dict(l=10, r=10, t=40, b=10),
    yaxis=dict(title='Sales (₹)'),
    yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 105]),
    xaxis=dict(showticklabels=False, title='Customers (sorted by revenue)'),
    legend=dict(orientation='h', y=1.1)
)
st.plotly_chart(fig, use_container_width=True)

# ── Row 7: Treemap + State Choropleth ─────────────────────────────────────────
c9, c10 = st.columns([3, 2])

with c9:
    fig = px.treemap(fdf, path=['Zone', 'Product Category 1'],
                     values='Sales value',
                     title="🍩 Revenue Contribution — Zone → Product",
                     color='Sales value', color_continuous_scale='RdBu')
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

with c10:
    state_sales = fdf.groupby('State')['Sales value'].sum().reset_index().sort_values('Sales value', ascending=False).head(15)
    fig = px.bar(state_sales, x='Sales value', y='State', orientation='h',
                 title="🗾 Top 15 States by Revenue",
                 color='Sales value', color_continuous_scale='Oranges')
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10), yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 8: Customer Segmentation Bubble ───────────────────────────────────────
st.subheader("🫧 Customer Segmentation")
cust_seg = fdf.groupby(['Customer Name', 'Customer Category']).agg(
    Sales=('Sales value', 'sum'),
    Qty=('Quantity', 'sum'),
    Invoices=('Invoice No.', 'nunique')
).reset_index()
cust_seg['Qty_abs'] = cust_seg['Qty'].abs()
fig = px.scatter(cust_seg, x='Invoices', y='Sales', size='Qty_abs',
                 color='Customer Category', hover_name='Customer Name',
                 title="Customer Segmentation — Sales vs Order Frequency (bubble = quantity)",
                 color_discrete_sequence=px.colors.qualitative.Vivid)
fig.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig, use_container_width=True)

# ── Row 9: Credit Notes Analysis ──────────────────────────────────────────────
st.subheader("⚠️ Credit Notes / Negative Sales Analysis")
neg = fdf[fdf['Sales value'] < 0].copy()
c11, c12 = st.columns(2)

with c11:
    neg_cust = neg.groupby('Customer Name')['Sales value'].sum().reset_index().sort_values('Sales value')
    fig = px.bar(neg_cust, x='Sales value', y='Customer Name', orientation='h',
                 title="Credit Notes by Customer",
                 color='Sales value', color_continuous_scale='Reds_r')
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10), yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c12:
    neg_zone = neg.groupby('Zone')['Sales value'].sum().reset_index()
    fig = px.pie(neg_zone, names='Zone', values='Sales value',
                 title="Credit Notes by Zone", hole=0.4,
                 color_discrete_sequence=px.colors.sequential.Reds_r)
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ── Row 10: Week-over-Week + Cluster Analysis ─────────────────────────────────
c13, c14 = st.columns(2)

with c13:
    weekly = fdf.groupby('Week')['Sales value'].sum().reset_index()
    fig = px.bar(weekly, x='Week', y='Sales value',
                 title="📅 Weekly Sales Distribution",
                 color='Sales value', color_continuous_scale='Blues')
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c14:
    cluster_sales = fdf.groupby('Cluster')['Sales value'].sum().reset_index().sort_values('Sales value', ascending=False).head(15)
    fig = px.bar(cluster_sales, x='Cluster', y='Sales value',
                 title="🏙 Top 15 City Clusters by Sales",
                 color='Sales value', color_continuous_scale='Purples')
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 11: Retailers Zone Analysis ────────────────────────────────────
st.subheader("🛒 Retailers Analysis by Zone")
retail_df = fdf[fdf['Customer Category'] == 'Retailer']

c15, c16, c17 = st.columns(3)

with c15:
    retail_cust = retail_df.groupby('Zone')['Customer Name'].nunique().reset_index()
    retail_cust.columns = ['Zone', 'Unique Retail Customers']
    fig = px.bar(retail_cust.sort_values('Unique Retail Customers', ascending=False),
                 x='Zone', y='Unique Retail Customers', color='Zone',
                 title="Unique Retail Customers per Zone",
                 color_discrete_sequence=px.colors.qualitative.Set2,
                 text='Unique Retail Customers')
    fig.update_traces(textposition='outside')
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c16:
    retail_rev = retail_df.groupby('Zone')['Sales value'].sum().reset_index()
    fig = px.bar(retail_rev.sort_values('Sales value', ascending=False),
                 x='Zone', y='Sales value', color='Zone',
                 title="Retail Revenue per Zone",
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 text_auto='.2s')
    fig.update_traces(textposition='outside')
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10), showlegend=False, yaxis_title="Sales (₹)")
    st.plotly_chart(fig, use_container_width=True)

with c17:
    retail_inv = retail_df.groupby('Zone')['Invoice No.'].nunique().reset_index()
    retail_inv.columns = ['Zone', 'Invoices']
    retail_cust2 = retail_df.groupby('Zone')['Customer Name'].nunique().reset_index()
    retail_cust2.columns = ['Zone', 'Customers']
    merged = retail_inv.merge(retail_cust2, on='Zone')
    merged['Avg Invoices/Customer'] = (merged['Invoices'] / merged['Customers']).round(1)
    fig = px.bar(merged.sort_values('Avg Invoices/Customer', ascending=False),
                 x='Zone', y='Avg Invoices/Customer', color='Zone',
                 title="Avg Invoices per Retail Customer",
                 color_discrete_sequence=px.colors.qualitative.Bold,
                 text='Avg Invoices/Customer')
    fig.update_traces(textposition='outside')
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Insight callout
west_retail = retail_df[retail_df['Zone']=='West']['Customer Name'].nunique()
north_retail = retail_df[retail_df['Zone']=='North']['Customer Name'].nunique()
north_rev = retail_df[retail_df['Zone']=='North']['Sales value'].sum()
west_rev = retail_df[retail_df['Zone']=='West']['Sales value'].sum()
st.info(
    f"🔍 **Retail Insight:** West Zone has the most retail customers ({west_retail}), but North Zone "
    f"generates higher retail revenue (₹{north_rev:,.0f} vs ₹{west_rev:,.0f}) with one fewer customer ({north_retail}), "
    f"indicating North's retail customers have a higher average order value."
)

# ── Raw Data ──────────────────────────────────────────────────────────────────
with st.expander("🗃 Raw Data"):
    st.dataframe(fdf, use_container_width=True)
