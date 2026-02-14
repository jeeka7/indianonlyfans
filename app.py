import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(page_title="Indian Creator Earnings Calc", page_icon="📈", layout="centered")

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #1f77b4; }
    .stSelectbox label, .stNumberInput label { font-weight: bold; color: #444; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("💰 Creator Earnings Calc (India)")
st.caption("Estimate take-home pay for Indian Influencers & Subscription Creators.")
st.divider()

# --- INPUT SECTION ---
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        subscribers = st.number_input("Subscribers", min_value=0, value=100, step=10)
        sub_charge = st.number_input("Monthly Charge (₹)", min_value=0, value=290, step=10)
    
    with col2:
        # Based on your research: Web vs App Store vs Small Business
        platform_type = st.selectbox(
            "Platform / Payment Method",
            options=["Web-based (OnlyFans/Fanvue)", "App Store (Small Business/Instagram)", "App Store (Standard 30%)", "Custom %"],
            help="Small Business programs (Apple/Google) usually charge 15% for creators earning under $1M."
        )
        
        if platform_type == "Web-based (OnlyFans/Fanvue)":
            commission_pct = 20
        elif platform_type == "App Store (Small Business/Instagram)":
            commission_pct = 15
        elif platform_type == "App Store (Standard 30%)":
            commission_pct = 30
        else:
            commission_pct = st.slider("Custom Commission (%)", 0, 50, 20)

# --- CALCULATIONS ---
gross_revenue = subscribers * sub_charge
commission_amt = (commission_pct / 100) * gross_revenue
net_earnings = gross_revenue - commission_amt

# --- RESULTS ---
st.subheader("Monthly Revenue Summary")

res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric("Gross Revenue", f"₹{gross_revenue:,}")
res_col2.metric("Fees ({commission_pct}%)", f"-₹{int(commission_amt):,}", delta_color="inverse")
res_col3.metric("Net Take-home", f"₹{int(net_earnings):,}")

# --- ANALYTICS & INSIGHTS ---
st.divider()

if net_earnings > 0:
    # Adding a yearly projection
    yearly_net = net_earnings * 12
    st.success(f"📅 **Annual Net Income:** ₹{int(yearly_net):,}")
    
    # Pro-tip based on your input about "Alternative Payment Methods"
    if commission_pct >= 30:
        st.warning("💡 **Pro-Tip:** High App Store fees are eating your margins. Encourage fans to subscribe via your **Website** to save ~15-20% on fees.")
    elif commission_pct == 15:
        st.info("✅ You are likely using the **Small Business Program** or Instagram Subscriptions rate.")

    # Visual Comparison Table
    with st.expander("Comparison: Web vs. App Store"):
        web_net = gross_revenue * 0.80
        app_net = gross_revenue * 0.70
        st.write(f"**Net via Web (20% fee):** ₹{int(web_net):,}")
        st.write(f"**Net via App Store (30% fee):** ₹{int(app_net):,}")
        st.write(f"**Potential Monthly Savings:** ₹{int(web_net - app_net):,}")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "Calculations based on 2026 Platform Policies. Not financial advice."
    "</div>", 
    unsafe_allow_html=True
)
