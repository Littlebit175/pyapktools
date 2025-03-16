#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Android APK管理ツール

機能概要:
1. 接続デバイス情報取得（CSV出力）
2. インストール済アプリ一覧取得（テキスト出力）
3. APKダウンロード（Android → PC）
4. APKインストール（PC → Android）
"""

import argparse
import subprocess
import csv
import shlex
import os
import sys
import logging
from typing import List, Dict

# ログ設定
logging.basicConfig(
    filename='apk_manager_error.log',
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

def run_adb_command(command: str, device_id: str = None) -> subprocess.CompletedProcess:
    """
    ADBコマンドを実行する（Windows用に修正）
    
    Args:
        command (str): 実行するADBコマンド
        device_id (str, optional): 対象デバイスID
    
    Returns:
        subprocess.CompletedProcess: 実行結果
    """
    try:
        # コマンドをリスト形式で構築
        base_cmd = ["adb"]
        if device_id:
            base_cmd.extend(["-s", device_id])
        # Windows用のコマンドパーシング（shlexでPOSIXモード無効化）
        base_cmd.extend(shlex.split(command, posix=False))
        
        logging.info(f"実行コマンド: {' '.join(base_cmd)}")
        
        return subprocess.run(
            base_cmd,
            shell=False,
            check=True,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        error_msg = f"ADBエラー: {e.stderr}\nコマンド: {' '.join(e.cmd)}"
        logging.error(error_msg)
        raise RuntimeError(error_msg) from e
    except FileNotFoundError:
        logging.error("ADBが見つかりません。PATHを確認してください")
        raise

def get_connected_devices(output_file: str) -> None:
    """
    接続デバイス情報をCSVに出力
    
    Args:
        output_file (str): 出力CSVファイル名
    """
    try:
        result = run_adb_command("devices -l")
        devices = []
        
        # デバイス情報解析
        for line in result.stdout.splitlines()[1:]:
            if "device" in line and not line.startswith("*"):
                parts = line.split()
                device_id = parts[0]
                model = next((p.split(':')[1] for p in parts if p.startswith('model:')), 'N/A')
                android_version = next((p.split(':')[1] for p in parts if p.startswith('release:')), 'N/A')
                
                devices.append({
                    'device_id': device_id,
                    'model': model,
                    'android_version': android_version
                })
        
        # CSV書き込み
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['device_id', 'model', 'android_version'])
            writer.writeheader()
            writer.writerows(devices)
            
    except Exception as e:
        logging.error(f"デバイス情報取得エラー: {e}")
        raise

def get_installed_apps(output_file: str, device_id: str = None) -> None:
    """
    インストール済アプリ一覧を取得（パッケージ名のみ抽出）
    
    Args:
        output_file (str): 出力ファイル名
        device_id (str, optional): 対象デバイスID
    """
    try:
        result = run_adb_command("shell pm list packages -f -3", device_id)
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in result.stdout.splitlines():
                if line.strip():
                    # 最後の'='以降のパッケージ名を抽出
                    package_name = line.strip().rsplit('=', 1)[-1]
                    f.write(package_name + '\n')
    except Exception as e:
        logging.error(f"アプリ一覧取得エラー: {e}")
        raise

def download_apk(package_names: List[str] = None, device_id: str = None, input_file: str = None) -> None:
    """
    APKをダウンロード
    
    Args:
        package_names (List[str], optional): パッケージ名リスト（非推奨）
        device_id (str, optional): 対象デバイスID
        input_file (str, optional): パッケージリストファイルパス
    """
    try:
        # パッケージ名をファイルから読み込む
        if input_file:
            with open(input_file, 'r', encoding='utf-8') as f:
                package_names = [line.strip() for line in f if line.strip()]
        if not package_names:
            raise ValueError("パッケージ名が指定されていません")

        # APKsディレクトリを作成
        os.makedirs("apks", exist_ok=True)

        for package in package_names:
            # パッケージのAPKパスを取得
            result = run_adb_command(f"shell pm path {shlex.quote(package)}", device_id)
            
            # パッケージ用のディレクトリを作成
            package_dir = os.path.join("apks", package)
            os.makedirs(package_dir, exist_ok=True)

            # 各APKファイルをダウンロード
            for line in result.stdout.splitlines():
                if line.startswith("package:"):
                    # package:プレフィックスを除去してパスを取得
                    apk_path = line[8:].strip()
                    
                    # パスの正規化とクォート処理
                    safe_path = f'"{apk_path}"'
                    safe_dest = f'"{os.path.abspath(package_dir)}"'
                    
                    # APKファイルをダウンロード
                    run_adb_command(f"pull {safe_path} {safe_dest}", device_id)

    except Exception as e:
        logging.error(f"APKダウンロードエラー: {e}")
        raise

def install_apk(device_ids: List[str], package_dir: str) -> None:
    """
    APKをインストール
    
    Args:
        device_ids (List[str]): デバイスIDリスト
        package_dir (str): パッケージディレクトリ
    """
    try:
        apk_files = [os.path.join(package_dir, f) for f in os.listdir(package_dir) if f.endswith('.apk')]
        if not apk_files:
            raise ValueError("APKファイルが見つかりません")
            
        for device in device_ids:
            # 分割APK対応のためinstall-multipleを使用し、フルパスを指定
            apk_paths = [f'"{f}"' for f in apk_files]
            run_adb_command(f"install-multiple {' '.join(apk_paths)}", device)
            
    except Exception as e:
        logging.error(f"APKインストールエラー: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Android APK管理ツール')
    subparsers = parser.add_subparsers(dest='command')
    
    # デバイス情報取得
    devices_parser = subparsers.add_parser('get_devices', help='接続デバイス情報取得')
    devices_parser.add_argument('-o', '--output', required=True, help='出力CSVファイル名')
    
    # アプリ一覧取得
    apps_parser = subparsers.add_parser('get_apps', help='インストール済アプリ一覧取得')
    apps_parser.add_argument('-o', '--output', required=True, help='出力ファイル名')
    apps_parser.add_argument('-d', '--device', help='対象デバイスID')
    
    # APKダウンロード
    dl_parser = subparsers.add_parser('download', help='APKダウンロード')
    # パッケージ指定方法（ファイルまたは直接指定）
    package_group = dl_parser.add_mutually_exclusive_group(required=True)
    package_group.add_argument('-p', '--packages', nargs='+', help='直接パッケージ名を指定（スペース区切り）')
    package_group.add_argument('-f', '--file', type=argparse.FileType('r'),
                             help='パッケージリストファイル（get_appsで出力した形式）')
    dl_parser.add_argument('-d', '--device', help='対象デバイスID')
    
    # APKインストール
    install_parser = subparsers.add_parser('install', help='APKインストール')
    install_parser.add_argument('-d', '--devices', nargs='+', required=True, help='デバイスIDリスト')
    install_parser.add_argument('-p', '--package_dir', required=True, help='パッケージディレクトリ')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'get_devices':
            get_connected_devices(args.output)
            
        elif args.command == 'get_apps':
            get_installed_apps(args.output, args.device)
            
        elif args.command == 'download':
            download_apk(
                package_names=args.packages,
                device_id=args.device,
                input_file=args.file
            )
            
        elif args.command == 'install':
            install_apk(args.devices, args.package_dir)
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()