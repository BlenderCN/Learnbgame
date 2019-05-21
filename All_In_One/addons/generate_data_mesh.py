import bpy
from bpy.types import Operator, Panel

bl_info = {
    "name": "Generate data mesh",
    "description": "Save the data of the active object in a .py file",
    "author": "Legigan Jeremy AKA Pistiwique",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "Text Editor",
    "category": "Learnbgame"
}


extend_template = '''bl_info = {
"name": "Add %s",
"author": "Your Name Here",
"version": (1, 0),
"blender": (2, 75, 0),
"location": "View3D > Add > Mesh > New Object",
"description": "Add %s Object",
"category": "Add Mesh",
}

%s

def add_%s_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_cutom_%s.bl_idname,
        text="Add %s",
        icon='PLUGIN')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(add_%s_button)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(add_%s_button)

if __name__ == "__main__":
    register()
'''

template = '''import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

def add_object(self, context):
    verts = %s

    edges = []

    faces = %s

    mesh = bpy.data.meshes.new(name = "%s")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(context, mesh, operator = self)


class OBJECT_OT_add_cutom_%s(Operator, AddObjectHelper):
    bl_idname = 'mesh.add_custom_%s'
    bl_label = "Add %s"
    bl_options = {'REGISTER'}

    def execute(self, context):
        add_object(self, context)

        return {'FINISHED'}'''


def get_valid_name(name):
    validName = ""

    for l in name:
        if not l.isalpha():
            validName += "_"
        else:
            validName += l

    return validName


class GENERATOR_generate_data_mesh(Operator):
    ''' Create a new text and write completed template '''
    bl_idname = 'text.generate_code'
    bl_label = "Generate"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.object is not None\
               and context.object.type == 'MESH'\
               and context.active_object

    def execute(self, context):
        wm = context.window_manager
        OBJ = context.active_object
        # Get all vertices location from the active object
        objectVerts = [v.co for v in OBJ.data.vertices]
        # Get vertices index from each faces
        objectFaces = [[v for v in f.vertices] for f in OBJ.data.polygons]

        # Create new text
        newText = bpy.data.texts.new(OBJ.name + "_datas.py")
        bpy.context.space_data.text = newText
        obName = OBJ.name
        validName = get_valid_name(OBJ.name)

        # Write the code in the new text
        if wm.extend_to_addon:
            newText.write(extend_template %(obName,
                                            obName,
                                            template % (objectVerts.__repr__(),
                                                        objectFaces.__repr__(),
                                                        validName,
                                                        validName,
                                                        validName,
                                                        obName
                                                        ),
                                            validName,
                                            validName,
                                            obName,
                                            validName,
                                            validName
                                            )
                          )

        else:
            newText.write(template %(objectVerts.__repr__(),
                                     objectFaces.__repr__(),
                                     validName,
                                     validName,
                                     validName,
                                     obName
                                     )
                          )

        return {'FINISHED'}


class TEXT_PT_generate_data_mesh_panel(Panel):
    bl_label = "Generate Data Mesh"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        layout.prop(wm, 'extend_to_addon')
        layout.operator('text.generate_code')


def register():
    bpy.types.WindowManager.extend_to_addon = bpy.props.BoolProperty(
            name = "Extend to addon",
            default = False,
            )

    bpy.utils.register_module(__name__)


def unregister():
    del bpy.types.WindowManager.extend_to_addon
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()