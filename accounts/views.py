from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm
from django.contrib.auth import authenticate, login


def signup(request):                #signupにアクセスが来たときに呼び出し
    """新規作成を行う処理"""

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()      #SignupFormのsave()が実行されてパスワードをハッシュ化したうえでUserをDBに保存

            return redirect("accounts:login")

    else:
        form = SignupForm()

    context = {
        "form": form
    }
    return render(request, "accounts/sign-up.html", context)

def login_view(request):
     if request.user.is_authenticated:

          return redirect("conversions:convert")

     if request.method == "POST":
          form = LoginForm(request.POST)

          if form.is_valid():
               email = form.cleaned_data["email"]
               password = form.cleaned_data["password"]

               user = authenticate(
                    request,
                    email=email,
                    password=password,
               )

               if user is not None:
                    login(request, user)
                    return redirect("conversions:convert")

               else:
                    form.add_error(
                         None,
                         "メールアドレスまたはパスワードが正しくありません"
                    )


     else:
          form = LoginForm()

     context = {
          "form": form,
     }
     return render(request, "accounts/login.html", context)