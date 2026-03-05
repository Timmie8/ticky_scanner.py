import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import pandas as pd

# --- 1. PAGINA CONFIGURATIE (Altijd bovenaan) ---
st.set_page_config(page_title="StockConsultant Pro Dashboard", layout="wide")

# --- 2. BROWSER SETUP FUNCTIE ---
@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def get_detailed_stock_data(driver, symbol):
    """Haalt alle technische data op van StockConsultant."""
    url = f"https://www.stockconsultant.com/consultnow/basicplus.cgi?symbol={symbol}&extot=1&searcht=1&srng=0,10&charts=1&fselect=sscroll#lsearch"
    
    try:
        driver.get(url)
        # Wacht tot de pagina geladen is
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(6) 
        
        full_text = driver.find_element(By.TAG_NAME, "body").text
        
        # --- DATA EXTRACTIE ---
        # Score
        score = "N/A"
        score_match = re.search(r"(?:Score|Technical Score)[:\s]*(\d+\.?\d*)", full_text, re.IGNORECASE)
        if score_match: score = score_match.group(1)

        # Trade Quality
        quality = "N/A"
        quality_match = re.search(r"(?:Quality|Trade Quality)[:\s]*(\d+\.?\d*)", full_text, re.IGNORECASE)
        if quality_match: quality = quality_match.group(1)

        # Sentiment
        sentiment = "Neutral"
        if "BULLISH" in full_text.upper(): sentiment = "Bullish 📈"
        elif "BEARISH" in full_text.upper(): sentiment = "Bearish 📉"

        # Support & Resistance
        support = "N/A"
        resistance = "N/A"
        sup_match = re.search(r"support\s+(?:at|is)\s+([\d\.]+)", full_text, re.IGNORECASE)
        res_match = re.search(r"resistance\s+(?:at|is)\s+([\d\.]+)", full_text, re.IGNORECASE)
        if sup_match: support = sup_match.group(1)
        if res_match: resistance = res_match.group(1)

        return {
            "Symbool": symbol,
            "Score": score,
            "Trade Quality": quality,
            "Sentiment": sentiment,
            "Support": support,
            "Resistance": resistance
        }
    except Exception as e:
        return {"Symbool": symbol, "Score": "Error", "Trade Quality": "Error", "Sentiment": "Error", "Support": "-", "Resistance": "-"}

# --- 3. UI DASHBOARD (Zichtbare gedeelte) ---
st.title("🚀 Stock Analysis Dashboard")
st.markdown("Vul hieronder de symbolen in die je wilt analyseren.")

# HET INVOERVELD (Nu gegarandeerd zichtbaar)
input_symbols = st.text_input("Aandelen (bijv: PAYO, TSLA, NVDA):", "PAYO")
symbol_list = [s.strip().upper() for s in input_symbols.split(",") if s.strip()]

# De Analyse Knop
if st.button("Start Analyse"):
    if not symbol_list:
        st.warning("Voer a.u.b. minimaal één symbool in.")
    else:
        driver = get_driver()
        all_results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, sym in enumerate(symbol_list):
            status_text.text(f"Bezig met scannen van {sym}...")
            data = get_detailed_stock_data(driver, sym)
            all_results.append(data)
            progress_bar.progress((idx + 1) / len(symbol_list))
        
        status_text.text("✅ Klaar! Resultaten staan hieronder.")
        
        # Resultaten in Tabel
        df = pd.DataFrame(all_results)
        st.divider()
        st.subheader("Marktanalyse Overzicht")
        st.dataframe(df, use_container_width=True)

        # Download Knop
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download als CSV", csv, "stock_report.csv", "text/csv")
else:
    st.info("Klik op de knop om de gegevens van StockConsultant op te halen.")

st.divider()
st.caption("Draait op Selenium/Chromium via Streamlit Cloud.")
