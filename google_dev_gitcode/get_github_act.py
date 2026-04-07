import imaplib
import email
import re
import time
from email.header import decode_header

HOST = "imap.gmail.com"
PORT = 993
USERNAME = "kalawssimatrix@gmail.com"
PASSWORD = "bwokhaeitjbdhiqm"
from_email="uwdhwarq2763@techxbox.eu.org"

def get_code(from_email, retries=10, delay=6):
    print("=" * 49)
    print(" Login to Email ;)")
    print("=" * 49)
    mail = imaplib.IMAP4_SSL(HOST, PORT)
    mail.login(USERNAME, PASSWORD)
    mail.select("INBOX")

    for _ in range(retries):
        _, msg_ids = mail.search(None, f'TO "{from_email}"')
        ids = msg_ids[0].split()
        print(f"Found {len(ids)} emails to {from_email}")
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

            # print(f"Body preview: {body[:300]}")
            match = re.search(r'entering the code below:\s*(\d{8})', body)
            if match:
                mail.logout()
                return match.group(1)

        time.sleep(delay)

    mail.logout()
    return None

# get_code(from_email, retries=10, delay=6)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python get_github_act.py <email>")
        sys.exit(1)
    result = get_code(sys.argv[1], retries=10, delay=6)
    print(f"Code: {result}")
