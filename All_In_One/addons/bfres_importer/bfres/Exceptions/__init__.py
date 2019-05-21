class UnsupportedFileTypeError(Exception):
    """File type not supported"""
    def __init__(self, magic):
        super().__init__()
        self.magic = magic


    def __str__(self):
        return "UnsupportedFileTypeError(%s)" % str(self.magic)


class UnsupportedFormatError(Exception):
    """Some particular format used in this file is not supported."""


class MalformedFileError(Exception):
    """File is corrupted or unreadable."""
