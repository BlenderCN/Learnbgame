bl_info = {
    "name": "Used Indexes",
    "author": "Alex Saplacan",
    "version": (0, 3),
    "blender": (2, 78, 0),
    "location": "Properties",
    "description": "Displays the Material or object indexes already used.",
    "warning": "",
    "wiki_url": "",
    "category": "UI",
    }

import bpy

def draw_indexes(self, context, idx_list):

    draw_text = str(idx_list[0])
    for ind in idx_list[1:]:
        draw_text += ', %s' %(ind)

    layout = self.layout
    col = layout.column()
    col.label("Indexes already used:")
    col.label(draw_text)


def draw_obj_used_indexes(self, context):
    """
    Display the Object IDs already used
    """
    scene = context.scene

    ob_indx_list = []
    for obj in bpy.context.scene.objects:
        idx = obj.pass_index
        if idx not in ob_indx_list:
            ob_indx_list.append(idx)
    ob_indx_list.sort()
    draw_indexes(self, context, ob_indx_list)

def draw_mat_used_indexes(self, context):
    """
    Display IDs already used by other materials.
    """
    mat_indx_list = []
    for material in bpy.data.materials:
        idx = material.pass_index
        if idx not in mat_indx_list:
            mat_indx_list.append(idx)
    mat_indx_list.sort()
    draw_indexes(self, context, mat_indx_list)

def register():
    bpy.types.OBJECT_PT_relations.append(draw_obj_used_indexes)
    bpy.types.CyclesMaterial_PT_settings.append(draw_mat_used_indexes)

def unregister():
    bpy.types.OBJECT_PT_relations.remove(draw_obj_used_indexes)
    bpy.types.CyclesMaterial_PT_settings.remove(draw_mat_used_indexes)

if __name__ == "__main__":
    register()
