from api.utils import get_timestamp;
class Cart:
    def __init__(self, user_id, product_id, quantity):
        self.user_id = user_id
        self.products = [{'product_id': product_id, 'quantity': quantity}]
        self.created_at = get_timestamp()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'products': self.products,
            'created_at': self.created_at
        }