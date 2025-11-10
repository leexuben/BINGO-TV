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
BRANCH = 'main'  # 根据实际情况修改

KEYWORDS = ['荐片', '采集', '.spider']

# ======================
# 2. 搜索GitHub代码
# ======================
def get_file_content(repo_owner, repo_name, file_path, token):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}'
    headers = {'Authorization': f'token {token}'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content = response.json()
        return base64.b64decode(content['content']).decode('utf-8')
    except Exception as e:
        print(f"❌ 获取文件内容失败: {str(e)}")
        return None

def search_and_save_github_code(keyword):
    headers = {'Authorization': f'token {GH_TOKEN}'}
    all_contents = []
    
    print(f"\n🔍 正在搜索关键词: '{keyword}'")
    url = f'https://api.github.com/search/code?q={keyword}+in:file&per_page=100'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ 找到 {len(data.get('items', []))} 个匹配文件")
        
        for item in data.get('items', []):
            try:
                repo_owner = item['repository']['owner']['login']
                repo_name = item['repository']['full_name'].split('/')[1]
                file_path = item['path']
                file_content = get_file_content(repo_owner, repo_name, file_path, GH_TOKEN)
                
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
        return
    
    # 保存结果到文件
    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S_(UTC)')
    filename = f"results_{keyword}_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_contents))
    
    print(f"✅ 结果已保存到文件: {filename}")

# ======================
# 3. 主程序
# ======================
def main():
    print("\n🚀 开始执行TVBox配置抓取任务...\n")
    
    # 搜索并保存每个关键词的结果
    for keyword in KEYWORDS:
        search_and_save_github_code(keyword)
    
    print("\n✨ 所有任务完成！")

if __name__ == '__main__':
    main()
