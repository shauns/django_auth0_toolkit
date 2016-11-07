#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import pytest
import responses

from django_auth0_toolkit.auth_api import get_user_info_with_id_token, \
    get_token_info_from_authorization_code
from django_auth0_toolkit.exceptions import InvalidTokenException


@responses.activate
def test_get_user_info_with_id_token():
    responses.add(
        responses.GET,
        'https://testing.auth0.com/tokeninfo?id_token=id-token-here',
        status=200,
        json={'user_id': 'auth0|123456789'},
        match_querystring=True,
    )

    res = get_user_info_with_id_token('id-token-here')

    assert res == {'user_id': 'auth0|123456789'}


@responses.activate
def test_get_user_info_with_id_token_fails():
    responses.add(
        responses.GET,
        'https://testing.auth0.com/tokeninfo?id_token=id-token-here',
        status=401,
        body='Unauthorized',
        match_querystring=True,
    )

    with pytest.raises(InvalidTokenException):
        get_user_info_with_id_token('id-token-here')


@responses.activate
def test_get_token_info_from_authorization_code():
    def request_callback(request):
        assert request.headers['content-type'] == 'application/json'
        payload = json.loads(request.body)
        assert payload == {
            'code': 'auth-code',
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://testserver/callback',
            'client_id': 'client-id-from-auth0',
            'client_secret': 'client-secret-from-auth0',
        }
        return (200, {}, json.dumps({'id_token': 'id-token-here'}))

    responses.add_callback(
        responses.POST,
        'https://testing.auth0.com/oauth/token',
        callback=request_callback,
    )

    res = get_token_info_from_authorization_code(
        'auth-code', 'http://testserver/callback',
    )

    assert res == {'id_token': 'id-token-here'}


@responses.activate
def test_get_token_info_from_authorization_code_fails():
    def request_callback(request):
        return (400, {}, json.dumps({
            'error': 'invalid_grant',
            'error_description': 'Invalid authorization code',
        }))

    responses.add(
        responses.POST,
        'https://testing.auth0.com/oauth/token',
        status=403,
        json={
            'error': 'invalid_grant',
            'error_description': 'Invalid authorization code',
        },
    )

    with pytest.raises(InvalidTokenException):
        get_token_info_from_authorization_code(
            'auth-code', 'http://testserver/callback',
        )
