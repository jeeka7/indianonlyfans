import streamlit as st
from fpdf import FPDF

# --- PAGE CONFIG ---
st.set_page_config(page_title="Creator Earnings Calc", page_icon="💰")

# --- APP INTERFACE ---
st.title("🇮🇳 Creator Earnings Calculator")

# 1. Creator Details
st.subheader("Profile Information")
c1, c2 = st.columns(2)
with c1:
    creator_name = st.text_input("Name of the Creator", placeholder="e.g. Ananya Rao")
with c2:
    creator_user = st.text_input("Username", placeholder="e.g. @ananya_creations")

# 2. Earnings Inputs
st.divider()
col1, col2 = st.columns(2)
with col1:
    subscribers = st.number_input("Total Subscribers", min_value=0, value=100)
    sub_charge = st.number_input("Monthly Charge (₹)", min_value=0, value=290)
with col2:
    platform_fee = st.slider("Platform Commission (%)", 0, 50, 20)

# --- CALCULATIONS ---
gross_monthly = subscribers * sub_charge
net_monthly = gross_monthly * (1 - (platform_fee / 100))
annual_income = net_monthly * 12

# --- DISPLAY BIG METRIC ---
st.divider()
st.metric(label="📊 TOTAL ESTIMATED ANNUAL INCOME", value=f"₹{int(annual_income):,}")

# --- PDF GENERATION (FIXED FOR FPDF2) ---
def generate_pdf_bytes(name, user, subs, charge, fee, m_net, y_net):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 20, "EARNINGS REPORT", ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 14)
    pdf.ln(10)
    pdf.cell(0, 10, f"Creator: {name} ({user})", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Report Body
    pdf.cell(100, 10, "Total Subscribers:", 0)
    pdf.cell(0, 10, f"{subs:,}", 0, ln=True)
    
    pdf.cell(100, 10, "Subscription Price:", 0)
    pdf.cell(0, 10, f"Rs. {charge}", 0, ln=True)
    
    pdf.cell(100, 10, "Platform Fee:", 0)
    pdf.cell(0, 10, f"{fee}%", 0, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(100, 10, "Net Monthly Income:", 0)
    pdf.cell(0, 10, f"Rs. {int(m_net):,}", 0, ln=True)
    
    pdf.set_text_color(30, 144, 255) # Blue for the big number
    pdf.cell(100, 10, "ESTIMATED ANNUAL INCOME:", 0)
    pdf.cell(0, 10, f"Rs. {int(y_net):,}", 0, ln=True)
    
    # Return raw bytes
    return pdf.output()

# --- DOWNLOAD LOGIC ---
st.write("### Generate Download")
if st.button("Generate Final Report"):
    if creator_name:
        report_bytes = generate_pdf_bytes(creator_name, creator_user, subscribers, sub_charge, platform_fee, net_monthly, annual_income)
        
        # We use a unique key to ensure Streamlit handles the state correctly
        st.download_button(
            label="📩 Download PDF Report",
            data=report_bytes,
            file_name=f"{creator_name}_Earnings.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please enter a name to generate the report.")
