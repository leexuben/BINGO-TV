import os
import requests
import base64
from datetime import datetime

# ======================
# 1. 配置部分
# ======================
GH_TOKEN = os.getenv('GH_TOKEN')
if not GH_TOKEN:
    print("❌ 错误：未设置GH_TOKEN环境变量！")
    exit(1)

REPO_OWNER = 'leexuben'
REPO_NAME = 'BINGO-TV'
FILE_PATH = 'merge/source.txt'
BRANCH = 'main'  # 根据实际情况修改

KEYWORDS = ['荐片', '采集', '.spider']

# ======================
# 2. 搜索GitHub代码
# ======================
def search_github_code():
    headers = {'Authorization': f'token {GH_TOKEN}'}
    all_contents = []
    
    for keyword in KEYWORDS:
        print(f"\n🔍 正在搜索关键词: '{keyword}'")
        url = f'https://api.github.com/search/code?q={keyword}+in:file&per_page=100'
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ 找到 {len(data.get('items', []))} 个匹配文件")
            
            for item in data.get('items', []):
                try:
                    file_url = item['download_url']
                    file_content = requests.get(file_url, headers=headers).text
                    
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
            
    return all_contents

# ======================
# 3. 更新GitHub文件
# ======================
def update_github_file(content):
    headers = {
        'Authorization': f'token {GH_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 准备文件内容
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S (UTC)')
    header = f"🔍 自动抓取时间: {timestamp}\n"
    full_content = header + "\n".join(content)
    
    # 获取文件SHA（如果存在）
    try:
        url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            sha = response.json()['sha']
            print(f"📄 文件 {FILE_PATH} 已存在，将更新")
        else:
            sha = None
            print(f"📄 文件 {FILE_PATH} 不存在，将创建")
            
    except Exception as e:
        print(f"❌ 检查文件状态失败: {str(e)}")
        return False
    
    # 更新文件
    try:
        encoded_content = base64.b64encode(full_content.encode('utf-8')).decode('utf-8')
        
        data = {
            'message': '🤖 自动更新TVBox配置代码片段',
            'content': encoded_content,
            'branch': BRANCH,
            'sha': sha
        }
        
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"✅ 成功更新文件: {FILE_PATH}")
        return True
        
    except Exception as e:
        print(f"❌ 更新文件失败: {str(e)}")
        return False

# ======================
# 4. 主程序
# ======================
def main():
    print("\n🚀 开始执行TVBox配置抓取任务...")
    
    # 搜索代码
    print("\n=== 第一步：搜索GitHub代码 ===")
    contents = search_github_code()
    
    if not contents:
        print("\n❌ 警告：没有找到任何匹配的代码片段")
        return
    
    print(f"\n📦 共找到 {len(contents)} 个代码片段")
    
    # 更新文件
    print("\n=== 第二步：更新GitHub文件 ===")
    success = update_github_file(contents)
    
    if success:
        print("\n✨ 任务完成！")
    else:
        print("\n❌ 任务失败，请检查错误信息")

if __name__ == '__main__':
    main()
