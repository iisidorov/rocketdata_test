from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique id
    for authentication instead of login(username).
    """
    def create_user(self, email, password, **kwargs):
        """
        Create and save a User with the given email, password and kwargs.
        """
        if not email: raise ValueError(_('Enter the email.'))
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        """
        Create and save a SuperUser with the given email, password and kwargs.
        """
        return self.create_user(email, password, **kwargs, is_staff=True, is_superuser=True)
