import bpy


def read_point_data(context, filepath, shift, name_col, x_col, y_col, z_col, separator):
    print("running read point file...")
    f = open(filepath, 'r', encoding='utf-8')
#    data = f.read()
    arr=f.readlines()  # store the entire file in a variable
    f.close()

    for p in arr:
        p0 = p.split(separator)  # use colon as separator
        ItemName = p0[int(name_col)]
        x_coor = float(p0[int(x_col)])
        y_coor = float(p0[int(y_col)])
        z_coor = float(p0[int(z_col)])
         
        if shift == True:
            shift_x = context.scene.BL_x_shift
            shift_y = context.scene.BL_y_shift
            shift_z = context.scene.BL_z_shift
            x_coor = x_coor-shift_x
            y_coor = y_coor-shift_y
            z_coor = z_coor-shift_z  

        # Generate UV sphere at x = lon and y = lat (and z = 0 )
        o = bpy.data.objects.new( ItemName, None )
        bpy.context.scene.objects.link( o )
        o.location.x = x_coor
        o.location.y = y_coor
        o.location.z = z_coor
        o.show_name = True

    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportCoorPoints(Operator, ImportHelper):
    """Tool to import coordinate points from a txt file"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Coordinate Points"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob = StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    shift = BoolProperty(
            name="Shift coordinates",
            description="Shift coordinates using the General Shift Value (GSV)",
            default=False,
            )

    col_name = EnumProperty(
            name="Name",
            description="Column with the name",
            items=(('0', "Column 1", "Column 1"),
                   ('1', "Column 2", "Column 2"),
                   ('2', "Column 3", "Column 3"),
                   ('3', "Column 4", "Column 4")),
            default='0',
            )
  
    col_x = EnumProperty(
            name="X",
            description="Column with coordinate X",
            items=(('0', "Column 1", "Column 1"),
                   ('1', "Column 2", "Column 2"),
                   ('2', "Column 3", "Column 3"),
                   ('3', "Column 4", "Column 4")),
            default='1',
            ) 

    col_y = EnumProperty(
            name="Y",
            description="Column with coordinate X",
            items=(('0', "Column 1", "Column 1"),
                   ('1', "Column 2", "Column 2"),
                   ('2', "Column 3", "Column 3"),
                   ('3', "Column 4", "Column 4")),
            default='2',
            )

    col_z = EnumProperty(
            name="Z",
            description="Column with coordinate X",
            items=(('0', "Column 1", "Column 1"),
                   ('1', "Column 2", "Column 2"),
                   ('2', "Column 3", "Column 3"),
                   ('3', "Column 4", "Column 4")),
            default='3',
            )     

    separator = EnumProperty(
            name="separator",
            description="Separator type",
            items=((',', "comma", "comma"),
                   (' ', "space", "space"),
                   (';', "semicolon", "semicolon")),
            default=',',
            )

    def execute(self, context):
        return read_point_data(context, self.filepath, self.shift, self.col_name, self.col_x, self.col_y, self.col_z, self.separator)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportCoorPoints.bl_idname, text="Coordinate points Import Operator")


#def register():
#    bpy.utils.register_class(ImportCoorPoints)
#    bpy.types.INFO_MT_file_import.append(menu_func_import)


#def unregister():
#    bpy.utils.unregister_class(ImportCoorPoints)
#    bpy.types.INFO_MT_file_import.remove(menu_func_import)


#if __name__ == "__main__":
#    register()

    # test call
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')