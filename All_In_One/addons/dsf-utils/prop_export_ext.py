bl_info = {
  "name": "DS Prop Export",
  "description": "export props-files to DazStudio",
  "author": "Millighost <millighost@googlemail.com",
  "version": (1, 0),
  "blender": (2, 7, 0),
  "wiki_url": "http://nonexistent",
  "category": "Import-Export"
}

def register ():
  import dsf.export_prop_op
  dsf.export_prop_op.register ()
def unregister ():
  import dsf.export_prop_op
  dsf.export_prop_op.unregister ()
