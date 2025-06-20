class CompleteQRCodeData:
    """完整的 TapTap QR 码数据集合"""

    def __init__(self, code: dict):
        """:param code: 部分 TapTap QR 码数据对象。"""
        self.deviceID = code["devideId"]
        self.deviceCode = code["data"]["device_code"]
        self.expiresInSeconds: int = code["data"]["expires_in"]
        self.url: str = code["data"]["qrcode_url"]
        self.interval = code["data"]["interval"]
