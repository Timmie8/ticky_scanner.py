import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re

# --- CONFIGURATIE ---
st.set_page_config(page_title="Ticky 0-100 Scanner", layout="centered")

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

def extract_ticky_100(text):
    """
    Zoekt specifiek naar het getal achter 'Score:' of 'SCORE:' in de tekst.
    """
    # Zoekt naar 'Score:' gevolgd door een getal (0-100)
    match = re.search(r"Score:\s*(\d+\.?\d*)", text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None

# --- UI ---
st.title("🎯 Ticky Score (0-100) Dashboard")
st.markdown("Voer een symbool in om de Trade-Ideas score te analyseren.")

symbol = st.text_input("Aandeel Symbool:", placeholder="Bijv. NVDA").upper()

if symbol:
    try:
        driver = get_driver()
        with st.spinner(f"Bezig met scannen van {symbol}..."):
            url = f"https://www.trade-ideas.com/ticky/ticky.html?symbol={symbol}"
            driver.get(url)
            
            # Trade-Ideas heeft tijd nodig om de score te berekenen via JS
            time.sleep(5) 
            
            page_content = driver.find_element("tag name", "body").text
            score = extract_ticky_100(page_content)

            if score is not None:
                st.divider()
                st.subheader(f"Resultaat voor {symbol}")
                
                # Visualisatie van de 0-100 score
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.metric(label="Huidige Score", value=f"{score}/100")
                
                with col2:
                    # Bepaal kleur van de balk (Groen boven 70, Oranje boven 40, Rood daaronder)
                    st.write("Sentiment Sterkte:")
                    st.progress(score / 100)
                
                # Interpretatie van de score
                if score >= 70:
                    st.success(f"🔥 Sterk positief sentiment ({score})")
                elif score >= 40:
                    st.warning(f"⚖️ Neutraal tot gematigd sentiment ({score})")
                else:
                    st.error(f"❄️ Zwak sentiment ({score})")

                with st.expander("Bekijk volledige brontekst"):
                    st.code(page_content)
            else:
                st.error("Kon de 'Score: XX' niet vinden in de data.")
                st.info("Ruwe data ontvangen:")
                st.text(page_content)
                
    except Exception as e:
        st.error("Er is een technisch probleem opgetreden.")
        st.exception(e)
else:
    st.info("Typ een symbool en druk op Enter.")

st.divider()
st.caption("Gebouwd voor Trade-Ideas data-extractie via Selenium.")


