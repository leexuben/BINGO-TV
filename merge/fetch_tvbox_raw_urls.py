import requests
import os
from datetime import datetime

# ======================
# 🔧 配置区域
# ======================

# 你要搜索的关键词
KEYWORDS = ['荐片', '采集', '.spider']

# GitHub Token（强烈建议申请一个，能提升限额，但搜公开库不用权限也可运行）
GITHUB_TOKEN = os.getenv('MY_GH_TOKEN')  # 从环境变量读取，或直接取消注释下面一行并填入
# GITHUB_TOKEN = '你的_token_here'  # ← 如果你不想用环境变量，就取消注释并填入你的 token

HEADERS = {'Accept': 'application/vnd.github.v3+json'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'

# 输出文件夹与文件名
OUTPUT_DIR = 'merge'
OUTPUT_FILENAME = 'tvbox_repos.txt'  # 最终保存的仓库名 txt 文件名



# ======================
# 🚀 核心功能：搜索 GitHub，提取仓库名，按更新时间排序，保存到 merge/tvbox_repos.txt
# ======================

def save_github_repos_sorted_by_update():
    all_repos = []  # 存放所有仓库及更新时间

    for keyword in KEYWORDS:
        print(f"🔍 正在搜索关键词：【{keyword}】")

        url = f'https://api.github.com/search/code?q={keyword}+in:file&per_page=100'

        try:
            resp = requests.get(url, headers=HEADERS)
            resp.raise_for_status()
            data = resp.json()
            items = data.get('items', [])

            print(f"✅ 找到 {len(items)} 个包含关键词「{keyword}」的文件")

            for item in items:
                repo = item.get('repository')
                if not repo:
                    continue

                repo_full_name = repo.get('full_name')  # 如：作者/仓库名
                updated_at = repo.get('updated_at')     # 如：2024-01-01T12:00:00Z

                if repo_full_name and updated_at:
                    updated_time = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
                    all_repos.append({
                        'repo_name': repo_full_name,
                        'updated_at': updated_time
                    })

        except Exception as e:
            print(f"❌ 搜索关键词「{keyword}」时出错：{e}")

    # 按更新时间倒序排序（最新的在前面）
    sorted_repos = sorted(all_repos, key=lambda x: x['updated_at'], reverse=True)

    # 确保 merge 文件夹存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 保存仓库名到 merge/tvbox_repos.txt（每行一个，按更新时间排序）
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    with open(output_path, 'w', encoding='utf-8') as f:
        for repo in sorted_repos:
            f.write(repo['repo_name'] + '\n')

    print(f"\n✅ 已成功保存 {len(sorted_repos)} 个仓库名到文件：{output_path}")
    print(f"📝 文件内容为按更新时间排序的 GitHub 仓库名（最新的在前面），每行一个，仅仓库名！")

# ======================
# ▶️ 运行入口
# ======================
if __name__ == '__main__':
    save_github_repos_sorted_by_update()
