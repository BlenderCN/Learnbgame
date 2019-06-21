import bpy
import os

from bpy.types import Panel
from bpy.types import Operator
from bpy.types import PropertyGroup

from bpy_extras.io_utils import ImportHelper

from bpy.props import (BoolProperty,
                       FloatProperty,
                       IntProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

from .import_Agisoft_xml import *

# import points section ----------------------------------------------------------

class OBJECT_OT_IMPORTPOINTS(Operator):
    """Import points as empty objects from a txt file"""
    bl_idname = "import_points.txt"
    bl_label = "ImportPoints"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.import_test.some_data('INVOKE_DEFAULT')
        return {'FINISHED'}


def read_point_data(context, filepath, shift, name_col, x_col, y_col, z_col, separator):
    print("running read point file...")
    f = open(filepath, 'r', encoding='utf-8')
#    data = f.read()
    arr=f.readlines()  # store the entire file in a variable
    f.close()

    for p in arr:
        p0 = p.split(separator)  # use separator variable as separator
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

        # Generate object at x = lon and y = lat (and z = 0 )
        o = bpy.data.objects.new( ItemName, None )
        context.collection.objects.link(o)
 #       collection.objects.link
        o.location.x = x_coor
        o.location.y = y_coor
        o.location.z = z_coor
        o.show_name = True

    return {'FINISHED'}

class ImportCoorPoints(Operator, ImportHelper):
    """Tool to import coordinate points from a txt file"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Coordinate Points"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    shift: BoolProperty(
            name="Shift coordinates",
            description="Shift coordinates using the General Shift Value (GSV)",
            default=False,
            )

    col_name: EnumProperty(
            name="Name",
            description="Column with the name",
            items=(('0', "Column 1", "Column 1"),
                   ('1', "Column 2", "Column 2"),
                   ('2', "Column 3", "Column 3"),
                   ('3', "Column 4", "Column 4")),
            default='0',
            )
  
    col_x: EnumProperty(
            name="X",
            description="Column with coordinate X",
            items=(('0', "Column 1", "Column 1"),
                   ('1', "Column 2", "Column 2"),
                   ('2', "Column 3", "Column 3"),
                   ('3', "Column 4", "Column 4")),
            default='1',
            ) 

    col_y: EnumProperty(
            name="Y",
            description="Column with coordinate X",
            items=(('0', "Column 1", "Column 1"),
                   ('1', "Column 2", "Column 2"),
                   ('2', "Column 3", "Column 3"),
                   ('3', "Column 4", "Column 4")),
            default='2',
            )

    col_z: EnumProperty(
            name="Z",
            description="Column with coordinate X",
            items=(('0', "Column 1", "Column 1"),
                   ('1', "Column 2", "Column 2"),
                   ('2', "Column 3", "Column 3"),
                   ('3', "Column 4", "Column 4")),
            default='3',
            )     

    separator: EnumProperty(
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

    bpy.ops.import_test.some_data('INVOKE_DEFAULT')


# import multiple objs section ---------------------------------------------------

class ImportMultipleObjs(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_scene.multiple_objs"
    bl_label = "Import multiple OBJ's"
    bl_options = {'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".obj"

    filter_glob: StringProperty(
            default="*.obj",
            options={'HIDDEN'},
            )

    # Selected files
    files: CollectionProperty(type=PropertyGroup)

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    ngons_setting: BoolProperty(
            name="NGons",
            description="Import faces with more than 4 verts as ngons",
            default=True,
            )
    edges_setting: BoolProperty(
            name="Lines",
            description="Import lines and faces with 2 verts as edge",
            default=True,
            )
    smooth_groups_setting: BoolProperty(
            name="Smooth Groups",
            description="Surround smooth groups by sharp edges",
            default=True,
            )

    split_objects_setting: BoolProperty(
            name="Object",
            description="Import OBJ Objects into Blender Objects",
            default=True,
            )
    split_groups_setting: BoolProperty(
            name="Group",
            description="Import OBJ Groups into Blender Objects",
            default=True,
            )

    groups_as_vgroups_setting: BoolProperty(
            name="Poly Groups",
            description="Import OBJ groups as vertex groups",
            default=False,
            )

    image_search_setting: BoolProperty(
            name="Image Search",
            description="Search subdirs for any associated images "
                        "(Warning, may be slow)",
            default=True,
            )

    split_mode_setting: EnumProperty(
            name="Split",
            items=(('ON', "Split", "Split geometry, omits unused verts"),
                   ('OFF', "Keep Vert Order", "Keep vertex order from file"),
                   ),
            )

    clamp_size_setting: FloatProperty(
            name="Clamp Size",
            description="Clamp bounds under this value (zero to disable)",
            min=0.0, max=1000.0,
            soft_min=0.0, soft_max=1000.0,
            default=0.0,
            )
    axis_forward_setting: EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='Y',
            )

    axis_up_setting: EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Z',
            )

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "ngons_setting")
        row.prop(self, "edges_setting")

        layout.prop(self, "smooth_groups_setting")

        box = layout.box()
        row = box.row()
        row.prop(self, "split_mode_setting", expand=True)

        row = box.row()
        if self.split_mode_setting == 'ON':
            row.label(text="Split by:")
            row.prop(self, "split_objects_setting")
            row.prop(self, "split_groups_setting")
        else:
            row.prop(self, "groups_as_vgroups_setting")

#        layout = self.layout.column_flow(2)

        row.prop(self, "clamp_size_setting")
        layout.prop(self, "axis_forward_setting")
        layout.prop(self, "axis_up_setting")

        layout.prop(self, "image_search_setting")

    def execute(self, context):

        # get the folder
        folder = (os.path.dirname(self.filepath))

        # iterate through the selected files
        for i in self.files:
        
            print(i)
            path_to_file = (os.path.join(folder, i.name))

            bpy.ops.import_scene.obj(filepath = path_to_file,
                                axis_forward = self.axis_forward_setting,
                                axis_up = self.axis_up_setting,
                                use_edges = self.edges_setting,
                                use_smooth_groups = self.smooth_groups_setting,
                                use_split_objects = self.split_objects_setting,
                                use_split_groups = self.split_groups_setting,
                                use_groups_as_vgroups = self.groups_as_vgroups_setting,
                                use_image_search = self.image_search_setting,
                                split_mode = self.split_mode_setting)#,

        return {'FINISHED'}


# import agisoft xml section ----------------------------------------------------------

class OBJECT_OT_IMPORTAGIXML(Operator):
    """Import cams from an xml file"""
    bl_idname = "import_cams.agixml"
    bl_label = "ImportAgiXML"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.import_cam.agixml('INVOKE_DEFAULT')
        return {'FINISHED'}


def read_agixml_data(context, filepath, shift, chunk, allchunks):
    print("reading agisoft xml file...")
    load_create_cameras(filepath)
    

    return {'FINISHED'}

class ImportCamAgiXML(Operator, ImportHelper):
    """Tool to import cams and cams parameters from an Agisoft xml file"""
    bl_idname = "import_cam.agixml"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Agisoft XML cams"

    # ImportHelper mixin class uses this
    filename_ext = ".xml"

    filter_glob: StringProperty(
            default="*.xml",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    shift: BoolProperty(
            name="Shift coordinates",
            description="Shift coordinates using the General Shift Value (GSV)",
            default=False,
            )

    allchunks: BoolProperty(
            name="from all chunks",
            description="Import cams from all the chunks",
            default=False,
            )

    PSchunks: IntProperty(
            name="chunk number",
            default=1,
            description="number of chunk",
            )


    def execute(self, context):
        return read_agixml_data(context, self.filepath, self.shift, self.PSchunks, self.allchunks)

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportCoorPoints.bl_idname, text="Coordinate points Import Operator")

    bpy.ops.import_cam.agixml('INVOKE_DEFAULT')


