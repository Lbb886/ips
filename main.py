import requests
from bs4 import BeautifulSoup
import re
import time

# 目标URL
url_ipv4 = 'https://www.wetest.vip/page/cloudflare/total_v4.html'
url_ipv6 = 'https://www.wetest.vip/page/cloudflare/total_v6.html'

# 发送HTTP请求并获取响应
response_ipv4 = requests.get(url_ipv4)
response_ipv4.encoding = 'utf-8'  # 如果需要可以设置响应编码

# 使用BeautifulSoup解析HTML
soup_ipv4 = BeautifulSoup(response_ipv4.text, 'html.parser')

# 提取IPv4地址和延迟信息
ipv4s = []
ipv4_pattern = re.compile(r'(\d{1,3}\.){3}\d{1,3}')  # 正则表达式匹配IPv4地址

rows_ipv4 = soup_ipv4.find_all('tr')  # 找到所有的行
for row in rows_ipv4:
    cols = row.find_all('td')
    if len(cols) > 0:
        ip = cols[0].text.strip()  # 提取IP地址
        if ipv4_pattern.match(ip):  # 检查是否为有效的IPv4地址
            ipv4s.append(ip)

# 转换成IP, IP格式
ipv4_pairs = ','.join(ipv4s)

# 打印结果
print("IPv4地址:")
print(ipv4_pairs)

# 保存结果到文件
with open('ip.txt', 'w') as ipv4_file:
    ipv4_file.write(ipv4_pairs)

# 等待一定时间，然后处理IPv6地址
time.sleep(5)  # 延迟5秒

# 发送HTTP请求并获取IPv6网页响应
response_ipv6 = requests.get(url_ipv6)
response_ipv6.encoding = 'utf-8'  # 如果需要可以设置响应编码

# 使用BeautifulSoup解析HTML
soup_ipv6 = BeautifulSoup(response_ipv6.text, 'html.parser')

# 提取IPv6地址和延迟信息
ipv6s = []
ipv6_pattern = re.compile(r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}(([0-9]{1,3}\.){3}[0-9]{1,3})|([0-9a-fA-F]{1,4}:){1,4}:(([0-9]{1,3}\.){3}[0-9]{1,3}))') # 正则表达式匹配IPv6地址

rows_ipv6 = soup_ipv6.find_all('tr')  # 找到所有的行
for row in rows_ipv6:
    cols = row.find_all('td')
    if len(cols) > 0:
        ip = cols[0].text.strip()  # 提取IP地址
        if ipv6_pattern.match(ip):  # 检查是否为有效的IPv6地址
            ipv6s.append(ip)

# 转换成IP, IP格式
ipv6_pairs = ','.join(ipv6s)

# 打印结果
print("IPv6地址:")
print(ipv6_pairs)

# 保存结果到文件
with open('ipv6.txt', 'w') as ipv6_file:
    ipv6_file.write(ipv6_pairs)

# 创建汇总文件
with open('api.txt', 'w') as api_file:
    for ip in ipv4s:
        api_file.write(ip + '\n')
    for ip in ipv6s:
        api_file.write('[' + ip + ']\n')