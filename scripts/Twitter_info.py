import requests, asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

# tweet_url = "https://x.com/wild_sugichan/status/1865201284472766804"

async def extract_tweet_data(tweet_url):
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)


    try:
        driver.get(tweet_url)
        await asyncio.sleep(5)

        # Initialize WebDriverWait
        wait = WebDriverWait(driver, 10)

        # Extract image URL
        image_url = None
        try:
            image_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'img[alt="Image"].css-9pa8cd'))
            )
            image_url = image_element.get_attribute('src') if image_element else None
        except:
            pass

        # Extract tweet metrics
        reposts = quotes = likes = bookmarks = 'غير متاح'
        try:
            reposts_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/retweets')]/div/span/span/span"))
            )
            reposts = reposts_element.text
        except:
            pass

        try:
            quotes_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/retweets/with_comments')]/div/span/span/span"))
            )
            quotes = quotes_element.text
        except:
            pass

        try:
            likes_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/likes')]/div/span/span/span"))
            )
            likes = likes_element.text
        except:
            pass

        try:
            bookmarks_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[span[contains(text(), 'Bookmarks')]]/div/span/span/span"))
            )
            bookmarks = bookmarks_element.text
        except:
            pass

    except Exception as e:
        # print(f"Error extracting tweet data: {e}")
        image_url = reposts = quotes = likes = bookmarks = None
    finally:
        driver.quit()

    return image_url, reposts, quotes, likes, bookmarks

# print(extract_tweet_data(tweet_url))
