import requests
import json
from datetime import datetime

def get_top_ips(api_url, wechat_webhook):
    """
    获取API结果中avgScore排名前六（分数最低）的IP，并通过企业微信机器人推送
    
    参数:
        api_url: API接口地址
        wechat_webhook: 企业微信机器人webhook地址
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
        
        # 获取前六名（分数最低的六个）
        top_ips = sorted_ips[:6]
        
        # 格式化消息内容
        message = f"📊 IP性能排行榜 (Top 6 - 分数越低越好)\n"
        message += f"📅 数据时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for i, ip_info in enumerate(top_ips, 1):
            message += f"🥇 排名 {i}: {ip_info['ip']}\n"
            message += f"   平均分: {ip_info['avgScore']}\n"
            message += f"   测量时间: {ip_info['createdTime']}\n"
            message += f"   延迟统计: 电信: {ip_info['ydLatencyAvg']} ms 联通: {ip_info['dxLatencyAvg']} ms 移动: {ip_info['ltLatencyAvg']} ms\n\n"
        
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
        print(f"请求错误: {e}")
        return False
    except Exception as e:
        print(f"处理错误: {e}")
        return False

# 使用示例
if __name__ == "__main__":
    # 替换为实际的API地址和企业微信机器人webhook地址
    API_URL = "https://vps789.com/openApi/cfIpApi"
    WECHAT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=588d175e-f230-4505-86ac-cbe5bfda77fd"
    
    # 获取前六名IP（分数最低）并发送消息
    get_top_ips(API_URL, WECHAT_WEBHOOK)
