# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from functools import wraps

import requests
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http.response import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.decorators import available_attrs
from django.utils.six.moves.urllib.parse import urlparse


logger = logging.getLogger(__name__)


class Auth0(object):
    AUTH_RESPONSE_TYPE_CODE = 'code'


def sso_fallback(
    request,
    auth0_login_callback_view_name=None,
    auth0_authorization_url=None,
    login_url=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    intercept_auth0_redirect=True,
):
    # URL at auth0 to check if authed
    auth_url = auth0_authorization_url
    if auth_url is None:
        auth_url = (
            "https://{domain}/oauth/authorize".format(
                domain=settings.AUTH0_DOMAIN
            )
        )

    # the url of the page we are trying to get into, to pass along so
    # the callback url can redirect the user there, provided they
    # were authed
    target_page = request.build_absolute_uri()

    # View that handles auth0's callback
    login_callback_url = request.build_absolute_uri(resolve_url(
        auth0_login_callback_view_name or
        settings.AUTH0_LOGIN_CALLBACK_URL
    ))

    authorize_params = {
        'response_type': Auth0.AUTH_RESPONSE_TYPE_CODE,
        'client_id': settings.AUTH0_CLIENT_ID,
        'redirect_uri': login_callback_url,
        'state': target_page,
    }

    if not intercept_auth0_redirect:
        # If we're not interested in intercepting auth0's redirect, we
        # just need to tell the user where to go.
        prepared_request = requests.Request(
            'GET',
            auth_url,
            params=authorize_params,
        ).prepare()
        logger.debug('Sending user straight to %s', prepared_request.url)
        return HttpResponseRedirect(prepared_request.url)

    # hit auth0's authorize endpoint -- we'll get a redirect either
    # to the login_callback_url, meaning the user is already SSO-ed,
    # or to auth0's hosted login page.
    res = requests.get(auth_url, authorize_params, allow_redirects=False)

    # now presumably res has status 302
    if res.status_code != 302:
        # Yikes!
        logger.error("Unable to handle non-redirect response")
        raise NotImplementedError()

    # intercept auth0's redirection -- if the user isn't authed we
    # prefer they see our own login screen to auth0 hosted one
    auth0_redirect_to = res.headers['Location']

    if auth0_redirect_to.startswith(login_callback_url):
        # auth0 wants to go to the callback URL => the user is authed
        # let auth0's response propagate
        logger.debug(
            'Redirecting to %s as user already authenticated',
            auth0_redirect_to
        )
        return HttpResponseRedirect(auth0_redirect_to)

    else:
        # auth0 wants to go elsewhere => the user isn't authed
        # go to our own hosted login page -- as the normal
        # login_required decorator would.
        logger.debug('Redirecting to built-in login as user not authenticated')
        return redirect_login_required_to_login(
            request, login_url, redirect_field_name
        )


def user_passes_test_with_sso(
    test_func,
    auth0_login_callback_view_name=None,
    auth0_authorization_url=None,
    login_url=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    intercept_auth0_redirect=True,
):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)

            logger.debug('SSO fallback as user not authenticated')

            return sso_fallback(
                request,
                auth0_login_callback_view_name,
                auth0_authorization_url,
                login_url,
                redirect_field_name,
                intercept_auth0_redirect,
            )

        return _wrapped_view

    return decorator


def redirect_login_required_to_login(
    request, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME
):
    # Extracted from :func:`django.contrib.auth.login_required`
    # TODO could we use the actual decorator in some fashion?

    path = request.build_absolute_uri()
    resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)

    # If the login url is the same scheme and net location then just
    # use the path as the "next" url.
    login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
    current_scheme, current_netloc = urlparse(path)[:2]
    if ((not login_scheme or login_scheme == current_scheme) and
            (not login_netloc or login_netloc == current_netloc)):
        path = request.get_full_path()

    from django.contrib.auth.views import redirect_to_login
    return redirect_to_login(
        path, resolved_login_url, redirect_field_name)


def login_required_with_sso(
    function=None,
    auth0_login_callback_view_name=None,
    auth0_authorization_url=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url=None,
    intercept_auth0_redirect=True,
):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to auth0's SSO authorize endpoint, and then to the log-in page if necessary
    """
    actual_decorator = user_passes_test_with_sso(
        lambda u: u.is_authenticated(),
        auth0_login_callback_view_name,
        auth0_authorization_url,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
        intercept_auth0_redirect=intercept_auth0_redirect,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
