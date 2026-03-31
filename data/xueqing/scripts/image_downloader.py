#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片下载模块
从 URL 下载图片到本地临时目录
"""

import urllib.request
import ssl
import os
import time
import json
from datetime import datetime


class ImageDownloader:
    def __init__(self, output_dir, timeout=30, retry_times=3, retry_delay=2):
        self.output_dir = output_dir
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self.download_log = []

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 创建 SSL 上下文（不验证证书）
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def download_image(self, url, row_num):
        """
        下载单张图片

        Args:
            url: 图片 URL
            row_num: 源文件行号

        Returns:
            tuple: (success, file_path, error_msg)
        """
        filename = f"row_{row_num}_{int(time.time())}.jpg"
        file_path = os.path.join(self.output_dir, filename)

        for attempt in range(self.retry_times):
            try:
                # 创建请求，添加 User-Agent
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )

                # 下载图片
                with urllib.request.urlopen(req, context=self.ssl_context, timeout=self.timeout) as response:
                    data = response.read()

                # 保存文件
                with open(file_path, 'wb') as f:
                    f.write(data)

                # 验证文件大小
                if os.path.getsize(file_path) > 0:
                    self.download_log.append({
                        'row_num': row_num,
                        'url': url,
                        'file_path': file_path,
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    })
                    return True, file_path, None
                else:
                    raise Exception("Downloaded file is empty")

            except Exception as e:
                error_msg = str(e)
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    self.download_log.append({
                        'row_num': row_num,
                        'url': url,
                        'status': 'failed',
                        'error': error_msg,
                        'timestamp': datetime.now().isoformat()
                    })
                    return False, None, error_msg

        return False, None, "Unknown error"

    def batch_download(self, url_dict):
        """
        批量下载图片

        Args:
            url_dict: {row_num: url} 字典

        Returns:
            dict: {row_num: file_path} 成功下载的图片路径
        """
        results = {}
        total = len(url_dict)
        success_count = 0
        fail_count = 0

        print(f"开始下载 {total} 张图片...")

        for idx, (row_num, url) in enumerate(url_dict.items(), 1):
            success, file_path, error = self.download_image(url, row_num)

            if success:
                results[row_num] = file_path
                success_count += 1
            else:
                fail_count += 1
                print(f"[错误] 行 {row_num} 下载失败: {error}")

            # 每 10 张显示进度
            if idx % 10 == 0 or idx == total:
                print(f"[进度] {idx}/{total} 完成 (成功: {success_count}, 失败: {fail_count})")

        print(f"\n下载完成: 成功 {success_count}, 失败 {fail_count}")
        return results

    def save_log(self, log_file):
        """保存下载日志"""
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.download_log, f, ensure_ascii=False, indent=2)
        print(f"日志已保存: {log_file}")
