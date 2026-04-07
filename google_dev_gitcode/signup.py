import random
import string
from playwright.sync_api import sync_playwright

def random_email():
    name = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"{name}@techxbox.eu.org"

email = random_email()
print(f"Generated email: {email}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://github.com/", timeout=60000)
    page.wait_for_timeout(3000)

    page.fill("#hero_user_email", email)
    page.wait_for_timeout(1000)

    page.click("button.js-hero-action")
    print("Clicked sign up button")

    input("Press Enter to close...")
    browser.close()
