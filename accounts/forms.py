from django import forms
from .models import User
from django.contrib.auth.password_validation import validate_password

class SignupForm(forms.ModelForm):
    """新規登録のフォーム"""

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "パスワードを入力して下さい",
                "autocomplete": "new-password"
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "もう一度パスワードを入力してください",
                "autocomplete": "new-password"
            }
        )
    )

    class Meta:
        model = User

        fields = [
            "email",
            "name",
        ]

        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "メールアドレスを入力してください",
                    "autocomplete": "email"
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "placeholder": "名前を入力してください",
                    "autocomplete": "name"
                }
            ),
        }

    def clean_email(self):
        """emailの検証"""

        email = self.cleaned_data["email"]

        if email != email.lower():
            raise forms.ValidationError(
                "メールアドレスはすべて小文字で入力してください"
            )

        email = User.objects.normalize_email(email).lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "このメールアドレスは既に登録されています"
            )

        return email

    def clean(self):
        """passwordの検証"""

        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "パスワードが一致していません"
            )
        if password1:
            validate_password(password1, user=self.instance)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password1"]
        )

        if commit:
            user.save()

        return user
class LoginForm(forms.Form):
    """ログインフォーム"""
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "メールアドレスを入力してください",
                "autocomplete": "email"
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "パスワードを入力してください",
                "autocomplete": "current-password"
            }
        )
    )