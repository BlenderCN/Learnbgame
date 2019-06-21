import random
import string

def get_random_string(length):
    random.seed()
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))