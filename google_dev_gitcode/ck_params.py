ACCOUNTS = [
    "pollanalokazer87@youoneshell.eu.org",
    "vako57@itchigho.eu.org",
    "vendagiv61@bitcoin-plazza.eu.org",
    "divernyo79@itchigho.eu.org",
    "atsiag61@techxbox.eu.org",
]

def get_ck(session: int) -> str:
    return ACCOUNTS[session - 1]
