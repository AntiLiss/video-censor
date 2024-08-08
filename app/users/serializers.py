from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Profile

User = get_user_model()


class UserRegisterSerializer(RegisterSerializer):
    """User registration serializer"""

    # Override to remove username field
    username = None

    def validate_email(self, email):
        # Return err when email duplicates even if it's not verified
        if User.objects.filter(email=email):
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address."),
            )
        return super().validate_email(email)


class UserLoginSerializer(LoginSerializer):
    """User login serializer"""

    # Override to remove username field
    username = None


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer"""

    class Meta:
        model = User
        fields = ("id", "email")
        read_only_fields = ("id", "email")


class EmailSerializer(serializers.ModelSerializer):
    """Serializer to update user's email"""

    class Meta:
        model = User
        fields = ("email",)


class EmailResponseSerializer(serializers.Serializer):
    """Custom response for email change view"""

    detail = serializers.CharField()


class ProfileSerializer(serializers.Serializer):
    """User's profile serializer"""

    class Meta:
        model = Profile
        fields = ("id", "user", "profile_photo")
        read_only_fields = ("id", "user")
