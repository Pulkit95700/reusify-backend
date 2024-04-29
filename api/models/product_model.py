from api.utils import get_timestamp

class Product:
    def __init__(self, name, price, mrp, description, company_id, categories=[], imageUrls=[], created_at=get_timestamp()):
        self.name = name
        self.price = price
        self.mrp = mrp
        self.discount = round(((mrp - price) / mrp) * 100, 2)
        self.description = description
        self.company_id = company_id
        self.categories = categories
        self.rating = 3.0   # Default rating
        self.imageUrls = imageUrls
        self.created_at = created_at

    def to_dict(self):
        return {
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'company_id': self.company_id,
            'rating': self.rating,
            'mrp': self.mrp,
            'discount': self.discount,
            'categories': self.categories,
            'imageUrls': self.imageUrls,
            'created_at': self.created_at
        }
