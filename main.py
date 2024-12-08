import requests
from bs4 import BeautifulSoup
import re
import time

# 目标URL列表和对应的提取模式
urls = [
    # (url, 'v4') 表示仅提取IPv4地址
    # (url, 'v6') 表示仅提取IPv6地址
    # (url, 'both') 表示同时提取IPv4和IPv6地址
    ('https://www.wetest.vip/page/cloudflare/address_v4.html', 'v4'),
    ('https://www.wetest.vip/page/cloudflare/address_v6.html', 'v6'),
    ('https://cf.090227.xyz', 'v4'),
    # 在这里添加更多的URL和模式
]

# 正则表达式匹配IPv4和IPv6地址
ipv4_pattern = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
ipv6_pattern = re.compile(r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}(([0-9]{1,3}\.){3}[0-9]{1,3})|([0-9a-fA-F]{1,4}:){1,4}:(([0-9]{1,3}\.){3}[0-9]{1,3}))')

# 存储所有IPv4和IPv6地址
all_ipv4s = []
all_ipv6s = []

# 处理每个URL
for url, mode in urls:
    # 发送HTTP请求并获取响应
    response = requests.get(url)
    response.encoding = 'utf-8'  # 如果需要可以设置响应编码

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取IP地址和延迟信息
    ipv4s = []
    ipv6s = []
    rows = soup.find_all('tr')  # 找到所有的行
    for row in rows:
        cols = row.find_all('td')
        for col in cols:
            ip = col.text.strip()  # 提取当前列的文本
            # 检查是否为有效的IPv4或IPv6地址
            if ipv4_pattern.match(ip):
                ipv4s.append(ip)  # 添加到IPv4列表中
            elif ipv6_pattern.match(ip):
                ipv6s.append(ip)  # 添加到IPv6列表中

    # 根据模式选择要处理的IP地址
    if mode == 'v4':
        all_ipv4s.extend(ipv4s)
    elif mode == 'v6':
        all_ipv6s.extend(ipv6s)
    elif mode == 'both':
        all_ipv4s.extend(ipv4s)
        all_ipv6s.extend(ipv6s)

    # 打印结果
    if ipv4s:
        print(f"从 {url} 提取的IPv4地址:")
        print(','.join(ipv4s))
    if ipv6s:
        print(f"从 {url} 提取的IPv6地址:")
        print(','.join(ipv6s))

    # 等待一定时间
    time.sleep(5)  # 延迟5秒

# 保存结果到文件
with open('ip.txt', 'w') as ipv4_file:
    ipv4_file.write(','.join(all_ipv4s))

with open('ipv6.txt', 'w') as ipv6_file:
    ipv6_file.write(','.join(all_ipv6s))

# 创建汇总文件
with open('api.txt', 'w') as api_file:
    for ip in all_ipv4s:
        api_file.write(ip + '\n')
    for ip in all_ipv6s:
        api_file.write('[' + ip + ']\n')
