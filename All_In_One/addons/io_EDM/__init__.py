
bl_info = {
  'name': "Import: .EDM model files",
  'description': "Importing of .EDM model files",
  'author': "Nicholas Devenish",
  'version': (0,3,0),
  'blender': (2, 78, 0),
  'location': "File > Import/Export > .EDM Files",
  'category': 'Import-Export',
}

try:
  import bpy

  def register():
    from .io_operators import register as importer_register
    from .rna import register as rna_register
    from .panels import register as panels_register
    rna_register()
    panels_register()
    importer_register()

  def unregister():
    from .io_operators import unregister as importer_unregister
    from .rna import unregister as rna_unregister
    from .panels import unregister as panels_unregister
    importer_unregister()
    panels_unregister()
    rna_unregister()

  if __name__ == "__main__":
    register()
except ImportError:
  # Allow for now, as we might just want to import the sub-package
  pass