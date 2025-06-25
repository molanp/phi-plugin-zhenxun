import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


async def Decrypt(word):
    # JS: key = CryptoJS.enc.Base64.parse(...)
    key = base64.b64decode("6Jaa0qVAJZuXkZCLiOa/Ax5tIZVu+taKUN1V1nqwkks=")
    iv = base64.b64decode("Kk/wisgNYwcAV8WVGMgyUw==")
    # JS: encrypted = CryptoJS.enc.Base64.parse(word)
    encrypted = base64.b64decode(word)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted)
    return unpad(decrypted, AES.block_size)

