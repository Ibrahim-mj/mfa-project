from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("user-register/", views.UserRegistrationView.as_view(), name="user-register"),
    path(
        "activate/<uidb64>/<token>/",
        views.UserAccountActivationView.as_view(),
        name="activate",
    ),
    path("user-login/", views.UserLoginView.as_view(), name="user-login"),
    path("otp-verify/", views.UserOTPVerificationView.as_view(), name="otp-verify"),
    path("user-list/", views.UserListView.as_view(), name="user-list"),
    path("user-detail/<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
]
