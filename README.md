# Android APK管理ツール

## 概要
ADBコマンドを利用した高度なAndroidデバイス向けAPK管理ツールです。以下の機能を提供します。

## 主な機能
- 接続デバイス情報のCSV出力（マルチデバイス対応）
- インストール済みユーザーアプリ一覧のテキスト出力（フィルタリング機能付き）
- 複数APKの一括ダウンロード（Android → PC）
- 複数APKの一括インストール（PC → Android）
- 分割APK対応（自動マージ機能）
- 詳細エラーログ出力（エラー箇所特定機能）
- Windows/Linuxクロスプラットフォーム対応

## 新機能（v1.1）
- 強化されたパス処理（特殊文字/空白文字対応）
- 高度なデバッグモード（VSCode統合）
- 自動リトライ機能（ネットワーク不安定時）
- 進捗表示機能（リアルタイムプログレスバー）
- セーフモード（システムファイル保護）

## 動作環境
- **OS**: Windows 11 / Ubuntu 22.04 LTS
- **Python**: 3.10以上
- **必須ツール**:
  - ADB（Android Debug Bridge）v33.0.3以上
  - VSCode（デバッグ機能利用時）

## インストール
```bash
git clone https://github.com/your-repository/apk-manager.git
cd apk-manager
pip install -r requirements.txt
```

## 基本使用方法
### デバイス管理
```bash
# 接続デバイス一覧取得（CSV出力）
python apk_manager.py get_devices -o devices.csv

# アプリ一覧取得（テキスト出力）
python apk_manager.py apps -o apps.txt -d [デバイスID]
```

### APK操作
```bash
# 複数APKダウンロード（ファイル指定）
python apk_manager.py download -f apps.txt -d ABCD1234

# 分割APKインストール
python apk_manager.py install -p ./apks/package_name -d ABCD1234
```

## 高度な使用方法
### デバッグモード
1. VSCodeでプロジェクトを開く
2. `F5`キーでデバッグ開始
3. デバイスID入力プロンプトに接続デバイスのIDを入力

```bash
# デバッグログ有効化（詳細出力）
python apk_manager.py --debug [command]
```

### バッチ処理
```bash
# 複数デバイスへの一括インストール
python apk_manager.py batch-install -i devices.csv -p ./apks
```

## トラブルシューティング
```bash
# エラーログ確認
tail -f apk_manager_error.log

# ADB接続テスト
python apk_manager.py test-connection -d ABCD1234

# セーフモード起動
python apk_manager.py --safe-mode [command]
```

## 開発者向け情報
### デバッグ環境設定
`.vscode/launch.json` に以下のデバッグプロファイルが含まれます：
- APKダウンロードデバッグ
- ユニットテスト実行
- カバレッジ計測
- 複合デバッグセット

### テスト実行
```bash
# ユニットテスト（詳細出力）
python -m pytest tests/ -v

# カバレッジレポート生成
python -m pytest --cov=apk_manager --cov-report=html
```

## ライセンス
MIT License