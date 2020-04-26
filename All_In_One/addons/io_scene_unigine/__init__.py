bl_info = {
    "name": "Unigine import/export",
    "description": "import or export Unigine .mesh files",
    "author": "Danni coy",
    "version": (1,0),
    "blender": (2, 5, 7),
    "api": 31236,
    "location": "File > Import-Export",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Unigine",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=<number>",
    "category": "Learnbgame",
}

import bpy
from bpy.props import StringProperty, FloatProperty, IntProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

class ImportUnigine(bpy.types.Operator, ImportHelper):
    '''Load a BVH motion capture file'''
    bl_idname = "import_unigine.mesh"
    bl_label = "Import Unigine"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".mesh"
    filter_glob = StringProperty(default="*.mesh;*.smesh;*.node", options={'HIDDEN'})

    #use_lamps = BoolProperty(name="Lamps", description="Import Lights into scene",default=True)
    #use_cameras = BoolProperty(name="Cameras", description="Import Cameras into scene",default=False)
    #use_subsurfs = BoolProperty(name="SubSurface Modifier",description="Add subdivision surface modifier to each object",default=True)
    #use_hidden = BoolProperty(name="Hidden", description="Import hidden objects",default=True)

    def execute(self, context):
        from . import import_unigine
        return import_unigine.load(self, context, **self.as_keywords(ignore=("filter_glob",)))

    #def draw(self,context):
      #layout = self.layout

      #layout.prop(self,"use_lamps")
      #layout.prop(self,"use_cameras")
      #layout.prop(self,"use_subsurfs")
      #layout.prop(self,"use_hidden")

class ExportUnigine(bpy.types.Operator, ExportHelper):
  '''Save a Unigine3d file'''
  bl_idname = "export_unigine.mesh"
  bl_label = "Export Unigine"
  filename_ext = ".mesh"
  filter_glob = StringProperty(default="*.mesh", options={'HIDDEN'})
  def execute(self, context):
    from . import export_unigine
    return export_unigine.save(self, context, **self.as_keywords(ignore=("check_existing", "filter_glob")))

def menu_func_import(self, context):
    self.layout.operator(ImportUnigine.bl_idname, text="Unigine (.mesh)")

def menu_func_export(self, context):
   self.layout.operator(ExportUnigine.bl_idname, text="Unigine3d (.mesh)")

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