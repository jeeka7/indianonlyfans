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
page = st.sidebar.radio("Navigation", ["Earnings Calculator", "Featured Creators", "Support Development"])

# --- ADMIN LOGIN (SIDEBAR) ---
st.sidebar.divider()
admin_pass = st.sidebar.text_input("Admin Password", type="password")
is_admin = admin_pass == st.secrets["ADMIN_PASSWORD"]

# ==========================================
# PAGE 1: EARNINGS CALCULATOR
# ==========================================
if page == "Earnings Calculator":
    st.title("🇮🇳 Creator Earnings Calculator")
    
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
        subscribers = st.number_input("Total Subscribers", min_value=0, value=100, step=10)
        sub_charge = st.number_input("Monthly Charge (₹)", min_value=0, value=290, step=10)
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

    # PDF Report Logic
    if st.button("Prepare Professional PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 20, "EARNINGS ESTIMATION REPORT", ln=True, align="C")
        
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Creator: {creator_name} ({creator_user})", ln=True)
        pdf.ln(10)
        
        pdf.set_fill_color(230, 244, 234)
        pdf.cell(0, 20, f"  Monthly Net: Rs. {format_indian_currency(net_monthly)}", fill=True, ln=True)
        pdf.set_fill_color(232, 240, 254)
        pdf.cell(0, 20, f"  Annual Net: Rs. {format_indian_currency(annual_income)}", fill=True, ln=True)
        
        st.session_state['pdf_report'] = bytes(pdf.output())
        st.success("✅ Report Ready!")

    if 'pdf_report' in st.session_state:
        st.download_button("📩 Download PDF", st.session_state['pdf_report'], f"{creator_name}_Earnings.pdf")

# ==========================================
# PAGE 2: FEATURED CREATORS
# ==========================================
elif page == "Featured Creators":
    st.title("🌟 Featured Indian Creators")
    
    try:
        client = get_db_client()

        if is_admin:
            st.sidebar.success("Logged in as Admin")
            with st.expander("➕ Add New Featured Creator"):
                new_name = st.text_input("Name")
                new_subs = st.text_input("Followers (e.g. 1.2M)")
                new_link = st.text_input("Insta Link")
                if st.button("Save Creator"):
                    client.execute("INSERT INTO featured_creators (name, subs, insta_link) VALUES (?, ?, ?)", 
                                 (new_name, new_subs, new_link))
                    st.success("Creator Added!")
                    st.rerun()

        # FETCH DATA
        res = client.execute("SELECT id, name, subs, insta_link FROM featured_creators WHERE is_active = 1 ORDER BY id DESC")
        
        if len(res.rows) == 0:
            st.info("No creators featured yet.")
        else:
            for row in res.rows:
                cid, name, subs, link = row
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    st.subheader(name)
                    st.write(f"📊 {subs} Followers | [Instagram]({link})")
                
                if is_admin:
                    with col_del:
                        if st.button("🗑️", key=f"del_{cid}"):
                            client.execute("DELETE FROM featured_creators WHERE id = ?", (cid,))
                            st.warning(f"Deleted {name}")
                            st.rerun()
                st.divider()
        client.close()
    except Exception as e:
        st.error(f"Database Error: {e}")

# ==========================================
# PAGE 3: SUPPORT DEVELOPMENT
# ==========================================
elif page == "Support Development":
    st.title("❤️ Support & Feature Requests")
    st.write("Support the development of this tool or pay to get featured on the main list.")
    
    upi_id = "jktechservices@ybl"
    name = "JK TECH AND SERVICES"
    upi_link = f"upi://pay?pa={upi_id}&pn={name.replace(' ', '%20')}&cu=INR"

    st.subheader("1. Instant Payment (Mobile Only)")
    st.markdown(f'''
        <a href="{upi_link}" style="text-decoration:none;">
            <button style="background-color:#673ab7; color:white; border:none; padding:15px; border-radius:8px; width:100%; font-weight:bold; cursor:pointer;">
                🚀 Open GPay / PhonePe / Paytm
            </button>
        </a>
    ''', unsafe_allow_html=True)
    st.caption("Works only if you have a UPI app installed on your phone.")

    st.divider()

    st.subheader("2. Scan QR Code")
    try:
        st.image("phonepeQR.jpg", caption="Scan to Pay / Support", width=350)
    except:
        st.warning("QR Code image (phonepeQR.jpg) not found in repository.")

    st.info(f"💎 **Business Inquiries:** For featuring requests or custom app development, reach out at `{upi_id}`.")
