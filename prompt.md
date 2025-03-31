# 指示
- 下記仕様のPythonスクリプトを作成してください。
  - ファイルヘッダコメント、関数ヘッダコメント、コードの説明を日本語で丁寧に記載すること
- requirement.txtを作成すること
- Pythonスクリプトの機能一覧や使い方を日本語で記したREADME.mdを作成すること

# 動作環境
- Windows 11 / Ubuntu　（双方で動作すること）
- VSCode

# ユースケース
- AndoidからPCへ複数のapkを一括ダウンロードしたい
- PCからAndroidへ複数のapkを一括インストールしたい

## 接続デバイス情報取得
- PCに接続された複数のAndroidのデバイス情報を取得し、CSV出力すること
- CSV出力するデバイス情報
  - デバイスID
  - モデル名
  - Androidバージョン
- コマンドライン引数で本機能を選択し、実行できること
- 出力するCSVファイル名はコマンドライン引数で指定できること

## インストール済アプリ一覧取得
- PCにUSB接続したAndroidにインストールされているアプリ一覧をテキストファイルに出力すること
  - 一覧化するアプリはユーザがインストールしたアプリとする（システムアプリは含まない）
  - adbコマンド例: adb shell pm list packages -f -3
- コマンドライン引数で本機能を選択し、実行できること
- 出力するファイル名はコマンドライン引数で指定できること
- 複数のAndroidを接続している場合は、取得対象をデバイスIDで指定できること
  - Androidを１台しか接続していない場合、本コマンドライン引数は任意でよい

## インストール済アプリのapkダウンロード (Android -> PC)
- コマンドライン引数で本機能を選択し、実行できること
- コマンドライン引数でダウンロード対象のアプリを複数指定できること
  - 指定フォーマットは、「インストール済アプリ一覧取得」で出力したテキストファイルと同様とする
- 複数のAndroidを接続している場合は、取得対象をデバイスIDで指定できること
  - Androidを１台しか接続していない場合、本コマンドライン引数は任意でよい
- コマンドライン引数でダウンロードしたいアプリのパッケージ名を指定できること
  - 例: jp.ne.paypay.android.app
- カレントディレクトリ内にパッケージ名（上記例の場合"jp.ne.paypay.android.app"）のフォルダを新規作成し、そのフォルダ内にダウンロードしたapkファイルを格納すること
- apkが複数に分割されている場合、すべての分割apkをすべてダウンロードすること
  - 例えば下記adbコマンドで分割されているかどうか判別できる（paypayは４つのapkに分割されている）
    - adb shell pm path jp.ne.paypay.android.app
      - package:/data/app/~~sLwpDiKDTEyVvoSYQYBVuA==/jp.ne.paypay.android.app-mkVPxbLI7UhTYZ7_1MYVxQ==/base.apk
      - package:/data/app/~~sLwpDiKDTEyVvoSYQYBVuA==/jp.ne.paypay.android.app-mkVPxbLI7UhTYZ7_1MYVxQ==/split_config.arm64_v8a.apk
      - package:/data/app/~~sLwpDiKDTEyVvoSYQYBVuA==/jp.ne.paypay.android.app-mkVPxbLI7UhTYZ7_1MYVxQ==/split_config.ja.apk
      - package:/data/app/~~sLwpDiKDTEyVvoSYQYBVuA==/jp.ne.paypay.android.app-mkVPxbLI7UhTYZ7_1MYVxQ==/split_config.xxhdpi.apk

## apkインストール (PC -> Android)
- コマンドライン引数で本機能を選択し、実行できること
- 複数のAndroidにインストールしたい場合、コマンドライン引数でデバイスIDが格納されたCSVファイルを指定できること
  - 指定フォーマットは「接続デバイス情報取得」で出力したCSVファイルと同様とする
  - Androidを１台しか接続していない場合、本コマンドライン引数は任意でよい
- コマンドライン引数でインストール対象のパッケージを指定できること
  - 指定フォーマットは、「インストール済アプリ一覧取得」で出力したテキストファイルと同様とする
  - 「インストール済アプリのapkダウンロード」で作成したフォルダ内にapkが入っているものとする
- apkが複数に分割されている場合のインストールにも対応すること

## エラーハンドリング
- 予期せぬエラーが発生した場合は、エラーログをテキストファイル出力すること


---
【追加prompt】
# get_installed_appsの変更要求
get_installed_appsにおいて、
```shell pm list packages -f -3```
の結果が下記の場合、

package:/data/app/~~khSLShYhaYc5Q4Aq6vxiBA==/jp.ne.paypay.android.app-dTIfIJaR7plW97Ruu9KyMQ==/base.apk=jp.ne.paypay.android.app

出力するテキストは
```jp.ne.paypay.android.app```
とすること。
つまり、コマンド出力の文字列を右から検索し、最初の```=```の後方の文字列を抽出すること。
これは、パッケージ名のみを抽出することを意味する。

# download_apkの変更要求
download_apkのinput_file引数として、get_installed_appsで作成したテキストファイルを入力するよう仕様変更すること。
つまり、download_apk内でパッケージ名を抽出する処理は不要である。

次に、パッケージ名でapkパスを検索する。例えば
```adb shell pm path jp.ne.paypay.android.app```
に対する応答は、
```
package:/data/app/~~khSLShYhaYc5Q4Aq6vxiBA==/jp.ne.paypay.android.app-dTIfIJaR7plW97Ruu9KyMQ==/base.apk
package:/data/app/~~khSLShYhaYc5Q4Aq6vxiBA==/jp.ne.paypay.android.app-dTIfIJaR7plW97Ruu9KyMQ==/split_config.arm64_v8a.apk
package:/data/app/~~khSLShYhaYc5Q4Aq6vxiBA==/jp.ne.paypay.android.app-dTIfIJaR7plW97Ruu9KyMQ==/split_config.ja.apk
package:/data/app/~~khSLShYhaYc5Q4Aq6vxiBA==/jp.ne.paypay.android.app-dTIfIJaR7plW97Ruu9KyMQ==/split_config.xxhdpi.apk
```
である。
これは、```jp.ne.paypay.android.app```が４つに分割されたapkであることを意味する。

また、apkのファイルパスは```package:```の後方である。
例：```/data/app/~~khSLShYhaYc5Q4Aq6vxiBA==/jp.ne.paypay.android.app-dTIfIJaR7plW97Ruu9KyMQ==/base.apk```

次に、カレントディレクトリに、```apks```ディレクトリを作成する（無ければ）。

```apks```ディレクトリ上に、```jp.ne.paypay.android.app```ディレクトリを作成する。

次に、作成したディレクトリ内に分割apkをすべてダウンロードする。
例：
```
adb pull /data/app/~~sLwpDiKDTEyVvoSYQYBVuA==/jp.ne.paypay.android.app-mkVPxbLI7UhTYZ7_1MYVxQ==/base.apk
adb pull /data/app/~~sLwpDiKDTEyVvoSYQYBVuA==/jp.ne.paypay.android.app-mkVPxbLI7UhTYZ7_1MYVxQ==/split_config.arm64_v8a.apk
adb pull /data/app/~~sLwpDiKDTEyVvoSYQYBVuA==/jp.ne.paypay.android.app-mkVPxbLI7UhTYZ7_1MYVxQ==/split_config.ja.apk
adb pull /data/app/~~sLwpDiKDTEyVvoSYQYBVuA==/jp.ne.paypay.android.app-mkVPxbLI7UhTYZ7_1MYVxQ==/split_config.xxhdpi.apk
```

main関数やinstall_apk関数なども、上記仕様変更に合わせて修正すること。


---

apk_manager.pyのAPKインストール処理について、Android端末のインストール処理時間に拘束され、
複数台のAndroid端末にインストールするに時間が掛かることが課題である。

この課題を解決するため、複数のAndroid端末に対し同時並行でインストール処理を実施するプログラムに修正して。