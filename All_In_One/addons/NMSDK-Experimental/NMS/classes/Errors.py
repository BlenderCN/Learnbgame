# some custom errors
# TODO: move?


class MissingDataError(Exception):
    # custom exception to raise if a node is created without some required data
    def __init__(self):
        pass
