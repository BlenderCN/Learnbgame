import bpy
import bmesh
from mathutils import Vector

bl_info = {
    'name': 'Add Empties',
    'author': 'Dealga McArdle (zeffii)',
    'version': (1, 0, 0),
    'blender': (2, 6, 3),
    'location': 'Add > Empties',
    'description': 'adds new Empty while in edit mode',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh'}


def add_to_selected(context):

    # be in edit mode to run this code  
    myob = bpy.context.active_object  
    bpy.ops.object.mode_set(mode = 'OBJECT')  
      
    # collect selected verts
    selected_idx = [i.index for i in myob.data.vertices if i.select]

    if len(selected_idx) == 0:
        print('no verts selected')
        return

    # seems good to go! 
    original_object = myob.name

    for v_index in selected_idx:
        # get local coordinate, turn into word coordinate
        vert_coordinate = myob.data.vertices[v_index].co  
        vert_coordinate = myob.matrix_world * vert_coordinate
          
        # unselect all  
        for item in bpy.context.selectable_objects:  
            item.select = False  
        
        # this deals with adding the empty      
        bpy.ops.object.add(type='EMPTY', location=vert_coordinate)  
        mt = bpy.context.active_object  
        mt.location = vert_coordinate
        mt.empty_draw_size = mt.empty_draw_size / 4  
          
        bpy.ops.object.select_all(action='TOGGLE')  
        bpy.ops.object.select_all(action='DESELECT')  
        
    # set original object to active, selects it, place back into editmode
    bpy.context.scene.objects.active = myob
    myob.select = True  
    bpy.ops.object.mode_set(mode = 'EDIT')
    return



class AddEmpties(bpy.types.Operator):
    """Add a vertex to 3d cursor location"""
    bl_idname = "object.empties_add"
    bl_label = "Add Empties"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_to_selected(context)    
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddEmpties.bl_idname, icon='EMPTY_DATA')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.prepend(menu_func)
    

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
