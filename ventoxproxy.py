import requests
import re
from concurrent.futures import ThreadPoolExecutor
import os

# Danh sách nguồn proxy (cập nhật thêm)
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/proxies.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt"
]

# Hàm lấy proxy từ một URL
def fetch_proxies_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', response.text)
        print(f"[+] Fetched {len(proxies)} proxies from {url}")
        return proxies
    except Exception as e:
        print(f"[-] Failed to fetch from {url}: {e}")
        return []

# Kiểm tra proxy hoạt động
def is_proxy_live(proxy):
    try:
        res = requests.get('https://httpbin.org/ip', proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=5)
        if res.status_code == 200:
            print(f"[LIVE] {proxy}")
            return proxy
    except:
        pass
    return None

# Hàm kiểm tra nhiều proxy song song
def check_proxies_concurrently(proxies, max_workers=50):
    live_proxies = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(is_proxy_live, proxies)
        for proxy in results:
            if proxy:
                live_proxies.append(proxy)
    return live_proxies

# Gửi file proxy đến Telegram group
def send_file_to_telegram(bot_token, chat_id, file_path):
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                f'https://api.telegram.org/bot{bot_token}/sendDocument',
                data={'chat_id': chat_id},
                files={'document': f}
            )
        if response.status_code == 200:
            print("[+] File sent to Telegram group successfully.")
        else:
            print(f"[-] Failed to send file to Telegram: {response.text}")
    except Exception as e:
        print(f"[-] Error sending file: {e}")

# Chạy toàn bộ quy trình
if __name__ == '__main__':
    all_proxies = []
    for source in PROXY_SOURCES:
        all_proxies.extend(fetch_proxies_from_url(source))

    print(f"[i] Total proxies fetched: {len(all_proxies)}")
    live_proxies = check_proxies_concurrently(list(set(all_proxies)))
    print(f"[i] Total live proxies: {len(live_proxies)}")

    # Lưu vào file
    os.makedirs("output", exist_ok=True)
    file_path = "output/live_proxies.txt"
    with open(file_path, "w") as f:
        f.write("\n".join(live_proxies))
    print("[+] Saved to output/live_proxies.txt")

    # Gửi file qua Telegram
    BOT_TOKEN = '8185929921:AAHnaIAgjDV1L0lZNyEx255uAcLP4IdMp-A'
    CHAT_ID = '-1002390825493'
    send_file_to_telegram(BOT_TOKEN, CHAT_ID, file_path)