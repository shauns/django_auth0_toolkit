# TODO support 'get user model' approach
from django.contrib.auth.models import User


class Auth0Backend(object):
    """ Handle auth0 backed authentication, by serialising auth0 data into a
    standard Django user.

    """

    def authenticate(self, user_info=None):
        # TODO in newer Django, username has flexible length
        username = user_info['user_id'][-30:]

        is_new = False
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username, password='auth0')
            is_new = True

        user.is_new = is_new

        if user_info.get('email') and not user.email:
            user.email = user_info['email'][:254]

        if user_info.get('family_name') or user_info.get('given_name'):
            if user_info.get('family_name') and not user.last_name:
                user.last_name = user_info['family_name'][:30]
            if user_info.get('given_name') and not user.first_name:
                user.first_name = user_info['given_name'][:30]

        elif user_info.get('name') and ' ' in user_info.get('name'):
            names = user_info.get('name').split(' ', 1)
            if not user.first_name:
                user.first_name = names[0][:30]
            if not user.last_name:
                user.last_name = names[1][:30]

        # TODO extension hooks for profile and e.g. is_staff/superuser

        user.save()

        return user

    def get_user(self, user_id):
        return User.objects.get(pk=user_id)
