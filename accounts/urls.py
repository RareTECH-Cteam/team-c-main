from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("password-reset/", views.PasswordReset.as_view(), name="password-reset"),
    path("password-reset-done/", views.PasswordResetDone.as_view(), name="password-reset-done"),
    path("password-reset-confirm/<uidb64>/<token>/", views.PasswordResetConfirm.as_view(), name="password-reset-confirm"),
    path("password-reset-complete/", views.PasswordResetComplete.as_view(), name="password-reset-complete")
    ]