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
st.title("Indian Onlyfans Earnings Calculator")

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

# --- UI HIGHLIGHTED BOXES ---
st.divider()
st.markdown("""
<style>
    .monthly-box { background-color: #e6f4ea; padding: 20px; border-radius: 10px; border-left: 5px solid #34a853; margin-bottom: 20px; }
    .annual-box { background-color: #e8f0fe; padding: 20px; border-radius: 10px; border-left: 5px solid #4285f4; margin-bottom: 20px; }
    .box-label { font-size: 14px; color: #555; font-weight: bold; margin-bottom: 5px; }
    .box-value { font-size: 32px; color: #000; font-weight: 800; }
    .box-words { font-size: 12px; color: #666; font-style: italic; }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="monthly-box"><div class="box-label">MONTHLY NET</div><div class="box-value">₹ {format_indian_currency(net_monthly)}</div><div class="box-words">{amount_to_words(net_monthly)}</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="annual-box"><div class="box-label">ANNUAL NET</div><div class="box-value">₹ {format_indian_currency(annual_income)}</div><div class="box-words">{amount_to_words(annual_income)}</div></div>', unsafe_allow_html=True)

# --- PDF GENERATION FUNCTION ---
def generate_pdf_bytes(name, user, subs, charge, fee, m_net, y_net):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 20, "EARNINGS ESTIMATION REPORT", ln=True, align="C")
    
    # Profile Info
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Creator: {name} ({user})", ln=True)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Detailed Breakdown Table
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(90, 10, "Component", border=1, fill=True)
    pdf.cell(90, 10, "Value", border=1, fill=True, ln=True)
    
    pdf.set_font("Helvetica", "", 12)
    items = [
        ("Subscribers", f"{subs:,}"),
        ("Subscription Price", f"Rs. {charge}"),
        ("Platform Fee", f"{fee}%")
    ]
    for label, val in items:
        pdf.cell(90, 10, label, border=1)
        pdf.cell(90, 10, val, border=1, ln=True)
    
    pdf.ln(15)

    # --- HIGHLIGHTED PDF SECTIONS ---
    # Monthly Highlight (Green Box)
    pdf.set_fill_color(230, 244, 234) # Light Green
    pdf.set_text_color(52, 168, 83)   # Green Text
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 12, "  ESTIMATED NET MONTHLY INCOME", ln=True, fill=True)
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 18, f"  Rs. {format_indian_currency(m_net)}", ln=True, fill=True)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, f"  ({amount_to_words(m_net)})", ln=True, fill=True)
    
    pdf.ln(10)
    
    # Annual Highlight (Blue Box)
    pdf.set_fill_color(232, 240, 254) # Light Blue
    pdf.set_text_color(66, 133, 244)  # Blue Text
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 12, "  ESTIMATED ANNUAL NET INCOME", ln=True, fill=True)
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 18, f"  Rs. {format_indian_currency(y_net)}", ln=True, fill=True)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, f"  ({amount_to_words(y_net)})", ln=True, fill=True)

    # Footer
    pdf.set_y(-25)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Generated via Indian Creator Earnings Calculator. For estimation only.", align="C")
    
    return bytes(pdf.output())

# --- DOWNLOAD LOGIC ---
st.divider()
if st.button("Prepare Professional PDF Report"):
    with st.spinner("Styling your Report..."):
        pdf_data = generate_pdf_bytes(creator_name, creator_user, subscribers, sub_charge, platform_fee, net_monthly, annual_income)
        st.session_state['pdf_report'] = pdf_data
        st.success("✅ Your high-visibility report is ready!")

if 'pdf_report' in st.session_state:
    st.download_button(label="📩 Download High-Visibility PDF", data=st.session_state['pdf_report'], file_name=f"{creator_name}_Earnings_Statement.pdf", mime="application/pdf")
