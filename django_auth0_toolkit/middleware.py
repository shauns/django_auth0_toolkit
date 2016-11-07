from __future__ import unicode_literals

from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.utils.six import text_type

from django_auth0_toolkit.auth_api import get_user_info_with_id_token
from django_auth0_toolkit.django_auth import register_and_login_auth0_user
from django_auth0_toolkit.tokens import get_decoded_token


def get_user_from_request(request):
    """
    Returns the user model instance associated with the given request session.
    If no user is retrieved an instance of `AnonymousUser` is returned.

    """
    from django.contrib.auth.models import AnonymousUser
    user = None

    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, text_type):
        auth = auth.encode('iso-8859-1')

    auth = auth.split()

    if auth and len(auth) == 2 and auth[0].lower() == 'bearer'.encode():
        try:
            id_token = auth[1].decode()
        except UnicodeError:
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
                pass
            else:
                user_info = get_user_info_with_id_token(
                    id_token
                )

                user = register_and_login_auth0_user(request, user_info)

    return user or AnonymousUser()


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
