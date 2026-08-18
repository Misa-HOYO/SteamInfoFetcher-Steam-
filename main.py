import requests
import os
import re
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}
COOKIES = {
    'birthtime': '568022401',
    'mature_content': '1',
    'lastagecheckage': '1-January-2001',
    'wants_mature_content': '1',
}

def get(app_id):
    """信息获取"""
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=schinese&cc=cn"
    print("正在请求")
    response = requests.get(url, headers=HEADERS, verify=False)
    print("请求完毕")
    response.raise_for_status()
    data = response.json()
    game_data = data[str(app_id)]['data']

    info = {
        'name': game_data.get('name'),
        'short_description': game_data.get('short_description'),
        'header_image': game_data.get('header_image'),  # 封面图链接
        'screenshots': [s['path_full'] for s in game_data.get('screenshots', [])],
        "detailed_description": game_data.get("detailed_description")
    }

    return info
def download_image(url, save_path):
    """下载单张图片并保存"""
    try:
        # 发送GET请求，设置超时防止卡死[reference:2]
        response = requests.get(url, timeout=30)
        # 检查HTTP状态码，如果出错（如404）则抛出异常[reference:3]
        response.raise_for_status()
        
        # 以二进制写模式打开文件并保存图片内容[reference:4][reference:5]
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ 下载成功: {save_path}")
    except Exception as e:
        print(f"❌ 下载失败: {url}, 错误: {e}")
def search_steam_store(query):

    """在 Steam 商店搜索，返回结果列表（可能为空）"""
    url = 'https://store.steampowered.com/search/'
    params = {
        'term': query,
        'cc': 'cn',
        'l': 'schinese',
        'ndl': '1',
    }
    resp = requests.get(url, params=params, headers=HEADERS, cookies=COOKIES, timeout=15, verify=False)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []

    for a in soup.select('a.search_result_row'):
        appid = a.get('data-ds-appid')
        if not appid:
            href = a.get('href', '')
            m = re.search(r'/app/(\d+)', href)
            if m:
                appid = m.group(1)

        title_elem = a.select_one('.title')
        title = title_elem.get_text(strip=True) if title_elem else a.get_text(strip=True)

        if appid and title:
            results.append({'appid': appid, 'title': title})

    return results
def choose_from_results(results):

    """显示搜索结果并让用户选择，返回选中的结果或 None"""
    if not results:
        return None

    print('\n搜索结果：')
    for i, r in enumerate(results[:10], 1):
        print(f'{i}. [{r["appid"]}] {r["title"]}')

    if len(results) == 1:
        return results[0]

    choice_str = input('请选择序号（默认 1）: ').strip()
    if not choice_str:
        choice = 1
    else:
        try:
            choice = int(choice_str)
        except ValueError:
            choice = 1

    if 1 <= choice <= len(results):
        return results[choice - 1]
    else:
        return results[0]
def sanitize_filename(name):
    """清理文件名中的非法字符，用于文件夹命名"""
    return re.sub(r'[\\/*?:"<>|]', '_', name)

# main
save_folder = r"Save"
while True:
    # 搜索
    url_input = input("请输入 Steam 商店链接 或 游戏名称: ")
    match = re.search(r'/app/(\d+)/', url_input)
    if match:
        app_id = match.group(1)
        print(f"从链接提取到 appid: {app_id}")
    else:
        # 视为游戏名称，执行搜索
        print(f"正在搜索: {url_input}")
        results = search_steam_store(url_input)
        if not results:
            print("未找到相关游戏，请检查名称或直接输入链接。")
        selected = choose_from_results(results)
        if selected:
            app_id = selected['appid']
            print(f"已选择: {selected['title']} (appid {app_id})")
        else:
            print("未选择有效游戏，退出。")
    # 信息输出
    info = get(app_id)
    name = info.get("name")
    short_description = info.get("short_description")
    print(f"名称: {name}")
    print(f"简介: {short_description}")
    # 设置保存文件夹
    safe_name = sanitize_filename(name)
    game_folder = os.path.join(save_folder, f"{app_id}_{safe_name}")
    os.makedirs(game_folder, exist_ok=True)
    os.startfile(game_folder)
    # 图片下载
    # 准备所有下载任务（截图 + 封面图）
    download_tasks = []  # 每个元素为 (url, save_path)

    screenshots = info.get("screenshots", [])
    for i, url in enumerate(screenshots):
        filename = f"screenshot_{i:03d}.jpg"
        save_path = os.path.join(game_folder, filename)
        download_tasks.append((url, save_path))

    header_url = info.get("header_image")
    if header_url:
        filename = "header.jpg"
        save_path = os.path.join(game_folder, filename)
        download_tasks.append((header_url, save_path))

    # 使用线程池并行下载
    max_workers = 10  # 可根据需要调整并发线程数
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_image, url, path) for url, path in download_tasks]
        # 等待所有任务完成（可选，但建议保留以捕获异常）
        for future in futures:
            future.result()  # 如果线程内发生未处理异常，会在这里抛出
    
    # 保存带样式的详细简介（HTML格式）
    detailed_html = info.get("detailed_description")
    if detailed_html:
    # 构建简洁内容：游戏名称、简介、详细描述（原样）
        content = f"<b>游戏原名:{name}\n\n</b><br><br><b>游戏简介:{short_description}\n\n</b><br><br>{detailed_html}"
    else:
        content = f"<b>游戏原名:{name}\n\n<br><br>游戏简介:{short_description}</b>"

    html_filename = "game_info.html"
    html_path = os.path.join(game_folder, html_filename)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 游戏信息已保存到: {html_path}")