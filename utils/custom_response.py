from rest_framework.response import Response

def success_response(data=None, message="Success", status_code=200):
    return Response({
        "success": True,
        "data": data,
        "message": message
    }, status=status_code)


def error_response(message="Something went wrong", errors=None, status_code=400):
    return Response({
        "success": False,
        "errors": errors,
        "message": message
    }, status=status_code)
