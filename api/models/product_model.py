from api.utils import get_timestamp

class Product:
    def __init__(self, name, price, description, categories, company, imageUrls=[], created_at=get_timestamp()):
        self.name = name
        self.price = price
        self.description = description
        self.categories = categories
        self.rating = 3.0   # Default rating
        self.company = company
        self.imageUrls = imageUrls
        self.created_at = created_at

    def to_dict(self):
        return {
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'categories': self.categories,
            'company': self.company,
            'imageUrls': self.imageUrls,
            'created_at': self.created_at
        }
