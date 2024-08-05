from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    # If a user with the same email exists, link the social account
    # to this user.
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        email = sociallogin.user.email
        if email:
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass
