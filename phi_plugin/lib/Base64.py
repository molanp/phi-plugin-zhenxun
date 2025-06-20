import base64 as b64


class Base64:
    def decode(self, data):
        try:
            if isinstance(data, str):
                result = b64.b64decode(data)
                return result.hex()
            return data
        except Exception:
            return data

    def encode(self, data):
        try:
            if isinstance(data, str):
                result = bytes.fromhex(data)
                return b64.b64encode(result).decode()
            return data
        except Exception:
            return data


# 创建单例实例
base64 = Base64()
