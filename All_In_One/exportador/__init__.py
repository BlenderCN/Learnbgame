bl_info = {
    "name":         "OpenglExportador",
    "author":       "forestmedina",
    "blender":      (2,6,2),
    "version":      (0,0,1),
    "location":     "File > Import-Export",
    "description":  "Exportar para OPENGL personalizado",
    "category": "Learnbgame",
}

# Ensure that we reload our dependencies if we ourselves are reloaded by Blender
if "bpy" in locals():
    import imp;
    if "gp3d" in locals():
        imp.reload(gp3d);
else:
    from gpbexporter.gp3d import (
            Exporter,
            )
        
import bpy;


def menu_func(self, context):
    self.layout.operator(Exporter.bl_idname, text="Opengl Personalizado(.mesh)");

def register():
   
    bpy.utils.register_module(__name__);
    bpy.types.INFO_MT_file_export.append(menu_func);
    bpy.types.Object.colisionador=bpy.props.BoolProperty(name="colisionador",description="Este objeto sera usado como un colisionador",default=False,options={'HIDDEN'})

    
def unregister():
    import imp;
    bpy.utils.unregister_module(__name__);
    bpy.types.INFO_MT_file_export.remove(menu_func);

if __name__ == "__main__":
    register()
