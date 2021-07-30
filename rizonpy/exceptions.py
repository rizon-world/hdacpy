class BadRequestException(Exception):
    """Bad request error"""
    pass


class EmptyMsgException(Exception):
    """Empy message in tx preparation"""
    pass

class NotEnoughParametersException(Exception):
    def __str__(self):
        return "not enough parameter is provided"
