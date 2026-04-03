import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Sales Dashboard", layout="wide", initial_sidebar_state="expanded")

# -------------------- CUSTOM CSS FOR ANIMATIONS --------------------
st.markdown("""
<style>
    /* Fade-in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Slide-up animation */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Pulse animation for KPIs */
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Smooth glow effect */
    @keyframes glow {
        from { box-shadow: 0 0 5px rgba(100, 149, 237, 0.3); }
        to { box-shadow: 0 0 15px rgba(100, 149, 237, 0.6); }
    }
    
    .metric-card {
        animation: slideUp 0.6s ease-out;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .chart-container {
        animation: slideUp 0.8s ease-out;
        border-radius: 10px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    .title-animated {
        animation: slideUp 0.5s ease-out;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: slideUp 0.5s ease-out, gradientShift 3s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .subheader-animated {
        animation: fadeIn 0.6s ease-out;
        border-left: 4px solid #667eea;
        padding-left: 10px;
    }
    
    div[data-testid="metric-container"] {
        animation: pulse 2s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data/Test Data 22 Intern (1).xlsx")
    return df

df = load_data()

# -------------------- DATA CLEANING --------------------
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month_name()
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
df['Sales value'] = pd.to_numeric(df['Sales value'], errors='coerce').fillna(0)

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🔍 Filters")

year_filter = st.sidebar.multiselect(
    "Year",
    options=sorted(df['Year'].dropna().unique()),
    default=sorted(df['Year'].dropna().unique())
)

zone_filter = st.sidebar.multiselect(
    "Zone",
    options=df['Zone'].dropna().unique(),
    default=df['Zone'].dropna().unique()
)

state_filter = st.sidebar.multiselect(
    "State",
    options=df['State'].dropna().unique(),
    default=df['State'].dropna().unique()
)

rep_filter = st.sidebar.multiselect(
    "External Sales Rep",
    options=df['External Sales Representative'].dropna().unique(),
    default=df['External Sales Representative'].dropna().unique()
)

# -------------------- FILTER DATA --------------------
filtered_df = df[
    (df['Year'].isin(year_filter)) &
    (df['Zone'].isin(zone_filter)) &
    (df['State'].isin(state_filter)) &
    (df['External Sales Representative'].isin(rep_filter))
]

# -------------------- KPIs --------------------
total_sales = filtered_df['Sales value'].sum()
pending_bills = filtered_df[filtered_df['Sales value'] < 0]['Sales value'].sum()
TARGET = 650000000
achievement = (total_sales / TARGET) * 100 if TARGET else 0

# -------------------- TITLE --------------------
st.markdown('<h1 class="title-animated">📊 SALES DASHBOARD</h1>', unsafe_allow_html=True)

# -------------------- KPI GRID WITH ANIMATION --------------------
st.markdown('<div style="margin: 20px 0;"></div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Sales Value</h3>
        <h2>₹{total_sales:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Pending Bills</h3>
        <h2>₹{pending_bills:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Target</h3>
        <h2>₹{TARGET:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Achievement %</h3>
        <h2>{achievement:.2f}%</h2>
    </div>
    """, unsafe_allow_html=True)

# -------------------- CHART DATA --------------------
yearly = filtered_df.groupby('Year')['Sales value'].sum().reset_index()
quarterly = filtered_df.groupby('Quarter')['Sales value'].sum().reset_index()
zone_sales = filtered_df.groupby('Zone')['Sales value'].sum().reset_index()
rep_sales = filtered_df.groupby('External Sales Representative')['Sales value'].sum().reset_index()
product_sales = filtered_df.groupby('Product Category 1')['Sales value'].sum().reset_index()

# -------------------- ENHANCED CHARTS WITH ANIMATIONS --------------------
def style_chart(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
        hovermode='x unified',
        transition=dict(duration=500, easing='cubic-in-out'),
        template='plotly_white',
        font=dict(family="Arial, sans-serif", size=11),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.5)',
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Sales: ₹%{y:,.0f}<extra></extra>',
        marker=dict(line=dict(width=0.5)),
        textposition='outside'
    )
    return fig

# Create charts with enhanced styling
fig_year = px.bar(
    yearly, x='Year', y='Sales value',
    title="📈 Yearly Sales",
    color='Sales value',
    color_continuous_scale='Viridis'
)
fig_year = style_chart(fig_year)

fig_quarter = px.pie(
    quarterly, names='Quarter', values='Sales value',
    title="📊 Quarterly Sales",
    hole=0.3
)
fig_quarter.update_traces(textposition='inside', textinfo='percent+label')
fig_quarter = style_chart(fig_quarter)

fig_zone = px.bar(
    zone_sales, x='Zone', y='Sales value',
    color='Zone',
    title="🌍 Zonal Sales"
)
fig_zone = style_chart(fig_zone)

fig_rep = px.bar(
    rep_sales.sort_values(by='Sales value', ascending=False),
    x='External Sales Representative', y='Sales value',
    title="👥 Sales by Representative",
    color='Sales value',
    color_continuous_scale='Blues'
)
fig_rep = style_chart(fig_rep)

fig_product = px.bar(
    product_sales.sort_values(by='Sales value', ascending=False),
    x='Product Category 1', y='Sales value',
    title="📦 Product Sales",
    color='Sales value',
    color_continuous_scale='Greens'
)
fig_product = style_chart(fig_product)

# -------------------- GRID LAYOUT --------------------
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    st.plotly_chart(fig_year, use_container_width=True)

with c2:
    st.plotly_chart(fig_quarter, use_container_width=True)

with c3:
    st.plotly_chart(fig_zone, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
c4, c5 = st.columns(2)

with c4:
    st.plotly_chart(fig_rep, use_container_width=True)

with c5:
    st.plotly_chart(fig_product, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------- EXTRA SECTION --------------------
st.markdown('<h3 class="subheader-animated">📉 Negative Sales (Credit Notes)</h3>', unsafe_allow_html=True)
st.dataframe(
    filtered_df[filtered_df['Sales value'] < 0],
    use_container_width=True,
    hide_index=True
)

# -------------------- TOP PERFORMERS --------------------
st.markdown('<h3 class="subheader-animated">🏆 Top Sales Representatives</h3>', unsafe_allow_html=True)

top_sales = rep_sales.sort_values(by='Sales value', ascending=False).head(10)

fig_top = px.bar(
    top_sales,
    x='Sales value',
    y='External Sales Representative',
    orientation='h',
    title="Top 10 Sales Reps",
    color='Sales value',
    color_continuous_scale='Oranges'
)
fig_top = style_chart(fig_top)

st.plotly_chart(fig_top, use_container_width=True)

# Top 5 and Bottom 5 with animations
col1, col2 = st.columns(2)

with col1:
    st.markdown('<h4 class="subheader-animated">📌 Top 5 Sales Representatives</h4>', unsafe_allow_html=True)
    top5 = rep_sales.nlargest(5, 'Sales value')
    st.dataframe(top5, use_container_width=True, hide_index=True)

with col2:
    st.markdown('<h4 class="subheader-animated">📌 Bottom 5 Sales Representatives</h4>', unsafe_allow_html=True)
    bottom5 = rep_sales.nsmallest(5, 'Sales value')
    st.dataframe(bottom5, use_container_width=True, hide_index=True)

# -------------------- CUSTOMER REVENUE CONCENTRATION --------------------
st.markdown('<h3 class="subheader-animated">📊 Customer Revenue Concentration (Pareto Analysis)</h3>', unsafe_allow_html=True)

customer_sales = df.groupby('Customer Name')['Sales value'].sum().sort_values(ascending=False).reset_index()
customer_sales['Cumulative %'] = customer_sales['Sales value'].cumsum() / customer_sales['Sales value'].sum() * 100

fig = px.bar(
    customer_sales,
    x='Customer Name',
    y='Sales value',
    title="Customer Sales Distribution",
    color='Sales value',
    color_continuous_scale='Viridis'
)

fig.add_scatter(
    x=customer_sales['Customer Name'],
    y=customer_sales['Cumulative %'],
    mode='lines+markers',
    name='Cumulative %',
    yaxis='y2',
    line=dict(color='red', width=3),
    marker=dict(size=6)
)

fig.update_layout(
    yaxis2=dict(overlaying='y', side='right', title='Cumulative %'),
    hovermode='x unified',
    transition=dict(duration=500)
)

st.plotly_chart(fig, use_container_width=True)

# -------------------- CUSTOMER SEGMENTATION --------------------
st.markdown('<h3 class="subheader-animated">🫧 Customer Segmentation</h3>', unsafe_allow_html=True)

cust_seg = df.groupby('Customer Name').agg({
    'Sales value': 'sum',
    'Quantity': 'sum',
    'Invoice No.': 'count'
}).reset_index()

cust_seg['Type'] = cust_seg['Sales value'].apply(lambda x: 'Positive' if x >= 0 else 'Negative')
cust_seg['Quantity_abs'] = cust_seg['Quantity'].abs()

fig = px.scatter(
    cust_seg,
    x='Invoice No.',
    y='Sales value',
    size='Quantity_abs',
    color='Type',
    hover_name='Customer Name',
    title="Customer Segmentation (Positive vs Negative)",
    color_discrete_map={'Positive': '#00CC96', 'Negative': '#EF553B'},
    size_max=50
)
fig = style_chart(fig)

st.plotly_chart(fig, use_container_width=True)

# -------------------- PRODUCT VS ZONE HEATMAP --------------------
st.markdown('<h3 class="subheader-animated">🔥 Product vs Zone Heatmap</h3>', unsafe_allow_html=True)

pivot = pd.pivot_table(
    df,
    values='Sales value',
    index='Product Category 1',
    columns='Zone',
    aggfunc='sum',
    fill_value=0
)

fig = px.imshow(
    pivot,
    text_auto=True,
    aspect="auto",
    title="Product vs Zone Sales Heatmap",
    color_continuous_scale='RdYlGn',
    labels=dict(x="Zone", y="Product")
)
fig.update_layout(height=500, transition=dict(duration=500))

st.plotly_chart(fig, use_container_width=True)

# -------------------- SALES REP EFFICIENCY --------------------
st.markdown('<h3 class="subheader-animated">🎯 Sales Rep Efficiency</h3>', unsafe_allow_html=True)

rep_eff = df.groupby('External Sales Representative').agg({
    'Sales value': 'sum',
    'Invoice No.': 'count'
}).reset_index()

fig = px.scatter(
    rep_eff,
    x='Invoice No.',
    y='Sales value',
    hover_name='External Sales Representative',
    size='Sales value',
    title="Sales Rep Efficiency (Invoices vs Sales Value)",
    color='Sales value',
    color_continuous_scale='Plasma',
    size_max=50
)
fig = style_chart(fig)

st.plotly_chart(fig, use_container_width=True)

# -------------------- MONTHLY SALES TREND --------------------
st.markdown('<h3 class="subheader-animated">📈 Monthly Sales Trend</h3>', unsafe_allow_html=True)

monthly_sales = df.groupby(df['Date'].dt.to_period('M'))['Sales value'].sum().reset_index()
monthly_sales['Month'] = monthly_sales['Date'].astype(str)

fig = px.line(
    monthly_sales,
    x='Month',
    y='Sales value',
    title="Monthly Sales Trend",
    markers=True,
    line=dict(color='#636EFA', width=3),
    marker=dict(size=8)
)
fig.update_traces(fill='tozeroy', fillcolor='rgba(99, 110, 250, 0.2)')
fig = style_chart(fig)

st.plotly_chart(fig, use_container_width=True)

# -------------------- CONTRIBUTION ANALYSIS --------------------
st.markdown('<h3 class="subheader-animated">🍩 Contribution Analysis</h3>', unsafe_allow_html=True)

df_clean = df.copy()
df_clean['Zone'] = df_clean['Zone'].fillna("Unknown")
df_clean['Product Category 1'] = df_clean['Product Category 1'].fillna("Unknown")
df_clean['Product Category 1'] = df_clean['Product Category 1'].replace("", "Unknown")

fig = px.treemap(
    df_clean,
    path=['Zone', 'Product Category 1'],
    values='Sales value',
    title="Revenue Contribution by Zone & Product",
    color='Sales value',
    color_continuous_scale='Sunsetdark'
)
fig.update_layout(height=600, transition=dict(duration=500))

st.plotly_chart(fig, use_container_width=True)

# -------------------- NEGATIVE SALES ANALYSIS --------------------
st.markdown('<h3 class="subheader-animated">⚠️ Negative Sales Analysis</h3>', unsafe_allow_html=True)

neg = df[df['Sales value'] < 0]
neg_group = neg.groupby('Customer Name')['Sales value'].sum().reset_index()

fig = px.bar(
    neg_group,
    x='Customer Name',
    y='Sales value',
    title="Negative Sales by Customer",
    color='Sales value',
    color_continuous_scale='Reds'
)
fig = style_chart(fig)

st.plotly_chart(fig, use_container_width=True)

# -------------------- CUSTOMER RETENTION COHORT --------------------
st.markdown('<h3 class="subheader-animated">🔁 Customer Retention (Cohort)</h3>', unsafe_allow_html=True)

df['Month'] = df['Date'].dt.strftime('%b %Y')
cohort = df.groupby(['Customer Name', 'Month']).size().reset_index(name='count')
pivot = cohort.pivot(index='Customer Name', columns='Month', values='count').fillna(0)

fig = px.imshow(
    pivot,
    aspect="auto",
    title="Customer Cohort Analysis",
    color_continuous_scale='Blues'
)
fig.update_layout(height=800, transition=dict(duration=500))

st.plotly_chart(fig, use_container_width=True)

# -------------------- PRODUCT BASKET ANALYSIS --------------------
st.markdown('<h3 class="subheader-animated">🧠 Product Basket Analysis</h3>', unsafe_allow_html=True)

basket = df.groupby('Customer Name')['Product Category 1'] \
    .apply(lambda x: ', '.join(sorted(set(x.dropna().astype(str))))) \
    .reset_index()

st.dataframe(basket, use_container_width=True, hide_index=True)

# -------------------- FOOTER --------------------
st.markdown("""
<hr>
<p style="text-align: center; color: gray; font-size: 12px;">
    Dashboard Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
    <br>Data Source: Test Data 22 Intern
</p>
""", unsafe_allow_html=True)
