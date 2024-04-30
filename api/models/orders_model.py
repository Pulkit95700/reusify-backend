from api.utils import get_timestamp

class Order:
    def __init__(self, order_id, product_name, quantity, price, customer_name, customer_email, created_at=get_timestamp()):
        self.order_id = order_id
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': self.price,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'created_at': self.created_at
        }
