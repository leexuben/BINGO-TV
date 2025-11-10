import requests

# ======================
# 1. 配置
# ======================
KEYWORDS = ['荐片', '采集', '.spider']  # 您要搜索的 3 个关键词
OUTPUT_FILE = 'tvbox_raw_sources.txt'  # 最终输出的文件名（会保存在 merge/ 目录下）

# ======================
# 2. 搜索并提取 Raw URL
# ======================
def main():
    all_raw_urls = []

    for keyword in KEYWORDS:
        print(f"🔍 正在搜索关键词: {keyword}")
        url = f'https://api.github.com/search/code?q={keyword}+in:file&per_page=100'

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            items = data.get('items', [])
            print(f"✅ 找到 {len(items)} 个包含 '{keyword}' 的文件")

            for item in items:
                try:
                    raw_url = item.get('download_url')
                    if raw_url:
                        all_raw_urls.append(raw_url)
                except Exception as e:
                    print(f"⚠️ 解析文件出错: {e}")

        except requests.exceptions.RequestException as e:
            print(f"❌ 搜索关键词 '{keyword}' 失败: {e}")

    # 去重
    unique_raw_urls = list(set(all_raw_urls))
    print(f"🔢 总共找到 {len(unique_raw_urls)} 个唯一 Raw URL")

    # 保存到文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for url in unique_raw_urls:
            f.write(url + '\n')

    print(f"✅ Raw URL 已保存到文件: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
