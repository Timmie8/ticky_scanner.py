import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Pagina instellingen
st.set_page_config(page_title="Ticky Score Dashboard", layout="wide")

st.title("📈 Trade-Ideas Ticky Dashboard")
st.subheader("Haal live scores op zonder de website te bezoeken")

# Chrome opties configureren voor Cloud omgeving
@st.cache_resource
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Gebruik webdriver-manager om de juiste driver te installeren
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Initialiseer de browser
driver = get_driver()

# Input gedeelte
col1, col2 = st.columns([2, 1])
with col1:
    symbol = st.text_input("Voer een aandeel symbool in (bijv. NVDA, TSLA):", "").upper()

if symbol:
    with st.spinner(f"Bezig met ophalen van data voor {symbol}..."):
        try:
            url = f"https://www.trade-ideas.com/ticky/ticky.html?symbol={symbol}"
            driver.get(url)
            
            # Wacht 3 seconden zodat de JavaScript de score kan laden
            time.sleep(3)
            
            # Pak de tekst van de gehele body
            raw_text = driver.find_element("tag name", "body").text
            
            # Dashboard weergave
            st.success(f"Resultaten voor {symbol}")
            
            # We maken een mooie box voor de ruwe data
            st.info("### Gevonden Score Data:")
            st.code(raw_text, language="text")
            
            # Optioneel: Directe link als backup
            st.markdown(f"[Klik hier om de bron te bekijken]({url})")
            
        except Exception as e:
            st.error(f"Er is een fout opgetreden: {e}")
else:
    st.info("Voer hierboven een symbool in om te beginnen.")

# Footer
st.divider()
st.caption("Gebouwd met Python, Selenium en Streamlit.")
