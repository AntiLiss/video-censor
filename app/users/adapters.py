from django.contrib.auth import get_user_model
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress


class CustomAccountAdapter(DefaultAccountAdapter):
    # Prevent sending email when trying to register using existing email
    def send_account_already_exists_mail(self, email):
        pass


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    # If the social email matches the local email then automatically
    # connect the social to the user
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email")

        # Skip if the social already connected to user
        if sociallogin.is_existing:
            return

        try:
            # Check if a user with this email already exists
            user = get_user_model().objects.get(email=email)
            # Link the social account to that user
            sociallogin.connect(request, user)
            
            # Set the email as verified
            email_address = EmailAddress.objects.filter(
                user=user,
                email=email,
            )
            if email_address:
                email_address[0].verified = True
                email_address[0].save()
        except get_user_model().DoesNotExist:
            pass
