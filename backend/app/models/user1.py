class User:
    def __init__(self, code):
        self.code = code

    @staticmethod
    def find_by_code(code):
        # buscar en DB
        pass

    def save(self):
        # guardar en DB
        pass
