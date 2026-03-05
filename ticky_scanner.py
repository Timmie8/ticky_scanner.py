import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time

# --- PAGINA CONFIGURATIE ---
st.set_page_config(page_title="Ticky Dashboard", page_icon="📈")

# --- BROWSER SETUP ---
@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Gebruik ChromeType.CHROMIUM voor Linux/Streamlit omgevingen
    # Dit installeert automatisch de juiste driver voor de Chromium browser
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    
    return webdriver.Chrome(service=service, options=options)

# --- DASHBOARD UI ---
st.title("📊 Trade-Ideas Ticky Scanner")

symbol = st.text_input("Aandeel Symbool (bijv. AAPL):", "").upper()

if symbol:
    try:
        driver = get_driver()
        with st.spinner(f"Gegevens ophalen voor {symbol}..."):
            url = f"https://www.trade-ideas.com/ticky/ticky.html?symbol={symbol}"
            driver.get(url)
            
            # Wacht op de JavaScript berekening van Trade-Ideas
            time.sleep(5) 
            
            # Haal de tekst op uit de body
            page_content = driver.find_element("tag name", "body").text
            
            if page_content:
                st.success(f"Resultaat voor {symbol}")
                st.info(f"**Gevonden Data:**\n\n{page_content}")
            else:
                st.warning("Geen data gevonden. Is het symbool correct?")
                
    except Exception as e:
        st.error("Er is een probleem met de browserverbinding.")
        st.exception(e) # Dit toont de volledige foutmelding voor debugging
else:
    st.write("Voer een symbool in om de scan te starten.")

st.divider()
st.caption("Draait op Streamlit Cloud met Selenium & Chromium")

