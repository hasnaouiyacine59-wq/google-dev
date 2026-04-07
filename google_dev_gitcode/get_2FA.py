import imaplib
import email
import re
import time

HOST = "imap.gmail.com"
PORT = 993
USERNAME = "kalawssimatrix@gmail.com"
PASSWORD = "bwokhaeitjbdhiqm"

def get_2fa(from_email, retries=10, delay=6):
    mail = imaplib.IMAP4_SSL(HOST, PORT)
    mail.login(USERNAME, PASSWORD)
    mail.select("INBOX")

    for attempt in range(1, retries + 1):
        _, msg_ids = mail.search(None, f'TO "{from_email}"')
        ids = msg_ids[0].split()
        print(f"[2FA] attempt {attempt}/{retries} — {len(ids)} emails found for {from_email}")
        if ids:
            _, data = mail.fetch(ids[-1], "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            match = re.search(r'Verification code[:\s]+(\d{6})', body)
            if match:
                mail.store(ids[-1], '+FLAGS', '\\Deleted')
                mail.expunge()
                mail.logout()
                return match.group(1)

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
