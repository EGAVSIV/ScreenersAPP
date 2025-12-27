import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

# ================= STREAMLIT CONFIG =================
st.set_page_config(
    page_title="Screener.in Multi Scanner",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Screener.in Multi-Scanner (No API)")
st.caption("Cookie-based | Fast | Reliable")

# ================= SCREENER LINKS =================
SCREENS = {
    "ROE > ROCE": "https://www.screener.in/screen/raw/?query=Return+on+equity+%3E+Return+on+capital+employed+",

    "Sales Growth 3Y > 5Y": "https://www.screener.in/screen/raw/?query=Sales+growth+3Years+%3E+Sales+growth+5Years+",

    "FII & DII Increasing (>1%)": "https://www.screener.in/screen/raw/?query=Change+in+FII+holding+%3E1%25+AND+Change+in+DII+holding+%3E1%25",

    "Low Public Holding (<10%)": "https://www.screener.in/screen/raw/?query=Public+holding+%3C+10%25+",

    "High Debt vs Market Cap": "https://www.screener.in/screen/raw/?query=Mkt+Cap+To+Debt+Cap+%3C1",

    "High Price to Book": "https://www.screener.in/screen/raw/?query=Price+to+book+value+%3E10.5%25",

    "High ROCE & ROE": "https://www.screener.in/screen/raw/?query=Return+on+capital+employed+%3E17%25+AND+Return+on+equity+%3E20%25",

    "EBITDA Growth Acceleration": "https://www.screener.in/screen/raw/?query=EBIDT+growth+3Years+%3E+EBIDT+growth+5Years+AND+EBIDT+growth+5Years+%3E+EBIDT+growth+7Years+"
}

# ================= SIDEBAR =================
with st.sidebar:
    st.header("🔐 Screener Login Cookies")

    sessionid = st.text_input("sessionid", type="password")
    csrftoken = st.text_input("csrftoken", type="password")

    st.markdown("---")
    scan_name = st.selectbox("📌 Select Scan", list(SCREENS.keys()))

    run = st.button("🔍 Run Scan")

# ================= FETCH FUNCTION =================
def fetch_screener(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
        "Referer": "https://www.screener.in/"
    }

    cookies = {
        "sessionid": sessionid,
        "csrftoken": csrftoken
    }

    all_dfs = []
    page = 1

    while True:
        paged_url = f"{url}&page={page}"
        r = requests.get(paged_url, headers=headers, cookies=cookies, timeout=15)

        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table")

        if table is None:
            break  # no more pages

        df = pd.read_html(str(table))[0]

        if df.empty:
            break

        all_dfs.append(df)
        page += 1

    if not all_dfs:
        return None

    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df = final_df.drop_duplicates()

    return final_df


# ================= RUN =================
if run:
    if not sessionid or not csrftoken:
        st.warning("⚠️ Please enter cookies")
    else:
        with st.spinner("Fetching Screener data..."):
            df = fetch_screener(SCREENS[scan_name])

        if df is None:
            st.error("❌ Failed to fetch data. Cookies expired or invalid.")
        else:
            st.success(f"✅ {len(df)} stocks found")

            st.subheader(f"📋 Scan: {scan_name}")
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV",
                csv,
                f"{scan_name.replace(' ', '_').lower()}.csv",
                "text/csv"
            )
