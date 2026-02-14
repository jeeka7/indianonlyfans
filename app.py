import streamlit as st
from fpdf import FPDF
from num2words import num2words
import re
import libsql_client

# --- PAGE CONFIG ---
st.set_page_config(page_title="Creator Hub India", page_icon="💰", layout="centered")

# --- DATABASE CONNECTION ---
def get_db_client():
    url = st.secrets["TURSO_DATABASE_URL"]
    token = st.secrets["TURSO_AUTH_TOKEN"]
    return libsql_client.create_client_sync(url=url, auth_token=token)

# --- FORMATTERS ---
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
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Earnings Calculator", "Featured Creators"])

# ==========================================
# PAGE 1: EARNINGS CALCULATOR
# ==========================================
if page == "Earnings Calculator":
    st.title("🇮🇳 Creator Earnings Calculator")
    
    # Optional Inputs
    st.subheader("Profile Information (Optional)")
    c1, c2 = st.columns(2)
    with c1:
        raw_name = st.text_input("Full Name", placeholder="Default: XYZ")
    with c2:
        raw_user = st.text_input("Platform Username", placeholder="Default: XYZ")

    creator_name = raw_name if raw_name.strip() != "" else "XYZ"
    creator_user = raw_user if raw_user.strip() != "" else "XYZ"

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        subscribers = st.number_input("Total Subscribers", min_value=0, value=100)
        sub_charge = st.number_input("Monthly Charge (₹)", min_value=0, value=290)
    with col2:
        platform_fee = st.slider("Platform Commission (%)", 0, 50, 20)

    # Calculations
    net_monthly = (subscribers * sub_charge) * (1 - (platform_fee / 100))
    annual_income = net_monthly * 12

    # High-Visibility UI
    st.markdown("""
    <style>
        .monthly-box { background-color: #e6f4ea; padding: 20px; border-radius: 10px; border-left: 5px solid #34a853; margin-bottom: 20px; }
        .annual-box { background-color: #e8f0fe; padding: 20px; border-radius: 10px; border-left: 5px solid #4285f4; margin-bottom: 20px; }
        .box-label { font-size: 14px; color: #555; font-weight: bold; }
        .box-value { font-size: 32px; color: #000; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="monthly-box"><div class="box-label">MONTHLY NET</div><div class="box-value">₹ {format_indian_currency(net_monthly)}</div><div>{amount_to_words(net_monthly)}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="annual-box"><div class="box-label">ANNUAL NET</div><div class="box-value">₹ {format_indian_currency(annual_income)}</div><div>{amount_to_words(annual_income)}</div></div>', unsafe_allow_html=True)

    # PDF Logic
    if st.button("Prepare PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 20, "EARNINGS REPORT", ln=True, align="C")
        pdf.set_fill_color(230, 244, 234)
        pdf.cell(0, 20, f" Monthly: Rs. {format_indian_currency(net_monthly)}", fill=True, ln=True)
        pdf.set_fill_color(232, 240, 254)
        pdf.cell(0, 20, f" Annual: Rs. {format_indian_currency(annual_income)}", fill=True, ln=True)
        st.session_state['pdf_report'] = bytes(pdf.output())
        st.success("✅ PDF Ready!")

    if 'pdf_report' in st.session_state:
        st.download_button("📩 Download PDF", st.session_state['pdf_report'], f"{creator_name}_Earnings.pdf")

# ==========================================
# PAGE 2: FEATURED CREATORS
# ==========================================
elif page == "Featured Creators":
    st.title("🌟 Featured Indian Creators")
    
    # --- ADMIN LOGIN SECTION ---
    st.sidebar.divider()
    st.sidebar.subheader("Admin Login")
    admin_password = st.sidebar.text_input("Enter Admin Password", type="password")
    
    is_admin = admin_password == st.secrets["ADMIN_PASSWORD"]

    try:
        client = get_db_client()

        if is_admin:
            st.success("Admin Mode Active")
            with st.expander("➕ Add New Featured Creator"):
                new_name = st.text_input("Name")
                new_subs = st.text_input("Followers (e.g. 1.2M)")
                new_link = st.text_input("Insta Link")
                if st.button("Save to Database"):
                    if new_name and new_link:
                        client.execute("INSERT INTO featured_creators (name, subs, insta_link) VALUES (?, ?, ?)", 
                                    (new_name, new_subs, new_link))
                        st.success(f"Added {new_name}!")
                        st.rerun()
        else:
            if admin_password != "":
                st.sidebar.error("Incorrect Password")

        st.divider()

        # FETCH DATA
        res = client.execute("SELECT name, subs, insta_link FROM featured_creators WHERE is_active = 1 ORDER BY id DESC")
        
        if len(res.rows) == 0:
            st.info("No creators featured yet.")
        else:
            for row in res.rows:
                c_info, c_action = st.columns([3, 1])
                with c_info:
                    st.subheader(row[0])
                    st.write(f"📊 {row[1]} Followers")
                with c_action:
                    st.link_button("Profile", row[2])
                st.divider()
        
        client.close()

    except Exception as e:
        st.error(f"Database Error: {e}")
        st.info("If this is a new DB, ensure you created the 'featured_creators' table first.")
