from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

# Create your views here.

class PasswordReset(PasswordResetView):
     """パスワードのリセット送信画面"""

     template_name = "accounts/password-reset.html"
     success_url = reverse_lazy(
          "accounts:password-reset-done"
     )
     email_template_name = "mail/password-reset-email.txt"
     subject_template_name = "mail/password-reset-subject.txt"

class PasswordResetDone(PasswordResetDoneView):
     """パスワードリセットメール送信完了画面"""

     template_name = "accounts/password-reset-done.html"

class PasswordResetConfirm(PasswordResetConfirmView):
     """新しいパスワード設定画面"""

     template_name = "accounts/password-reset-confirm.html"
     success_url = reverse_lazy(
          "accounts:password-reset-complete"
     )

class PasswordResetComplete(PasswordResetCompleteView):
     """パスワードの設定の完了画面"""

     template_name = "accounts/password-reset-complete.html"
