from __future__ import unicode_literals

import logging

from django.conf import settings
from django.contrib import auth as django_auth
from django.utils.functional import SimpleLazyObject
from django.utils.six import text_type

from django_auth0_toolkit.auth_api import get_user_info_with_id_token
from django_auth0_toolkit.django_auth import register_and_login_auth0_user
from django_auth0_toolkit.tokens import get_decoded_token


logger = logging.getLogger(__name__)


def get_user_from_request(request):
    """
    Returns the user model instance associated with the given request session.
    If no user is retrieved an instance of `AnonymousUser` is returned.

    """
    user = None

    auth_header = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth_header, text_type):
        auth_header = auth_header.encode('iso-8859-1')

    auth_header = auth_header.split()

    if (
        auth_header and len(auth_header) == 2 and
        auth_header[0].lower() == 'bearer'.encode()
    ):
        try:
            logger.debug('Received ID token %s', auth_header[1])
            id_token = auth_header[1].decode()
        except UnicodeError:
            logger.debug('Auth failed due to unicode error in token')
            pass
        else:
            # Confirm its not a phoney token
            try:
                get_decoded_token(
                    id_token,
                    settings.AUTH0_CLIENT_SECRET,
                    settings.AUTH0_CLIENT_ID,
                )
            except ValueError:
                logger.debug('Auth failed due to bad ID token')
                pass
            else:
                # TODO if there is already a logged in user, and it's this
                # user, don't re-fetch their details.

                # TODO avoid a fetch if the token already includes a rich
                # profile

                user_info = get_user_info_with_id_token(
                    id_token
                )

                user = register_and_login_auth0_user(request, user_info)

    # if no user, we fall back to Django's normal AuthenticationMiddleware
    return user or django_auth.get_user(request)


def get_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = get_user_from_request(request)
    return request._cached_user


class Auth0AuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        request.user = SimpleLazyObject(lambda: get_user(request))
