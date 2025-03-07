

blacklisted_tokens = set()
def add_to_blacklist(token: str):
    blacklisted_tokens.add(token)

def is_blacklisted(token: str):
    return token in blacklisted_tokens