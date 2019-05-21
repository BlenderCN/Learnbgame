# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.

#Base information
bl_info = {
    "name": "P3D importer/exporter for Crashday/Crashday Redline Edition (.p3d)",
    "author": "Maxim Johansson (Maximus)",
    "version": (0, 9, 0),
    "blender": (2, 78, 0),
    "location": "File > Import-Export > Crashday (.p3d) ",
    "description": "P3D importer/exporter for Crashday/Crashday Redline Edition",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

#Import required namespaces
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bpy.props import IntProperty, CollectionProperty
from bpy.types import Panel, UIList


#File writer function
def writeFile(context, filepath, use_some_setting):
    print("running write_some_data...")
    f = open(filepath, 'w', encoding='utf-8')
    f.write("Hello World %s" % use_some_setting)
    f.close()
    return {'FINISHED'}

#File reader function
def readFile(context, filepath, use_some_setting):
    print("running read_some_data...")
    f = open(filepath, 'r', encoding='utf-8')
    data = f.read()
    f.close()
    print(data) # would normally load the data here
    return {'FINISHED'}


class CustomProp(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    id = IntProperty()


# ui list item actions
class Uilist_actions(bpy.types.Operator):
    bl_idname = "custom.list_action"
    bl_label = "List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('CLEAR', "Clear", ""),
            ('SCAN', "Scan", ""),
        )
    )

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.custom_index

        try:
            item = scn.custom[idx]
        except IndexError:
            pass
        else:
            if self.action == 'CLEAR':
                for i in scn.custom:
                    scn.custom_index = 0
                    scn.custom.remove(0)

        if self.action == 'SCAN':
            required_items = ["main", "lod"] # The list of required items
            warning_items = ["mg_body", "maincoll", "mainshad", "headl_l", "headl_r", "headl_rl", "headl_rr", "brakel_l", "brakel_r"] # Warnings about files with exact names
            names_containing = ["det_", "gls_"] # Warnings about files with names containing some part
            
            for index, obj in enumerate(required_items):
                if bpy.data.objects.get(obj) is None:
                    item = scn.custom.add()
                    item.name = '"%s" is a crucial part and is missing!' %obj
            
            for index, obj in enumerate(names_containing):
                if bpy.data.objects.get(obj) is None:
                    item = scn.custom.add()
                    item.name = 'Atleast one object containing "%s" is missing!' %obj
            
            for index, obj in enumerate(warning_items):
                if bpy.data.objects.get(obj) is None:
                    item = scn.custom.add()
                    item.name = '"%s" is missing!' %obj
        
        info = 'Console has finished analyzing your model!'
        self.report({'INFO'}, info)
        return {"FINISHED"}

# Console custom list
class UL_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, translate=False, icon="ERROR")
    def invoke(self, context, event):
        pass   

#Export window GUI
class ExportData(Operator, ExportHelper, Panel):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export a P3D"
    filename_ext = ".p3d"
    
    filter_glob = StringProperty(
            default="Export as *.p3d",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
        )
        
    fix_flares = BoolProperty(
            name="Check omni-light flags",
            description="This will check and auto add the omni-light flags by the car lights if they are missing, if this option is greyed out, this means you already have the corresponding flare flags added",
            default=True,
        )
        
    fix_normals = BoolProperty(
            name="Check normals",
            description="Check if all the normals of all the faces are facing in the right direction and flip them if the direction is wrong",
            default=True,
        )

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.scene
        layout.label("Options:")
        
        box = layout.box()
        box.prop(self, "fix_flares")
        box.prop(self, "fix_normals")
        layout.row().separator()
        
        row = layout.row()
        row.label("Error Log:")
        layout.template_list("UL_items", "", obj, "custom", obj, "custom_index")
        
    def execute(self, context):
        return writeFile(context, self.filepath, self.fix_flares)

#Import window GUI
class ImportData(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import a P3D"
    # ImportHelper mixin class uses this
    filename_ext = ".p3d"
    filter_glob = StringProperty(
            default="*.p3d",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )

    def execute(self, context):
        return readFile(context, self.filepath, self.use_setting)

# Add the Import and Export options to Blender's "File > Import/Export" menu
def menu_func_export(self, context):
    self.layout.operator(ExportData.bl_idname, text="Crashday P3D (.p3d)").action = 'SCAN'
    
def menu_func_import(self, context):
    self.layout.operator(ImportData.bl_idname, text="Crashday P3D (.p3d)")

#Register and deregister
def register():
    bpy.utils.register_class(ExportData)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.utils.register_class(ImportData)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.custom = CollectionProperty(type=CustomProp)
    bpy.types.Scene.custom_index = IntProperty()


def unregister():
    bpy.utils.unregister_class(ExportData)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(ImportData)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index

if __name__ == "__main__":
    register()

    #Invoke on start (just for testing)!
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')
    #bpy.ops.import_test.some_data('INVOKE_DEFAULT')
