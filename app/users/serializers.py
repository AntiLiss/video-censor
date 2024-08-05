from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer

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


class EmailChangeSerializer(serializers.ModelSerializer):
    """Serializer to change email"""

    class Meta:
        model = User
        fields = ("email",)


class EmailChangeResponseSerializer(serializers.Serializer):
    """Custom response for email change view"""

    detail = serializers.CharField()
