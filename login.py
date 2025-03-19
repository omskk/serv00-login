import os
import base64
import paramiko
import requests
import json
from datetime import datetime, timezone, timedelta
import time
import hmac
import hashlib
import urllib.parse

# 钉钉机器人配置
DD_BOT_SECRET = os.getenv('DD_BOT_SECRET')
DD_BOT_ACCESS_TOKEN = os.getenv('DD_BOT_ACCESS_TOKEN')

def login(hosts_info, command):
    users = []
    hostnames = []
    failed_hosts = []  # 新增失败服务器列表
    for host_info in hosts_info:
        hostname = host_info['hostname']
        username = host_info['username']
        password = host_info['password']

        print(f"===> 正在连接服务器：{hostname}...")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname, port=22, username=username, password=password)
            print(f"    ✅ 连接成功：{hostname}")

            stdin, stdout, stderr = ssh.exec_command(command)
            user = stdout.read().decode().strip()
            users.append(user)
            hostnames.append(hostname)
            print(f"    🔄 执行命令 '{command}' 返回：{user}")

            ssh.close()
        except Exception as e:
            print(f"    ❌ 连接 {hostname} 失败: {str(e)}")
            failed_hosts.append(hostname+"|"+username)  # 记录失败主机
    return users, hostnames, failed_hosts  # 返回新增的失败列表


def main():
    print("========================================")
    print("SSH服务器登录流程开始")
    print("========================================")

    # 步骤1：加载配置文件
    print("步骤1/4：正在加载SSH配置文件...")
    try:
        # 切换本地配置文件路径
        # with open('ssh_config.json', 'r') as f:
        #     hosts_info = json.load(f)
        # 切换环境变量配置文件路径
        ssh_info_str = os.getenv('SSH_INFO', '[]')
        hosts_info = json.loads(ssh_info_str)
        print(f"    ✅ 配置文件加载成功，共找到 {len(hosts_info)} 台服务器")
    except Exception as e:
        print(f"    ❌ 配置文件加载失败: {str(e)}")
        hosts_info = []

    # 步骤2：执行SSH命令（修改返回值）
    print("\n步骤2/4：开始执行SSH命令...")
    command = 'whoami'
    user_list, hostname_list, failed_hosts = login(hosts_info, command)
    user_num = len(user_list)

    # 步骤3：收集系统信息
    print("\n步骤3/4：正在收集系统信息...")
    beijing_timezone = timezone(timedelta(hours=8))
    time = datetime.now(beijing_timezone).strftime('%Y-%m-%d %H:%M:%S')
    print("    🌐 正在获取本地IP地址...")
    loginip = requests.get('https://api.ipify.org?format=json').json()['ip']
    print(f"    ✅ 当前IP：{loginip}")

    # 步骤4：生成最终报告
    print("\n步骤4/4：生成最终报告...")
    content = "SSH服务器登录信息：\n"
    for user, hostname in zip(user_list, hostname_list):
        content += f"用户名：{user}，服务器：{hostname}\n"
    content += f"\n本次登录用户共： {user_num} 个\n登录时间：{time}\n登录IP：{loginip}"

    # 新增失败服务器输出
    failed_count = len(failed_hosts)
    if failed_count > 0:
        content += f"\n\n失败的服务器：{', '.join(failed_hosts)}"

    print("========================================")
    print("最终执行结果：")
    print("========================================")
    print(content)
    print("========================================")
    print("SSH服务器登录流程结束")
    print("========================================")


def dingding_bot(title, content):
    timestamp = str(round(time.time() * 1000))  # 时间戳
    secret_enc = DD_BOT_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DD_BOT_SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc,
                         digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # 签名
    print('开始使用 钉钉机器人 推送消息...', end='')
    url = f'https://oapi.dingtalk.com/robot/send?access_token={DD_BOT_ACCESS_TOKEN}&timestamp={timestamp}&sign={sign}'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        'msgtype': 'text',
        'text': {'content': f'{title}\n\n{content}'}
    }
    response = requests.post(url=url, data=json.dumps(
        data), headers=headers, timeout=15).json()
    if not response['errcode']:
        print('推送成功！')
    else:
        print('推送失败！')

if __name__ == "__main__":
    main()
