from uuid import uuid4

from Crypto.Cipher import AES
from nonebot import get_driver
from nonebot.adapters.red import Bot
from nonebot.adapters.red import Message, MessageSegment
from nonebot.adapters.red.event import MemberAddEvent
from nonebot.log import logger
from nonebot.plugin import on_notice
from requests import post

import smtplib
from email.mime.text import MIMEText
from email.header import Header


def email(qq: str, msg: str):
    sender = get_driver().config.oauth_email_sender
    receivers = [f'{qq}@qq.com']

    mail_host = get_driver().config.oauth_email_host
    mail_pass = get_driver().config.oauth_email_pwd

    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header(f"{sender.split('@')[0]} <{sender}>")
    message['To'] = Header(f"{qq}@qq.com", 'utf-8')
    message['Subject'] = Header("杭电身份认证", 'utf-8')
    s = smtplib.SMTP()
    s.connect(mail_host, get_driver().config.oauth_email_port)
    s.login(sender, mail_pass)
    s.sendmail(sender, receivers, message.as_string())


def padding(msg: bytes):
    return msg + bytes.fromhex((hex(16 - len(msg) % 16)[2:]).rjust(2, "0")) * (16 - len(msg) % 16)


def encrypt(msg: bytes, key: bytes) -> bytes:
    msg = padding(msg)
    return AES.new(key, AES.MODE_CBC, key[:16]).encrypt(msg)


async def isIncreaseNotice(event: MemberAddEvent) -> bool:
    return isinstance(event, MemberAddEvent) and event.peerUid in get_driver().config.oauth_group


welcome = on_notice(rule=isIncreaseNotice, block=False)
manager = get_driver().config.oauth_manager


@welcome.handle()
async def handle(bot: Bot, event: MemberAddEvent):
    await bot.mute_member(int(event.peerUid), int(event.get_user_id()), duration=2592000)
    token = str(uuid4())
    url: str = get_driver().config.oauth_server.strip("/") + "/oauth/register"
    data = {
        "code": token,
        "qq": event.get_user_id(),
        "gp": event.peerUid
    }
    cookie = {
        "reg-code": get_driver().config.oauth_register_code
    }
    response = post(url, data=data, cookies=cookie)
    if response.status_code != 200:
        logger.error("Failed to register token")
        await bot.send_group_message(
            target=event.peerUid,
            message=Message(MessageSegment.at(event.get_user_id())) + f" 身份验证出现了点儿小问题，请私聊管理员: {manager}"
        )
        return
    qq = encrypt(event.get_user_id().encode(), get_driver().config.oauth_secret.encode()).hex()
    group = encrypt(event.peerUid.encode(), get_driver().config.oauth_secret.encode()).hex()
    msg = "在您正式加入群聊前，需要您进行杭电学生认证，以确认您的真实身份\n"
    msg += "请访问一下链接进行认证，请注意该链接只能访问一次：\n"
    msg += f"{get_driver().config.oauth_server.strip('/')}/oauth/request/?qq={qq}&gp={group}&token={token}"
    try:
        email(event.get_user_id(), msg=msg)
        await bot.send_group_message(
            target=event.peerUid,
            message=Message(MessageSegment.at(event.get_user_id())) + " 身份验证邮件已发送至您的QQ邮箱，请验证后继续群聊，感谢配合"
        )
    except Exception as e:
        logger.error(f"Failed to send email to {event.get_user_id()}: {e}")
        await bot.send_group_message(
            target=event.peerUid,
            message=Message(MessageSegment.at(event.get_user_id())) + f" 身份验证出现了点儿小问题，请私聊管理员: {manager}"
        )
