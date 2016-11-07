# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate, login


def register_and_login_auth0_user(request, user_info, do_login=True):
    # NB: Expects an authentication backend that can handle these kwargs.
    user = authenticate(user_info=user_info)
    if do_login and user.is_active:
        login(request, user)

    return user
