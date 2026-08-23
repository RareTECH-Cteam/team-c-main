from django import forms
from .models import User


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

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password1"]
        )

        if commit:
            user.save()

        return user
