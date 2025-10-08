from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailOrUsernameBackend(ModelBackend):
    """Authenticate with either email or username (case-insensitive)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None or password is None:
            return None
        lookup = {'username__iexact': username}
        if '@' in username:
            lookup = {'email__iexact': username}
        try:
            user = User.objects.get(**lookup)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

