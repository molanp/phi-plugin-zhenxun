class CompleteQRCodeData:
    def __init__(self, code_data):
        self.device_id = code_data["deviceId"]
        self.device_code = code_data["data"]["device_code"]
        self.expires_in = code_data["data"]["expires_in"]
        self.qr_url = code_data["data"]["qrcode_url"]
        self.interval = code_data["data"]["interval"]
