import hashlib

from zhenxun.services.log import logger


def md5(text: str) -> str:
    """
    计算字符串的 MD5 哈希值
    :param text: 输入字符串
    :return: MD5 哈希值的十六进制字符串
    """
    try:
        return hashlib.md5(text.encode()).hexdigest()
    except Exception as e:
        logger.warning(f"Error calculating MD5: {e}")
        return ""
