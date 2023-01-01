import random
import string

def get_random_string(length: str):
    return "".join(random.choices(string.digits + string.ascii_letters, k=length))