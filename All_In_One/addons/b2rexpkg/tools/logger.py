import logging

VERBOSE_LEVEL = logging.DEBUG

ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
ch.setLevel(VERBOSE_LEVEL)

class B2RexLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name)
        self.addHandler(ch)
        self.setLevel(VERBOSE_LEVEL)

logging.setLoggerClass(B2RexLogger)

logger = logging.getLogger("b2rex")

