import os
import requests
import re
import subprocess

# ======================
# 1. 配置
# ======================
KEYWORDS = ['荐片', '采集', '.spider']  # 您要搜索的 3 个关键词
OUTPUT_DIR = 'merge'  # 输出目录
OUTPUT_FILE = 'tvbox_raw_sources.txt'  # 输出文件名
TOKEN_ENV_NAME = 'MY_GH_TOKEN'  # 环境变量名，用于 GitHub API 搜索认证

# ======================
# 2. 从环境变量获取 GitHub Token
# ======================
gh_token = os.getenv(TOKEN_ENV_NAME)
headers = {}
if gh_token:
    headers = {
        'Authorization': f'token {gh_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
else:
    print(f"⚠️ 未检测到环境变量 {TOKEN_ENV_NAME}，将使用匿名请求（可能有速率限制）")

# Raw URL 正则（匹配类似 https://raw.githubusercontent.com/... 的链接）
RAW_URL_REGEX = re.compile(r'https://raw\.githubusercontent\.com/[\w\-]+/[\w\-]+/[\w\-]+/[\w\-/]+')

# ======================
# 3. 搜索每个关键词，获取文件内容并提取 Raw URL
# ======================
def main():
    all_raw_urls = []  # 存储所有提取到的 Raw URL

    for keyword in KEYWORDS:
        print(f"🔍 搜索关键词: {keyword}")
        url = f'https://api.github.com/search/code?q={keyword}+in:file&per_page=100'

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            items = data.get('items', [])
            print(f"✅ 找到 {len(items)} 个包含 '{keyword}' 的文件")

            for item in items:
                try:
                    # 获取文件的 GitHub 页面链接和 Raw 文件内容链接（用于调试，可选）
                    file_html_url = item.get('html_url')
                    file_path = item.get('path')
                    repo_full_name = item.get('repository', {}).get('full_name')
                    ref = item.get('sha') or 'main'  # 默认用 main 分支，实际情况可能需要解析

                    # 🌟 关键：获取文件内容（文本内容）
                    file_content_url = item.get('download_url')  # 注意：这个 download_url 是文件内容的 Raw 文本链接！
                    if not file_content_url:
                        print(f"⚠️ 文件 {file_html_url} 无内容链接，跳过")
                        continue

                    print(f"📄 获取文件内容: {file_html_url}")
                    content_response = requests.get(file_content_url, headers=headers)
                    content_response.raise_for_status()
                    file_content = content_response.text  # 文件文本内容

                    # 🎯 用正则从文件内容里提取 Raw URL
                    found_urls = RAW_URL_REGEX.findall(file_content)
                    if found_urls:
                        print(f"🔗 从文件 {file_html_url} 中提取到 {len(found_urls)} 个 Raw URL")
                        all_raw_urls.extend(found_urls)
                    else:
                        print(f"⚠️ 文件 {file_html_url} 中未提取到 Raw URL")

                except Exception as e:
                    print(f"⚠️ 解析文件 {item.get('html_url')} 出错: {e}")

        except requests.exceptions.RequestException as e:
            print(f"❌ 搜索关键词 '{keyword}' 失败: {e}")

    # ======================
    # 4. 去重
    # ======================
    unique_raw_urls = list(set(all_raw_urls))
    print(f"🔢 总共找到 {len(unique_raw_urls)} 个唯一 Raw URL")

    # ======================
    # 5. 保存到 merge/tvbox_raw_sources.txt
    # ======================
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    with open(output_path, 'w', encoding='utf-8') as f:
        for url in unique_raw_urls:
            f.write(url + '\n')

    print(f"✅ Raw URL 已保存到文件: {output_path}")

    # ======================
    # 6. 自动 Git 操作：add / commit / push
    # ======================
    if os.path.exists(output_path):
        try:
            subprocess.run(['git', 'add', output_path], check=True)
            subprocess.run([
                'git', 'commit',
                '-m', '🤖 自动更新 TVBox 全网 Raw 源文件链接 (关键词：荐片、采集、.spider)'
            ], check=True)
            subprocess.run(['git', 'push'], check=True)
            print("✅ Git 提交并推送成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ Git 操作失败: {e}")
    else:
        print("⚠️ merge/tvbox_raw_sources.txt 文件未生成，跳过 Git 提交")

if __name__ == '__main__':
    main()
