import streamlit as st
from fpdf import FPDF

# --- REFRESHED PDF FUNCTION ---
def generate_pdf_bytes(name, user, subs, charge, fee, m_net, y_net):
    # Initialize PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 20, "EARNINGS REPORT", ln=True, align="C")
    
    # Creator Info
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Creator Name: {name}", ln=True)
    pdf.cell(0, 10, f"Username: {user}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Data Table
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(100, 10, "Metric", border=1)
    pdf.cell(0, 10, "Value", border=1, ln=True)
    
    pdf.set_font("Helvetica", "", 12)
    stats = [
        ("Subscribers", f"{subs:,}"),
        ("Monthly Charge", f"INR {charge}"),
        ("Platform Fee", f"{fee}%"),
        ("Monthly Net", f"INR {int(m_net):,}"),
        ("Annual Net", f"INR {int(y_net):,}")
    ]
    
    for label, val in stats:
        pdf.cell(100, 10, label, border=1)
        pdf.cell(0, 10, val, border=1, ln=True)
    
    # IMPORTANT: Returning output as bytes
    # In fpdf2, .output() with no arguments returns the byte-string directly.
    return bytes(pdf.output())

# --- BUTTON LOGIC ---
if st.button("Prepare PDF for Download"):
    if creator_name:
        # Generate the data
        final_pdf = generate_pdf_bytes(creator_name, creator_user, subscribers, sub_charge, platform_fee, net_monthly, annual_income)
        
        # Store in session state so it persists during the button click for download
        st.session_state['pdf_report'] = final_pdf
        st.success("✅ Report Ready!")
    else:
        st.error("Please enter a name first.")

# Show download button ONLY if PDF exists in session state
if 'pdf_report' in st.session_state:
    st.download_button(
        label="📩 Download Report Now",
        data=st.session_state['pdf_report'],
        file_name=f"{creator_name}_Earnings.pdf",
        mime="application/pdf"
    )
