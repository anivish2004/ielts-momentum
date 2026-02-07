import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def wake_up_app():
    app_url = os.environ.get("STREAMLIT_URL")
    if not app_url:
        print("Error: STREAMLIT_URL environment variable is not set.")
        return

    print(f"Opening {app_url}...")

    # Configure Chrome to run headless (without a visible window)
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )

    try:
        driver.get(app_url)
        # Wait up to 30 seconds for the page to load
        time.sleep(5) 
        
        # Check if the "Yes, get this app back up!" button exists
        # This button appears when the app is in hibernation
        try:
            wake_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Yes, get this app back up')]")
                )
            )
            print("Sleep mode detected. Clicking 'Wake Up' button...")
            wake_button.click()
            
            # Wait a bit to ensure the click registered
            time.sleep(10)
            print("Wake up signal sent.")
        except:
            print("App seems to be running (no wake button found).")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    wake_up_app()
