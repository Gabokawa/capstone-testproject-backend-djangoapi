from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Look up the user by email instead of username
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # No user found with that email
            return None

        if user.check_password(password):
            # If the user exists and the password is correct, return the user object
            return user
        return None

    def get_user(self, user_id):
        # Required method for a custom backend
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None