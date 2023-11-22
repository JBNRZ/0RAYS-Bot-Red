# nonebot2

## example
```
HOST = 0.0.0.0
PORT = 8080
COMMAND_START = [""]  # 配置命令起始字符
COMMAND_SEP = [""]  # 配置命令分割字符
SUPERUSERS = [""]
NICKNAME = [""]
APSCHEDULER_AUTOSTART = true

OAUTH_SERVER = "https://example.com"
OAUTH_GROUP = ["123", "456"]
OAUTH_MANAGER = "123456"
OAUTH_REGISTER_CODE = "xxx"
OAUTH_SECRET = "xxx"
OAUTH_EMAIL_SENDER = "test@example.com"
OAUTH_EMAIL_PWD = "secret"
OAUTH_EMAIL_HOST = "smtp.example.com"
OAUTH_EMAIL_PORT = 25

WX_KEY = "xxx"
WX_TOKEN = "xxx"
WX_APPID = "xxx"
WX_NOTICE_GROUP = ["123456"]
WX_MANAGER = "123456"

OPENAI_API_KEYS = ["", "", ""]
OPENAI_MODEL_NAME = "gpt-3.5-turbo"
OPENAI_MAX_HISTORY_LIMIT = 30   # 保留与每个用户的聊天记录条数
ENABLE_PRIVATE_CHAT = True   # 私聊开关，默认开启，改为False关闭

DRIVER=~fastapi+~aiohttp
RED_BOTS='
[
  {
    "port": "xxx",
    "token": "xxxxxx",
    "host": "xx.xx.xx.xx"
  }
]
'
```
