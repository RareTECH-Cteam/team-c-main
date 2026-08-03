from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager # Djangoの認証機能から2つのクラスを読み込んでいますAbstractUserはUserモデルの土台,BaseUserManagerはカスタムUserManagerを作る土台
class UserManager(BaseUserManager): # BaseUserManagerを継承したクラスの定義
    def create_user(self, email, password=None, **extra_fields): # 通常ユーザーの作成用メソッド
        if not email:
            raise ValueError("メールアドレスは必須です") # emailが空ならエラーを返します

        email = self.normalize_email(email) # ドメイン部分(@より後ろ)を正規化(大小の文字のの統一)
        user = self.model(email=email, **extra_fields) # ユーザーインスタンスの作成
        user.set_password(password) # パスワードをハッシュ化して保存
        user.save(using=self._db) # DBへの保存がされる

        return user # Userインスタンスを呼び出し元に戻す
    
    def create_superuser(self, email, password=None, **extra_fields): # 管理ユーザー作成用メソッド
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
# extra_fields辞書に該当キーがまだ存在していない場合のみ指定の値をセットする処理

        if extra_fields.get("is_staff") is not True: # 値の取得True以外なら例外処理
            raise ValueError("管理者はis_staff=Trueである必要があります") # 例外時の呼び出し処理

        if extra_fields.get("is_superuser") is not True: # 値の取得True以外なら例外処理
            raise ValueError("管理者はis_superuser=Trueである必要があります")# 例外時の呼び出し処理

        return self.create_user(email, password, **extra_fields)
    # extra_fieldsを使ってcreate_userを呼び出し作成済ユーザーを返す

class User(AbstractUser): # カスタムユーザーの仮定義
    username = None # ユーザーnameでのログインを無効化

    email = models.EmailField(
        unique=True, # メールアドレスに一意制約をつけている
        verbose_name="メールアドレス", # 管理画面などでの表示名
    )

    name = models.CharField(
        max_length=50, # nameの文字数を50文字以内に制限している
        verbose_name="ユーザー名", # 管理画面などでの表示名
    )

    USERNAME_FIELD = "email" # ログインに使用するフィールドをemailに指定
    REQUIRED_FIELDS = ["name"] # スーパーユーザー作成時に入力必須にするフィールドを指定

    objects = UserManager() # UserManagerをデフォルトに差し替え

    def __str__(self):
        return self.email
# 管理画面やshellでUserインスタンスを表示する際にemailを返す