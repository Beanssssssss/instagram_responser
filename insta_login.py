# insta_login.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os, pickle, time, unicodedata
from dotenv import load_dotenv

load_dotenv()
INSTAGRAM_ID = '01042467280'
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
USE_COOKIES = True

def clean_text(s):
    return unicodedata.normalize("NFC", s).strip()

def close_alert_popup_if_present(driver, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@role="dialog"]//button[text()="나중에 하기"]'))
        ).click()
    except TimeoutException:
        pass

def click_chat_by_name(driver, target_name="박신영", timeout=10):
    target_name = clean_text(target_name)
    try:
        spans = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "xuxw1ft")]'))
        )
        for span in spans:
            name = clean_text(span.text)
            if name == target_name:
                parent = span.find_element(By.XPATH, "./ancestor::div[@role='presentation']")
                driver.execute_script("arguments[0].click();", parent)
                return
    except Exception as e:
        print("❌ 채팅 클릭 실패:", e)

def get_logged_in_driver(chat_name="박신영"):
    options = Options()
    service = Service("/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get("https://www.instagram.com/")
    time.sleep(3)

    if USE_COOKIES and os.path.exists("insta_cookies.pkl"):
        with open("insta_cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
    else:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(INSTAGRAM_ID)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(INSTAGRAM_PASSWORD)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        time.sleep(5)
        with open("insta_cookies.pkl", "wb") as f:
            pickle.dump(driver.get_cookies(), f)

    close_alert_popup_if_present(driver)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/direct/inbox/"]'))
    ).click()
    close_alert_popup_if_present(driver)
    click_chat_by_name(driver, chat_name)
    return driver