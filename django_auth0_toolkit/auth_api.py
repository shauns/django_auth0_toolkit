# -*- coding: utf-8 -*-
""" Functions for working with the Auth0 authentication API.

https://auth0.com/docs/api/authentication

"""
import json
import logging

import requests
from django.conf import settings

from django_auth0_toolkit.exceptions import InvalidTokenException


logger = logging.getLogger(__name__)


def get_token_info_from_authorization_code(authorization_code, redirect_url):
    """ Exchanges an authorization code passed to your callback URL for tokens
    for the authenticated user.

    :param authorization_code: Authorization code provided to your callback URL
    :type authorization_code: str
    :param redirect_url: URL of your callback
    :type redirect_url: str
    :return: Tokens for further API access, including ``id_token``.
    :rtype: dict[str, str]
    :raises InvalidTokenException: The exchange failed.
    """
    json_header = {'content-type': 'application/json'}

    token_url = "https://{domain}/oauth/token".format(
        domain=settings.AUTH0_DOMAIN
    )

    token_payload = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'redirect_uri': redirect_url,
        'code': authorization_code,
        'grant_type': 'authorization_code'
    }

    res = requests.post(
        token_url, data=json.dumps(token_payload), headers=json_header
    )

    try:
        res.raise_for_status()
    except requests.HTTPError:
        logger.exception('Authorization Code-Token exchange failed')
        raise InvalidTokenException(authorization_code)

    token_info = res.json()
    return token_info


def get_user_info_with_id_token(id_token):
    """ Fetches a user's profile from Auth0, based on an ID token for them.

    :param id_token: ID token belonging to the user who's profile we want
    :type id_token: str
    :return: User profile dictionary from Auth0
    :rtype: dict[str, object]
    :raises InvalidTokenException: id_token is reported as invalid by Auth0
    """
    user_from_token_url = 'https://{domain}/tokeninfo'.format(
        domain=settings.AUTH0_DOMAIN,
    )

    res = requests.get(
        user_from_token_url, {'id_token': id_token}
    )

    try:
        res.raise_for_status()
    except requests.HTTPError:
        logger.exception('ID token-profile exchange failed')
        raise InvalidTokenException(id_token)

    user_info = res.json()
    return user_info
