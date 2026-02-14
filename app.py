import streamlit as st
from fpdf import FPDF
from num2words import num2words
import re
import libsql_client

# --- DATABASE CONNECTION ---
def get_db_client():
    # These should be set in Streamlit Secrets
    url = st.secrets["TURSO_DATABASE_URL"]
    token = st.secrets["TURSO_AUTH_TOKEN"]
    return libsql_client.create_client_sync(url=url, auth_token=token)

def format_indian_currency(number):
    s = str(int(number))
    if len(s) <= 3: return s
    last_three = s[-3:]
    remaining = s[:-3]
    remaining = re.sub(r'(\d+?)(?=(\d{2})+$)', r'\1,', remaining)
    return f"{remaining},{last_three}"

def amount_to_words(number):
    try:
        words = num2words(int(number), lang='en_IN').title()
        return f"{words} Rupees Only"
    except: return ""

# --- NAVIGATION ---
st.sidebar.title("Creator Hub")
page = st.sidebar.radio("Go to", ["Earnings Calculator", "Featured Creators"])

# ==========================================
# PAGE 1: EARNINGS CALCULATOR
# ==========================================
if page == "Earnings Calculator":
    st.title("🇮🇳 Creator Earnings Calculator")
    
    # Creator Details Section
    st.subheader("Profile Information (Optional)")
    c1, c2 = st.columns(2)
    with c1:
        raw_name = st.text_input("Full Name", placeholder="Default: XYZ")
    with c2:
        raw_user = st.text_input("Platform Username", placeholder="Default: XYZ")

    creator_name = raw_name if raw_name.strip() != "" else "XYZ"
    creator_user = raw_user if raw_user.strip() != "" else "XYZ"

    # Earnings Inputs
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        subscribers = st.number_input("Total Subscribers", min_value=0, value=100)
        sub_charge = st.number_input("Monthly Charge (₹)", min_value=0, value=290)
    with col2:
        platform_fee = st.slider("Platform Commission (%)", 0, 50, 20)

    # Calculations
    gross_monthly = subscribers * sub_charge
    net_monthly = gross_monthly * (1 - (platform_fee / 100))
    annual_income = net_monthly * 12

    # UI Highlight Boxes
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

    # PDF Logic (Simplified for brevity)
    def generate_pdf_bytes(name, user, m_net, y_net):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 20, "EARNINGS REPORT", ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Creator: {name} ({user})", ln=True)
        pdf.ln(10)
        # Monthly
        pdf.set_fill_color(230, 244, 234)
        pdf.cell(0, 20, f" Monthly: Rs. {format_indian_currency(m_net)}", fill=True, ln=True)
        # Annual
        pdf.set_fill_color(232, 240, 254)
        pdf.cell(0, 20, f" Annual: Rs. {format_indian_currency(y_net)}", fill=True, ln=True)
        return bytes(pdf.output())

    if st.button("Prepare PDF"):
        st.session_state['pdf_report'] = generate_pdf_bytes(creator_name, creator_user, net_monthly, annual_income)
        st.success("Report Ready!")

    if 'pdf_report' in st.session_state:
        st.download_button("Download PDF", st.session_state['pdf_report'], f"{creator_name}_Earnings.pdf")

# ==========================================
# PAGE 2: FEATURED CREATORS (Turso DB)
# ==========================================
elif page == "Featured Creators":
    st.title("🌟 Featured Indian Creators")
    st.write("Want to get listed and boost your reach? Contact us for pricing!")
    
    db = get_db_client()

    # Admin: Add New Creator
    with st.expander("➕ Add Featured Creator (Admin Only)"):
        new_name = st.text_input("Name")
        new_subs = st.text_input("Followers (e.g. 1.2M)")
        new_link = st.text_input("Insta Link")
        if st.button("Save to Database"):
            if new_name and new_link:
                db.execute("INSERT INTO featured_creators (name, subs, insta_link) VALUES (?, ?, ?)", 
                           (new_name, new_subs, new_link))
                st.success(f"Successfully listed {new_name}!")
                st.rerun()

    st.divider()

    # Fetch and Display Creators
    res = db.execute("SELECT name, subs, insta_link FROM featured_creators WHERE is_active = 1 ORDER BY id DESC")
    
    for row in res.rows:
        with st.container():
            c_info, c_action = st.columns([3, 1])
            with c_info:
                st.subheader(row[0])
                st.write(f"📊 {row[1]} Followers")
            with c_action:
                st.link_button("Profile", row[2])
            st.divider()

    st.info("💎 **Boost Your Visibility:** Contact `jktechservices@ybl` to be featured on this page.")
