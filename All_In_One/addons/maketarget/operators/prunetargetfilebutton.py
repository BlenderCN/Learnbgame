import bpy
from ..utils import *
from ..error import *
from bpy.props import StringProperty
from ..maketarget import getSettings, readLines
from bpy_extras.io_utils import ExportHelper, ImportHelper

def pruneTarget(ob, filepath):
    settings = getSettings(ob)
    lines = []
    before,after = readLines(filepath, -1,-1)
    for vn,string in after:
        if vn < settings.nTotalVerts and ob.data.vertices[vn].select:
            lines.append((vn, string))
    print(("Pruning", len(before), len(after), len(lines)))
    fp = open(filepath, "w", encoding="utf-8", newline="\n")
    for vn,string in lines:
        fp.write(str(vn) + " " + string)
    fp.close()


def pruneFolder(ob, folder):
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isdir(path):
            if ob.MhPruneRecursively:
                pruneFolder(ob, path)
        else:
            (name,ext) = os.path.splitext(file)
            if ext == ".target":
                print(("Prune", path))
                pruneTarget(ob, path)

class VIEW3D_OT_PruneTargetFileButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mh.prune_target_file"
    bl_label = "Prune Target File"
    bl_description = "Remove not selected vertices from target file(s)"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for target file",
        maxlen= 1024, default= "")

    @classmethod
    def poll(self, context):
        return (context.object and context.object.MhPruneEnabled)

    def execute(self, context):
        try:
            setObjectMode(context)
            ob = context.object
            if ob.MhPruneWholeDir:
                folder = os.path.dirname(self.properties.filepath)
                pruneFolder(ob, folder)
                print("Targets pruned")
            else:
                pruneTarget(ob, self.properties.filepath)
                print("Target pruned")
        except MHError:
            handleMHError(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}