"""
Auth URL configuration.
"""
from django.urls import path

from .views import LoginView, RefreshTokenView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
]
