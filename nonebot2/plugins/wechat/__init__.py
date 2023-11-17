from json.decoder import JSONDecodeError
from nonebot import get_driver
from nonebot.drivers.fastapi import Driver
from fastapi import Request
from nonebot.log import logger


def register_route(d: Driver):
    try:
        return d.server_app
    except Exception as e:
        logger.error(f"Failed to get app: {e}")


app = register_route(get_driver())


@app.get('/')
async def test(request: Request) -> dict:
    try:
        body = await request.json()
    except JSONDecodeError:
        body = await request.body()
    ret = {
        "headers": request.headers,
        "cookies": request.cookies,
        "body": body
    }
    logger.info(ret)
    return ret
