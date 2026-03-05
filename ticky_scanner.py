import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# --- PAGINA CONFIGURATIE ---
st.set_page_config(page_title="Ticky Dashboard", page_icon="📈", layout="centered")

# --- BROWSER SETUP ---
@st.cache_resource
def get_driver():
    """Initialiseert een headless Chrome browser voor Streamlit Cloud."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Op Streamlit Cloud staan de binaries op deze vaste locaties:
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    
    return webdriver.Chrome(service=service, options=options)

# --- DASHBOARD UI ---
st.title("📊 Trade-Ideas Ticky Scanner")
st.markdown("""
Voer een aandeel-symbool in om de live score op te halen van de Trade-Ideas Ticky tool.
""")

# Inputveld voor de gebruiker
symbol = st.text_input("Aandeel Symbool (bijv. AAPL, TSLA, NVDA):", "").upper()

if symbol:
    # Start de browser via de gecachte functie
    driver = get_driver()
    
    with st.spinner(f"Bezig met ophalen van data voor {symbol}..."):
        try:
            # Ga naar de URL
            url = f"https://www.trade-ideas.com/ticky/ticky.html?symbol={symbol}"
            driver.get(url)
            
            # Wacht 3 seconden tot de JavaScript de score heeft berekend
            time.sleep(3)
            
            # Zoek de tekst op de pagina
            page_content = driver.find_element("tag name", "body").text
            
            if page_content.strip() == "":
                st.warning("De pagina is geladen, maar lijkt leeg te zijn. Controleer of het symbool correct is.")
            else:
                st.subheader(f"Resultaten voor {symbol}")
                
                # We tonen de data in een mooie 'Card' stijl
                st.info(f"**Gevonden Data:**\n\n{page_content}")
                
                # Bonus: Een directe link voor de gebruiker
                st.markdown(f"[Bekijk originele bron op Trade-Ideas]({url})")

        except Exception as e:
            st.error(f"Er is een fout opgetreden tijdens het scrapen: {e}")
            st.info("Tip: Controleer of je `packages.txt` correct is geüpload naar GitHub.")

else:
    st.write("Wachtend op invoer...")

# --- FOOTER ---
st.divider()
st.caption("Deze tool gebruikt Selenium in headless mode op een Streamlit Cloud server.")
