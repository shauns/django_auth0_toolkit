""" Functions for working with JWTs

https://jwt.io/

"""
import base64
import logging

import jwt


logger = logging.getLogger(__name__)


def prepare_secret(secret):
    """ Converts an auth0 secret to its byte equivalent for JWT lib

    :param secret: Auth0 secret to convert, in base64 (as per Auth0 dashboard)
    :type secret: str
    :return: Decoded secret, compatible with :mod:`PyJWT`
    :rtype: str

    """
    return base64.b64decode(secret.replace("_", "/").replace("-", "+"))


def get_decoded_token(token, secret, client_id):
    """ Decodes a JWT

    :param token: JWT to decode, such as an ``id_token``.
    :type token: str
    :param secret: Secret used to sign the JWT
    :type secret: str
    :param client_id: Client application ID the JWT is for (``aud`` key).
    :type client_id: str
    :return: Decoded JWT object
    :rtype: dict[str, object]
    :raises ValueError: The token, secret, or client ID was invalid.

    """
    try:
        return jwt.decode(
            token,
            prepare_secret(secret),
            audience=client_id,
        )
    except jwt.InvalidTokenError:
        logger.exception('JWT failed to decode')
        raise ValueError('Invalid Token')
