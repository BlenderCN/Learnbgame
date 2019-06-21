import sys
if sys.version_info[0] == 2:
    from .b24.baseapp import Base24Application as BaseApplication
    blender_version = 24
else:
    from .baseapp import BaseApplication
    blender_version = 25
