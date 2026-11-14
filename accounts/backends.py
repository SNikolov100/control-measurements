from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if not username or password is None:
            return None

        username = username.strip()
        if "@" in username:
            try:
                user = UserModel.objects.get(email__iexact=username)
            except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
                pass
            else:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user

        return super().authenticate(request, username=username, password=password,**kwargs)