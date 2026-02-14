import streamlit as st
from fpdf import FPDF
from num2words import num2words
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="Creator Earnings Calc", page_icon="💰", layout="centered")

# --- HELPER FUNCTIONS ---
def format_indian_currency(number):
    """Formats a number into the Indian numbering system (Lakhs/Crores)."""
    s = str(int(number))
    if len(s) <= 3:
        return s
    last_three = s[-3:]
    remaining = s[:-3]
    remaining = re.sub(r'(\d+?)(?=(\d{2})+$)', r'\1,', remaining)
    return f"{remaining},{last_three}"

def amount_to_words(number):
    """Converts a number to Indian English words (Lakhs/Crores)."""
    try:
        words = num2words(int(number), lang='en_IN').title()
        return f"{words} Rupees Only"
    except Exception:
        return ""

# --- APP INTERFACE ---
st.title("🇮🇳 Creator Earnings Calculator")
st.markdown("Professional revenue estimation with high-visibility financial reporting.")

# 1. Creator Details Section (Optional)
st.subheader("Profile Information (Optional)")
c1, c2 = st.columns(2)
with c1:
    raw_name = st.text_input("Full Name", placeholder="Default: XYZ")
with c2:
    raw_user = st.text_input("Platform Username", placeholder="Default: XYZ")

creator_name = raw_name if raw_name.strip() != "" else "XYZ"
creator_user = raw_user if raw_user.strip() != "" else "XYZ"

# 2. Earnings Inputs
st.divider()
col1, col2 = st.columns(2)
with col1:
    subscribers = st.number_input("Total Subscribers", min_value=0, value=100, step=10)
    sub_charge = st.number_input("Monthly Charge (₹)", min_value=0, value=290, step=10)
with col2:
    platform_fee = st.slider("Platform Commission (%)", 0, 50, 20)

# --- CALCULATIONS ---
gross_monthly = subscribers * sub_charge
net_monthly = gross_monthly * (1 - (platform_fee / 100))
annual_income = net_monthly * 12

# --- HIGHLIGHTED RESULTS SECTION ---
st.divider()

# Custom CSS for the colored boxes
st.markdown("""
<style>
    .monthly-box {
        background-color: #e6f4ea;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #34a853;
        margin-bottom: 20px;
    }
    .annual-box {
        background-color: #e8f0fe;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4285f4;
        margin-bottom: 20px;
    }
    .box-label { font-size: 14px; color: #555; font-weight: bold; margin-bottom: 5px; }
    .box-value { font-size: 32px; color: #000; font-weight: 800; }
    .box-words { font-size: 12px; color: #666; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# Monthly Highlight (Green)
st.markdown(f"""
<div class="monthly-box">
    <div class="box-label">ESTIMATED NET MONTHLY INCOME</div>
    <div class="box-value">₹ {format_indian_currency(net_monthly)}</div>
    <div class="box-words">{amount_to_words(net_monthly)}</div>
</div>
""", unsafe_allow_html=True)

# Annual Highlight (Blue)
st.markdown(f"""
<div class="annual-box">
    <div class="box-label">ESTIMATED ANNUAL NET INCOME</div>
    <div class="box-value">₹ {format_indian_currency(annual_income)}</div>
    <div class="box-words">{amount_to_words(annual_income)}</div>
</div>
""", unsafe_allow_html=True)

# --- PDF GENERATION FUNCTION ---
def generate_pdf_bytes(name, user, subs, charge, fee, m_net, y_net):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "EARNINGS ESTIMATION REPORT", ln=True, align="C")
    
    # Creator Info
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(5)
    pdf.cell(0, 8, f"Creator Name: {name}", ln=True)
    pdf.cell(0, 8, f"Username: {user}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Table Data
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(90, 10, "Description", border=1, fill=True)
    pdf.cell(95, 10, "Amount/Value", border=1, fill=True, ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    data = [
        ("Total Active Subscribers", f"{subs:,}"),
        ("Subscription Price", f"Rs. {charge}"),
        ("Platform Fee Deduction", f"{fee}%"),
        ("Net Monthly Take-home", f"Rs. {format_indian_currency(m_net)}"),
        ("Estimated Annual Income", f"Rs. {format_indian_currency(y_net)}")
    ]
    
    for label, val in data:
        pdf.cell(90, 10, label, border=1)
        pdf.cell(95, 10, val, border=1, ln=True)
    
    # Word Representation
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Monthly Income (In Words):", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 8, amount_to_words(m_net))
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Annual Income (In Words):", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 8, amount_to_words(y_net))
    
    # Footer
    pdf.set_y(-25)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Generated via Creator Earnings Calc - For Information Purposes Only", align="C")
    
    return bytes(pdf.output())

# --- DOWNLOAD LOGIC ---
st.divider()
if st.button("Prepare Final Report"):
    with st.spinner("Processing..."):
        pdf_data = generate_pdf_bytes(
            creator_name, creator_user, subscribers, 
            sub_charge, platform_fee, net_monthly, annual_income
        )
        st.session_state['pdf_report'] = pdf_data
        st.success(f"✅ Report Ready for {creator_name}!")

if 'pdf_report' in st.session_state:
    st.download_button(
        label="📩 Download Report PDF",
        data=st.session_state['pdf_report'],
        file_name=f"{creator_name}_Earnings_Report.pdf",
        mime="application/pdf"
    )
