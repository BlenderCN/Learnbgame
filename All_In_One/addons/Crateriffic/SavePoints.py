import bpy
import csv

def write_some_data(context, filepath):
    print("running write_some_data...")
    f = open(filepath, 'w', encoding='utf-8')
    writer = csv.writer(f)

    mesh = bpy.data.meshes['scan']
    points = [list(v.co) for v in mesh.vertices]

    writer.writerows(points)
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

# TODO: Re-write to export the data from the mesh holding the scan results.
class PSY_OT_ExportRayScan(Operator, ExportHelper):
    """Save any scan data to a csv file."""
    bl_idname = "export_scan.points"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Save Scan"

    # ExportHelper mixin class uses this
    filename_ext = ".csv"

    filter_glob = StringProperty(
            default="*.csv",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )



    def execute(self, context):
        return write_some_data(context, self.filepath)
