# Creating the User model in flask application with Flask PyMongo
class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def to_json(self):
        return {
            'username': self.username,
            'password': self.password,
            'role': self.role
        }