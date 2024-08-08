import os

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


def get_profile_image_path(instance, filename):
    """Generate profile image path"""
    return os.path.join("uploads", "user", filename)


class UserManager(BaseUserManager):
    """User model manager"""

    def create_user(self, email, password=None, **fields):
        user = self.model(
            email=self.normalize_email(email),
            **fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **fields):
        fields.setdefault("is_staff", True)
        fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model"""

    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    objects = UserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    """Users' profile model"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    profile_photo = models.ImageField(
        upload_to=get_profile_image_path, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
