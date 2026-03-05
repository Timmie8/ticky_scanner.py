from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. Instellingen voor de browser (onzichtbaar maken)
chrome_options = Options()
chrome_options.add_argument("--headless") # Draait op de achtergrond zonder venster

# 2. Start de browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def get_ticky_score(symbol):
    url = f"https://www.trade-ideas.com/ticky/ticky.html?symbol={symbol}"
    driver.get(url)
    
    # 3. Wacht even tot de JavaScript de score heeft geladen
    time.sleep(3) 
    
    # 4. Haal de tekst van de pagina op
    score_data = driver.find_element("tag name", "body").text
    return score_data

# Testen
symbool = input("Welk aandeel wil je checken? ").upper()
resultaat = get_ticky_score(symbool)
print(f"\nResultaten voor {symbool}:")
print(resultaat)

driver.quit()
