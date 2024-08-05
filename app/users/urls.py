from django.urls import path, include, re_path
from dj_rest_auth.views import PasswordResetConfirmView
from allauth.socialaccount.views import signup
from users.views import (
    ConfirmEmailRedirectView,
    EmailChangeView,
    GoogleLogin,
    GoogleCallbackView,
)


urlpatterns = [
    re_path(
        r"^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("email/change/", EmailChangeView.as_view()),
    path("google/callback/", GoogleCallbackView.as_view()),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("", include("dj_rest_auth.urls")),
    # Override the account_confirm_email URL
    re_path(
        r"^registration/account-confirm-email/(?P<key>[-:\w]+)/$",
        ConfirmEmailRedirectView.as_view(),
        name="account_confirm_email",
    ),
    path("registration/", include("dj_rest_auth.registration.urls")),
]


# https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=http://127.0.0.1:8000/api/users/google/callback/&prompt=consent&response_type=code&client_id=225796669062-p78i7r3b8qfk1s3bbhv7i359ekviqnfj.apps.googleusercontent.com&scope=openid%20email%20profile&access_type=offline
