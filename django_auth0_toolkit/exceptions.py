class Auth0Exception(Exception):
    pass


class InvalidTokenException(Auth0Exception):
    def __init__(self, token):
        self.token = token
