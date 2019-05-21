bl_info = {
        "name": "material List",
    'description': '"material List from Hard Ops addon."',
    'author': 'bookyakuno',
    'version': (1,1),
    'blender': (2, 76, 0),
    'warning': "",
    'location': 'View3D > Ctrl + Shift + F',
    'category': 'Material'
}


import bpy
import bmesh
# import os
# from bpy.types import Panel
#
# from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty
from bpy.props import (
                        StringProperty,
                        BoolProperty,
                        EnumProperty,
                        PointerProperty,
                        )

from bpy.props import *
from bpy.types import Menu, Operator, Panel, UIList
from bpy.app.handlers import persistent



set_material_name_z = StringProperty(
        name="New Material name",
        description="What Base name pattern to use for a new created Material\n"
                    "It is appended by an automatic numeric pattern depending\n"
                    "on the number of Scene's materials containing the Base",
        default="Material_New",
        maxlen=128,
        )






def c_need_of_viewport_colors():
    # check the context where using Viewport color and friends are needed
    # Cycles and BI are supported
    if c_render_engine("Cycles"):
        if c_context_use_nodes() and c_context_mat_preview() == 'SOLID':
            return True
        elif c_context_mat_preview() in ('SOLID', 'TEXTURED', 'MATERIAL'):
            return True
    elif (c_render_engine("BI") and not c_context_use_nodes()):
        return True

    return False





class VIEW3D_MT_select_material_xx(bpy.types.Menu):
    bl_label = "Select by Material"
    bl_options = {"REGISTER","UNDO"}

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        ob = context.object
        layout.label
        if ob.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT') #編集
            #show all used materials in entire blend file
            for material_name, material in bpy.data.materials.items():
                if material.users > 0:
                    layout.operator("view3d.select_material_by_name",
                                    text=material_name,
                                    icon='MATERIAL_DATA',
                                    ).matname = material_name

        elif ob.mode == 'EDIT':
            bpy.ops.mesh.select_all(action='DESELECT')#編集
            #show only the materials on this object
            mats = ob.material_slots.keys()
            for m in mats:
                layout.operator("view3d.select_material_by_name",
                    text=m,
                    icon='MATERIAL_DATA').matname = m





#Apply Material
class ApplyMaterial(bpy.types.Operator):
    bl_idname = "object.apply_material_z"
    bl_label = "Apply material"
    bl_options = {"REGISTER","UNDO"}

    mat_to_assign = bpy.props.StringProperty(default="")

    def execute(self, context):

        if context.object.mode == 'EDIT':
            obj = context.object
            bm = bmesh.from_edit_mesh(obj.data)


            selected_face = [f for f in bm.faces if f.select]  # si des faces sont sélectionnées, elles sont stockées dans la liste "selected_faces"

            mat_name = [mat.name for mat in bpy.context.object.material_slots if len(bpy.context.object.material_slots)] # pour tout les material_slots, on stock les noms des mat de chaque slots dans la liste "mat_name"


            if self.mat_to_assign in mat_name: # on test si le nom du mat sélectionné dans le menu est présent dans la liste "mat_name" (donc, si un des slots possède le materiau du même nom). Si oui:
                context.object.active_material_index = mat_name.index(self.mat_to_assign) # on definit le slot portant le nom du comme comme étant le slot actif
                bpy.ops.object.material_slot_assign() # on assigne le matériau à la sélection
            else: # sinon
                bpy.ops.object.material_slot_add() # on ajout un slot
                bpy.context.object.active_material = bpy.data.materials[self.mat_to_assign] # on lui assigne le materiau choisi
                bpy.ops.object.material_slot_assign() # on assigne le matériau à la sélection

            return {'FINISHED'}

        elif context.object.mode == 'OBJECT':

            obj_list = [obj.name for obj in context.selected_objects]

            for obj in obj_list:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[obj].select = True
                bpy.context.scene.objects.active = bpy.data.objects[obj]
                bpy.context.object.active_material_index = 0

                if self.mat_to_assign == bpy.data.materials:
                    bpy.context.active_object.active_material = bpy.data.materials[mat_name]

                else:
                    if not len(bpy.context.object.material_slots):
                        bpy.ops.object.material_slot_add()

                    bpy.context.active_object.active_material = bpy.data.materials[self.mat_to_assign]

            for obj in obj_list:
                bpy.data.objects[obj].select = True

            return {'FINISHED'}







#Apply Material
class new_mat(bpy.types.Operator):
    bl_idname = "object.new_mat"
    bl_label = "New Material"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):


        ob = bpy.context.active_object

        # Get material
        # mat = bpy.data.materials.get("_cmnmat_")
        # if mat is None:
        # create material
        mat = bpy.data.materials.new(name="Material")

        # Assign it to object
        if ob.data.materials:
            # assign to 1st material slot
            ob.data.materials[0] = mat
        else:
            # no slots
            ob.data.materials.append(mat)

        if context.scene.render.engine == 'CYCLES':
            bpy.context.object.active_material.use_nodes = True

        return {'FINISHED'}


# Material
class MaterialListMenu_z(bpy.types.Menu):
    bl_idname = "object.material_list_menu_z"
    bl_label = "Material_list_xz"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        ################################################################
        col.operator("object.new_mat")
        col.separator()

        if len(bpy.data.materials):
            for mat in bpy.data.materials:
                name = mat.name
                try:
                    icon_val = layout.icon(mat)
                except:
                    icon_val = 1
                    print ("WARNING [Mat Panel]: Could not get icon value for %s" % name)

                op = col.operator("object.apply_material_z", text=name, icon_value=icon_val)
                op.mat_to_assign = name
        else:
            col.label("No data materials")

        col.separator()



################################################################




#
# =====================================================
# =====================================================
# =====================================================
# =====================================================
#
class ExtraMaterialList_PT_z(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_label = "mat List"
    def draw(self, context):
        layout = self.layout
        cs = context.scene
        sdata = context.space_data
        props = cs.extra_material_list
        #--- Object materials
        layout.template_list(
            "extra_material_list.material_list", "",
            bpy.data, "materials",
            props, "material_id",
            rows = len(bpy.data.materials)
        )
        split = layout.split(percentage=0.7)
        split.operator("material.del_mat",text="del_active_mat",icon="CANCEL")
        split.operator("material.del_0_mat",icon="X")




# =====================================================
# =====================================================


class del_mat(Operator):
    bl_idname = "material.del_mat"
    bl_label = "del mat"
    bl_description = "Perfect Delete Material in Project"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        for material in bpy.context.active_object.data.materials:
            material.user_clear()
            bpy.data.materials.remove(material)

        return{'FINISHED'}

class del_0_mat(Operator):
    bl_idname = "material.del_0_mat"
    bl_label = "del 0 user mat"
    bl_description = "Clean 0 user Material in Project"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        for material in bpy.data.materials:
            if not material.users:
                bpy.data.materials.remove(material)
        return {'FINISHED'}




#
#   =====================================================
# =====================================================
#

def register():
    bpy.utils.register_module(__name__)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu', 'F', 'PRESS', ctrl = True)
        kmi.properties.name = "object.material_list_menu_z"

def unregister():
    bpy.utils.unregister_module(__name__)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps['3D View']
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu':
                if kmi.properties.name == "object.material_list_menu_z":
                    km.keymap_items.remove(kmi)
                    break

if __name__ == "__main__":
    register()
