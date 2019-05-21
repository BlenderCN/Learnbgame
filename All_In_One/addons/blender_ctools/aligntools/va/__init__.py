import importlib
import sys

# reload
for name, mod in sys.modules.items():
    if name.startswith(__package__ + '.'):
        importlib.reload(mod)