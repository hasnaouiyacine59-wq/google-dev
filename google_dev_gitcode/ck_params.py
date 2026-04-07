ACCOUNTS = [
    "tech-stuff04@techxbox.eu.org",
    "tech-stuff05@itchigho.eu.org",
    "vitrasue61@itchigho.eu.org",
    "doc82@itchigho.eu.org",
    "mylastres0rt05+011@gmail.com",
]

def get_ck(session: int) -> str:
    return ACCOUNTS[session - 1]
