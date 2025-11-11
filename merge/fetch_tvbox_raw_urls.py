import os
import requests
import subprocess



# ======================
# 1. 配置
# ======================
KEYWORDS = ['荐片', '采集', '.spider']  # 您要搜索的 3 个关键词
OUTPUT_DIR = '.'  # 输出目录，因为最终文件要放到 merge 目录，这里先放当前目录，后续再移动
OUTPUT_FILE = 'tvbox_raw_sources.txt'  # 输出文件名
TOKEN_ENV_NAME = 'MY_GH_TOKEN'  # 环境变量名，用于 GitHub API 搜索认证（可选）

# ======================
# 2. 从环境变量获取 GitHub Token（仅用于 API 搜索，可选）
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



# ======================
# 3. 搜索每个关键词，将 Raw URL 保存到字典（内存）
# ======================
def main():
    all_raw_urls_dict = {}  # 用字典存每个关键词的 Raw URL（内存）

    for keyword in KEYWORDS:
        print(f"🔍 搜索关键词: {keyword}")
        url = f'https://api.github.com/search/code?q={keyword}+in:file&per_page=100'

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            items = data.get('items', [])
            print(f"✅ 找到 {len(items)} 个包含 '{keyword}' 的文件")

            raw_urls = []
            for item in items:
                try:
                    raw_url = item.get('download_url')
                    if raw_url:
                        raw_urls.append(raw_url)
                except Exception as e:
                    print(f"⚠️ 解析文件出错: {e}")

            all_raw_urls_dict[keyword] = raw_urls

        except requests.exceptions.RequestException as e:
            print(f"❌ 搜索关键词 '{keyword}' 失败: {e}")

    # ======================
    # 4. 从字典中提取所有 Raw URL，去重
    # ======================
    all_raw_urls = []
    for keyword in all_raw_urls_dict:
        all_raw_urls.extend(all_raw_urls_dict[keyword])

    unique_raw_urls = list(set(all_raw_urls))
    print(f"🔢 总共找到 {len(unique_raw_urls)} 个唯一 Raw URL")

    # ======================
    # 5. 确保 merge/ 目录存在，然后保存到 merge/tvbox_raw_sources.txt
    # ======================
    os.makedirs('merge', exist_ok=True)
    output_path = os.path.join('merge', OUTPUT_FILE)

    with open(output_path, 'w', encoding='utf-8') as f:
        for url in unique_raw_urls:
            f.write(url + '\n')

    print(f"✅ Raw URL 已保存到文件: {output_path}")

    # ======================
    # 6. 自动 Git 操作：add / commit / push（如果文件存在）
    # ======================
    if os.path.exists(output_path):
        try:
            # Git add
            subprocess.run(['git', 'add', output_path], check=True)

            # Git commit
            subprocess.run([
                'git', 'commit',
                '-m', '🤖 自动更新 TVBox 全网 Raw 源文件链接 (关键词：荐片、采集、.spider)'
            ], check=True)

            # Git push
            subprocess.run(['git', 'push'], check=True)

            print("✅ Git 提交并推送成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ Git 操作失败: {e}")
    else:
        print("⚠️ merge/tvbox_raw_sources.txt 文件未生成，跳过 Git 提交")



if __name__ == '__main__':
    main()

