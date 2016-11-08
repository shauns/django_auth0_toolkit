# -*- coding: utf-8 -*-
import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from django_auth0_toolkit.auth_api import (
    get_token_info_from_authorization_code,
    get_user_info_with_id_token,
)
from django_auth0_toolkit.django_auth import register_and_login_auth0_user


logger = logging.getLogger(__name__)


class LoginError(Exception):
    def __init__(self, error_description):
        self.error_description = error_description


def generic_auth0_callback(request):
    user_info = get_user_in_auth0_callback(request)

    user = register_and_login_auth0_user(request, user_info)

    return user_info, user


def get_user_in_auth0_callback(request):
    code = request.GET.get('code', None)
    if code is None:
        # Failed to log in.
        logger.debug('Auth0 callback did not include Authorization Code')
        error_description = request.GET.get(
            'error_description', _('Unknown Error')
        )
        raise LoginError(error_description)

    token_info = get_token_info_from_authorization_code(
        code, request.build_absolute_uri()
    )
    if 'id_token' not in token_info:
        # Failed to log in.
        logger.debug("Token-Authorization Code swap didn't yield an ID token")
        error_description = request.GET.get(
            'error_description', _('Unknown Error')
        )
        raise LoginError(error_description)

    user_info = get_user_info_with_id_token(token_info['id_token'])
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
