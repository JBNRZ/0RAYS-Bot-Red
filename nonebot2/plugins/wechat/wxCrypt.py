from hashlib import sha1
from base64 import b64decode
from xml.etree import ElementTree
from Crypto.Cipher import AES
from socket import ntohl
from struct import unpack


def sign(token: str, timestamp: str, nonce: str, encrypted: str) -> str:
    return sha1("".join(sorted([token, timestamp, nonce, encrypted])).encode()).hexdigest()


def extract(xml: str):
    tree = ElementTree.fromstring(xml)
    encrypted = tree.find("Encrypt").text
    name = tree.find("ToUserName").text
    return encrypted, name


def content(xml: str) -> str:
    tree = ElementTree.fromstring(xml)
    if tree.find("MsgType").text == "image":
        return tree.find("PicUrl").text
    return tree.find("Content").text


class PKCS7Encoder:

    block_size = 32

    def encode(self, text: bytes) -> bytes:
        text_length = len(text)
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        return text + chr(amount_to_pad).encode() * amount_to_pad


class PrpCrypt:

    def __init__(self, key: bytes):
        self.key = key
        self.mode = AES.MODE_CBC

    def decrypt(self, msg: str, appid: str) -> str:
        aes = AES.new(self.key, self.mode, self.key[:16])
        msg = aes.decrypt(b64decode(msg.encode()))
        msg = msg[16:-msg[-1]]
        xml_len = ntohl(unpack("I", msg[: 4])[0])
        xml_content = msg[4: xml_len + 4].decode()
        from_appid = msg[xml_len + 4:].decode()
        assert from_appid == appid
        return xml_content


class WXCrypt:

    def __init__(self, sToken: str, sEncodingAESKey: str, sAppId: str):
        self.key = b64decode(sEncodingAESKey + "=")
        assert len(self.key) == 32
        self.token = sToken
        self.appid = sAppId

    def decrypt(self, sPostData: str, sMsgSignature: str, sTimestamp: str, sNonce: str) -> str:
        msg, name = extract(sPostData)
        signed = sign(self.token, sTimestamp, sNonce, msg)
        assert signed == sMsgSignature
        return PrpCrypt(self.key).decrypt(msg, self.appid)
