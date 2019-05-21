bl_info = {
    "name": "Add heightmap",
    "author": "Spencer Alves",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "File > Import > Import heightmap",
    "description": "Generates a mesh from a heightmap image",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
    }


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, IntProperty, StringProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from bpy_extras.image_utils import load_image

def add_object(self, context):
    scale_x = self.scale.x
    scale_y = self.scale.y
    scale_z = self.scale.z

    img = load_image(self.filename, self.directory)

    precision = self.precision
    
    width, height = img.size

    verts = []
    edges = []
    faces = []
    
    for x in range(0, width, precision):
        for y in range(0, height, precision):
            px = (x+(height-y-1)*width)*4
            verts.append(Vector((x*scale_x/width,
                                 y*scale_y/height,
                                 img.pixels[px]*scale_z)))

    nYVerts = height//precision
    for i in range(width//precision-1):
        for j in range(nYVerts-1):
            face = [j+i*nYVerts, (j+1)+i*nYVerts,
                    (j+1)+(i+1)*nYVerts, j+(i+1)*nYVerts]
            faces.append(face)

    mesh = bpy.data.meshes.new(name=img.name)
    mesh.from_pydata(verts, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh, operator=self)


class ImportHeightmap(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "import_image.to_heightmap"
    bl_label = "Import heightmap"
    bl_options = {'REGISTER', 'UNDO'}

    filename = StringProperty(name="File Name",
        description="Name of the file")
    directory = StringProperty(name="Directory",
        description="Directory of the file")

    scale = FloatVectorProperty(
            name="scale",
            default=(1.0, 1.0, 1.0),
            subtype='TRANSLATION',
            description="scaling",
            unit='LENGTH'
            )

    precision = IntProperty(
            name="precision",
            default=16,
            min=1)

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}

    def execute(self, context):

        add_object(self, context)

        return {'FINISHED'}


# Registration

def import_image_button(self, context):
    self.layout.operator(
        ImportHeightmap.bl_idname,
        text="Add heightmap")


def register():
    bpy.utils.register_class(ImportHeightmap)
    bpy.types.INFO_MT_file_import.append(import_image_button)
    bpy.types.INFO_MT_mesh_add.append(import_image_button)


def unregister():
    bpy.utils.unregister_class(ImportHeightmap)
    bpy.types.INFO_MT_file_import.append(import_image_button)
    bpy.types.INFO_MT_mesh_add.append(import_image_button)


if __name__ == "__main__":
    register()
