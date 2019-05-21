import bpy, mathutils, sys
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
try:
    import sternaMain
except ImportError:
    pass


def init():
    global sternaMain
    try:
        sternaMain
    except:
        sternaMain = sys.modules[modulesNames['sternaMain']]

def register():
    bpy.utils.register_class(SternaImport)
    bpy.types.INFO_MT_file_import.append(menu_sterna_import)
    init()

def unregister():
    bpy.utils.unregister_class(SternaImport)
    bpy.types.INFO_MT_file_import.remove(menu_sterna_import)

class SternaImport(Operator, ImportHelper):
    """ Import a sterna from a SNAC file
    """
    bl_label = "Import Snac"
    bl_idname = "sterna.imp"

    filename_ext = ".snac"

    filter_glob = StringProperty(
            default="*.snac",
            options={'HIDDEN'},
            maxlen=255,
            )

    use_setting = BoolProperty(
            name="Create mesh",
            description="TODO",
            default=False,
            )

    def execute(self, context):
        d = read_snac(self.filepath)
        bases = sternaMain.import_sterna_helix(d)
        sternaMain.create_sterna_helix(context, bases, 1.0)
        return {'FINISHED'}

def menu_sterna_import(self, context):
    self.layout.operator(SternaImport.bl_idname, text="Snac (.snac)")


def read_snac(snac):
    """ Reads a snac file.

    Args:
        snac -- The path to the SNAC file

    Returns:
        dictionary -- str => str, a map of parameters to their values
    """
    if snac.endswith(".snac"):
        path = snac
    else:
        path = snac + ".snac"
    d = {}
    with open(path) as f:
        last = None
        for l in f:
            if l.startswith("#"): continue
            if ":" in l:
                key, val = l.split(":")
                last = key.strip()
                val = val.strip()
            else:
                val = l.strip()
            if last:
                t = d.setdefault(last, [])
                t.append(val)
            else:
                print("Unexpected input: ", last)
    for a in d:
        d[a] = " ".join(d[a])
    return d

if __name__ == "__main__":
    register()
