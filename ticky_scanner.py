import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import pandas as pd
import gc # Garbage Collector om geheugen vrij te maken

# --- CONFIGURATIE ---
st.set_page_config(page_title="Ultra-Light Stock Scanner", layout="wide")

@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--memory-pressure-off") # Helpt bij lage RAM
    # Schakel afbeeldingen en advertenties uit om geheugen te sparen
    options.add_argument("--blink-settings=imagesEnabled=false") 
    
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=options)
    # Zet een limiet aan hoe lang een pagina mag laden (bespaart RAM)
    driver.set_page_load_timeout(15)
    return driver

def scrape_stock_efficient(driver, symbol):
    url = f"https://www.stockconsultant.com/consultnow/basicplus.cgi?symbol={symbol}"
    try:
        driver.get(url)
        time.sleep(4) # Iets kortere wachtrij
        
        # We pakken alleen de tekst, dat is lichtgewicht
        body_text = driver.find_element("tag name", "body").text
        
        # Extractie
        score = re.search(r"Score[:\s]*(\d+\.?\d*)", body_text, re.IGNORECASE)
        quality = re.search(r"Quality[:\s]*(\d+\.?\d*)", body_text, re.IGNORECASE)
        sup = re.search(r"support\s+(?:at|is)\s+([\d\.]+)", body_text, re.IGNORECASE)
        res = re.search(r"resistance\s+(?:at|is)\s+([\d\.]+)", body_text, re.IGNORECASE)
        
        # Geheugen opruimen na extractie
        del body_text
        gc.collect() 

        return {
            "Symbool": symbol,
            "Score": score.group(1) if score else "N/A",
            "Quality": quality.group(1) if quality else "N/A",
            "Support": sup.group(1) if sup else "N/A",
            "Resistance": res.group(1) if res else "N/A"
        }
    except Exception:
        return {"Symbool": symbol, "Score": "Error", "Quality": "-", "Support": "-", "Resistance": "-"}

# --- UI ---
st.title("🛡️ Low-Memory Stock Scanner")

input_symbols = st.text_input("Symbolen (max 5 aanbevolen):", "PAYO")
symbol_list = [s.strip().upper() for s in input_symbols.split(",") if s.strip()]

if st.button("Start Analyse"):
    if symbol_list:
        driver = get_driver()
        results = []
        
        progress = st.progress(0)
        for i, sym in enumerate(symbol_list):
            with st.spinner(f"Bezig met {sym}..."):
                data = scrape_stock_efficient(driver, sym)
                results.append(data)
                progress.progress((i + 1) / len(symbol_list))
        
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        
        # Ruim resultaten op na weergave
        del results
        gc.collect()
    else:
        st.warning("Voer een symbool in.")

st.divider()
st.caption("Geoptimaliseerd voor Streamlit Cloud Resource Limits.")


