import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import pandas as pd

# --- PAGINA CONFIG ---
st.set_page_config(page_title="Stock Scanner Pro", layout="wide")

# --- DE VERBETERDE BROWSER SETUP ---
@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # We laten Selenium zelf de driver koppelen aan de browser in /usr/bin/chromium
    # Dit voorkomt de SessionNotCreatedException
    try:
        service = Service() # Selenium 4.x vindt de driver nu vaak zelf op Linux
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception:
        # Backup plan voor specifieke Linux paden
        options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=options)

def scrape_stock(driver, symbol):
    url = f"https://www.stockconsultant.com/consultnow/basicplus.cgi?symbol={symbol}&extot=1&searcht=1&srng=0,10&charts=1&fselect=sscroll#lsearch"
    try:
        driver.get(url)
        time.sleep(6) # CGI sites hebben tijd nodig
        
        body_text = driver.find_element("tag name", "body").text
        
        # Extractie data
        score = re.search(r"Score[:\s]*(\d+\.?\d*)", body_text, re.IGNORECASE)
        quality = re.search(r"Quality[:\s]*(\d+\.?\d*)", body_text, re.IGNORECASE)
        support = re.search(r"support\s+(?:at|is)\s+([\d\.]+)", body_text, re.IGNORECASE)
        resistance = re.search(r"resistance\s+(?:at|is)\s+([\d\.]+)", body_text, re.IGNORECASE)
        
        sentiment = "Neutral"
        if "BULLISH" in body_text.upper(): sentiment = "Bullish 📈"
        elif "BEARISH" in body_text.upper(): sentiment = "Bearish 📉"
        
        return {
            "Symbool": symbol,
            "Score": score.group(1) if score else "N/A",
            "Trade Quality": quality.group(1) if quality else "N/A",
            "Sentiment": sentiment,
            "Support": support.group(1) if support else "N/A",
            "Resistance": resistance.group(1) if resistance else "N/A"
        }
    except Exception as e:
        return {"Symbool": symbol, "Score": "N/A", "Trade Quality": "Error", "Sentiment": "Error", "Support": "-", "Resistance": "-"}

# --- UI ---
st.title("📊 StockConsultant Advanced Scanner")

input_symbols = st.text_input("Vul symbolen in (bijv. PAYO, TSLA):", "PAYO")
symbol_list = [s.strip().upper() for s in input_symbols.split(",") if s.strip()]

if st.button("Start Scan"):
    if symbol_list:
        with st.spinner("Browser opstarten en data ophalen..."):
            try:
                driver = get_driver()
                results = []
                progress = st.progress(0)
                
                for i, sym in enumerate(symbol_list):
                    st.write(f"Scannen van {sym}...")
                    data = scrape_stock(driver, sym)
                    results.append(data)
                    progress.progress((i + 1) / len(symbol_list))
                
                df = pd.DataFrame(results)
                
                # Automatisch sorteren op Trade Quality (hoogste eerst)
                df['Trade Quality'] = pd.to_numeric(df['Trade Quality'], errors='coerce')
                df = df.sort_values(by="Trade Quality", ascending=False)

                st.success("Scan voltooid!")
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, "stock_data.csv", "text/csv")
                
            except Exception as e:
                st.error(f"Fout bij opstarten browser: {e}")
    else:
        st.warning("Voer eerst een symbool in.")

