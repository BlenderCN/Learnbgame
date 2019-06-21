import logging; log = logging.getLogger(__name__)
from .base import TextureFormat, fmts, types
from . import rgb, bc

for cls in TextureFormat.__subclasses__():
    fmts[cls.id] = cls

# define a subclass for each remaining format
for name, typ in types.items():
    if typ['id'] not in fmts:
        cls = type(name, (TextureFormat,), typ)
        fmts[typ['id']] = cls
