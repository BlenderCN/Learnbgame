import os
import sys

def ensure_modules_dir_on_path():
    modules_dir = os.path.join(os.path.dirname(__file__), 'modules')
    modules_dir = os.path.abspath(modules_dir)

    if not modules_dir in sys.path:
        sys.path.append(modules_dir)

    print(sys.path)
