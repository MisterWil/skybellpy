"""Skybellpy utility methods."""
import pickle
import random
import string
import uuid


def save_cache(data, filename):
    """Save cookies to a file."""
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle)


def load_cache(filename):
    """Load cookies from a file."""
    with open(filename, 'rb') as handle:
        return pickle.load(handle)


def gen_id():
    """Generate new Skybell IDs."""
    return str(uuid.uuid4())


def gen_token():
    """Generate a new Skybellpy token."""
    return ''.join(
        random.choice(
            string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(32))


def update(dct, dct_merge):
    """Recursively merge dicts."""
    for key, value in dct_merge.items():
        if key in dct and isinstance(dct[key], dict):
            dct[key] = update(dct[key], value)
        else:
            dct[key] = value
    return dct
