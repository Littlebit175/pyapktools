# Android APK管理ツール

Androidデバイスに対するAPKの管理を支援するコマンドラインツールです。

## 機能

1. 接続デバイス情報の取得（CSV出力）
2. インストール済アプリ一覧の取得
3. APKのダウンロード（Android → PC）
4. APKのインストール（PC → Android）

## 使用方法

### 1. デバイス情報の取得

接続されているAndroidデバイスの情報をCSVファイルに出力します。

```bash
python apk_manager.py get_devices -o devices.csv
```

### 2. アプリ一覧の取得

デバイスにインストールされているアプリの一覧を取得します。

```bash
# 単一デバイスの場合
python apk_manager.py get_apps -o apps.txt -d <デバイスID>

# デバイスIDを省略すると、接続されている最初のデバイスが対象になります
python apk_manager.py get_apps -o apps.txt
```

### 3. APKのダウンロード

デバイスからAPKファイルをダウンロードします。

```bash
# テキストファイルからパッケージ名を読み込む場合
python apk_manager.py download -f apps.txt -d <デバイスID>

# パッケージ名を直接指定する場合
python apk_manager.py download -p com.example.app1 com.example.app2 -d <デバイスID>
```

ダウンロードしたAPKは `./apks/<パッケージ名>/` ディレクトリに保存されます。

### 4. APKのインストール

PCからデバイスにAPKをインストールします。

```bash
# デバイスIDを直接指定してインストール
python apk_manager.py install -d <デバイスID1> <デバイスID2> -f apps.txt

# get_devicesで出力したCSVファイルを使用してインストール
python apk_manager.py install -c devices.csv -f apps.txt
```

指定されたパッケージリストに基づいて、`./apks/<パッケージ名>/`ディレクトリから
APKファイルを読み込み、指定されたデバイスにインストールします。

## 注意事項

- ADBがシステムパスに設定されている必要があります
- デバイスのUSBデバッグが有効になっている必要があります
- エラーログは `apk_manager_error.log` に出力されます
- Split APKsにも対応しています
- Android設定で以下を有効にする必要があります：
  1. 開発者オプション > USBデバッグ
  2. 開発者オプション > 不明なアプリのインストールを許可
  3. セキュリティ設定 > 提供元不明のアプリ（デバイスによって場所が異なる）
- インストール時に表示される確認ダイアログで「許可」を選択してください
- Android 10以降では権限の自動付与が制限される場合があります

## エラー発生時

エラーが発生した場合は、以下を確認してください：

1. ADBがインストールされ、パスが通っているか
2. デバイスが正しく接続されているか（`adb devices`で確認）
3. エラーログ（apk_manager_error.log）の内容