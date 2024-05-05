from api.utils import get_timestamp

class Order:
    def __init__(self, product_id, quantity, price, user_id, created_at=get_timestamp()):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.user_id = user_id
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price,
            'user_id': self.user_id,
            'created_at': self.created_at
        }
