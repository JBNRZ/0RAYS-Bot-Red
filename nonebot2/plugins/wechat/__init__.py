from nonebot import get_driver, get_bot
from nonebot.adapters.red import Bot
from nonebot.drivers.fastapi import Driver
from fastapi import Request, Response
from nonebot.log import logger
from .wxCrypt import WXCrypt, content


def register_route(d: Driver):
    try:
        return d.server_app
    except Exception as e:
        logger.error(f"Failed to get app: {e}")


app = register_route(get_driver())


@app.get('/wechat/')
async def check(request: Request) -> Response:
    return Response(content=request.query_params["echostr"])


@app.post("/wechat/")
async def receive(request: Request) -> dict:
    bot: Bot = get_bot()
    data = await request.body()
    msg_sign = request.query_params["msg_signature"]
    nonce = request.query_params["nonce"]
    timestamp = request.query_params["timestamp"]

    key = get_driver().config.wx_key
    token = get_driver().config.wx_token
    appid = get_driver().config.wx_appid
    msg = WXCrypt(token, key, appid).decrypt(data.decode(), msg_sign, nonce, timestamp)
    try:
        msg = f"收到来自微信公众号信息：{content(msg)}"
        for group in get_driver().config.wx_notice_group:
            await bot.send_group_message(target=group, message=msg)
    except Exception as e:
        await bot.send_friend_message(target=get_driver().config.wx_manager, message=f"{e}\n{msg}")
        logger.error(e)
        logger.info(msg)
    return {"status": "ok", "code": 0}


