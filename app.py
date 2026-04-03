import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# -------------------- LOAD DATA --------------------
# Replace with your file
df = pd.read_excel("data/Test Data 22 Intern (1).xlsx")

# -------------------- DATA CLEANING --------------------
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month_name()
df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)

# Ensure numeric
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
st.title("📊 SALES DASHBOARD")

# -------------------- KPI GRID --------------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("Sales Value", f"{total_sales:,.0f}")
k2.metric("Pending Bills", f"{pending_bills:,.0f}")
k3.metric("Target", f"{TARGET:,.0f}")
k4.metric("Achievement %", f"{achievement:.2f}%")
# print(filtered_df)
# -------------------- CHART DATA --------------------
yearly = filtered_df.groupby('Year')['Sales value'].sum().reset_index()
quarterly = filtered_df.groupby('Quarter')['Sales value'].sum().reset_index()
zone_sales = filtered_df.groupby('Zone')['Sales value'].sum().reset_index()
rep_sales = filtered_df.groupby('External Sales Representative')['Sales value'].sum().reset_index()
product_sales = filtered_df.groupby('Product Category 1')['Sales value'].sum().reset_index()

# -------------------- CHARTS --------------------
fig_year = px.bar(yearly, x='Year', y='Sales value', title="Yearly Sales")
fig_quarter = px.pie(quarterly, names='Quarter', values='Sales value', title="Quarterly Sales")
fig_zone = px.bar(zone_sales, x='Zone', y='Sales value', color='Zone', title="Zonal Sales")
fig_rep = px.bar(rep_sales.sort_values(by='Sales value', ascending=False),
                 x='External Sales Representative', y='Sales value',
                 title="Sales by Representative")
fig_product = px.bar(product_sales.sort_values(by='Sales value', ascending=False),
                     x='Product Category 1', y='Sales value',
                     title="Product Sales")

# -------------------- STYLE --------------------
def style_chart(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        height=320
    )
    return fig

fig_year = style_chart(fig_year)
fig_quarter = style_chart(fig_quarter)
fig_zone = style_chart(fig_zone)
fig_rep = style_chart(fig_rep)
fig_product = style_chart(fig_product)

# -------------------- GRID LAYOUT --------------------

# Row 1 → Big + 2 small (like PDF)
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    st.plotly_chart(fig_year, use_container_width=True)

with c2:
    st.plotly_chart(fig_quarter, use_container_width=True)

with c3:
    st.plotly_chart(fig_zone, use_container_width=True)

# Row 2 → 2 equal charts
c4, c5 = st.columns(2)

with c4:
    st.plotly_chart(fig_rep, use_container_width=True)

with c5:
    st.plotly_chart(fig_product, use_container_width=True)

# -------------------- EXTRA SECTION --------------------
st.subheader("📉 Negative Sales (Credit Notes)")
st.dataframe(filtered_df[filtered_df['Sales value'] < 0])

# -------------------- TOP PERFORMERS --------------------
st.subheader("🏆 Top Sales Representatives")

top_sales = rep_sales.sort_values(by='Sales value', ascending=False).head(10)

fig_top = px.bar(top_sales,
                 x='Sales value',
                 y='External Sales Representative',
                 orientation='h',
                 title="Top 10 Sales Reps")

st.plotly_chart(style_chart(fig_top), use_container_width=True)

top5 = rep_sales.nlargest(5, 'Sales value')
bottom5 = rep_sales.nsmallest(5, 'Sales value')
st.subheader("📌 Top 5 Sales Representatives")
st.table(top5)
st.subheader("📌 Bottom 5 Sales Representatives")
st.table(bottom5)


st.subheader("📊 Customer Revenue Concentration (Pareto Analysis)")

customer_sales = df.groupby('Customer Name')['Sales value'].sum().sort_values(ascending=False).reset_index()
customer_sales['Cumulative %'] = customer_sales['Sales value'].cumsum() / customer_sales['Sales value'].sum() * 100

fig = px.bar(customer_sales, x='Customer Name', y='Sales value', title="Customer Sales")

fig.add_scatter(
    x=customer_sales['Customer Name'],
    y=customer_sales['Cumulative %'],
    mode='lines',
    name='Cumulative %',
    yaxis='y2'
)

fig.update_layout(
    yaxis2=dict(overlaying='y', side='right', title='Cumulative %')
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("🫧 Customer Segmentation")

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
    title="Customer Segmentation (Positive vs Negative)"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🔥 Product vs Zone Heatmap")

pivot = pd.pivot_table(
    df,
    values='Sales value',
    index='Product Category 1',
    columns='Zone',
    aggfunc='sum',
    fill_value=0
)

fig = px.imshow(pivot, text_auto=True, aspect="auto", title="Product vs Zone Sales")

st.plotly_chart(fig, use_container_width=True)



st.subheader("🎯 Sales Rep Efficiency")

rep_eff = df.groupby('External Sales Representative').agg({
    'Sales value': 'sum',
    'Invoice No.': 'count'
}).reset_index()

fig = px.scatter(
    rep_eff,
    x='Invoice No.',
    y='Sales value',
    hover_name='External Sales Representative',
    title="Sales Rep Efficiency"
)

st.plotly_chart(fig, use_container_width=True)



st.subheader("📈 Monthly Sales Trend")
monthly_sales = df.groupby(df['Date'].dt.to_period('M'))['Sales value'].sum().reset_index()

# Convert for plotting
monthly_sales['Month'] = monthly_sales['Date'].astype(str)

fig = px.line(
    monthly_sales,
    x='Month',
    y='Sales value',
    title="Monthly Sales Trend"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🍩 Contribution Analysis")
df_clean = df.copy()

df_clean['Zone'] = df_clean['Zone'].fillna("Unknown")
df_clean['Product Category 1'] = df_clean['Product Category 1'].fillna("Unknown")

# Also handle empty strings
df_clean['Product Category 1'] = df_clean['Product Category 1'].replace("", "Unknown")

fig = px.treemap(
    df_clean,
    path=['Zone', 'Product Category 1'],
    values='Sales value',
    title="Revenue Contribution by Zone & Product"
)

st.plotly_chart(fig, use_container_width=True)




st.subheader("⚠️ Negative Sales Analysis")

neg = df[df['Sales value'] < 0]

neg_group = neg.groupby('Customer Name')['Sales value'].sum().reset_index()

fig = px.bar(neg_group, x='Customer Name', y='Sales value', color='Sales value')

st.plotly_chart(fig, use_container_width=True)





st.subheader("🔁 Customer Retention (Cohort)")
df['Month'] = df['Date'].dt.strftime('%b %Y')

cohort = df.groupby(['Customer Name', 'Month']).size().reset_index(name='count')

pivot = cohort.pivot(index='Customer Name', columns='Month', values='count').fillna(0)

fig = px.imshow(pivot, aspect="auto", title="Customer Cohort")

st.plotly_chart(fig, use_container_width=True)


st.subheader("🧠 Product Basket Analysis")

basket = df.groupby('Customer Name')['Product Category 1'] \
    .apply(lambda x: ', '.join(sorted(set(x.dropna().astype(str))))) \
    .reset_index()

st.dataframe(basket)