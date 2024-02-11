from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

import logging

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        logging.info(f'Authenticating: email={email}, password={password}')
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            logging.warning(f'User does not exist: email={email}')
            return None

        if user.check_password(password):
            return user

        logging.warning(f'Incorrect password: email={email}')
        return None

    def get_user(self, user_id):
        logging.info(f'Getting user: user_id={user_id}')
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            logging.warning(f'User does not exist: user_id={user_id}')
            return None