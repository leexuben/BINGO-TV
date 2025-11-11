import os
import requests
import re
import subprocess

# 配置部分
KEYWORDS = ['荐片', '采集', '.spider']
OUTPUT_DIR = 'merge'
OUTPUT_FILE = 'tvbox_raw_sources.txt'
TOKEN_ENV_NAME = 'MY_GH_TOKEN'  # 用于GitHub API认证的Token环境变量名

# 从环境变量获取GitHub Token
gh_token = os.getenv(TOKEN_ENV_NAME)
headers = {}
if gh_token:
    headers = {
        'Authorization': f'token {gh_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

# 用于匹配Raw URL的正则表达式
RAW_URL_REGEX = re.compile(r'https://raw\.githubusercontent\.com/[\w\-]+/[\w\-]+/[\w\-]+/[\w\-/]+')

def extract_raw_urls_from_content(content):
    """从文件内容中提取Raw URL"""
    return RAW_URL_REGEX.findall(content)

def main():
    all_raw_urls = []

    for keyword in KEYWORDS:
        print(f"🔍 正在搜索关键词: {keyword}")
        search_url = f'https://api.github.com/search/code?q={keyword}+in:file&per_page=100'
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            print(f"✅ 找到 {len(items)} 个包含 '{keyword}' 的文件")

            for item in items:
                file_html_url = item.get('html_url')
                try:
                    # 获取文件内容
                    file_content_url = item.get('download_url')
                    if not file_content_url:
                        print(f"⚠️ 文件 {file_html_url} 无内容链接，跳过")
                        continue
                    content_response = requests.get(file_content_url, headers=headers)
                    content_response.raise_for_status()
                    file_content = content_response.text
                    # 提取Raw URL
                    raw_urls = extract_raw_urls_from_content(file_content)
                    if raw_urls:
                        print(f"🔗 从文件 {file_html_url} 中提取到 {len(raw_urls)} 个Raw URL")
                        all_raw_urls.extend(raw_urls)
                    else:
                        print(f"⚠️ 文件 {file_html_url} 中未提取到Raw URL")
                except Exception as e:
                    print(f"⚠️ 处理文件 {file_html_url} 时出错: {e}")

        except requests.exceptions.RequestException as e:
            print(f"❌ 搜索关键词 '{keyword}' 时发生请求错误: {e}")

    # 去重
    unique_raw_urls = list(set(all_raw_urls))
    print(f"🔢 总共找到 {len(unique_raw_urls)} 个唯一Raw URL")

    # 保存到文件
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    if unique_raw_urls:
        with open(output_path, 'w', encoding='utf-8') as f:
            for url in unique_raw_urls:
                f.write(url + '
')
        print(f"✅ Raw URL已成功保存到文件: {output_path}")

        # Git操作
        try:
            subprocess.run(['git', 'add', output_path], check=True)
            subprocess.run([
                'git', 'commit',
                '-m', '🤖 自动更新TVBox全网Raw源文件链接 (关键词：荐片、采集、.spider)'
            ], check=True)
            subprocess.run(['git', 'push'], check=True)
            print("✅ Git提交并推送成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
    else:
        print("⚠️ 未找到有效的Raw URL，不进行Git提交")

if __name__ == '__main__':
    main()

