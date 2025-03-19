# Serv00全自动保活

## 使用方法

 - 添加Secrets；“Settings” > “Secrets”


| 参数名              | 备注               |
| ------------------- |------------------|
| SSH_INFO            | 需要保活的serv00服务器信息 |
| PUSH_TYPE           | 是否推送： false/true |
| DD_BOT_SECRET       | 钉钉机器人的SECRET     |
| DD_BOT_ACCESS_TOKEN | 钉钉机器人的TOKEN      |

## 定时自动运行
配置位置：项目/.github/workflows/login.yml
```
- cron: '0 1 1 * *'  # 每月的 1号 01 点运行
```
## SSH_INFO格式
```json
[
  {
    "host": "sxx.serv00.com",
    "username": "username",
    "password": "password"
  }
]
```
## 钉钉机器人推送
自己创建一个机器人，然后获取到secret和token，在Secrets中添加即可

## 切换本地运行环境
切换后可使用青龙运行详细方法自行研究
```
# login.py中搜索：
切换本地配置文件路径
```
- 配置文件放在脚本同目录 ：文件名称：ssh_config.json

- 文件格式：参考ssh_info










