import requests
import json
from datetime import datetime

def get_top_ips(api_url):
    """
    获取API结果中avgScore排名前五且不重复的IP
    """
    try:
        # 获取API数据
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # 提取所有IP和avgScore
        all_ips = []
        
        # 遍历所有类别(CT, CU, CM, AllAvg)
        for category in ['CT', 'CU', 'CM', 'AllAvg']:
            if category in data['data']:
                for item in data['data'][category]:
                    all_ips.append({
                        'ip': item['ip'],
                        'avgScore': item['avgScore'],
                        'createdTime': item['createdTime'],
                        'ydLatencyAvg': item['ydLatencyAvg'],
                        'dxLatencyAvg': item['dxLatencyAvg'],
                        'ltLatencyAvg': item['ltLatencyAvg']
                    })
        
        # 按avgScore升序排序（分数越低越好）
        sorted_ips = sorted(all_ips, key=lambda x: x['avgScore'])
        
        # 去重处理：保留分数最低的IP
        unique_ips = []
        seen_ips = set()
        
        for ip_info in sorted_ips:
            if ip_info['ip'] not in seen_ips:
                unique_ips.append(ip_info)
                seen_ips.add(ip_info['ip'])
                # 如果已经收集了5个不同的IP，则停止
                if len(unique_ips) >= 5:
                    break
        
        return unique_ips
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return []
    except Exception as e:
        print(f"处理错误: {e}")
        return []

def update_cloudflare_dns(domain, subdomain, api_token, ips):
    """
    更新Cloudflare DNS解析为指定的IP列表（支持子域名）
    """
    try:
        # Cloudflare API端点
        zone_url = f"https://api.cloudflare.com/client/v4/zones?name={domain}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # 获取区域ID
        zone_response = requests.get(zone_url, headers=headers)
        zone_response.raise_for_status()
        zone_data = zone_response.json()
        
        if zone_data['success'] and zone_data['result']:
            zone_id = zone_data['result'][0]['id']
        else:
            print("无法获取区域ID")
            return False
        
        # 构建完整子域名
        full_subdomain = f"{subdomain}.{domain}" if subdomain else domain
        
        # 获取DNS记录
        dns_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        dns_response = requests.get(dns_url, headers=headers)
        dns_response.raise_for_status()
        dns_data = dns_response.json()
        
        if not dns_data['success']:
            print("获取DNS记录失败")
            return False
        
        # 删除现有的A记录（只删除匹配子域名的记录）
        for record in dns_data['result']:
            if record['type'] == 'A' and record['name'] == full_subdomain:
                delete_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record['id']}"
                delete_response = requests.delete(delete_url, headers=headers)
                if delete_response.json()['success']:
                    print(f"已删除DNS记录: {record['name']} -> {record['content']}")
                else:
                    print(f"删除DNS记录失败: {record['name']} -> {record['content']}")
        
        # 添加新的A记录（使用轮询模式）
        for i, ip in enumerate(ips):
            record_data = {
                "type": "A",
                "name": full_subdomain,
                "content": ip['ip'],
                "ttl": 300,  # 5分钟TTL
                "proxied": False,
                "priority": 10  # 用于轮询
            }
            
            create_response = requests.post(dns_url, headers=headers, json=record_data)
            if create_response.json()['success']:
                print(f"已添加DNS记录: {full_subdomain} -> {ip['ip']} (分数: {ip['avgScore']})")
            else:
                print(f"添加DNS记录失败: {full_subdomain} -> {ip['ip']}")
                print(f"错误详情: {create_response.json()}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Cloudflare API请求错误: {e}")
        return False
    except Exception as e:
        print(f"Cloudflare DNS更新错误: {e}")
        return False

def send_to_wechat_bot(wechat_webhook, domain, subdomain, top_ips):
    """
    通过企业微信机器人发送消息
    """
    try:
        # 构建完整子域名
        full_subdomain = f"{subdomain}.{domain}" if subdomain else domain
        
        # 格式化消息内容
        message = f"📊 IP延迟排行榜 Top 5\n"
        message += f"📅 数据时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"🌐 更新域名: {full_subdomain}\n"
        message += f"🔢 去重后IP数量: {len(top_ips)}\n\n"
        
        for i, ip_info in enumerate(top_ips, 1):
            message += f"🥇 排名 {i}: {ip_info['ip']}\n"
            message += f"   平均延迟: {ip_info['avgScore']}\n"
            message += f"   测量时间: {ip_info['createdTime']}\n"
            message += f"   延迟统计: 电信:{ip_info['ydLatencyAvg']}ms 联通:{ip_info['dxLatencyAvg']}ms 移动:{ip_info['ltLatencyAvg']}ms\n\n"
        
        message += "✅ 已更新Cloudflare DNS解析为以上IP地址"
        
        # 发送到企业微信机器人
        payload = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(wechat_webhook, headers=headers, json=payload)
        response.raise_for_status()
        
        print("消息已成功发送到企业微信机器人")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"企业微信机器人请求错误: {e}")
        return False
    except Exception as e:
        print(f"企业微信机器人发送错误: {e}")
        return False

def main():
    # 配置参数
    API_URL = "https://vps789.com/openApi/cfIpApi"  # 替换为实际的API地址
    WECHAT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=588d175e-f230-4505-86ac-cbe5bfda77fd"  # 替换为企业微信机器人webhook地址
    CLOUDFLARE_DOMAIN = "njuvtk.ggff.net"  # 替换为您的域名
    CLOUDFLARE_SUBDOMAIN = "cdn"  # 替换为您要更新的子域名（如"www"、"cdn"等）
    CLOUDFLARE_API_TOKEN = "60nGx2La9pZU5eP0tXFxg0abBE1Phk2zQ35XVPTY"  # 替换为您的Cloudflare API令牌
    
    # 获取分数最低的5个不重复IP
    top_ips = get_top_ips(API_URL)
    
    if not top_ips:
        print("未能获取到有效的IP数据")
        return
    
    # 更新Cloudflare DNS解析
    if update_cloudflare_dns(CLOUDFLARE_DOMAIN, CLOUDFLARE_SUBDOMAIN, CLOUDFLARE_API_TOKEN, top_ips):
        print("Cloudflare DNS解析已更新")
    else:
        print("Cloudflare DNS解析更新失败")
    
    # 发送结果到企业微信机器人
    send_to_wechat_bot(WECHAT_WEBHOOK, CLOUDFLARE_DOMAIN, CLOUDFLARE_SUBDOMAIN, top_ips)

if __name__ == "__main__":
    main()
