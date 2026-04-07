import imaplib
import email
from email.utils import parsedate_to_datetime
import re
import time

HOST = "imap.gmail.com"
PORT = 993
USERNAME = "kalawssimatrix@gmail.com"
PASSWORD = "bwokhaeitjbdhiqm"

def get_2fa(target_email=None, retries=10, delay=6):
    mail = imaplib.IMAP4_SSL(HOST, PORT)
    mail.login(USERNAME, PASSWORD)
    mail.select("INBOX")

    for attempt in range(1, retries + 1):
        _, msg_ids = mail.search(None, "ALL")
        ids = msg_ids[0].split()
        print(f"[2FA] attempt {attempt}/{retries} — {len(ids)} total emails found")

        best_code = None
        best_time = None
        best_id = None

        for mid in ids:
            _, data = mail.fetch(mid, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            match = re.search(r'Verification code[:\s]+(\d{6})', body)
            if match:
                date_str = msg.get("Date")
                try:
                    msg_time = parsedate_to_datetime(date_str)
                except Exception:
                    msg_time = None

                if best_time is None or (msg_time and msg_time > best_time):
                    best_code = match.group(1)
                    best_time = msg_time
                    best_id = mid

        if best_code:
            mail.store(best_id, '+FLAGS', '\\Deleted')
            mail.expunge()
            mail.logout()
            return best_code

        time.sleep(delay)

    mail.logout()
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python get_2FA.py <email>")
        sys.exit(1)
    code = get_2fa(sys.argv[1])
    print(f"2FA Code: {code}")
