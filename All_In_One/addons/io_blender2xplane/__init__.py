
bl_info = {
    'name': 'Import/Export: XPlaneNG',
    'author': 'STS',
    'version': (1,00),
    'blender': (2, 5, 7),
    'api': 35622,
    'location': 'File > Import/Export > XPlaneNG ',
    'description': 'Import and Export XPlane objects/planes (.obj format)',
    'warning': 'beta', # used for warning icon and text in addons panel
    'category': 'Import-Export'}



if "bpy" in locals():
    import imp
    if "xplane_export" in locals():
        imp.reload(xplane_export)
else:
    import os
    import bpy
    from bpy.props import StringProperty, BoolProperty
    from bpy_extras.io_utils import ExportHelper, ImportHelper
    from . import xplane_export



class XPlaneNG_Export(bpy.types.Operator, ExportHelper):
    '''Export to XPlane Object file format (.obj)'''
    bl_idname = "xplane_export.obj"
    bl_label = 'Export XPlane Object'
    
    filepath = StringProperty(name="File Path", description="Filepath used for exporting the XPlane file(s)", maxlen= 1024, default=xplane_export.output_directory + os.path.sep + xplane_export.output_filename)
    filename_ext = '.obj'
    filter_glob = StringProperty(default="*.obj", options={'HIDDEN'})
    check_existing = BoolProperty(name="Check Existing", description="Check and warn on overwriting existing files", default=True, options={'HIDDEN'})

    def execute(self, context):
        filepath = self.properties.filepath
        if filepath=='':
            filepath = os.path.dirname(bpy.context.blend_data.filepath) + os.path.sep + "unnamed.obj"

        filepath = bpy.path.ensure_ext(filepath,self.filename_ext)
        path = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        xplane_export.output_directory = path
        xplane_export.output_filename = filename
        xplane_export.GoExport()

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func(self, context):
    self.layout.operator(XPlaneNG_Export.bl_idname, text="XPlaneNG Object (.obj)")

def register():
#    print("Initializing BLENDER2XPLANE")
    xplane_export.output_directory = os.path.dirname(bpy.context.blend_data.filepath)
    xplane_export.output_filename = "unnamed.obj"
    xplane_export.Register()
    bpy.utils.register_class(XPlaneNG_Export)
    bpy.types.INFO_MT_file_export.append(menu_func)
#    bpy.utils.register_module(__name__)

def unregister():    
#    print("Uninitializing BLENDER2XPLANE")
    xplane_export.Unregister()
    bpy.utils.unregister_class(XPlaneNG_Export)
    bpy.types.INFO_MT_file_export.remove(menu_func)
#    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
#