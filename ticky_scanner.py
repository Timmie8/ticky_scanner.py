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
st.set_page_config(page_title="Stock Scanner Pro", layout="wide")

@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # Vermom de bot als een echte browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def get_detailed_stock_data(driver, symbol):
    url = f"https://www.stockconsultant.com/consultnow/basicplus.cgi?symbol={symbol}&extot=1&searcht=1&srng=0,10&charts=1&fselect=sscroll#lsearch"
    
    try:
        # Stel een harde timeout in voor het laden van de pagina zelf
        driver.set_page_load_timeout(20)
        driver.get(url)
        
        # Wacht tot de body er is, maar maximaal 10 seconden
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Korte pauze voor de dynamische tabellen
        time.sleep(4) 
        
        full_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Data Extractie met Regex
        score = re.search(r"(?:Score|Technical Score)[:\s]*(\d+\.?\d*)", full_text, re.IGNORECASE)
        quality = re.search(r"(?:Quality|Trade Quality)[:\s]*(\d+\.?\d*)", full_text, re.IGNORECASE)
        support = re.search(r"support\s+(?:at|is)\s+([\d\.]+)", full_text, re.IGNORECASE)
        resistance = re.search(r"resistance\s+(?:at|is)\s+([\d\.]+)", full_text, re.IGNORECASE)

        sentiment = "Neutral"
        if "BULLISH" in full_text.upper(): sentiment = "Bullish 📈"
        elif "BEARISH" in full_text.upper(): sentiment = "Bearish 📉"

        return {
            "Symbool": symbol,
            "Score": score.group(1) if score else "N/A",
            "Trade Quality": quality.group(1) if quality else "N/A",
            "Sentiment": sentiment,
            "Support": support.group(1) if support else "N/A",
            "Resistance": resistance.group(1) if resistance else "N/A"
        }
    except Exception as e:
        return {"Symbool": symbol, "Score": "Timeout/Error", "Trade Quality": "-", "Sentiment": "N/A", "Support": "-", "Resistance": "-"}

# --- UI ---
st.title("🛡️ StockConsultant Batch Analysis")

input_symbols = st.text_input("Voer symbolen in (gescheiden door komma):", "PAYO, TSLA")
symbol_list = [s.strip().upper() for s in input_symbols.split(",") if s.strip()]

if st.button("Start Analyse"):
    if not symbol_list:
        st.error("Voer eerst symbolen in.")
    else:
        driver = get_driver()
        all_results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, sym in enumerate(symbol_list):
            status_text.text(f"Scannen: {sym} ({idx+1}/{len(symbol_list)})...")
            data = get_detailed_stock_data(driver, sym)
            all_results.append(data)
            progress_bar.progress((idx + 1) / len(symbol_list))
        
        status_text.text("✅ Scan voltooid!")
        df = pd.DataFrame(all_results)
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "report.csv", "text/csv")
else:
    st.info("Wachtend op start...")

st.divider()
st.caption("Gebruik kleine batches (max 5-10) voor de beste snelheid op Streamlit Cloud.")
