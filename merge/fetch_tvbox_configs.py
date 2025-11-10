import os
import requests
import base64
from datetime import datetime

# ======================
# 1. 配置部分
# ======================
GH_TOKEN = os.getenv('GH_TOKEN')  # 使用具有写入权限的 Token，请配置到 GitHub Actions Secrets 中
if not GH_TOKEN:
    print("❌ 错误：未设置 MY_GH_TOKEN 环境变量！请配置具有写入权限的 GitHub Token。")
    exit(1)

REPO_OWNER = 'leexuben'
REPO_NAME = 'BINGO-TV'
BRANCH = 'main'  # 如果您的分支是 merge，请改成 'merge'

KEYWORDS = ['荐片', '采集', '.spider']

# ======================
# 2. 主程序：搜索关键词并写入到 GitHub 仓库的 /merge/ 目录下
# ======================
def main():
    print("\n🚀 开始执行TVBox配置抓取任务...\n")

    for keyword in KEYWORDS:
        print(f"🔍 正在搜索关键词: '{keyword}'")
        url = f'https://api.github.com/search/code?q={keyword}+in:file&per_page=100'

        headers = {'Authorization': f'token {GH_TOKEN}'}
        all_contents = []

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            print(f"✅ 找到 {len(data.get('items', []))} 个匹配文件")

            for item in data.get('items', []):
                try:
                    file_url = item['download_url']
                    file_content = requests.get(file_url, headers={'Accept': 'text/plain'}).text

                    if file_content:
                        all_contents.append(
                            f"=== 来源: {item['html_url']} ===\n"
                            f"{file_content}\n"
                            "="*50 + "\n\n"
                        )

                except Exception as e:
                    print(f"⚠️ 无法获取文件内容 {item['html_url']}: {str(e)}")

        except requests.exceptions.RequestException as e:
            print(f"❌ 搜索关键词 '{keyword}' 失败: {str(e)}")
            continue

        if not all_contents:
            print(f"⚠️ 没有找到任何匹配 '{keyword}' 的内容")
            continue

        # ====== 写入到 GitHub 仓库的 /merge/keyword.txt 文件 ======
        file_path_in_repo = f"merge/{keyword}.txt"  # 例如：merge/荐片.txt
        api_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path_in_repo}'

        # 先尝试获取当前文件的 SHA（如果已存在）
        sha = None
        try:
            resp = requests.get(api_url, headers=headers)
            if resp.status_code == 200:
                sha = resp.json().get('sha')
        except Exception as e:
            print(f"⚠️ 获取 /merge/{keyword}.txt 的 SHA 失败: {e}")

        # 拼接所有内容
        content = "\n".join(all_contents)

        # 编码为 base64
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

        # 提交信息
        message = f"🤖 自动更新 /merge/{keyword}.txt 搜索结果"

        # 请求体
        data = {
            'message': message,
            'content': encoded_content,
            'branch': BRANCH,
            'sha': sha  # 如果文件存在则需提供，否则可省略
        }

        # 发起写入请求
        try:
            response = requests.put(api_url, headers=headers, json=data)
            response.raise_for_status()
            print(f"✅ 成功写入 /merge/{keyword}.txt")
        except Exception as e:
            print(f"❌ 写入 /merge/{keyword}.txt 失败: {e}")

    print("\n✨ 所有任务完成！")

# ======================
# 3. 入口
# ======================
if __name__ == '__main__':
    main()
