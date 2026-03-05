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

# --- CONFIGURATIE ---
st.set_page_config(page_title="StockConsultant Pro Dashboard", layout="wide")

@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def get_detailed_stock_data(driver, symbol):
    """Haalt Score, Sentiment, Support, Resistance en Trade Quality op."""
    url = f"https://www.stockconsultant.com/consultnow/basicplus.cgi?symbol={symbol}&extot=1&searcht=1&srng=0,10&charts=1&fselect=sscroll#lsearch"
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(6) # Genoeg tijd voor de CGI scripts en tabellen
        
        full_text = driver.find_element(By.TAG_NAME, "body").text
        
        # --- DATA EXTRACTIE LOGICA ---
        
        # 1. Score (Meestal Technical Score)
        score = "N/A"
        score_match = re.search(r"Score[:\s]*(\d+\.?\d*)", full_text, re.IGNORECASE)
        if score_match: score = score_match.group(1)

        # 2. Trade Quality (Vaak aangeduid als 'Quality' of 'Trade Quality')
        quality = "N/A"
        quality_match = re.search(r"Quality[:\s]*(\d+\.?\d*)", full_text, re.IGNORECASE)
        if quality_match: quality = quality_match.group(1)

        # 3. Sentiment
        sentiment = "Neutral"
        if "BULLISH" in full_text.upper(): sentiment = "Bullish 📈"
        elif "BEARISH" in full_text.upper(): sentiment = "Bearish 📉"

        # 4. Support & Resistance
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

# --- UI DASHBOARD ---
st.title("🚀 Advanced Stock Scanner")
st.markdown("Analyseer Score, Trade Quality en Prijsniveaus van StockConsultant.")

input_symbols = st.text_input("Voer symbolen in (scheid met komma's):", "PAYO, TSLA, AAPL")
symbol_list = [s.strip().upper() for s in input_symbols.split(",") if s.strip()]

if st.button("Start Volledige Analyse"):
    driver = get_driver()
    all_results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, sym in enumerate(symbol_list):
        status_text.text(f"Bezig met scannen van {sym}...")
        data = get_detailed_stock_data(driver, sym)
        all_results.append(data)
        progress_bar.progress((idx + 1) / len(symbol_list))
    
    status_text.text("Analyse voltooid!")
    
    # DataFrame maken
    df = pd.DataFrame(all_results)
    st.divider()
    
    # Tabel tonen met interactieve functies
    st.subheader("Overzicht Marktan


