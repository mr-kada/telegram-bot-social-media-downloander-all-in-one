import asyncio
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


async def GetTwitterInfoV2(url):
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    likes_count, comments_count, reposts_count, bookmarks_count = 'غير متاح', 'غير متاح', 'غير متاح', 'غير متاح'

    try:
        driver.get(url)
        await asyncio.sleep(4)

        try:
            like_div = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="like"]')
            likes_count = like_div.text
        except Exception as e:pass

        try:
            comments_div = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="reply"]')
            comments_count = comments_div.text
        except Exception as e:pass

        try:
            reposts_div = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="retweet"]')
            reposts_count = reposts_div.text
        except Exception as e:pass

        try:
            bookmarks_div = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="bookmark"]')
            bookmarks_count = bookmarks_div.text
        except Exception as e:pass

    finally:
        driver.quit()

    image_url = None
    return image_url, likes_count, comments_count, reposts_count, bookmarks_count


# url = "https://x.com/abodantee/status/1874217094906339460?s=46&t=lUD4RZ5AySQ-xonRvtUzKg"
# GetTwitterInfoV2(url)
