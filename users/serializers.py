from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import EmailValidator, RegexValidator

from .models import User, EmailOTPDevice


class UserSerializer(serializers.ModelSerializer):
    """
    For creating and updating user accounts
    """

    email = serializers.EmailField(
        validators=[
            EmailValidator(),
            UniqueValidator(
                queryset=User.objects.all(), message="Email already exists"
            ),
        ],
    )
    first_name = serializers.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                r"^[a-zA-Z-' ]+$",
                "Name must include letters, hyphens, or apostrophes only",
            ),
        ],
        required=False,
    )

    last_name = serializers.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                r"^[a-zA-Z-' ]+$",
                "Name must include letters, hyphens, or apostrophes only",
            ),
        ],
        required=False,
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "user_type",
            "is_approved",
        )
        read_only_fields = (
            "is_active",
            "date_joined",
        )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and getattr(request, "user", None):
            user = request.user
            if not user.is_staff:  # If not staff, remove these fields
                fields.pop("is_superuser")
                fields.pop("is_staff")
                fields.pop("is_approved")
                fields.pop("user_type")
        return fields

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    For logging in users
    """

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

class EmailOTPDeviceSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()