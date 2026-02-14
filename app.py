import streamlit as st
from fpdf import FPDF
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Creator Earnings Calc", page_icon="💰")

# --- APP INTERFACE ---
st.title("🇮🇳 Creator Earnings Calculator")
st.write("Professional revenue estimation for Indian content creators.")

# Creator Details Section
st.subheader("Personal Details")
col_a, col_b = st.columns(2)
with col_a:
    creator_name = st.text_input("Creator Name", placeholder="e.g. Priya Sharma")
with col_b:
    creator_user = st.text_input("Platform Username", placeholder="e.g. @priya_creations")

st.divider()

# Input Section
col1, col2 = st.columns(2)
with col1:
    subscribers = st.number_input("Current Subscribers", min_value=0, value=100, step=10)
    sub_charge = st.number_input("Monthly Charge (₹)", min_value=0, value=290, step=10)

with col2:
    platform_fee = st.slider("Platform Commission (%)", 0, 50, 20)

# --- CALCULATIONS ---
gross_monthly = subscribers * sub_charge
net_monthly = gross_monthly * (1 - (platform_fee / 100))
annual_income = net_monthly * 12

# --- DISPLAY METRICS ---
st.subheader("Earnings Overview")
# Highlighting Annual Income as requested
st.metric(label="Estimated Annual Net Income", value=f"₹{int(annual_income):,}")

m_col1, m_col2 = st.columns(2)
m_col1.metric("Gross Monthly Revenue", f"₹{int(gross_monthly):,}")
m_col2.metric("Net Monthly Take-home", f"₹{int(net_monthly):,}")

# --- PDF GENERATION LOGIC ---
def generate_pdf(name, username, subs, charge, fee, monthly, yearly):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", 'B', 20)
    pdf.cell(0, 10, "Creator Earnings Report", ln=True, align='C')
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(0, 10, f"Generated on: {datetime.date.today()}", ln=True, align='C')
    pdf.ln(10)
    
    # Content
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, f"Profile: {name} ({username})", ln=True)
    pdf.set_font("Helvetica", '', 12)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    data = [
        ["Total Subscribers", f"{subs:,}"],
        ["Subscription Price", f"Rs. {charge}"],
        ["Platform Fee", f"{fee}%"],
        ["Net Monthly Income", f"Rs. {int(monthly):,}"],
        ["Estimated Yearly Income", f"Rs. {int(yearly):,}"]
    ]
    
    for item in data:
        pdf.cell(90, 10, item[0], border=0)
        pdf.cell(90, 10, item[1], border=0, ln=True)
    
    pdf.ln(20)
    pdf.set_font("Helvetica", 'I', 10)
    pdf.multi_cell(0, 10, "Note: This report is an estimate based on provided figures and standard platform commissions in India.")
    
    return pdf.output()

# --- DOWNLOAD BUTTON ---
st.divider()
if st.button("Prepare Report PDF"):
    if not creator_name:
        st.error("Please enter a Creator Name first.")
    else:
        pdf_bytes = generate_pdf(creator_name, creator_user, subscribers, sub_charge, platform_fee, net_monthly, annual_income)
        st.download_button(
            label="Click here to Download PDF",
            data=pdf_bytes,
            file_name=f"{creator_name}_earnings_report.pdf",
            mime="application/pdf"
        )
