from api.utils import get_timestamp

class Banner:
    def __init__(self, title, imageURL, created_at=get_timestamp()):
        self.title = title
        self.imageURL = imageURL
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'title': self.title,
            'imageURL': self.imageURL,
            'created_at': self.created_at
        }