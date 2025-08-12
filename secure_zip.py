# Copyright (c) 2025 n1set
# Licensed under the MIT License

import os
import hashlib
import zipfile
import getpass
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import re

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_fernet_key(password):
    """Generate a Fernet key from password."""
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt', 100000)
    return base64.urlsafe_b64encode(key[:32])

def compress_and_encrypt_folder(input_folder, output_dir=None):
    """Compress and encrypt folder using Fernet symmetric encryption."""
    if not os.path.isdir(input_folder):
        print(f"错误：目录 '{input_folder}' 不存在。")
        return False, None

    password = getpass.getpass("请输入加密密码（留空则不加密）：")
    if not password:
        print("警告：未提供密码，将创建未加密的 ZIP 文件。")
    
    fernet = Fernet(generate_fernet_key(password)) if password else None
    temp_zip = "temp.zip"
    files_to_compress = []
    
    for root, _, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, input_folder)
            files_to_compress.append((file_path, rel_path))
    
    if not files_to_compress:
        print(f"错误：目录 '{input_folder}' 中未找到文件。")
        return False, None

    try:
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path, rel_path in files_to_compress:
                with open(file_path, 'rb') as f:
                    data = f.read()
                    if fernet:
                        data = fernet.encrypt(data)
                    zf.writestr(rel_path, data)
        
        zip_hash = calculate_file_hash(temp_zip)
        output_dir = output_dir or os.getcwd()
        final_zip = os.path.join(output_dir, f"{zip_hash}.zip")
        
        if os.path.exists(final_zip):
            print(f"错误：文件 '{final_zip}' 已存在，避免重复压缩。")
            os.remove(temp_zip)
            return False, None
        
        os.rename(temp_zip, final_zip)
        print(f"成功：已压缩并加密到 '{final_zip}'")
        print(f"SHA256 哈希值：{zip_hash}")
        return True, final_zip
    
    except Exception as e:
        print(f"压缩过程中出错：{str(e)}")
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        return False, None

def decrypt_and_extract_zip(zip_file, output_dir):
    """Decrypt and extract ZIP file with automatic hash verification from filename."""
    if not os.path.exists(zip_file):
        print(f"错误：ZIP 文件 '{zip_file}' 不存在。")
        return False
    
    filename = os.path.basename(zip_file)
    expected_hash = re.match(r'^([a-f0-9]{64})\.zip$', filename)
    expected_hash = expected_hash.group(1) if expected_hash else None
    
    if expected_hash:
        actual_hash = calculate_file_hash(zip_file)
        if actual_hash != expected_hash:
            print(f"错误：哈希验证失败。预期 {expected_hash}，实际 {actual_hash}")
            return False
        print(f"哈希验证成功：{actual_hash}")
    else:
        print("警告：无法从文件名提取 SHA256 哈希值，跳过哈希验证。")
        expected_hash = input("请输入预期的 SHA256 哈希值（留空则跳过验证）：").strip()
        if expected_hash:
            actual_hash = calculate_file_hash(zip_file)
            if actual_hash != expected_hash:
                print(f"错误：哈希验证失败。预期 {expected_hash}，实际 {actual_hash}")
                return False
            print(f"哈希验证成功：{actual_hash}")
    
    password = getpass.getpass("请输入解密密码：")
    fernet = Fernet(generate_fernet_key(password)) if password else None
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zf:
            for file_info in zf.infolist():
                try:
                    data = zf.read(file_info)
                    if fernet:
                        try:
                            data = fernet.decrypt(data)
                        except Exception as e:
                            print(f"错误：解密 {file_info.filename} 失败。密码错误？")
                            return False
                        
                    output_path = os.path.join(output_dir, file_info.filename)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(data)
                except Exception as e:
                    print(f"处理 {file_info.filename} 时出错：{str(e)}")
                    return False
        
        print(f"成功：已解压并解密到 '{output_dir}'")
        return True
    
    except Exception as e:
        print(f"解压过程中出错：{str(e)}")
        return False

def main():
    current_dir = os.getcwd()
    print(f"当前目录：{current_dir}")

    zip_files = [f for f in os.listdir(current_dir) if f.endswith('.zip')]
    
    if len(zip_files) == 1:
        action = 'uzip'
        input_path = os.path.join(current_dir, zip_files[0])
        print(f"检测到一个 ZIP 文件：{input_path}")
        print("将执行解压操作")
    else:
        action = 'zip'
        input_path = current_dir
        print("未检测到 ZIP 文件，将执行压缩操作")

    user_path = input("请输入文件夹或 ZIP 文件路径（按 Enter 使用当前目录/检测到的文件）：").strip()
    if user_path:
        input_path = os.path.abspath(user_path)
    
    if action == 'zip':
        output_dir = input("请输入输出目录（留空则使用当前目录）：").strip()
        output_dir = os.path.abspath(output_dir) if output_dir else None
        success, output_file = compress_and_encrypt_folder(input_path, output_dir)
        if success and output_file:
            print(f"文件已创建：{output_file}")
    
    elif action == 'uzip':
        output_dir = input("请输入解压文件输出目录（留空则使用 extracted 文件夹）：").strip()
        output_dir = os.path.abspath(output_dir) if output_dir else os.path.join(os.getcwd(), "extracted")
        success = decrypt_and_extract_zip(input_path, output_dir)
        if success:
            print(f"文件已解压到：{output_dir}")

if __name__ == "__main__":
    main()
