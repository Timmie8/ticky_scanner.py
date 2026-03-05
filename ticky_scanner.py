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
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def get_detailed_stock_data(driver, symbol):
    """Haalt Score, Trade Quality, Sentiment, Support en Resistance op."""
    url = f"https://www.stockconsultant.com/consultnow/basicplus.cgi?symbol={symbol}&extot=1&searcht=1&srng=0,10&charts=1&fselect=sscroll#lsearch"
    
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(6) # Cruciaal voor het laden van de CGI rapporten
        
        full_text = driver.find_element(By.TAG_NAME, "body").text
        
        # --- DATA EXTRACTIE ---
        
        # 1. Technical Score (0-100 of 0-10)
        score = "N/A"
        score_match = re.search(r"(?:Technical Score|Score)[:\s]*(\d+\.?\d*)", full_text, re.IGNORECASE)
        if score_match: score = score_match.group(1)

        # 2. Trade Quality
        quality = "N/A"
        quality_match = re.search(r"(?:Trade Quality|Quality)[:\s]*(\d+\.?\d*)", full_text, re.IGNORECASE)
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
st.markdown("Analyseer de technische staat van je aandelen via StockConsultant.")

#


