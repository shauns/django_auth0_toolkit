import pytest

from django_auth0_toolkit.tokens import prepare_secret, get_decoded_token


# Manually created based on test client id and secret. Does not expire.
TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
    "eyJpc3MiOiJodHRwczovL3Rlc3RpbmcuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfHF"
    "3ZXJ0eXVpb3AiLCJhdWQiOiJjbGllbnQtaWQtZnJvbS1hdXRoMCIsImlhdCI6MTIzND"
    "U2Nzh9."
    "hi4FG8pQ628E5u3z-jTKRb1eSfnOZi6uffB5fMbZv9Q"
)


@pytest.mark.parametrize("secret,expected", [
    ('c2VjcmV0cw==', b'secrets'),
    (u'Y_1-', b'c\xfd~')
])
def test_prepare_secret(secret, expected):
    assert expected == prepare_secret(secret)


def test_get_decoded_token():
    from django.conf import settings
    res = get_decoded_token(
        TOKEN,
        settings.AUTH0_CLIENT_SECRET,
        settings.AUTH0_CLIENT_ID,
    )

    assert res == {
        'aud': settings.AUTH0_CLIENT_ID,
        'iat': 12345678,
        'iss': 'https://testing.auth0.com/',
        'sub': 'auth0|qwertyuiop',
    }


@pytest.mark.parametrize('token', [
    # Audience mismatch (aud = 'client-secret-from-auth0!'
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
    'eyJpc3MiOiJodHRwczovL3Rlc3RpbmcuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfHF3ZXJ0e'
    'XVpb3AiLCJhdWQiOiJjbGllbnQtaWQtZnJvbS1hdXRoMCEiLCJpYXQiOjEyMzQ1Njc4fQ.'
    'OyBmHCupl2OLVR1IhJN0FK7ow1keMpiAjHTvSp2Z0z0',
    # Secret mismatch (secret = 'other')
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
    'eyJpc3MiOiJodHRwczovL3Rlc3RpbmcuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfHF3ZXJ0e'
    'XVpb3AiLCJhdWQiOiJjbGllbnQtaWQtZnJvbS1hdXRoMCIsImlhdCI6MTIzNDU2Nzh9.'
    'puu4Z99xI-4R_4QscZ6RZ2beEIvNx9yEY31quUPQFDk',
    # Expired
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
    'eyJpc3MiOiJodHRwczovL3Rlc3RpbmcuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfHF3ZXJ0e'
    'XVpb3AiLCJhdWQiOiJjbGllbnQtaWQtZnJvbS1hdXRoMCIsImlhdCI6MTIzNDU2NzgsImV4cC'
    'I6MTIzNDU2Nzl9.'
    'NKGfZC2Ht1BeOPwyW_cAuQXfH4MVBlc38q0S4_O5gow',
    # Weird token
    'what',
])
def test_get_decoded_token_bad_secret(token):
    from django.conf import settings
    with pytest.raises(ValueError):
        get_decoded_token(
            token,
            settings.AUTH0_CLIENT_SECRET,
            settings.AUTH0_CLIENT_ID,
        )
