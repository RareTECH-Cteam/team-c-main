from django.db import models #DjangoライブラリからDB定義用モジュールの読み込み

class ConversionTarget(models.Model): #ConversionTargetクラスの作成　(クラスはテーブルの設計図を示す)
    """
    変換相手マスタ
    例: 上司、社外向け、同僚向け、部下向け 
    """

    name = models.CharField(max_length=50, unique=True) # 名前のカラムの設定(文字数は50文字まで)
    code = models.CharField(max_length=50, unique=True) # 識別コード用カラム。(文字数制限は50文字でユニークな値になる)
    is_guest_available = models.BooleanField(default=False)  # 初期値はゲスト利用不可
    created_at = models.DateTimeField(auto_now_add=True) # 作成日用カラム(作成した時点の日時を保存する)

    class Meta: # モデル全体の追加設定
        db_table = "conversion_targets" # 今回のテーブル名を「conversion_targets」とする

    def __str__(self): # 管理画面での表示
        return self.name # 管理画面などでこのデータをnameの値で表示する


class ConversionScene(models.Model): # ConversionSceneクラスの作成　(クラスはテーブルの設計図を示す)
    """
    変換場面マスタ
    例: 依頼/謝罪/報告/お礼…みたいな選択肢を保存する 
    """

    name = models.CharField(max_length=50, unique=True) # 名前のカラムの設定(文字数は100文字まで)
    code = models.CharField(max_length=50, unique=True) # 識別コード用カラム。(文字数制限は50文字で重複不可)

    created_at = models.DateTimeField(auto_now_add=True) # 作成日用カラム(作成した時点の日時を保存する)

    class Meta: # モデル全体の追加設定
        db_table = "conversion_scenes" # 今回のテーブル名を「conversion_scenes」とする

    def __str__(self): # 管理画面での表示
        return self.name # 管理画面などでこのデータをnameの値で表示する


class ConversionRequest(models.Model): # ConversionRequestクラスの作成　(クラスはテーブルの設計図を示す)
    """
    1回の変換リクエストを保存する
    ※扱う情報は下記(中間発表時点)
    ・入力した文章
    ・変換タイプ
    ・場面（未指定可能）
    ・変換日時
    """

    input_text = models.TextField( # 入力フォームについて
        verbose_name="変換前",# 表示名
    )

    target = models.ForeignKey( # 参照キー
        ConversionTarget, # この名前のModelを持ってくる
        on_delete=models.PROTECT,# 使用中のマスタデータの削除を防ぐ
        verbose_name="変換タイプ",# 表示名を変換タイプとする
    )

    scene = models.ForeignKey( # 参照キー
        ConversionScene,# この名前のmodelを持ってくる
        on_delete=models.PROTECT,# 使用中のマスタデータの削除を防ぐ
        blank=True, # 空欄を許す
        null=True, # 空欄状態でもDBに登録できる
        verbose_name="場面タイプ", # 表示名を場面タイプ
    )

    created_at = models.DateTimeField(auto_now_add=True) # 作成日用カラム(作成した時点の日時を保存する)

    class Meta: # モデル全体の追加設定
        db_table = "conversion_requests" # 今回のテーブル名を「conversion_requests」とする


class ConversionResult(models.Model): # ConversionResultクラスの作成　(クラスはテーブルの設計図を示す)
    """
    1回の変換結果を保存する
    ※扱う情報は下記(中間発表時点)
    ・元になった変換リクエスト
    ・変換後の文章
    ・変換日時
    """

    conversion_request = models.OneToOneField( # 変換リクエストと1対1で関連付ける
        ConversionRequest, # 参照先
        related_name="result", # ConversionRequestから結果を参照するときの名前
        on_delete=models.CASCADE, # 元の変換リクエストが削除されたら結果も削除
        verbose_name="変換リクエスト", # 表示名
    )

    output_text = models.TextField( # 変換後の文章について
        verbose_name="変換後の文章", # 表示名
    )

    created_at = models.DateTimeField(auto_now_add=True) # 作成日用カラム(作成した時点の日時を保存する)

    class Meta: # モデル全体の追加設定
        db_table = "conversion_results" # 今回のテーブル名を「conversion_results」とする
