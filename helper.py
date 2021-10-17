def is_int(text: str):
    try:
        int(text)
    except ValueError:
        return False
    return True