def ApiError(status, message):
    return {
        'status': status,
        'message': message
    }