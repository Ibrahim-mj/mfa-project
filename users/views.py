from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate

from .models import User, EmailOTPDevice
from .serializers import UserSerializer, UserLoginSerializer, EmailOTPDeviceSerializer
from .permissions import IsAdminOrOwner


class UserRegistrationView(generics.CreateAPIView):
    """
    This is an endpoint for users to create their accounts
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.get(email=request.data.get("email"))
        user.is_active = False
        user.send_verification_email(request=request)
        user.user_type = "user"
        user.save()
        message = {
            "message": "Account created successfully, please check your email to activate your account"
        }
        response.data.update(message)
        return response

@extend_schema(parameters=[
    OpenApiParameter(name='uidb64', description='Base64 encoded user ID', type=OpenApiTypes.STR),
    OpenApiParameter(name='token', description='Account activation token', type=OpenApiTypes.STR)
])
class UserAccountActivationView(generics.RetrieveAPIView):
    """
    This is an endpoint for users to activate their accounts.
    This is a step to verify the user's email address.
    Inactive accounts are not allowed to login.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    @extend_schema(parameters=[
        OpenApiParameter(name='uidb64', description='Base64 encoded user ID', type=OpenApiTypes.STR),
        OpenApiParameter(name='token', description='Account activation token', type=OpenApiTypes.STR)
    ])

    def get_object(self):
        """
        This method decodes the uidb64 from the URL and gets the user object
        """
        uidb64 = self.kwargs.get("uidb64")
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user

    def retrieve(self, request, *args, **kwargs):
        """
        This method gets the user object and checks the token to activate the account.
        """
        super().retrieve(request, *args, **kwargs)
        instance = self.get_object()
        token = self.kwargs.get("token")
        if instance is not None and default_token_generator.check_token(
            instance, token
        ):
            instance.is_active = True
            instance.save()
            return Response(
                {
                    "message": "Account activated successfully, The Admins will approve your account soon."
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST
        )


class UserLoginView(generics.GenericAPIView):
    """
    This is an endpoint for users to login to their accounts
    """

    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def send_otp(self, user):
        email_device, created = EmailOTPDevice.objects.get_or_create(user=user)
        email_device.generate_challenge()

    def is_admin(self, user):
        return user.user_type == "admin"

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        print(email, password)

        user = authenticate(request, email=email, password=password)
        print(user)

        if user is None:
            return Response(
                {"message": "Invalid login credentials or account not activated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"message": "Your account is not yet approved"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self.is_admin(user):
            return Response(
                {"message": "Kindly use the admin login page"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.send_otp(user)

        return Response(
            {
                "message": "An OTP has been sent to your email. Please enter the code to continue"
            },
            status=status.HTTP_200_OK,
        )

class UserOTPVerificationView(generics.CreateAPIView):
    """
    This is an endpoint for users to verify their OTP and generate JWT token
    """

    queryset = User.objects.all()
    serializer_class = EmailOTPDeviceSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp = request.data.get("otp")

        user = User.objects.get(email=email)
        email_device = EmailOTPDevice.objects.get(user=user)
        if email_device.verify_token(otp):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "message": "OTP verified successfully",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "Invalid or expired OTP"},
            status=status.HTTP_400_BAD_REQUEST,
        )

class UserListView(generics.ListAPIView):
    """
    This is an endpoint for users to view the list of all users
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = User.objects.all()
        user_type = self.request.query_params.get("user_type")
        is_active = self.request.query_params.get("is_active")
        is_approved = self.request.query_params.get("is_approved")
        if user_type is not None:
            queryset = queryset.filter(user_type=user_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        if is_approved is not None:
            queryset = queryset.filter(is_approved=is_approved)
        return queryset

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    This is an endpoint for users to view the details of a specific user
    Admins can approve users and do other admin stuff here too
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner] # Could have used django groups for permissions but this could work for this small project