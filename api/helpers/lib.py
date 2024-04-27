class Lib:
    bcrypt = None
    def __init__(self):
        pass

    def init_bcrypt(self, bcrypt):
        self.bcrypt = bcrypt

    def get_bcrypt(self):
        return self.bcrypt
    
lib = Lib()