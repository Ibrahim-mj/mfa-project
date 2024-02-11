from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from django_otp.plugins.otp_email.models import EmailDevice


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_approved", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault(
            "user_type", "admin"
        )  # Superuser is an admin. This is used to manage the roles instead of django groups since this is a simple project.

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


USER_TYPE_CHOICES = (
    ("user", "Normal User"),
    ("admin", "Admin"),
)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=50, default="user", choices=USER_TYPE_CHOICES
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def send_verification_email(self, request):
        """
        Sends a verification email to a user
        """
        token = default_token_generator.make_token(self)
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        site = get_current_site(request)
        mail_subject = "Innovative Tech Solutions - Activate Your Account"
        message = f"""
            Hi {self.get_short_name()},
            Please click the link below to activate your account.
            http://{site.domain}{reverse('users:activate', kwargs={'uidb64': uid, 'token': token})}
            """
        html_message = f"""
            <p>Hi {self.get_short_name()},</p>
            <p>Please click the link below to activate your account.</p>
            <a href="http://{site.domain}{reverse('users:activate', kwargs={'uidb64': uid, 'token': token})}">Activate Account</a>
            """

        send_mail(
            mail_subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=html_message,
        )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class EmailOTPDevice(EmailDevice):
    class Meta:
        proxy = True
        verbose_name = "Email OTP Device"
        verbose_name_plural = "Email OTP Devices"
