"""
selenium_options.py

Centralized Selenium browser configuration for DataMorph AI.

✔ Works on Local PC
✔ Safe for Cloud (won't crash if Selenium unavailable)
✔ Headless Chrome configuration
✔ Compatible with undetected-chromedriver
"""

import os

def get_chrome_options(headless: bool = True):
    """
    Returns configured Chrome Options object.
    """
    try:
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        return None

    options = Options()

    if headless:
        # New headless mode (Chrome 109+)
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")

    return options


def get_selenium_driver(headless: bool = True):
    """
    Tries to create a Selenium WebDriver.
    Priority:
    1. undetected-chromedriver
    2. normal selenium webdriver

    Returns:
        driver or None
    """

    # ------------------------------
    # Try undetected-chromedriver
    # ------------------------------
    try:
        import undetected_chromedriver as uc

        options = get_chrome_options(headless)
        driver = uc.Chrome(options=options)
        return driver
    except Exception:
        pass

    # ------------------------------
    # Fallback: normal Selenium
    # ------------------------------
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = get_chrome_options(headless)
        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception:
        return None
