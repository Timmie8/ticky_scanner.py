import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# --- CONFIGURATIE ---
st.set_page_config(page_title="StockConsultant Pro Scanner", layout="wide")

@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def get_stock_data(driver, symbol):
    """Haalt gericht data op uit de tabellen van StockConsultant."""
    url = f"https://www.stockconsultant.com/consultnow/basicplus.cgi?symbol={symbol}&extot=1&searcht=1&srng=0,10&charts=1&fselect=sscroll#lsearch"
    
    try:
        driver.get(url)
        # Wacht maximaal 10 seconden tot de body geladen is
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5) # Extra tijd voor de CGI scripts van de site
        
        full_text = driver.find_element(By.TAG_NAME, "body").text
        
        # We zoeken naar specifieke trefwoorden in de tekst
        # StockConsultant gebruikt vaak 'Technical Score' of 'Breakout Score'
        score = "N/A"
        if "Score" in full_text:
            # We pakken een stukje tekst rondom het woord Score
            parts = full_text.split("Score")
            if len(parts) > 1:
                # Pak de eerste 10 karakters na 'Score' en filter het getal eruit
                score_chunk = parts[1][:10]
                import re
                nums = re.findall(r"(\d+\.?\d*)", score_chunk)
                score = nums[0] if nums else "N/A"

        # Sentiment bepaling
        sentiment = "Neutral"
        if "BULLISH" in full_text.upper(): sentiment = "Bullish 📈"
        if "BEARISH" in full_text.upper(): sentiment = "Bearish 📉"

        return {
            "Symbool": symbol,
            "Score": score,
            "Sentiment": sentiment,
            "Link": url
        }
    except Exception as e:
        return {"Symbool": symbol, "Score": "Fout", "Sentiment": str(e)[:20], "Link": url}

# --- UI ---
st.title("🚀 StockConsultant Batch Scanner")
st.write("Voer de symbolen in die je wilt controleren.")

input_symbols = st.text_input("Symbolen (scheid met komma's):", "PAYO, TSLA, AAPL")
symbol_list = [s.strip().upper() for s in input_symbols.split(",") if s.strip()]

if st.button("Start Analyse"):
    driver = get_driver()
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, sym in enumerate(symbol_list):
        status_text.text(f"Bezig met ophalen van {sym}...")
        data = get_stock_data(driver, sym)
        results.append(data)
        progress_bar.progress((idx + 1) / len(symbol_list))
    
    status_text.text("Scan voltooid!")
    
    # Resultaten tonen
    df = pd.DataFrame(results)
    st.divider()
    
    # Tabel met styling
    st.dataframe(df, use_container_width=True)
    
    # Download optie
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download als CSV", csv, "stocks.csv", "text/csv")
else:
    st.info("Vul symbolen in en klik op de knop.")

st.divider()
st.caption("Opmerking: Deze tool werkt het beste als de symbolen correct zijn gespeld.")

