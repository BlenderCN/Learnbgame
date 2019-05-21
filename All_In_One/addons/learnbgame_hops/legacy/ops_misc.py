import bpy
import bmesh
from bpy.props import BoolProperty
import bpy.utils.previews


class HOPS_OT_MakeLink(bpy.types.Operator):
    bl_idname = "make.link"
    bl_label = "Make Link"
    bl_description = "Link Object Mesh Data"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.object.make_links_data(type='OBDATA')
        bpy.ops.object.make_links_data(type='MODIFIERS')

        return {"FINISHED"}

# Solid All


class HOPS_OT_SolidAll(bpy.types.Operator):
    bl_idname = "object.solid_all"
    bl_label = "Solid All"
    bl_description = "Make Object Solid Shaded"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # for obj in bpy.data.objects:
        #     if bpy.context.selected_objects:
        #         if obj.select:

        for obj in context.selected_objects:
            if obj.display_type == 'WIRE' or 'BOUNDS':
                obj.display_type = 'SOLID'
                bpy.context.object.show_wire = False
                bpy.context.object.display_type = 'TEXTURED'
                bpy.context.object.cycles_visibility.shadow = True
                bpy.context.object.cycles_visibility.camera = True
                bpy.context.object.cycles_visibility.diffuse = True
                bpy.context.object.cycles_visibility.glossy = True
                bpy.context.object.cycles_visibility.transmission = True
                bpy.context.object.cycles_visibility.scatter = True
            elif obj.display_type == 'SOLID':
                obj.display_type = 'WIRE'

            else:
                obj.display_type = 'WIRE'

        bpy.context.object.cycles_visibility.camera = True
        bpy.context.object.show_wire = False
        bpy.context.object.cycles_visibility.shadow = True
        bpy.context.object.display_type = 'TEXTURED'

        return {'FINISHED'}


class HOPS_OT_ReactivateWire(bpy.types.Operator):
    bl_idname = "showwire.objects"
    bl_label = "showWire"
    bl_description = "Make Object Wire Shaded"
    bl_options = {'REGISTER', 'UNDO'}

    noexist: BoolProperty(default=False)

    realagain: BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop(self, 'noexist', text="Unrenderable")
        box.prop(self, 'realagain', text="Make Real")

    def execute(self, context):
        bpy.context.object.show_wire = True
        bpy.context.object.display_type = 'WIRE'
        bpy.context.object.show_all_edges = True

        if self.noexist:
            bpy.context.object.cycles_visibility.camera = False
            bpy.context.object.cycles_visibility.diffuse = False
            bpy.context.object.cycles_visibility.glossy = False
            bpy.context.object.cycles_visibility.transmission = False
            bpy.context.object.cycles_visibility.scatter = False
            bpy.context.object.cycles_visibility.shadow = False

        if self.realagain:
            bpy.context.object.cycles_visibility.camera = True
            bpy.context.object.cycles_visibility.diffuse = True
            bpy.context.object.cycles_visibility.glossy = True
            bpy.context.object.cycles_visibility.transmission = True
            bpy.context.object.cycles_visibility.scatter = True
            bpy.context.object.cycles_visibility.shadow = True
            bpy.context.object.display_type = 'WIRE'
            bpy.context.object.display_type = 'TEXTURED'
            bpy.context.object.show_all_edges = False
            bpy.context.object.show_wire = False

        else:
            bpy.context.object.cycles_visibility.camera = False
            bpy.context.object.cycles_visibility.shadow = False
            bpy.context.object.cycles_visibility.transmission = False
            bpy.context.object.cycles_visibility.scatter = False
            bpy.context.object.cycles_visibility.diffuse = False
            bpy.context.object.cycles_visibility.glossy = False

        return {'FINISHED'}

# Show Overlays


class HOPS_OT_ShowOverlays(bpy.types.Operator):
    bl_idname = "object.showoverlays"
    bl_label = "Show Overlays"
    bl_description = "Show Marked Edge Overlays"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.object.data.show_edge_crease = True
        bpy.context.object.data.show_edge_sharp = True
        bpy.context.object.data.show_edge_bevel_weight = True

        return {"FINISHED"}

# Hide Overlays


class HOPS_OT_HideOverlays(bpy.types.Operator):
    bl_idname = "object.hide_overlays"
    bl_label = "Hide Overlays"
    bl_description = "Hide Marked Edge Overlays"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.object.data.show_edge_crease = False
        bpy.context.object.data.show_edge_sharp = False
        bpy.context.object.data.show_edge_bevel_weight = False
        return {"FINISHED"}

# Place Object


class HOPS_OT_UnLinkObjects(bpy.types.Operator):
    bl_idname = "unlink.objects"
    bl_label = "UnLink_Objects"
    bl_description = "Unlink Object Mesh Data"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
        return {"FINISHED"}

# Apply Material


class HOPS_OT_ApplyMaterial(bpy.types.Operator):
    bl_idname = "object.apply_material"
    bl_label = "Apply material"
    bl_description = "Apply scene material to object"

    mat_to_assign: bpy.props.StringProperty(default="")

    def execute(self, context):

        if context.object.mode == 'EDIT':
            obj = context.object
            bm = bmesh.from_edit_mesh(obj.data)

            selected_face = [f for f in bm.faces if f.select]  # si des faces sont sélectionnées, elles sont stockées dans la liste "selected_faces"

            mat_name = [mat.name for mat in bpy.context.object.material_slots if len(bpy.context.object.material_slots)]  # pour tout les material_slots, on stock les noms des mat de chaque slots dans la liste "mat_name"

            if self.mat_to_assign in mat_name:  # on test si le nom du mat sélectionné dans le menu est présent dans la liste "mat_name" (donc, si un des slots possède le materiau du même nom). Si oui:
                context.object.active_material_index = mat_name.index(self.mat_to_assign)  # on definit le slot portant le nom du comme comme étant le slot actif
                bpy.ops.object.material_slot_assign()  # on assigne le matériau à la sélection
            else:  # sinon
                bpy.ops.object.material_slot_add()  # on ajout un slot
                bpy.context.object.active_material = bpy.data.materials[self.mat_to_assign]  # on lui assigne le materiau choisi
                bpy.ops.object.material_slot_assign()  # on assigne le matériau à la sélection

            return {'FINISHED'}

        elif context.object.mode == 'OBJECT':

            obj_list = [obj.name for obj in context.selected_objects]

            for obj in obj_list:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[obj].select_set(state=True)
                bpy.context.view_layer.objects.active = bpy.data.objects[obj]
                bpy.context.object.active_material_index = 0

                if self.mat_to_assign == bpy.data.materials:
                    bpy.context.active_object.active_material = bpy.data.materials[mat_name]

                else:
                    if not len(bpy.context.object.material_slots):
                        bpy.ops.object.material_slot_add()

                    bpy.context.active_object.active_material = bpy.data.materials[self.mat_to_assign]

            for obj in obj_list:
                bpy.data.objects[obj].select_set(state=True)

            return {'FINISHED'}

# Delete modifiers


class HOPS_OT_DeleteModifiers(bpy.types.Operator):
    bl_idname = "delete.modifiers"
    bl_label = "Delete modifiers"
    bl_description = "Delete all modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selection = bpy.context.selected_objects

        if not(selection):
            for obj in bpy.data.objects:
                for mod in obj.modifiers:
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_remove(modifier=mod.name)
        else:
            for obj in selection:
                for mod in obj.modifiers:
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_remove(modifier=mod.name)
        return {'FINISHED'}


class HOPS_OT_BevelWeighSwap(bpy.types.Operator):
    bl_idname = "weight.swap"
    bl_label = "Swap bevel weight"
    bl_description = "Swap Bevel Weight"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # go to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Select all edges that have bewel weight below 0.5  (it can be use as >01 and <03 to select exact one)
        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        cr = bm.edges.layers.bevel_weight.verify()

        me.show_edge_bevel_weight = True

        for e in bm.edges:
            if (e[cr] < 0.5):
                # select edges
                e.select_set(state=True)
                print(e[cr])

        bmesh.update_edit_mesh(me, False, False)

        # add 07 Bweight to selected ones
        bpy.ops.transform.edge_bevelweight(value=0.7)

        # go back to obj mode
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


# By: 'Sybren A. Stüvel',
class HOPS_OT_MaterialOtSimplifyNames(bpy.types.Operator):
    bl_idname = "material.simplify"
    bl_label = "Link materials to remove 00X mats"
    bl_description = "Consolidates materials to remove duplicates"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for ob in context.selected_objects:
            for slot in ob.material_slots:
                self.fixup_slot(slot)

        return {'FINISHED'}

    def split_name(self, material):
        name = material.name

        if not '.' in name:
            return name, None

        base, suffix = name.rsplit('.', 1)
        try:
            num = int(suffix, 10)
        except ValueError:
            # Not a numeric suffix
            return name, None

        return base, suffix

    def fixup_slot(self, slot):
        if not slot.material:
            return

        base, suffix = self.split_name(slot.material)
        if suffix is None:
            return

        try:
            base_mat = bpy.data.materials[base]
        except KeyError:
            print('Base material %r not found' % base)
            return

        slot.material = base_mat
