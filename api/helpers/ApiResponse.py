def ApiResponse(status, message, data = None):
    return {
        'status': status,
        'message': message,
        'data': data
    }