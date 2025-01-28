from functools import wraps
import hashlib
import os
import warnings

from flask import request


def check_auth(username, password):
    """
    Check basic auth.

    The expected username and password come from an environmental variable structured as follows-

    ```shell
    HASHEDPASS=$(echo -n supersecret | md5)
    export BASIC_HTTP_AUTH=superman:$HASHEDPASS
    ```

    Note, this is intended to be baked into a container without the need for a configmap or settings file.

    @param username: (str) User supplied username to be checked against that supplied in the environment.
    @param password: (str)
    @return: bool

    """
    env_label = "BASIC_HTTP_AUTH"
    if env_label not in os.environ:

        msg = "Expected environmental variable 'BASIC_HTTP_AUTH' needed for authentication but not set."
        warnings.warn(msg)
        return False

    if os.environ[env_label].count(":") != 1:
        msg = "'BASIC_HTTP_AUTH' not in the correct format."
        warnings.warn(msg)
        return False

    expected_username, expected_password = os.environ[env_label].split(":", 1)
    hashed_password = hashlib.md5(password.encode("utf-8")).hexdigest()

    return username == expected_username and hashed_password == expected_password


def login_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        if not (auth and check_auth(auth.username, auth.password)):
            return ("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'})

        return f(**kwargs)

    return wrapped_view
