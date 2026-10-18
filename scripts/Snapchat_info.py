from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")



async def scrape_snapchat_profile(url):
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        account_name = subscribers = 'غير متاح'

        try:
            account_name_element = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//span[starts-with(@class, "PublicProfileDetailsCard_displayNameTextOnMedia")]')
                )
            )
            account_name = account_name_element.text
        except:pass


        try:
            subscribers_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="subscribersCountText"]'))
            )
            subscribers = subscribers_element.text
        except:pass


        return {
            "account_name": account_name,
            "subscribers": subscribers
        }

    finally:
        driver.quit()