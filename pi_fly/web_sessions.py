'''
Really, really simple sessions - just a long life cookie.

It has the equivalent security of http basic auth but doesn't require interaction
from the http server (e.g. gunigorn).

Created on 7 Jan 2021

@author: si
'''
from functools import wraps
import hashlib
import random
from urllib.parse import urlencode

from flask import request, redirect, current_app

SESSION_COOKIE_NAME = 'pi_fly_session'


def session_token_create(secret_key):
    """
    Args:
        secret_key (str)

    Returns (str)
    """
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    seed = "".join([random.choice(alphabet) for _ in range(5)])
    plain_text = seed + secret_key
    sha1_hash = hashlib.sha1(plain_text.encode('utf-8')).hexdigest()
    return f"{seed}:{sha1_hash}"


def session_token_valid(secret_key, session_token):
    """
    Args:
        secret_key (str)
        session_token (str)

    Returns (bool)
    """
    seed, token = session_token.split(":", 1)
    if not seed.isalnum() or not token.isalnum():
        return False

    plain_text = seed + secret_key
    sha1_hash = hashlib.sha1(plain_text.encode('utf-8')).hexdigest()
    return token == sha1_hash


def valid_session():
    """
    decorator to check user is logged in and session is valid.
    """
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):

            secret_key = current_app.config['SESSION_PASSWORD']
            session_token = request.cookies.get(SESSION_COOKIE_NAME, None)
            if not session_token or not session_token_valid(secret_key, session_token):
                # .. when there are views
                # -- url_for('authentication_views.user_login')
                login_url = request.host_url[:-1] + "/login/"
                assert request.url.startswith(request.host_url)
                next_hop_path = request.url[len(request.host_url):]
                next_hop = urlencode({'next': next_hop_path})
                return redirect(login_url + "?" + next_hop)

            return f(*args, **kwargs)
        return decorated_view
    return wrapper
