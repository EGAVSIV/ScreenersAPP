import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

# ================= STREAMLIT CONFIG =================
st.set_page_config(
    page_title="Screener.in PE vs Industry PE",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Screener.in Scanner")
st.subheader("Price to Earnings < Industry PE")

# ================= USER INPUT =================
with st.sidebar:
    st.header("🔐 Screener Cookies (One Time)")
    sessionid = st.text_input("sessionid", type="password")
    csrftoken = st.text_input("csrftoken", type="password")

    st.markdown("---")
    run = st.button("🔄 Fetch Data")

# ================= FETCH FUNCTION =================
def fetch_screener():
    url = (
        "https://www.screener.in/screen/raw/"
        "?query=Price+to+Earning+%3C+Industry+PE"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
        "Referer": "https://www.screener.in/",
    }

    cookies = {
        "sessionid": sessionid,
        "csrftoken": csrftoken
    }

    r = requests.get(url, headers=headers, cookies=cookies, timeout=15)

    if r.status_code != 200:
        st.error("❌ Failed to fetch data. Check cookies.")
        return None

    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find("table")

    if table is None:
        st.error("❌ Table not found. Cookies invalid or expired.")
        return None

    df = pd.read_html(str(table))[0]
    return df

# ================= RUN =================
if run:
    if not sessionid or not csrftoken:
        st.warning("⚠️ Please enter cookies")
    else:
        with st.spinner("Fetching Screener data..."):
            df = fetch_screener()

        if df is not None:
            st.success(f"✅ {len(df)} stocks fetched")

            st.dataframe(
                df,
                use_container_width=True
            )

            csv = df.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV",
                csv,
                "pe_less_than_industry_pe.csv",
                "text/csv"
            )
