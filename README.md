# 0RAYS-Bot
基于Nonebot2的QQ机器人

# 开发文档
基于 Red 协议的临时替代：https://github.com/nonebot/adapter-red/

nonebot: https://nonebot.dev/

# Bug
对于目前开发的 adapter-red 存在一个 MemberAddEvent 的小bug

主要问题在于对群号和QQ号的正则匹配存在问题，将该类修改如下

```python
class MemberAddEvent(NoticeEvent):
    """群成员增加事件"""

    memberUid: str
    operatorUid: str
    memberName: Optional[str]

    @override
    def get_event_name(self) -> str:
        return "notice.member_add"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Member {f'{self.memberName}({self.memberUid})' if self.memberName else self.memberUid} added to "  # noqa: E501
            f"{self.peerUin or self.peerUid}"
        )
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return self.memberUid

    @override
    def get_session_id(self) -> str:
        # 获取事件会话 ID 的方法，根据事件具体实现，如果事件没有相关 ID，则抛出异常
        return f"{self.peerUin or self.peerUid}_{self.memberUid}"

    @classmethod
    @override
    def convert(cls, obj: Any):
        assert isinstance(obj, MessageModel)
        params = {
            "msgId": obj.msgId,
            "msgRandom": obj.msgRandom,
            "msgSeq": obj.msgSeq,
            "cntSeq": obj.cntSeq,
            "chatType": obj.chatType,
            "msgType": obj.msgType,
            "subMsgType": obj.subMsgType,
            "peerUid": obj.peerUid,
            "peerUin": obj.peerUin,
        }
        if obj.elements[0].grayTipElement.xmlElement:  # type: ignore
            mat = findall(compile('jp="(\d+)".*?jp="(\d+)"'), obj.elements[0].grayTipElement.xmlElement.content)[0]
            if len(mat) != 2:
                mat = ("0", "0")
            params["operatorUid"] = mat[0]
            params["memberUid"] = mat[1]
        else:
            params["memberUid"] = obj.elements[0].grayTipElement.groupElement.memberUin  # type: ignore  # noqa: E501
            params["operatorUid"] = obj.elements[0].grayTipElement.groupElement.adminUin  # type: ignore  # noqa: E501
            params["memberName"] = obj.elements[0].grayTipElement.groupElement.memberNick  # type: ignore  # noqa: E501
        return cls(**params)
```
