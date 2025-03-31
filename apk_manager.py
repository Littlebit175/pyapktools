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
import threading
from typing import List, Dict

# ログ設定
logging.basicConfig(
    filename='apk_manager_error.log',
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    force=True  # 既存のハンドラーを上書き
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
            
        if isinstance(command, str):
            # Windows用のコマンドパーシング（shlexでPOSIXモード無効化）
            base_cmd.extend(shlex.split(command, posix=False))
        else:
            base_cmd.extend(command)
        
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
        input_file (str): パッケージリストファイルパス
    """
    try:
        if input_file:
            with open(input_file, 'r', encoding='utf-8') as f:
                package_names = [line.strip() for line in f if line.strip()]
        if not package_names:
            raise ValueError("パッケージ名が指定されていません")

        os.makedirs("apks", exist_ok=True)
        total = len(package_names)
        success_count = 0
        failed_packages = []

        print(f"合計 {total} 個のパッケージをダウンロードします...")

        for idx, package in enumerate(package_names, 1):
            print(f"\n[{idx}/{total}] {package} をダウンロード中...")
            try:
                result = run_adb_command(f"shell pm path {package}", device_id)
                package_dir = os.path.join("apks", package)
                os.makedirs(package_dir, exist_ok=True)

                apk_count = 0
                for line in result.stdout.splitlines():
                    if line.startswith("package:"):
                        apk_path = line[8:].strip()  # tripをstripに修正
                        print(f"  APKファイル: {os.path.basename(apk_path)} をダウンロード中...")
                        pull_cmd = ["pull", apk_path, os.path.abspath(package_dir)]
                        run_adb_command(pull_cmd, device_id)
                        apk_count += 1
                
                print(f"  ✓ {apk_count} 個のAPKファイルをダウンロードしました")
                success_count += 1

            except Exception as e:
                error_msg = f"パッケージ {package} のダウンロード中にエラー: {str(e)}"
                print(f"  ✗ {error_msg}")
                logging.error(error_msg, exc_info=True)  # スタックトレースを含める
                failed_packages.append(package)

        # 結果をログに記録
        result_msg = f"\n完了: {success_count}/{total} 成功"
        print(result_msg)
        if success_count < total:
            logging.error(result_msg)
            logging.error("失敗したパッケージ: %s", ", ".join(failed_packages))

        if failed_packages:
            print("失敗したパッケージ:")
            for pkg in failed_packages:
                print(f"  - {pkg}")

    except Exception as e:
        error_msg = f"APKダウンロード処理でエラー: {str(e)}"
        logging.error(error_msg, exc_info=True)
        print(f"エラーが発生しました: {error_msg}")
        raise

def install_apk(device_ids: List[str] = None, input_file: str = None, devices_csv: str = None, max_workers: int = 4, grant_permissions: bool = False) -> None:
    """
    APKを並列インストール
    
    Args:
        device_ids (List[str], optional): デバイスIDリスト
        input_file (str): パッケージリストファイル（get_appsで出力した形式）
        devices_csv (str, optional): get_devicesで出力したデバイス情報CSV
        max_workers (int): 最大同時接続数（デフォルト4）
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading
    from tqdm import tqdm
    
    try:
        if devices_csv:
            device_ids = []
            with open(devices_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                device_ids = [row['device_id'] for row in reader]
        
        if not device_ids:
            raise ValueError("デバイスIDが指定されていません")

        with open(input_file, 'r', encoding='utf-8') as f:
            packages = [line.strip() for line in f if line.strip()]
        
        if not packages:
            raise ValueError("パッケージリストが空です")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        print_lock = threading.Lock()
        progress_bar = tqdm(total=len(device_ids)*len(packages), desc="インストール進捗", unit="pkg")

        def device_install(device: str) -> dict:
            """個別デバイスへのインストール処理"""
            nonlocal packages, script_dir
            failed_packages = []
            
            for package in packages:
                package_dir = os.path.join(script_dir, "apks", package)
                apk_files = []
                
                try:
                    if not os.path.exists(package_dir):
                        with print_lock:
                            tqdm.write(f"{device}: パッケージディレクトリ不存在 {package_dir}")
                        failed_packages.append(package)
                        progress_bar.update(1)
                        continue

                    files = [f for f in os.listdir(package_dir) if f.endswith('.apk')]
                    apk_files = [os.path.join("apks", package, f) for f in files]
                    
                    if not apk_files:
                        with print_lock:
                            tqdm.write(f"{device}: APKファイル不存在 {package}")
                        failed_packages.append(package)
                        progress_bar.update(1)
                        continue

                    install_cmd = ["install-multiple", "-r"]
                    if grant_permissions:
                        install_cmd.append("-g")
                    install_cmd += apk_files
                    
                    # リトライメカニズム（最大3回）
                    for attempt in range(3):
                        try:
                            run_adb_command(install_cmd, device)
                            with print_lock:
                                tqdm.write(f"{device}: {package} インストール成功 (試行{attempt+1}回目)")
                            break
                        except Exception as e:
                            if attempt == 2:
                                raise
                            time.sleep(1)
                            
                    progress_bar.update(1)
                    
                except Exception as e:
                    with print_lock:
                        tqdm.write(f"{device}: {package} インストール失敗 - {str(e)}")
                    failed_packages.append(package)
                    progress_bar.update(1)
            
            return {device: failed_packages}

        print(f"\n{len(packages)} パッケージを {len(device_ids)} デバイスに並列インストール...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(device_install, device) for device in device_ids]
            failed_devices = {}
            
            for future in as_completed(futures):
                result = future.result()
                failed_devices.update(result)

        progress_bar.close()
        success_devices = [d for d in device_ids if d not in failed_devices]
        
        print(f"\n完了: 成功 {len(success_devices)}/{len(device_ids)} デバイス")
        if failed_devices:
            print("\n失敗したデバイスとパッケージ:")
            for dev, pkgs in failed_devices.items():
                print(f"  デバイス {dev}:")
                for pkg in pkgs:
                    print(f"    - {pkg}")

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
    package_group.add_argument('-f', '--file', help='パッケージリストファイル（get_appsで出力した形式）')
    dl_parser.add_argument('-d', '--device', help='対象デバイスID')
    
    # APKインストール
    install_parser = subparsers.add_parser('install', help='APKインストール')
    device_group = install_parser.add_mutually_exclusive_group(required=True)
    device_group.add_argument('-d', '--devices', nargs='+', help='デバイスIDリスト')
    device_group.add_argument('-c', '--csv', help='get_devicesで出力したデバイス情報CSV')
    install_parser.add_argument('-f', '--file', required=True, help='パッケージリストファイル（get_appsで出力した形式）')
    install_parser.add_argument('-g', '--grant-permissions', action='store_true', help='権限を自動付与（-gオプション）')
    
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
            install_apk(
                device_ids=args.devices,
                input_file=args.file,
                devices_csv=args.csv,
                grant_permissions=args.grant_permissions
            )
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()