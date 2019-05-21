
bl_info = {
    "name": "Ogre Blender Importer",
    "author": "Julien De Loor",
    "location": "File > Import-Export",
    "blender": (2,76,0),
    "category": "Import-Export"
}

import bpy;
import os;

try:
    from OgreMeshSerializer import *
    from OgreMaterialSerializer import *
    from OgreSkeletonSerializer import *

except ImportError as e:
    directory = os.path.dirname(os.path.realpath(__file__));
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreMeshSerializer.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))
    srcfile="OgreMaterialSerializer.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))
    srcfile="OgreSkeletonSerializer.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))




class IMPORT_OT_ogre_mesh(bpy.types.Operator):
    bl_idname = "import.ogre_mesh";
    bl_label = "Import Ogre Mesh (.mesh)";
    bl_description = "Import mesh data from Ogre Mesh (.mesh files)";

    filename_ext = ".mesh";
    filter_glob = bpy.props.StringProperty(default="*.mesh", options={'HIDDEN'})
    files = bpy.props.CollectionProperty(name="File Path", type=bpy.types.OperatorFileListElement);
    directory = bpy.props.StringProperty(subtype='DIR_PATH');
    print_corrupted_chunks = bpy.props.BoolProperty(
        name="Report corrupted chunks",
        description="Report any corrupted chunks in the terminal (blender must be launched in terminal)",
        default=True);

    def execute(self, context):
        meshserializer = OgreMeshSerializer();
        if (self.print_corrupted_chunks):
            meshserializer.enableValidation();
        else:
            meshserializer.disableValidation();

        if (len(self.files) > 1):
            errors = 0 ;
            last_tb = None;
            filefails = [];
            for f in self.files:
                filepath = os.path.join(self.directory,f.name);
                meshfile = open(filepath,mode='rb');
                try:
                    meshserializer.importMesh(meshfile);
                except Exception as e:
                    errors = errors + 1;
                    filefails.append(f.name)
                    last_tb = sys.exc_info()[2];
                    print("Failed to load properly " + f.name + ": " + str(e));

            if errors > 0:
                raise RuntimeError(str(errors) + " errors while loading " + str(len(self.files)) +" files, load each file "+ str(filefails)+" separately for details").with_traceback(last_tb);

        elif (len(self.files)==1):
            filepath = os.path.join(self.directory,self.files[0].name);
            meshfile = open(filepath,mode='rb');
            meshserializer.importMesh(meshfile);

        return {'FINISHED'};


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self);
        return {'RUNNING_MODAL'};


def menu_func_import_ogre_mesh(self, context):
    self.layout.operator(IMPORT_OT_ogre_mesh.bl_idname, text="Ogre Mesh (.mesh)");

#def menu_func_import_ogre_material(self, context):
#    self.layout.operator(IMPORT_OT_ogre_mesh.bl_idname, text="Ogre Material (.material)");



def register():
    bpy.utils.register_module(__name__);
    bpy.types.INFO_MT_file_import.append(menu_func_import_ogre_mesh);

def unregister():
    bpy.utils.unregister_module(__name__);
    bpy.types.INFO_MT_file_import.remove(menu_func_import_ogre_mesh);


if __name__ == "__main__":
    register();
