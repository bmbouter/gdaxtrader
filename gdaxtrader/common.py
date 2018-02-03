import os

import gdax


def get_auth_client():
    key = os.environ['GDAX_KEY']
    b64_secret = os.environ['GDAX_B64SECRET']
    passphrase = os.environ['GDAX_PASSPHRASE']
    return gdax.AuthenticatedClient(key, b64_secret, passphrase)


def raise_exception_if_error(response):
    if 'message' in response:
        raise Exception(response['message'])
