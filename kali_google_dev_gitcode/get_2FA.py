import imaplib
import email
import os
from email.utils import parsedate_to_datetime
import re
import time

HOST = "imap.gmail.com"
PORT = 993
USERNAME = os.environ.get("IMAP_USERNAME", "")
PASSWORD = os.environ.get("IMAP_PASSWORD", "")

# GitHub OTP patterns
_PATTERNS = [
    r'(\d{6})\s+is your GitHub authentication code',
    r'Verification code[:\s]+(\d{6})',
    r'Enter this code[:\s]+(\d{6})',
    r'Your GitHub launch code[:\s]+(\d{6})',
    r'(?<!\d)(\d{6})(?!\d)',  # fallback: any standalone 6-digit number
]

def _extract_code(body):
    for pat in _PATTERNS:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            return m.group(1)
    return None

def _get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct in ("text/plain", "text/html"):
                return part.get_payload(decode=True).decode(errors="ignore")
    return msg.get_payload(decode=True).decode(errors="ignore")

def get_2fa(target_email=None, retries=12, delay=15):
    for attempt in range(1, retries + 1):
        try:
            mail = imaplib.IMAP4_SSL(HOST, PORT)
            mail.login(USERNAME, PASSWORD)
            mail.select("INBOX")

            # search ALL (not just UNSEEN) from GitHub, last 30
            search = '(FROM "noreply@github.com")'
            if target_email:
                search = f'(TO "{target_email}" FROM "noreply@github.com")'

            _, msg_ids = mail.search(None, search)
            ids = msg_ids[0].split()
            ids = ids[-30:]  # last 30 from github
            print(f"[2FA] attempt {attempt}/{retries} — {len(ids)} GitHub emails found")

            best_code = None
            best_time = None
            best_id = None

            for mid in reversed(ids):  # newest first
                _, data = mail.fetch(mid, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                body = _get_body(msg)
                code = _extract_code(body)
                if code:
                    date_str = msg.get("Date")
                    try:
                        msg_time = parsedate_to_datetime(date_str)
                    except Exception:
                        msg_time = None
                    if best_time is None or (msg_time and msg_time > best_time):
                        best_code = code
                        best_time = msg_time
                        best_id = mid

            if best_code:
                mail.store(best_id, '+FLAGS', '\\Seen')
                mail.logout()
                print(f"[2FA] found code: {best_code}")
                return best_code

            mail.logout()
        except Exception as e:
            print(f"[2FA] attempt {attempt} error: {e}")

        time.sleep(delay)

    return None

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    code = get_2fa(target)
    print(f"2FA Code: {code}")
