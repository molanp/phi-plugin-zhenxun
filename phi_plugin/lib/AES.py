import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


async def encrypt(text: str | bytes, key: str | bytes, iv: str | bytes) -> bytes:
    """
    加密数据

    :param text: 待加密数据
    :param key: 密钥
    :param iv: 初始化向量
    :return: 加密后的数据
    """
    if isinstance(text, str):
        text = text.encode()
    if isinstance(key, str):
        key = key.encode()
    if isinstance(iv, str):
        iv = iv.encode()
    paddedData = pad(text, AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encryptedData = cipher.encrypt(paddedData)
    return base64.b64encode(encryptedData)


async def decrypt(word: str | bytes) -> bytes:
    """
    解密数据

    :param word: 待解密数据
    :return: 解密后的数据
    """
    if isinstance(word, str):
        word = word.encode()
    key = base64.b64decode("6Jaa0qVAJZuXkZCLiOa/Ax5tIZVu+taKUN1V1nqwkks=")
    iv = base64.b64decode("Kk/wisgNYwcAV8WVGMgyUw==")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decryptedData = cipher.decrypt(base64.b64decode(word))
    return unpad(decryptedData, AES.block_size)
