def success(data=None):
    response = {"status": "success"}
    if data is not None:
        response["data"] = data
    return response


def error(message):
    return {"status": "error", "message": message}
