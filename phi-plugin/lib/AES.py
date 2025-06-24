import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


async def Encrypt(text, key, iv):
    # key, iv, text 都是字符串，需转为bytes
    key_bytes = key.encode("utf-8")
    iv_bytes = iv.encode("utf-8")
    text_bytes = text.encode("utf-8")
    # PKCS7 padding
    padded = pad(text_bytes, AES.block_size)
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    encrypted = cipher.encrypt(padded)
    # 返回base64字符串
    return base64.b64encode(encrypted).decode()


async def Decrypt(word):
    # 固定key和iv，base64解码
    key = base64.b64decode("6Jaa0qVAJZuXkZCLiOa/Ax5tIZVu+taKUN1V1nqwkks=")
    iv = base64.b64decode("Kk/wisgNYwcAV8WVGMgyUw==")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = base64.b64decode(word)
    decrypted = cipher.decrypt(encrypted)
    # 去除PKCS7 padding
    try:
        result = unpad(decrypted, AES.block_size)
    except ValueError:
        result = decrypted  # 如果不是标准填充，直接返回原始
    # 返回16进制字符串
    return result.hex()
