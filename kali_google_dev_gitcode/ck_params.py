ACCOUNTS = [
    "kode61lobi@alpha804.eu.org",
    "mustang10302@youoneshell.eu.org",
    "ugoovio5903@techxbox.eu.org",
    "itigowh9504@bitcoin-plazza.eu.org",
    "pulyong5505@techxbox.eu.org",
]
# ACCOUNTS = [
#     "gunon74@itchigho.eu.org",
#     "mustang10302@youoneshell.eu.org",
#     "ugoovio5903@techxbox.eu.org",
#     "itigowh9504@bitcoin-plazza.eu.org",
#     "pulyong5505@techxbox.eu.org",
# ]

def get_ck(session: int) -> str:
    return ACCOUNTS[session - 1]
