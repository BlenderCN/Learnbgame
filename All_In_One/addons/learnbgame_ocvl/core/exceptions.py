class OCVLNodeException(Exception):
    pass


class LackRequiredSocket(OCVLNodeException):
    pass


class NoDataError(OCVLNodeException):
    pass
