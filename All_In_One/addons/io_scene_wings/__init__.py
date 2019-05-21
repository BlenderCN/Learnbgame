bl_info = {
    "name": "Wings3d import/export",
    "description": "import or export Wings3d .wings files",
    "author": "Danni coy",
    "version": (1,0),
    "blender": (2, 5, 7),
    "api": 31236,
    "location": "File > Import-Export",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Wings3d",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=<number>",
    "category": "Learnbgame"
}

import bpy
from bpy.props import StringProperty, FloatProperty, IntProperty, BoolProperty, EnumProperty
from io_utils import ImportHelper, ExportHelper

class ImportWings(bpy.types.Operator, ImportHelper):
    '''Load a BVH motion capture file'''
    bl_idname = "import_wings.wings"
    bl_label = "Import Wings"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".wings"
    filter_glob = StringProperty(default="*.wings", options={'HIDDEN'})

    use_lamps = BoolProperty(name="Lamps", description="Import Lights into scene",default=True)
    use_cameras = BoolProperty(name="Cameras", description="Import Cameras into scene",default=False)
    use_subsurfs = BoolProperty(name="SubSurface Modifier",description="Add subdivision surface modifier to each object",default=True)
    use_hidden = BoolProperty(name="Hidden", description="Import hidden objects",default=True)
    
    def execute(self, context):
        from . import import_wings
        return import_wings.load(self, context, **self.as_keywords(ignore=("filter_glob",)))

    def draw(self,context):
      layout = self.layout

      layout.prop(self,"use_lamps")
      layout.prop(self,"use_cameras")
      layout.prop(self,"use_subsurfs")
      layout.prop(self,"use_hidden")
      
class ExportWings(bpy.types.Operator, ExportHelper):
  '''Save a Wings3d file'''
  bl_idname = "export_wings.wings"
  bl_label = "Export Wings"
  filename_ext = ".wings"
  filter_glob = StringProperty(default="*.wings", options={'HIDDEN'})
  def execute(self, context):
    from . import export_wings
    return export_wings.save(self, context, **self.as_keywords(ignore=("check_existing", "filter_glob")))

def menu_func_import(self, context):
    self.layout.operator(ImportWings.bl_idname, text="Wings3d (.wings)")

def menu_func_export(self, context):
   self.layout.operator(ExportWings.bl_idname, text="Wings3d (.wings)")
  
def register():
  bpy.utils.register_module(__name__);
  bpy.types.INFO_MT_file_import.append(menu_func_import);
  bpy.types.INFO_MT_file_export.append(menu_func_export);

def unregister():
  bpy.utils.unregister_module(__name__);
  bpy.types.INFO_MT_file_import.remove(menu_func_import);
  bpy.types.INFO_MT_file_export.remove(menu_func_export);

if __name__ == "__main__":
  register()