import requests
import json
from datetime import datetime

def extract_top_ips(api_url):
    """
    从API获取数据并提取avgScore最低的前6个IP
    """
    try:
        # 调用API获取数据
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 提取所有IP和对应的avgScore
        all_ips_scores = []
        
        # 遍历所有运营商的数据
        for operator in ['CT', 'CU', 'CM', 'AllAvg']:
            if operator in data.get('data', {}):
                for item in data['data'][operator]:
                    ip = item.get('ip')
                    avg_score = item.get('avgScore')
                    if ip and avg_score is not None:
                        all_ips_scores.append({
                            'ip': ip,
                            'avgScore': avg_score,
                            'operator': operator
                        })
        
        # 按avgScore升序排序（分数越低越好）
        all_ips_scores.sort(key=lambda x: x['avgScore'])
        
        # 取前6个
        top_6_ips = all_ips_scores[:6]
        
        return top_6_ips
        
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def send_wechat_webhook(webhook_url, top_ips):
    """
    发送企业微信机器人消息
    """
    if not top_ips:
        return False
    
    # 构建消息内容
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 创建markdown格式的消息
    markdown_content = f"## 🚀 网络性能最佳IP推荐\n\n"
    markdown_content += f"**更新时间**: {current_time}\n\n"
    markdown_content += "| 排名 | IP地址 | 运营商 | 综合评分 |\n"
    markdown_content += "|------|--------|--------|----------|\n"
    
    for i, ip_info in enumerate(top_ips, 1):
        operator_map = {
            'CT': '电信',
            'CU': '联通', 
            'CM': '移动',
            'AllAvg': '综合'
        }
        operator_name = operator_map.get(ip_info['operator'], ip_info['operator'])
        markdown_content += f"| {i} | `{ip_info['ip']}` | {operator_name} | {ip_info['avgScore']} |\n"
    
    markdown_content += f"\n**说明**: 评分越低表示网络性能越好\n"
    
    # 构建消息payload
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": markdown_content
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            timeout=10
        )
        response.raise_for_status()
        print("企业微信消息发送成功")
        return True
    except requests.exceptions.RequestException as e:
        print(f"企业微信消息发送失败: {e}")
        return False

def main():
    # 配置信息 - 请替换为您的实际配置
    API_URL = "https://vps789.com/openApi/cfIpApi"  # 替换为您的API地址
    WECHAT_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=588d175e-f230-4505-86ac-cbe5bfda77fd"  # 替换为您的企业微信机器人webhook地址
    
    print("开始获取网络性能数据...")
    
    # 获取前6个最佳IP
    top_ips = extract_top_ips(API_URL)
    
    if top_ips:
        print(f"找到 {len(top_ips)} 个最佳IP:")
        for i, ip_info in enumerate(top_ips, 1):
            print(f"{i}. IP: {ip_info['ip']}, 评分: {ip_info['avgScore']}, 运营商: {ip_info['operator']}")
        
        # 发送到企业微信
        print("正在发送到企业微信...")
        send_wechat_webhook(WECHAT_WEBHOOK_URL, top_ips)
    else:
        print("未能获取到有效数据")

if __name__ == "__main__":
    main()
