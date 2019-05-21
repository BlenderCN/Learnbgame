import logging; log = logging.getLogger(__name__)

class FresObject:
    """Base class for an object in an FRES."""

    def __init__(self, fres):
        self.fres = fres


    def readFromFRES(self, offset=None):
        """Read this object from the FRES."""
        raise NotImplementedError
