import requests
import os
from datetime import datetime

# 搜索关键词
KEYWORDS = ['荐片', '采集', '.spider']
# GitHub Token，可去 https://github.com/settings/tokens 申请，公开库搜索可不填
GITHUB_TOKEN = os.getenv('MY_GH_TOKEN')
HEADERS = {'Accept': 'application/vnd.github.v3+json'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'

# 输出目录和文件名
OUTPUT_DIR = 'merge'
OUTPUT_FILE = 'tvbox_repos.txt'

def get_repositories():
    repos = []
    for keyword in KEYWORDS:
        print(f"正在搜索关键词: {keyword}")
        url = f'https://api.github.com/search/code?q={keyword}+in:file&per_page=100'
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            print(f"找到 {len(items)} 个包含关键词 '{keyword}' 的文件")
            for item in items:
                repo = item.get('repository')
                if repo:
                    repo_name = repo.get('full_name')
                    updated_at = repo.get('updated_at')
                    if repo_name and updated_at:
                        updated_time = datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%SZ')
                        repos.append((repo_name, updated_time))
        except requests.RequestException as e:
            print(f"搜索关键词 {keyword} 时出错: {e}")
    # 去重并排序
    unique_repos = {}
    for repo_name, updated_time in repos:
        if repo_name not in unique_repos or updated_time > unique_repos[repo_name]:
            unique_repos[repo_name] = updated_time
    sorted_repos = sorted(unique_repos.items(), key=lambda x: x[1], reverse=True)
    return [repo[0] for repo in sorted_repos]

def save_to_file(repos):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        for repo in repos:
            f.write(repo + '
')
    print(f"已保存 {len(repos)} 个仓库名到 {output_path}，按更新时间排序，最新的在前。")

if __name__ == "__main__":
    repos = get_repositories()
    save_to_file(repos)

