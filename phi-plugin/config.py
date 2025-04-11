from zhenxun.configs.config import Config as C


class Config:
    @classmethod
    def get(cls, key: str):
        key = key.upper()
        return C.get_config("phigros", key)
