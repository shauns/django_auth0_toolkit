#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django_auth0_toolkit
----------------------------------

Tests for `django_auth0_toolkit` module.
"""
from django.utils.six.moves.urllib import parse as urlparse
import responses

from django_auth0_toolkit import sso


def test_sso_without_intercept(rf):
    res = sso.sso_fallback(
        rf.get('/restricted-page/'),
        intercept_auth0_redirect=False,
    )

    assert res.status_code == 302

    actual = urlparse.urlparse(res['Location'])

    assert actual.scheme == 'https'
    assert actual.netloc == 'testing.auth0.com'
    assert actual.path == '/oauth/authorize'
    assert urlparse.parse_qs(actual.query) == {
        'client_id': ['client-id-from-auth0'],
        'redirect_uri': ['http://testserver/handle-auth0-callback'],
        'response_type': ['code'],
        'state': ['http://testserver/restricted-page/'],
    }


@responses.activate
def test_sso_with_intercept_is_authed(rf):
    def request_callback(request):
        headers = {
            'Location': 'http://testserver/handle-auth0-callback?code=foo'
        }
        return (302, headers, None)

    responses.add_callback(
        responses.GET,
        'https://testing.auth0.com/oauth/authorize',
        callback=request_callback,
    )

    res = sso.sso_fallback(
        rf.get('/restricted-page/'),
        intercept_auth0_redirect=True,
    )

    assert len(responses.calls) == 1

    assert res.status_code == 302
    assert res['Location'] == (
        'http://testserver/handle-auth0-callback?code=foo'
    )


@responses.activate
def test_sso_with_intercept_is_anon(rf):
    def request_callback(request):
        headers = {
            'Location': 'https://testing.auth0.com/login'
        }
        return (302, headers, None)

    responses.add_callback(
        responses.GET,
        'https://testing.auth0.com/oauth/authorize',
        callback=request_callback,
    )

    res = sso.sso_fallback(
        rf.get('/restricted-page/'),
        intercept_auth0_redirect=True,
    )

    assert len(responses.calls) == 1

    assert res.status_code == 302
    assert res['Location'] == (
        '/accounts/login/?next=/restricted-page/'
    )
