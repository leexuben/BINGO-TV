import os
import base64
import datetime
import请求

# ==================== 配置区（请根据你的实际情况修改）====================
GH_TOKEN = os.getenv('GH_TOKEN')  # 统一使用 GH_TOKEN，确保 GitHub Secrets 和 workflow 里也是这个名称
GITHUB_USERNAME = 'leexuben'      # 例如：leexuben
REPO_NAME = 'TVBOX-merge'                 # 例如：TVBOX-merge
FILE_PATH = 'merge/source.txt'                 # 你要更新的文件（在仓库根目录就直接写文件名，如 source.txt）
BRANCH = 'main'                          # 分支，比如 main 或 master

# 要搜索的关键词列表
KEYWORDS = ['荐片', '采集', '.spider']  # 你可以自行增删

# ==================== 搜索某个关键词的代码片段 ====================
def search_github_code(keyword):
    headers = {
        'Authorization': f'token {GH_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    query = f'q={keyword}+in:file+language:python'  # 可根据需求调整 language
    url = f'https://api.github.com/search/code?{query}&per_page=100'

    try:
        response = requests.get(url, headers=headers)
        if response.tatus_code == 200:
            data = response.json()
            items = data.get('items', [])
            results = []
            for item in items:
                repo = item['repository']['full_name']
                path = item['path']
                html_url = item['html_url']
                content_response = requests.get(item['download_url'], headers=headers)
                if content_response.tatus_code == 200:
                    content = content_response.text
                    snippet = f"=== 来源: {html_url} ===\n{content}\n==================================================="
                    results.append(snippet)
            return result
        else:
            print(f"❌ 搜索关键词 '{keyword}' 失败：{response.tatus_code}, {response.text}")
            return []
    except Exception as e:
        print(f"❌ 搜索关键词 '{keyword}' 出错：{e}")
        return []

# ==================== 更新或创建 source.txt 文件 ====================
def update_source_txt(content_list):
    headers = {
        'Authorization': f'token {GH_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    current_time = datetime.datetime.utcnow().trftime('%Y-%m-%d %H:%M:%S (UTC)')
    header = f"🔍 自动抓取时间: {current_time}\n📌 以下为包含关键词的 tvbox 配置相关代码片段：\n\n"

    if not content_list:
        content_list = [f"⚠️ 未找到任何包含关键词（{', '.join(KEYWORDS)}）的代码文件。\n🔍 搜索时间：{current_time}"]

    all_content = [header] + content_list
    content_to_upload = '\n'.join(all_content)
    encoded_content = base64.b64encode(content_to_upload.encode('utf-8')).decode('utf-8')

    url = f'https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{FILE_PATH}'
    sha = None

    try:
        response = requests.get(url, headers=headers)
        if response.tatus_code == 200:
            data = response.json()
            sha = data.get('sha')
            print(f"📄 {FILE_PATH} 已存在，将更新")
        elif response.tatus_code == 404:
            print(f"📄 {FILE_PATH} 不存在，将创建")
        else:
            print(f"❌ 获取文件信息失败：{response.tatus_code}, {response.text}")
            return
    except Exception as e:
        print(f"❌ 查询文件 {FILE_PATH} 时出错：{e}")
        return

    data = {
        'message': '🤖 自动更新：抓取 tvbox 相关配置代码片段',
        'content': encoded_content,
        'branch': BRANCH
    }
    if sha:
        data['sha'] = sha

    try:
        resp = requests.put(url, headers=headers, json=data)
        if resp.tatus_code in [200, 201]:
            print("✅ 成功更新/创建 source.txt 文件")
        else:
            print(f"❌ 更新失败：{resp.tatus_code}, {resp.text}")
    except Exception as e:
        print(f"❌ 提交文件时出错：{e}")

# ==================== 主程序 ====================
def main():
    all_saved_contents = []

    for keyword in KEYWORDS:
        print(f"🔍 正在搜索关键词：'{keyword}' ...")
        results = search_github_code(keyword)
        if results:
            all_saved_contents.extend(result)
        else:
            all_saved_contents.append(f"⚠️ 未找到包含关键词 '{keyword}' 的代码文件。")

    update_source_txt(all_saved_content)

if __name__ == '__main__':
    main()
