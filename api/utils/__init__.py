from datetime import datetime

def get_timestamp():
    return str(datetime.isoformat(datetime.now()))