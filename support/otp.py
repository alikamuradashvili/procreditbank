from getpass import getpass


def request_sms_code(length):
    """Read a fresh code locally without echoing or persisting it."""
    code = getpass(f'ტელეფონზე მოსული {length}-ციფრიანი SMS კოდი: ').strip()
    if not code.isascii() or not code.isdigit() or len(code) != length:
        raise ValueError(f'Expected exactly {length} ASCII digits.')
    return code
