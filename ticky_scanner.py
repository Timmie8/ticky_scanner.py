import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re

# --- CONFIGURATIE ---
st.set_page_config(page_title="Ticky Dashboard", layout="centered")

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

def extract_score(text):
    """
    Zoekt naar een getal in de tekst (bijv. '7.5' of '-2.1').
    """
    # Zoek naar getallen (ook negatief en met decimalen)
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    if numbers:
        return float(numbers[0])
    return None

# --- UI ---
st.title("📈 Ticky Score Dashboard")
symbol = st.text_input("Voer symbool in (bijv. TSLA):", "").upper()

if symbol:
    try:
        driver = get_driver()
        with st.spinner(f"Analyseert {symbol}..."):
            url = f"https://www.trade-ideas.com/ticky/ticky.html?symbol={symbol}"
            driver.get(url)
            time.sleep(5) 
            
            page_content = driver.find_element("tag name", "body").text
            score = extract_score(page_content)

            if score is not None:
                st.subheader(f"Resultaat voor {symbol}")
                
                # Kleur bepalen op basis van score
                color = "normal"
                if score > 2:
                    color = "inverse" # Groenachtig in Streamlit
                elif score < -2:
                    color = "off" # Roodachtig/Grijs
                
                # De mooie Dashboard Widget
                col1, col2 = st.columns(2)
                col1.metric(label="Ticky Score", value=f"{score}", delta=score)
                
                # Visuele indicator
                if score > 0:
                    st.success(f"De sentiment score voor {symbol} is Positief.")
                else:
                    st.error(f"De sentiment score voor {symbol} is Negatief.")
                
                with st.expander("Bekijk ruwe data"):
                    st.write(page_content)
            else:
                st.warning("Pagina geladen, maar geen score kunnen extraheren.")
                st.write("Ruwe tekst gevonden:", page_content)
                
    except Exception as e:
        st.error("Er is een fout opgetreden.")
        st.exception(e)
else:
    st.info("Voer een symbool in om de live score te zien.")

st.divider()
st.caption("Data afkomstig van Trade-Ideas Ticky Tool")

