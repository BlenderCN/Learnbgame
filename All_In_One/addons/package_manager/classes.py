import bpy
from bpy.props import StringProperty

class PackageManagerAddon(bpy.types.PropertyGroup):
    """PropertyGroup representing an add-on available for download."""
    
    source = StringProperty()
    name = StringProperty()
    description = StringProperty()
    author = StringProperty()
    wiki_url = StringProperty()
    tracker_url = StringProperty()
    location = StringProperty()
    category = StringProperty()
    version = StringProperty()
    blender = StringProperty()
    warning = StringProperty()
    support = StringProperty()
    module_name = StringProperty()
    download_url = StringProperty()