class ModifyStrategy:
    def __init__(self, data):
        self.data = data

    def apply(self, data):
        try:
            raise OSError()
        except Exception as e:
            return str(e)
