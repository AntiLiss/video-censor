import requests
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.account.utils import send_email_confirmation
from allauth.socialaccount.models import EmailAddress
from dj_rest_auth.registration.views import SocialLoginView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import EmailChangeSerializer, EmailChangeResponseSerializer


class ConfirmEmailRedirectView(APIView):
    """
    Redirect to frontend for email confirmation within needed params
    """

    # settings.EMAIL_CONFIRM_REDIRECT_URL is http://localhost:3000/email/confirm/

    # The idea is that when user is redirected to http://localhost:3000/email/confirm/{key}/
    # react immediately sends post req to `verify-email/` of backend with {key} from parameter in body.
    # And then based on server response it redirects user either to home page or shows error msg

    def get(self, request, key, *args, **kwargs):
        # return redirect(f'{settings.EMAIL_CONFIRM_REDIRECT_URL}{key}/')

        verify_url = request.build_absolute_uri(reverse("rest_verify_email"))
        res = requests.post(verify_url, {"key": key})
        return Response(res.json(), res.status_code)


# class PasswordResetConfirmRedirectView(APIView):
#     """
#     Redirect to frontend for password confirmation within needed params
#     """

#     def get(self, request, uidb64, token, *args, **kwargs):
#         return redirect(
#             f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_URL}{uidb64}/{token}/"
#         )


class EmailChangeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailChangeSerializer

    @extend_schema(responses=EmailChangeResponseSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_email_confirmation(
            request,
            request.user,
            email=request.user.email,
        )
        return Response({"detail": "Verification e-mail sent."})


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/api/users/google/callback/"
    client_class = OAuth2Client


class GoogleCallbackView(APIView):
    def get(self, request):
        code = self.request.query_params.get("code")
        url = request.build_absolute_uri(reverse("google_login"))
        print("+" * 300, code, url, sep="\n")
        # res = requests.post(url, {"code": code})
        return Response(code)
