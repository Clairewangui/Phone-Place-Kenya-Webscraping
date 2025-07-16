# Importing all the necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback

# Setup WebDriver
def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to dismiss "Got it" popup if present
def dismiss_got_it_popup(driver):
    try:
        wait = WebDriverWait(driver, 10)
        got_it_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[contains(text(), 'Got it')]"
        )))
        got_it_button.click()
        print("✅ Dismissed 'Got it' popup.")
        time.sleep(1)
    except:
        print("ℹ️ 'Got it' popup not found or already dismissed.")

# Click the span that contains 'Popular homes in Mombasa' text
def click_mombasa_menu(driver, url):
    try:
        driver.get(url)
        dismiss_got_it_popup(driver)

        wait = WebDriverWait(driver, 15)

        # Click the outer <span> that has the text and nested SVG
        mombasa_span = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//span[contains(text(), 'Popular homes in Mombasa')]"
        )))
        mombasa_span.click()
        print("✅ Clicked Popular homes in Mombasa")
        time.sleep(5)
    except Exception as e:
        print("❌ Error clicking Popular homes in Mombasa")
        traceback.print_exc()

# Main execution
if __name__ == "__main__":
    driver = setup_driver()
    try:
        url = "https://www.airbnb.com/"
        click_mombasa_menu(driver, url)
    finally:
        driver.quit()
