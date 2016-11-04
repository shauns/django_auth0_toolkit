# -*- coding: utf-8 -*-
import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _


class LoginError(Exception):
    def __init__(self, error_description):
        self.error_description = error_description


def generic_auth0_callback(request):
    user_info = get_user_in_auth0_callback(request)

    user = register_and_login_auth0_user(request, user_info)

    return user_info, user


def register_and_login_auth0_user(request, user_info, do_login=True):
    # Expects an authentication backend that can handle these kwargs.
    user = authenticate(user_info=user_info)
    if do_login and user.is_active:
        login(request, user)

    return user


def get_user_in_auth0_callback(request):
    code = request.GET.get('code', None)
    if code is None:
        # Failed to log in.
        error_description = request.GET.get(
            'error_description', _('Unknown Error')
        )
        raise LoginError(error_description)

    token_info = get_token_info_from_access_code(
        code, request.build_absolute_uri()
    )
    if 'access_token' not in token_info:
        # Failed to log in.
        error_description = request.GET.get(
            'error_description', _('Unknown Error')
        )
        raise LoginError(error_description)

    user_info = get_user_info_with_access_token(token_info['access_token'])
    return user_info


def get_token_info_from_access_code(code, redirect_url):
    json_header = {'content-type': 'application/json'}

    token_url = "https://{domain}/oauth/token".format(
        domain=settings.AUTH0_DOMAIN
    )

    token_payload = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'redirect_uri': redirect_url,
        'code': code,
        'grant_type': 'authorization_code'
    }

    token_info = requests.post(
        token_url, data=json.dumps(token_payload), headers=json_header
    ).json()
    return token_info


def get_user_info_with_access_token(access_token):
    user_url = "https://{domain}/userinfo?access_token={access_token}".format(
        domain=settings.AUTH0_DOMAIN, access_token=access_token
    )

    user_info = requests.get(user_url).json()
    return user_info


def auth0_callback(request):
    """ Standard auth0 log-in callback view.

    Receives query parameters `state` - the 'next' page once authentication is
    finished, and `code` - an access code that can be used to get token info
    for the authenticated user.

    """
    try:
        generic_auth0_callback(request)
    except LoginError as exc:
        messages.add_message(
            request,
            messages.ERROR,
            _('Error logging in: {error_description}').format(
                error_description=exc.error_description
            ),
        )
        # TODO provide a way of specifying page for a failed log-in payload
        return HttpResponseRedirect('/')
    else:
        # 'next' URL passed along as state
        next_url = request.GET.get('state', None)
        # TODO provide a way of specifying post log-in page if no state given
        return HttpResponseRedirect(next_url or '/')
