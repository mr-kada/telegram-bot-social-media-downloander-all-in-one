from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")


async def fetch_tiktok_data(url):
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    try:
        # Wait for the necessary elements to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "strong[data-e2e='like-count']"))
        )

        # Profile Image URL
        profile_image_element = driver.find_element(By.CSS_SELECTOR, "img.css-1zpj2q-ImgAvatar")
        profile_image_url = profile_image_element.get_attribute('src') if profile_image_element else "غير متاح"

        # Account Name
        account_name_element = driver.find_element(By.CSS_SELECTOR, "span[data-e2e='browse-username']")
        account_name = account_name_element.text if account_name_element else "غير متاح"

        # Likes, Comments, Favorites, Shares
        likes = driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='like-count']").text if driver.find_element(
            By.CSS_SELECTOR, "strong[data-e2e='like-count']") else "غير متاح"
        comments = driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='comment-count']").text if driver.find_element(
            By.CSS_SELECTOR, "strong[data-e2e='comment-count']") else "غير متاح"
        favorites = driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='undefined-count']").text if driver.find_element(
            By.CSS_SELECTOR, "strong[data-e2e='undefined-count']") else "غير متاح"
        shares = driver.find_element(By.CSS_SELECTOR, "strong[data-e2e='share-count']").text if driver.find_element(
            By.CSS_SELECTOR, "strong[data-e2e='share-count']") else "غير متاح"

        # Video Duration
        video_duration_element = driver.find_element(By.CSS_SELECTOR, "div.css-1cuqcrm-DivSeekBarTimeContainer")
        video_duration = video_duration_element.text.split('/')[-1].strip() if video_duration_element else "غير متاح"

        # Country Code (from <script> tag)
        country_code = "غير متاح"
        scripts = driver.find_elements(By.TAG_NAME, "script")
        for script in scripts:
            if '"region":"' in script.get_attribute("innerHTML"):
                country_code = script.get_attribute("innerHTML").split('"region":"')[1].split('"')[0]
                break

        # Collecting data
        data = {
            "account_name": account_name,
            "profile_image_url": profile_image_url,
            "likes": likes,
            "comments": comments,
            "favorites": favorites,
            "shares": shares,
            "video_duration": video_duration,
            "country_code": country_code
        }

        return data

    except Exception as e:
        data = {
            "account_name": "غير متاح",
            "profile_image_url": "غير متاح",
            "likes": "غير متاح",
            "comments": "غير متاح",
            "favorites": "غير متاح",
            "shares": "غير متاح",
            "video_duration": "غير متاح",
            "country_code": "غير متاح"
        }

        return data
    finally:
        driver.quit()