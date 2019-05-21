import os, sys  # NOQA
imp_dir = os.path.realpath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, imp_dir)

import lsystemLexer
import lsystemParser

sys.path.remove(imp_dir)
