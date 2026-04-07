ACCOUNTS = [
    "kalawssimatrix+0123@gmail.com",
    "bailirm52@youoneshell.eu.org",
    "vitrasue61@itchigho.eu.org",
    "doc82@itchigho.eu.org",
    "mylastres0rt05+011@gmail.com",
]

def get_ck(session: int) -> str:
    return ACCOUNTS[session - 1]
