from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT = "Kessebohmer_Sales_Dashboard_Report.pdf"

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

BRAND   = colors.HexColor("#1B3A6B")
ACCENT  = colors.HexColor("#2E86AB")
LIGHT   = colors.HexColor("#F0F4F8")
WARN    = colors.HexColor("#E63946")
GREEN   = colors.HexColor("#2DC653")

title_style = ParagraphStyle("Title", parent=styles["Title"],
    fontSize=22, textColor=BRAND, spaceAfter=6, alignment=TA_CENTER)

subtitle_style = ParagraphStyle("Sub", parent=styles["Normal"],
    fontSize=11, textColor=ACCENT, spaceAfter=14, alignment=TA_CENTER)

h1 = ParagraphStyle("H1", parent=styles["Heading1"],
    fontSize=14, textColor=BRAND, spaceBefore=18, spaceAfter=6,
    borderPad=4, leading=18)

h2 = ParagraphStyle("H2", parent=styles["Heading2"],
    fontSize=11, textColor=ACCENT, spaceBefore=12, spaceAfter=4)

body = ParagraphStyle("Body", parent=styles["Normal"],
    fontSize=9.5, leading=15, spaceAfter=6, alignment=TA_JUSTIFY)

bullet = ParagraphStyle("Bullet", parent=styles["Normal"],
    fontSize=9.5, leading=15, leftIndent=16, spaceAfter=4,
    bulletIndent=6)

answer = ParagraphStyle("Answer", parent=styles["Normal"],
    fontSize=9.5, leading=15, leftIndent=20, spaceAfter=6,
    textColor=colors.HexColor("#2D3748"), alignment=TA_JUSTIFY)

caption = ParagraphStyle("Caption", parent=styles["Normal"],
    fontSize=8, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=8)

# ── Helpers ───────────────────────────────────────────────────────────────────
def hr(): return HRFlowable(width="100%", thickness=0.5, color=ACCENT, spaceAfter=8, spaceBefore=4)

def section(title): return [Spacer(1, 0.2*cm), Paragraph(title, h1), hr()]

def qa(q, a):
    return [
        Paragraph(f"<b>Q: {q}</b>", h2),
        Paragraph(a, answer),
        Spacer(1, 0.15*cm)
    ]

def table(data, col_widths, header_bg=BRAND):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  header_bg),
        ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,0),  9),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,1), (-1,-1), 8.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT, colors.white]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E0")),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ])
    t.setStyle(style)
    return t

# ── Content ───────────────────────────────────────────────────────────────────
story = []

# Cover
story += [
    Spacer(1, 2*cm),
    Paragraph("Kessebohmer India", title_style),
    Paragraph("Sales Analytics Dashboard — Internship Assignment Report", subtitle_style),
    Spacer(1, 0.3*cm),
    HRFlowable(width="60%", thickness=2, color=ACCENT, hAlign="CENTER"),
    Spacer(1, 0.5*cm),
    Paragraph("Data Period: January 2022 – June 2022", ParagraphStyle("c", parent=styles["Normal"],
        fontSize=10, alignment=TA_CENTER, textColor=colors.grey)),
    Paragraph("Prepared by: Sanjay  |  Role: Data Analytics Intern", ParagraphStyle("c2", parent=styles["Normal"],
        fontSize=10, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=4)),
    Spacer(1, 2*cm),
]

# Summary box
summary_data = [
    ["Metric", "Value"],
    ["Total Transactions", "5,600"],
    ["Gross Sales", "₹13.38 Crore"],
    ["Credit Notes", "₹25.27 Lakh"],
    ["Net Sales", "₹13.12 Crore"],
    ["Unique Customers", "319"],
    ["Unique Products", "483"],
    ["States Covered", "21"],
    ["Cities Covered", "84"],
    ["Sales Representatives", "26"],
    ["Data Period", "Jan 2022 – Jun 2022"],
]
story.append(table(summary_data, [8*cm, 8*cm]))
story.append(PageBreak())

# ── Section 1: Dataset Overview ───────────────────────────────────────────────
story += section("1. Dataset Overview")
story.append(Paragraph(
    "The dataset contains <b>5,600 sales transaction records</b> for Kessebohmer India spanning "
    "<b>January to June 2022</b> (H1 2022). It covers 30 columns including customer details, "
    "product hierarchy, geographic data (city, state, zone), sales representative mapping, "
    "invoice metadata, and temporal fields. The data spans <b>4 zones</b> (North, South, East, West), "
    "<b>21 states</b>, <b>84 cities</b>, and <b>319 unique customers</b> across 6 customer categories.",
    body))

story += section("2. Data Quality Assessment")
story += qa(
    "What data quality issues were found?",
    "Three columns had significant null values: Product Category 1 & 2 (1,627 nulls each — 29% of rows), "
    "Product Category 3 (2,167 nulls — 39%), and Delivered Quantity Set/Pcs (5,600 nulls — 100% missing, "
    "making it unusable). Customer Category had 11 nulls and Cluster had 49 nulls. "
    "All nulls in categorical fields were filled with 'Uncategorised' or 'Unknown' to avoid "
    "dropping valid sales records."
)
story += qa(
    "Were there any negative sales values and how were they handled?",
    "Yes — 144 out of 5,600 rows (2.6%) had negative Sales values totalling ₹25.27 Lakh. "
    "These represent credit notes and rate difference adjustments (confirmed by Product Description values "
    "like 'Credit Note' and 'Rate Difference'). They were kept in the dataset and analysed separately "
    "rather than removed, as they represent real business events (returns, corrections)."
)
story += qa(
    "Were there duplicate or inconsistent records?",
    "The 'Internal Organization' and 'Internal organisation' categories in Product Category 1 appear to be "
    "the same category with inconsistent capitalisation — a minor data entry issue. "
    "Date fields were already in datetime format. Invoice numbers were numeric and consistent."
)

story += section("3. Key Business Questions & Answers")

story += qa(
    "Which zone generates the highest revenue?",
    "West Zone leads with ₹6.06 Crore (45.3% of total), followed by South (₹4.48 Crore, 33.5%), "
    "North (₹2.27 Crore, 17.0%), and East (₹31.2 Lakh, 2.3%). "
    "West also has the most customers (136) and invoices (814)."
)

story += qa(
    "Which zone has the most retail customers?",
    "West Zone has the most retail customers with 24 unique retail customers, closely followed by "
    "North with 23. South has 12 and East has only 4. "
    "However, North Zone generates more retail revenue (₹69.6 Lakh) than West (₹68.7 Lakh) despite "
    "having one fewer retail customer — indicating North's retail customers have a higher average order value. "
    "West also leads in retail invoice count (189 invoices) vs North (134), confirming West retailers "
    "transact more frequently but at lower average ticket size."
)

# Retail table
retail_data = [
    ["Zone", "Unique Retail Customers", "Retail Revenue (₹)", "Retail Invoices", "Avg Revenue/Customer (₹)"],
    ["West",  "24", "68,67,161", "189", "2,86,132"],
    ["North", "23", "69,59,396", "134", "3,02,582"],
    ["South", "12", "44,06,004",  "94", "3,67,167"],
    ["East",   "4", "10,42,439",  "22", "2,60,610"],
]
story.append(table(retail_data, [3*cm, 4.5*cm, 4.5*cm, 3.5*cm, 4.5*cm]))
story.append(Paragraph("Table: Retail customer breakdown by zone", caption))

story += qa(
    "Who are the top performing sales representatives?",
    "Manish Sir leads with ₹2.77 Crore (20.7% of total sales), followed by Piyush Dhami (₹2.19 Crore, 16.4%), "
    "Abdul Shaikh (₹1.17 Crore, 8.8%), Shubhankar Nale (₹81.4 Lakh), and Ramesh Kumar (₹68.9 Lakh). "
    "The top 2 reps alone account for 37% of all revenue — a concentration risk."
)

rep_data = [
    ["Rank", "Sales Representative", "Sales Value (₹)", "Share %"],
    ["1", "Manish Sir",         "2,77,06,487", "20.7%"],
    ["2", "Piyush Dhami",       "2,19,03,420", "16.4%"],
    ["3", "Abdul Shaikh",       "1,17,47,266",  "8.8%"],
    ["4", "Shubhankar Nale",      "81,44,001",  "6.1%"],
    ["5", "Ramesh Kumar",         "68,89,561",  "5.2%"],
]
story.append(table(rep_data, [2*cm, 6*cm, 5*cm, 3*cm]))
story.append(Paragraph("Table: Top 5 External Sales Representatives", caption))

story += qa(
    "Which customers drive the most revenue?",
    "Asian Paints Limited (Sleek) is the single largest customer at ₹2.50 Crore — nearly 18.7% of total revenue. "
    "The top 5 customers together contribute ₹4.44 Crore (33.2%). This extreme concentration means losing "
    "Asian Paints alone would reduce revenue by nearly a fifth."
)

cust_data = [
    ["Rank", "Customer Name", "Sales Value (₹)", "Share %"],
    ["1", "Asian Paints Limited (Sleek)",          "2,49,64,083", "18.7%"],
    ["2", "HomeInteriorDesigns ECommerce Pvt Ltd",   "72,23,825",  "5.4%"],
    ["3", "Pickel Concept",                          "59,72,467",  "4.5%"],
    ["4", "Airava Interior Solutions (Wurfel)",       "33,62,058",  "2.5%"],
    ["5", "Fiore Living Private Limited",             "28,38,489",  "2.1%"],
]
story.append(table(cust_data, [2*cm, 7*cm, 4.5*cm, 2.5*cm]))
story.append(Paragraph("Table: Top 5 Customers by Revenue", caption))

story += qa(
    "What is the monthly sales trend?",
    "Sales were relatively stable across H1 2022, ranging from ₹2.06 Crore (April) to ₹2.43 Crore (March). "
    "March was the peak month, likely driven by financial year-end purchasing. "
    "April dipped (new FY start), then recovered steadily through June (₹2.18 Crore). "
    "There is no dramatic seasonality, suggesting consistent demand throughout H1."
)

monthly_data = [
    ["Month", "Sales Value (₹)", "MoM Change"],
    ["January 2022",  "2,08,36,497", "—"],
    ["February 2022", "2,15,21,879", "+3.3%"],
    ["March 2022",    "2,42,93,852", "+12.9%"],
    ["April 2022",    "2,05,89,121", "-15.2%"],
    ["May 2022",      "2,21,56,266", "+7.6%"],
    ["June 2022",     "2,18,44,057", "-1.4%"],
]
story.append(table(monthly_data, [5*cm, 5*cm, 5*cm]))
story.append(Paragraph("Table: Monthly Sales Trend", caption))

story += qa(
    "Which product categories perform best?",
    "Among categorised products, Tall Cabinet and Base Cabinet are the dominant categories. "
    "The top individual product line is TANDEM (Set Tandem ARENAplus Style SS 60er) at ₹1.02 Crore. "
    "However, 1,627 rows (29%) have no Product Category 1 assigned — these are primarily credit notes "
    "and rate difference entries, which explains the high null count."
)

story += qa(
    "What does the Zone × Product heatmap reveal?",
    "West Zone dominates across almost all product categories. South Zone shows strong performance "
    "in Bedroom and Tall Cabinet categories. The heatmap reveals that Internal Organisation products "
    "are almost exclusively sold in West and South, while Corner Cabinet has negligible presence in East. "
    "This suggests East Zone may need targeted product introduction campaigns."
)

story += qa(
    "What is the Pareto distribution of customers?",
    "The top 20% of customers (approximately 64 customers) account for roughly 80% of revenue — "
    "a classic Pareto distribution. Asian Paints alone (1 customer = 0.3% of base) drives 18.7% of revenue. "
    "This concentration is both a strength (key account management is tractable) and a risk "
    "(churn of top accounts would be catastrophic)."
)

story += qa(
    "How significant are credit notes / returns?",
    "Credit notes total ₹25.27 Lakh across 144 transactions — 1.9% of gross sales. "
    "The largest credit note issuers are concentrated in West and South zones. "
    "HomeInteriorDesigns ECommerce Pvt Ltd appears in both top customers and top credit note issuers, "
    "suggesting a high-volume but operationally complex relationship."
)

story += section("4. Visualisation Design Decisions")

story += qa(
    "Why use an Area chart for Monthly Trend instead of a Line chart?",
    "An area chart fills the space under the line, making volume magnitude visually intuitive. "
    "Since we have only 6 data points (months), the filled area prevents the chart from looking sparse "
    "and emphasises cumulative volume rather than just directional movement."
)
story += qa(
    "Why use a Donut chart for Quarterly Split and Customer Category?",
    "Donut charts work well when there are fewer than 6 categories and the goal is part-to-whole comparison. "
    "With only 2 quarters and 6 customer categories, a donut is cleaner than a bar chart and the hole "
    "in the centre can display a summary metric (total) in a dashboard context."
)
story += qa(
    "Why use a Heatmap for Zone × Product?",
    "A heatmap is the most efficient way to show a matrix of two categorical variables against a numeric value. "
    "With 13 product categories × 4 zones = 52 cells, a grouped bar chart would be cluttered. "
    "The colour gradient immediately highlights high and low performers without reading individual values."
)
story += qa(
    "Why use a Scatter plot for Rep Efficiency?",
    "A scatter plot with bubble size reveals three dimensions simultaneously: invoice volume (x-axis), "
    "total sales (y-axis), and average order value (bubble size). This separates reps who are high-volume "
    "low-ticket from those who are low-volume high-ticket — a distinction a simple bar chart cannot show."
)
story += qa(
    "Why use a Pareto (bar + line combo) for Customer Concentration?",
    "The Pareto chart is the standard tool for ABC analysis. The bar shows individual customer contribution "
    "while the cumulative % line immediately reveals the 80/20 threshold. This is directly actionable "
    "for key account management prioritisation."
)
story += qa(
    "Why use a Treemap for Zone → Product contribution?",
    "A treemap shows hierarchical data as nested rectangles, making it easy to see both the zone-level "
    "and product-level contribution in a single view. It is space-efficient and visually striking "
    "for executive presentations compared to stacked bar charts."
)
story += qa(
    "Why use a Bubble chart for Customer Segmentation?",
    "Customer segmentation requires plotting multiple attributes simultaneously. The bubble chart maps "
    "order frequency (x), revenue (y), and quantity (bubble size) while colour encodes customer category. "
    "This allows instant identification of high-value, high-frequency customers vs occasional bulk buyers."
)

story += section("5. Business Recommendations")
recs = [
    ("West Zone Retail Focus",
     "West has the most retail customers (24) but North generates more retail revenue per customer. "
     "Investigate whether West retailers need upselling support or if product mix differs."),
    ("Reduce Revenue Concentration Risk",
     "Asian Paints (18.7% of revenue) and top-2 reps (37% of revenue) represent concentration risks. "
     "Develop a mid-tier customer growth programme and cross-train sales reps."),
    ("East Zone Expansion",
     "East has only 11 customers and ₹31.2 Lakh revenue — 2.3% of total. "
     "It is significantly underpenetrated compared to other zones and represents the highest growth opportunity."),
    ("Product Category Data Hygiene",
     "29% of rows lack Product Category 1 assignment. Fixing this at the ERP/invoicing level would "
     "unlock more accurate product-level analytics and commission calculations."),
    ("March Peak Capitalisation",
     "March is consistently the highest sales month (FY-end effect). Pre-position inventory and "
     "sales resources in February to maximise March throughput."),
    ("Credit Note Reduction",
     "144 credit notes worth ₹25.27 Lakh suggest order/delivery errors. "
     "Root cause analysis by customer and product could reduce this by 30-50%."),
]
for title, text in recs:
    story.append(Paragraph(f"<b>{title}:</b> {text}", bullet))
    story.append(Spacer(1, 0.1*cm))

story += section("6. Tools & Technology Stack")
story.append(Paragraph(
    "The dashboard was built using <b>Python 3</b> with the following libraries:", body))
tech_data = [
    ["Library", "Purpose"],
    ["Streamlit",    "Web dashboard framework — interactive UI with sidebar filters"],
    ["Pandas",       "Data loading, cleaning, aggregation, and transformation"],
    ["Plotly Express", "Interactive charts (bar, area, pie, scatter, heatmap, treemap)"],
    ["Plotly Graph Objects", "Custom composite charts (Pareto bar + line overlay)"],
    ["OpenPyXL",     "Excel file reading backend for pandas"],
    ["ReportLab",    "PDF report generation"],
]
story.append(table(tech_data, [5*cm, 11*cm]))

story += [Spacer(1, 1*cm), hr(),
    Paragraph("End of Report", ParagraphStyle("end", parent=styles["Normal"],
        fontSize=9, textColor=colors.grey, alignment=TA_CENTER))]

# ── Build ─────────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
doc.build(story)
print(f"PDF saved → {OUTPUT}")
