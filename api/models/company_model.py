from api.utils import get_timestamp

class Company:
    def __init__(self, name, address, phone, email, imageUrl, created_at=get_timestamp()):
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.imageUrl = imageUrl
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'imageUrl': self.imageUrl,
            'created_at': self.created_at
        }