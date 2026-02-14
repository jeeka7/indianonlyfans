import streamlit as st
from fpdf import FPDF
from num2words import num2words
import re
import libsql_client
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="Creator Hub India", page_icon="💰", layout="centered")

# --- DATABASE CONNECTION ---
def get_db_client():
    url = st.secrets["TURSO_DATABASE_URL"]
    token = st.secrets["TURSO_AUTH_TOKEN"]
    return libsql_client.create_client_sync(url=url, auth_token=token)

# --- HELPER FUNCTIONS ---
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
    # ... (Keep existing calculator code here) ...

# ==========================================
# PAGE 2: FEATURED CREATORS (With Delete)
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
# PAGE 3: SUPPORT DEVELOPMENT (UPI Intent)
# ==========================================
elif page == "Support Development":
    st.title("❤️ Support the Development")
    st.write("If you find this app helpful, consider supporting the developer or pay to get featured.")
    
    # UPI Link details
    upi_id = "jktechservices@ybl"
    name = "JK TECH AND SERVICES"
    
    # UPI Intent Link (This opens GPay/PhonePe on Mobile)
    upi_link = f"upi://pay?pa={upi_id}&pn={name.replace(' ', '%20')}&cu=INR"

    st.subheader("1. Pay via Mobile App")
    st.markdown(f'<a href="{upi_link}" style="text-decoration:none;"><button style="background-color:#673ab7; color:white; border:none; padding:15px 32px; text-align:center; font-size:16px; border-radius:8px; cursor:pointer; width:100%;">Open UPI App (GPay/PhonePe)</button></a>', unsafe_allow_html=True)
    st.caption("Clicking this will automatically open Google Pay or PhonePe on your phone.")

    st.divider()

    st.subheader("2. Scan QR Code")
    st.image("phonepeQR.jpg", caption="Scan with any UPI App (PhonePe, GPay, Paytm)", width=350)

    st.info("💎 **Note:** After paying to get featured, please email your screenshot and profile link to `jktechservices@ybl`.")
