import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import pandas as pd

# --- CONFIGURATIE ---
st.set_page_config(page_title="StockConsultant Dashboard", layout="wide")

@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def scrape_stock_data(driver, symbol):
    """Haalt de data op van StockConsultant voor een specifiek symbool."""
    url = f"https://www.stockconsultant.com/consultnow/basicplus.cgi?symbol={symbol}&extot=1&searcht=1&srng=0,10&charts=1&fselect=sscroll#lsearch"
    
    try:
        driver.get(url)
        time.sleep(4) # Wacht op het laden van de rapporten
        
        page_text = driver.find_element("tag name", "body").text
        
        # We zoeken naar veelvoorkomende patronen op StockConsultant
        # Score extractie: we zoeken naar getallen in de buurt van 'Score' of 'Rating'
        score_match = re.search(r"(?:Score|Rating|Strength):\s*(\d+\.?\d*)", page_text, re.IGNORECASE)
        score = score_match.group(1) if score_match else "N/A"
        
        # Sentiment extractie (Bullish / Bearish)
        sentiment = "Neutral"
        if "Bullish" in page_text: sentiment = "Bullish 📈"
        if "Bearish" in page_text: sentiment = "Bearish 📉"
        
        return {
            "Symbool": symbol,
            "Score": score,
            "Sentiment": sentiment,
            "Status": "Succes"
        }
    except Exception as e:
        return {"Symbool": symbol, "Score": "Error", "Sentiment": "Error", "Status": f"Fout: {str(e)[:30]}"}

# --- UI ---
st.title("📊 Multi-Stock Consultant Dashboard")
st.markdown("Voer meerdere symbolen in om ze tegelijkertijd te scannen.")

# Input voor meerdere aandelen
input_symbols = st.text_input("Voer symbolen in (bijv: PAYO, TSLA, NVDA):", "PAYO")
symbols = [s.strip().upper() for s in input_symbols.split(",") if s.strip()]

if st.button("Start Batch Scan"):
    driver = get_driver()
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, sym in enumerate(symbols):
        status_text.text(f"Bezig met scannen van {sym} ({i+1}/{len(symbols)})...")
        data = scrape_stock_data(driver, sym)
        results.append(data)
        progress_bar.progress((i + 1) / len(symbols))
    
    status_text.text("Scan voltooid!")
    
    # Maak een mooie tabel (DataFrame)
    df = pd.DataFrame(results)
    
    # Tonen van de resultaten in het dashboard
    st.divider()
    st.subheader("Overzicht Resultaten")
    
    # Styling van de tabel
    def color_sentiment(val):
        color = 'white'
        if 'Bullish' in str(val): color = '#00ff88'
        elif 'Bearish' in str(val): color = '#ff4b4b'
        return f'color: {color}'

    st.table(df.style.applymap(color_sentiment, subset=['Sentiment']))
    
    # Download knop voor Excel/CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download resultaten als CSV", csv, "stock_results.csv", "text/csv")

else:
    st.info("Klik op 'Start Batch Scan' om de gegevens op te halen.")

st.divider()
st.caption("Bron: StockConsultant BasicPlus | Gebouwd met Selenium & Streamlit")
