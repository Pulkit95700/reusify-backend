from api.utils import get_timestamp

class Category:
    def __init__(self, category_name, description, imageUrl, created_at=get_timestamp()):
        self.category_name = category_name
        self.description = description
        self.imageUrl = imageUrl
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'category_name': self.category_name,
            'description': self.description,
            'imageUrl': self.imageUrl,
            'created_at': self.created_at
        }