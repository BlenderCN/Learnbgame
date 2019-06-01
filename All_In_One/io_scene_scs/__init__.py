##############################################################################
#
# Blender add-on for converting 3D models to SCS games
# Copyright (C) 2013  Simon Lušenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
# 
# For any additional information e-mail me to simon_lusenc (at) msn.com
#
##############################################################################

bl_info = {
    "name": "Blender2SCS: SCS software model import/export",
    "author": "Simon Lušenc",
    "version": (0, 3, 2),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Imports/exports models for SCS software game engine",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Learnbgame",
    }


from . import help_funcs, import_pmc


if "bpy" in locals():
    import imp

    if "help_funcs" in locals():
        imp.reload(help_funcs)
    if "import_pmg" in locals():
        imp.reload(import_pmg)
    if "import_pmd" in locals():
        imp.reload(import_pmd)
    if "import_tobj" in locals():
        imp.reload(import_tobj)
    if "import_mat" in locals():
        imp.reload(import_mat)
    if "import_scs" in locals():
        imp.reload(import_scs)
    if "import_pmc" in locals():
        imp.reload(import_pmc)

import bpy, bmesh, os, time, glob
from bpy.types import Panel
from bpy.props import (BoolProperty,
                       IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
)

from bpy_extras.io_utils import (ExportHelper,
                                 ImportHelper,
                                 path_reference_mode,
                                 axis_conversion,
)


def root_obj():
    """
    Function for returning SCS root object
    """
    obj_li = [ob for ob in bpy.data.objects if "scs_is_root" in ob]
    if len(obj_li) == 0:
        return None
    return obj_li[0]


def get_coll_type(self):
    if "scs_coll_type" in self:
        return self["scs_coll_type"]
    return -1


def set_coll_type(self, type):
    ob = self
    #scs_coll_init used for identifying initial set
    #from property set in toolbox
    if "scs_coll_init" in ob:
        self["scs_coll_type"] = type
        del (ob["scs_coll_init"])
        return

    me = ob.data
    loc = ob.location
    rot = ob.rotation_quaternion
    scale = (1, 1, 1)
    name = ob.name
    parent_ob = ob.parent
    variants = ob.get("scs_variant_visib")

    #remove old objects and mesh
    bpy.ops.object.delete(use_global=True)

    print("Query type:", type)
    if type == 0:  #"box":
        new_ob = import_pmc.draw_box(loc, rot, scale, name, parent_ob)
    elif type == 1:  #"cylinder":
        new_ob = import_pmc.draw_cylinder(loc, rot, scale[0], scale[2], name, parent_ob)
    elif type == 2:  #"geometry":
        verts = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)]
        faces = [(0, 1, 3, 2)]
        new_ob = import_pmc.draw_geometry(loc, rot, verts, faces, name, parent_ob)

    new_ob["scs_variant_visib"] = variants
    #select and set new object as active
    new_ob.select = True
    bpy.data.scenes[bpy.context.scene.name].objects.active = new_ob


def cls():
    os.system(['clear', 'cls'][os.name == 'nt'])


###################################################################
#
# SCS tools operators
#
###################################################################  
class SCS_OP_clear_scene(bpy.types.Operator):
    bl_idname = "scene.clear"
    bl_label = "Clears out all elements on scene"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.active_object is not None and not context.active_object.hide:
            bpy.ops.object.mode_set(mode='OBJECT')

        obj = 0
        while len(bpy.data.objects) > 0:
            for scene in bpy.data.scenes:
                if bpy.data.objects[0].name in scene.objects:
                    scene.objects.unlink( bpy.data.objects[0])
            bpy.data.objects.remove(bpy.data.objects[0])
            obj += 1

        mesh = 0
        while len(bpy.data.meshes) > 0:
            bpy.data.meshes[0].user_clear()
            bpy.data.meshes.remove(bpy.data.meshes[0])
            mesh += 1

        armature = 0
        while len(bpy.data.armatures) > 0:
            bpy.data.armatures[0].user_clear()
            bpy.data.armatures.remove(bpy.data.armatures[0])
            armature += 1

        actions = 0
        while len(bpy.data.actions) > 0:
            bpy.data.actions[0].user_clear()
            bpy.data.actions.remove(bpy.data.actions[0])
            actions += 1

        mats = 0
        while len(bpy.data.materials) > 0:
            bpy.data.materials.remove(bpy.data.materials[0])
            mats += 1

        texs = 0
        while len(bpy.data.textures) > 0:
            bpy.data.textures[0].user_clear()
            bpy.data.textures.remove(bpy.data.textures[0])
            texs += 1

        imgs = 0
        while len(bpy.data.images) > 1:
            bpy.data.images[0].user_clear()
            bpy.data.images.remove(bpy.data.images[0])
            imgs += 1

        lamps = 0
        while len(bpy.data.lamps) > 0:
            bpy.data.lamps[0].user_clear()
            bpy.data.lamps.remove(bpy.data.lamps[0])
            lamps += 1

        #print("Deleted objs:", obj, " Deleted meshes:", mesh)
        #print("Deleted materials:", mats, "Deleted textures:", texs, "Deleted images:", imgs)
        #print("Deleted lamps:", lamps)

        return {"FINISHED"}


class SCS_OP_delete_node(bpy.types.Operator):
    bl_idname = "object.delete_node"
    bl_label = "Delete active object and it's children"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    def select_children(self, ob):
        ob.select = True
        for child in ob.children:
            self.select_children(child)

    def execute(self, context):
        sel_node = context.active_object
        self.select_children(sel_node)
        bpy.ops.object.delete()
        if len(bpy.data.objects) > 0:
            ob = bpy.data.objects[0]
            while ob.parent is not None:
                ob = ob.parent
            context.scene.objects.active = ob

        return {'FINISHED'}


class SCS_OP_toggle_node(bpy.types.Operator):
    bl_idname = "object.toggle_node"
    bl_label = "Toggle visibility of active object and it's children"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    node = StringProperty()
    hide = BoolProperty()

    def check_additionals(self, context, ob):
        """
        Check if shading switching forbid object to be shown
        """
        hide_dic = context.scene["scs_hide_shading"]
        for key in hide_dic.keys():
            if hide_dic[key] and len(ob.material_slots) > 0:
                if ob.material_slots[0].material.scs_shading.count(key) > 0:
                    ob.hide = True
                    return

    def toggle_children(self, context, ob, hide):
        ob.hide = hide
        if not hide:
            self.check_additionals(context, ob)
        for child in ob.children:
            self.toggle_children(context, child, hide)

    def execute(self, context):
        sel_node = bpy.data.objects[self.node]
        hide = self.hide
        self.toggle_children(context, sel_node, hide)
        #sel_node.select = True
        return {'FINISHED'}


class SCS_OP_scs_toggle_variant(bpy.types.Operator):
    bl_idname = "object.scs_toggle_variant"
    bl_label = "Show/hide variant"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    variant = StringProperty()
    incl_col = BoolProperty(name="Include col", default=True)

    def toggle_node(self, context, ob, hide_p=None):
        #looking for carets which includes variants
        if ("scs_variant_visib" in ob and
                    ob["scs_variant_visib"].count(self.variant) == 1):
            if hide_p is None:
                hide_p = not ob.hide
            bpy.ops.object.toggle_node(node=ob.name, hide=hide_p)
        return hide_p

    def execute(self, context):
        hide_col = None
        for ob in context.active_object.children:
            #store hide_col to tell collisions whatever objects were
            #hiden or shown
            if hide_col is None:
                hide_col = self.toggle_node(context, ob)
            else:
                self.toggle_node(context, ob)
            if context.scene.scs_incl_col:
                if ob.name == "collisions":
                    for ob_col in ob.children:
                        self.toggle_node(context, ob_col, hide_col)

        return {'FINISHED'}

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "incl_col")


class SCS_OP_scs_switch_look(bpy.types.Operator):
    bl_idname = "object.scs_switch_look"
    bl_label = "Switch look"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    look_indx = IntProperty(default=0)


    def execute(self, context):
        curr_l = self.look_indx

        scene = bpy.data.scenes[context.scene.name]
        objs = [ob for ob in scene.objects if
                ob.type == 'MESH' and ob.parent != None and ob.parent.name != "collisions"]
        for ob in objs:
            ob.active_material_index = curr_l
            if len(ob.material_slots) > curr_l:
                for poly in ob.data.polygons:
                    poly.material_index = curr_l
            elif len(ob.material_slots) >= 0:
                msg = "Object '" + ob.name + "' doesn't have assigned enough materials!"
                self.report({'WARNING'}, msg)
                return {'FINISHED'}

        return {'FINISHED'}


class SCS_OP_scs_toggle_by_shading(bpy.types.Operator):
    bl_idname = "object.toggle_by_shading"
    bl_label = "Toggle objects visibility with shadow material"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    shading = StringProperty()

    def execute(self, context):
        shading = self.shading
        #first gather materials with given shading technique
        shadow_mats = [mat for mat in bpy.data.materials if mat.scs_shading.count(shading) > 0]
        """
        shadow_mats = []
        for mat in bpy.data.materials:
            if mat.scs_shading.count(shading) > 0:
                shadow_mats.append(mat)
        """
        #switch property for current shading technique
        hide = not context.scene["scs_hide_shading"][shading]
        bpy.context.scene["scs_hide_shading"][shading] = hide
        for ob in bpy.data.objects:
            if len(ob.material_slots) > 0:
                #check if any of gathered material match object material
                for mat in shadow_mats:
                    if ob.material_slots[0].material == mat:
                        #if parent is hidden then current object shouldn be visible
                        if not hide and ob.parent.hide:
                            continue
                        ob.hide = hide
        return {'FINISHED'}


class SCS_OP_scs_switch_incl_col(bpy.types.Operator):
    bl_idname = "scene.scs_switch_incl_col"
    bl_label = "By toggling variant also toggle collisions"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.scs_incl_col = not context.scene.scs_incl_col
        return {'FINISHED'}


class SCS_OP_scs_reset_variant_toggler(bpy.types.Operator):
    bl_idname = "scene.scs_reset_variant_toggler"
    bl_label = "Resets variant toggling and hides all models"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.toggle_node(node=root_obj().name
                                   , hide=True)
        return {'FINISHED'}


class SCS_OP_scs_add_look(bpy.types.Operator):
    bl_idname = "scene.scs_add_look"
    bl_label = "Adds new look to SCS model"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    name = StringProperty(default="NEW_LOOK", name="Look Name:")

    def execute(self, context):
        #first apply first look to avoid problems with reassign
        bpy.ops.object.scs_switch_look(look_indx=0)
        looks_dic = root_obj()["scs_looks"]
        ret = check_name(self, looks_dic)
        if ret is not None:
            return ret
            #add new look in root obj dictionary
        keys = sorted(looks_dic.keys(), key=lambda x: int(x))
        if len(keys) > 0:
            new_idx = str(int(keys[-1]) + 1)
        else:
            new_idx = str(0)
        looks_dic[new_idx] = self.name.upper()

        #Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
        #add new material slot to all objects and
        #alter material if look_idx == -1 or create new if look_idx > -1
        # objs = [ob for ob in bpy.data.objects if ob.type == 'MESH' and len(ob.material_slots) > 0]
        # mats_lib = {}
        # for ob in objs:
        #     old_mat = ob.material_slots[0].material
        #     if old_mat.scs_look_idx > -1:
        #         if old_mat.name+".001" in mats_lib:
        #             mat = mats_lib[old_mat.name+".001"]
        #         else:
        #             mat = old_mat.copy()
        #             mat.scs_look_idx = len(ob.material_slots)
        #             mats_lib[mat.name] = mat
        #     else:
        #         mat = old_mat
        #     ob.data.materials.append(mat)

        return redraw_properties(context)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)


class SCS_OP_scs_del_look(bpy.types.Operator):
    bl_idname = "scene.scs_del_look"
    bl_label = "Deletes given look of SCS model"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    indx = StringProperty()

    def execute(self, context):
        #first apply first look to avoid problems with reassign
        bpy.ops.object.scs_switch_look(look_indx=0)
        #delete look from root obj dictionary
        looks_dic = root_obj()["scs_looks"]
        i = int(self.indx)
        while i < len(looks_dic) - 1:
            looks_dic[str(i)] = looks_dic[str(i + 1)]
            i += 1
        del (looks_dic[str(i)])

        #Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
        #remove material slot to all objects on given index
        #alter materials greater then given index for -1
        # i = int(self.indx)
        # keys = sorted(looks_dic.keys(), key=lambda x:int(x))
        # objs = [ob for ob in bpy.data.objects if ob.type == 'MESH' and len(ob.material_slots) > 0]
        # mats_lib = {}
        # for ob in objs:
        #     mat = ob.material_slots[i].material
        #     #delete material from scene
        #     if mat not in mats_lib and mat.scs_look_idx > -1:
        #         mats_lib[mat.name] = mat
        #     j=i
        #     while j<len(ob.material_slots)-1:
        #        ob_mat = ob.material_slots[j]
        #        ob_mat1 = ob.material_slots[j+1]
        #        ob_mat.material = ob_mat1.material
        #        ob_mat.material.scs_look_idx -= 1
        #        j+=1
        #     ob.data.materials.pop(len(ob.material_slots)-1,
        #             update_data=True)
        #for mat in mats_lib.values():
        #    bpy.data.materials.remove(mat)
        return {'FINISHED'}


class SCS_OP_scs_rename_look(bpy.types.Operator):
    bl_idname = "scene.scs_rename_look"
    bl_label = "Renames given look of SCS model"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    key = StringProperty(name="Key(Do Not Change!):")
    name = StringProperty(name="New Look Name:")

    def execute(self, context):
        looks_dic = root_obj()["scs_looks"]
        ret = check_name(self, looks_dic)
        if ret is not None:
            return ret
        looks_dic[self.key] = self.name.upper()
        return redraw_properties(context)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="New Look Name:")
        row.prop(self, "name", text="")


class SCS_OP_scs_del_section_visib(bpy.types.Operator):
    bl_idname = "scene.scs_del_section_visib"
    bl_label = "Removes visibility of section in given variant"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    var_key = StringProperty()

    def execute(self, context):
        variants = context.object["scs_variant_visib"]
        context.object["scs_variant_visib"] = variants.replace(self.var_key, '')
        return {'FINISHED'}


class SCS_OP_scs_add_section_visib(bpy.types.Operator):
    bl_idname = "scene.scs_add_section_visib"
    bl_label = "Adds variant visibility in section"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    var_key = StringProperty()

    def execute(self, context):
        var_key = self.var_key
        variants = context.object["scs_variant_visib"]
        i = 0
        #find last variant before var_key value
        while i < len(variants) and ord(variants[i]) < ord(var_key):
            i += 1
        variants = variants[0:i] + var_key + variants[i:]
        context.object["scs_variant_visib"] = variants
        return {'FINISHED'}


class SCS_OP_scs_add_variant(bpy.types.Operator):
    bl_idname = "scene.scs_add_variant"
    bl_label = "Adds new variant to SCS model"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    name = StringProperty(default="NEW_NAME", name="Variant Name:")

    def execute(self, context):
        var_dic = root_obj()["scs_variants"]
        ret = check_name(self, var_dic)
        if ret is not None:
            return ret
        keys = var_dic.keys()
        if len(keys) == 0:
            var_dic['A'] = self.name.upper()
        else:
            var_ch = 'A'
            while var_ch in var_dic:
                var_ch = chr(ord(var_ch) + 1)
            var_dic[var_ch] = self.name.upper()

        return redraw_properties(context)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)


class SCS_OP_scs_delete_variant(bpy.types.Operator):
    bl_idname = "scene.scs_delete_variant"
    bl_label = "Deletes variant of SCS model"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    key = StringProperty()

    def execute(self, context):
        var_dic = root_obj()["scs_variants"]
        del (var_dic[self.key])
        sections = [ob for ob in bpy.data.objects if "scs_variant_visib" in ob]
        for ob in sections:
            if "scs_variant_visib" in ob:
                variants = ob["scs_variant_visib"]
                ob["scs_variant_visib"] = variants.replace(self.key, '')
        return {'FINISHED'}


class SCS_OP_scs_rename_variant(bpy.types.Operator):
    bl_idname = "scene.scs_rename_variant"
    bl_label = "Renames variant of SCS model"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    key = StringProperty(name="Key(Do Not Change!):")
    name = StringProperty(name="New Variant Name:")

    def execute(self, context):
        var_dic = root_obj()["scs_variants"]
        ret = check_name(self, var_dic)
        if ret is not None:
            return ret
        var_dic[self.key] = self.name.upper()
        return redraw_properties(context)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="New Variant Name:")
        row.prop(self, "name", text="")


class SCS_OP_scs_del_mat_option(bpy.types.Operator):
    bl_idname = "material.scs_del_option"
    bl_label = "Delete SCS material option"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    key = StringProperty(name="Name:")

    def execute(self, context):
        del (context.material["scs_mat_options"][self.key])
        return {'FINISHED'}


class SCS_OP_scs_edit_mat_option(bpy.types.Operator):
    bl_idname = "material.scs_edit_option"
    bl_label = "Edit SCS material option"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    key = StringProperty(name="Name:")
    value = StringProperty(name="Value:")

    def execute(self, context):
        from ast import literal_eval

        try:
            literal_eval(self.value)
        except:
            self.report({'INFO'}, "Wrong SCS option value format!")
            return {'FINISHED'}

        context.material["scs_mat_options"][self.key] = self.value
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)


class SCS_OP_scs_add_mat_option(bpy.types.Operator):
    bl_idname = "material.scs_add_option"
    bl_label = "Add new SCS material option"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    key = StringProperty(name="Name:", default="new_name")
    value = StringProperty(name="Value:", default="")

    def execute(self, context):
        if self.key in context.material["scs_mat_options"]:
            self.report({'INFO'}, "Material option with name '" + self.key + "' already added!")
            return {'FINISHED'}
        context.material["scs_mat_options"][self.key] = self.value
        return redraw_properties(context)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=200)


class SCS_OP_scs_edit_mat_shading(bpy.types.Operator):
    bl_idname = "material.scs_edit_shading"
    bl_label = "Edit SCS material shading type"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    value = StringProperty(name="Type:")

    def execute(self, context):
        context.material.scs_shading = self.value
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row = row.split(percentage=0.2)
        row.label(text="Type:")
        row.prop(self, "value", text="")


class SCS_OP_scs_add_custom_prop(bpy.types.Operator):
    bl_idname = "object.scs_add_custom_prop"
    bl_label = "Add new custom property to object"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    key = StringProperty(name="Name:")

    def execute(self, context):
        if self.key == "scs_variant_visib":
            context.object[self.key] = ""
        elif self.key == "scs_coll_type":
            context.object.scs_coll_type = 'box'
        return {'FINISHED'}


class SCS_OP_scs_add_custom_mat_prop(bpy.types.Operator):
    bl_idname = "material.scs_add_custom_prop"
    bl_label = "Add new custom property to material"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    key = StringProperty(name="Name:")

    def execute(self, context):
        #Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
        # if self.key == "scs_look_idx":
        #     context.material.scs_look_idx = -1
        #     context.material["scs_mat_options"] = {}
        # el
        if self.key == "scs_mat_options":
            mat = context.material
            mat["scs_mat_options"] = {}
        if self.key == "scs_tex_base":
            tex = context.texture
            tex["scs_tex_base"] = "texture_base"
            tex.type = 'IMAGE'
        elif self.key == "scs_extra_tex":
            context.texture["scs_extra_tex"] = ""
        return {'FINISHED'}


class SCS_OP_scs_del_custom_mat_prop(bpy.types.Operator):
    bl_idname = "material.scs_del_custom_prop"
    bl_label = "Removes custom property of material"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    key = StringProperty(name="Name:")

    def execute(self, context):
        if self.key == "scs_extra_tex":
            del (context.texture["scs_extra_tex"])
        return {'FINISHED'}


class SCS_OP_scs_reset_objects_transform(bpy.types.Operator):
    bl_idname = "object.scs_reset_transform"
    bl_label = "Applies selected objects transformations"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    #type of resetign: 0 - location rotation and scale, 1 - parent inverse
    type = IntProperty(default=0)

    def execute(self, context):
        objs = [ob for ob in bpy.data.objects if ob.select and ob.type == 'MESH']
        for ob in objs:
            bpy.data.scenes[bpy.context.scene.name].objects.active = ob
            if self.type == 0:
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            elif self.type == 1:
                bpy.ops.object.parent_clear(type='CLEAR_INVERSE')
        return {'FINISHED'}


class SCS_OP_scs_remove_nested_vertices(bpy.types.Operator):
    bl_idname = "object.scs_remove_nested_vertices"
    bl_label = "Removes nested vertices in selected objects"
    bl_description = bl_label
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objs = [ob for ob in bpy.data.objects if ob.select and ob.type == 'MESH']
        for ob in objs:
            bpy.data.scenes[bpy.context.scene.name].objects.active = ob
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='VERT', action='ENABLE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            for p in ob.data.polygons:
                for idx in p.loop_indices:
                    v = ob.data.loops[idx].vertex_index
                    vert = ob.data.vertices[v]
                    vert.select = True

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class SCS_OP_rip_by_uv(bpy.types.Operator):
    bl_idname = "mesh.scs_rip_by_uv"
    bl_label = "Rip Multiples"
    bl_description = "Rip faces which vertices has multiple UV coordinates"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        ob = context.object

        t = time.clock()
        bm = bmesh.new()
        bm.from_mesh(ob.data)

        uv_lay = bm.loops.layers.uv.active

        if uv_lay is not None:
            verts_uvs = {}
            for face in bm.faces:
                for loop in face.loops:
                    uv = loop[uv_lay].uv
                    vert = loop.vert
                    edge = loop.edge
                    if vert.index in verts_uvs:
                        if uv not in verts_uvs[vert.index]:
                            verts_uvs[vert.index].append(uv)
                    else:
                        verts_uvs[vert.index] = []
                        verts_uvs[vert.index].append(uv)

            keys = verts_uvs.keys()
            i = 0
            for index in keys:
                if len(verts_uvs[index]) > 1:
                    edges_to_rip = []
                    for loop in bm.verts[index].link_loops:
                        other_v = loop.edge.other_vert(bm.verts[index])
                        if (other_v is not None and loop.edge not in edges_to_rip and
                                    other_v.index in keys and len(verts_uvs[other_v.index]) > 1):
                            edges_to_rip.append(loop.edge)
                    bmesh.utils.vert_separate(bm.verts[index], edges_to_rip)
                i += 1
                print("\rRipping", i, "/", len(keys), end="")
        else:
            self.report({'INFO'}, "No active UV layer for selected object!")

        bm.to_mesh(ob.data)
        print("\nRipping took:", str(time.clock() - t)[:4] + "s")
        return {'FINISHED'}

    def gen_hash(self, co, uv):
        fact = 100
        hash = ""

        hash += str(int(co.x * fact))
        hash += str(int(co.y * fact))
        hash += str(int(co.z * fact))
        hash += str(int(uv.x * fact))
        hash += str(int(uv.y * fact))

        return hash


class SCS_OP_merge_by_uv(bpy.types.Operator):
    bl_idname = "mesh.scs_merge_by_uv"
    bl_label = "Merge Multiples"
    bl_description = "Merge vertices which shares same coordinate and UV"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        t = time.clock()
        ob = context.object

        bm = bmesh.new()
        bm.from_mesh(ob.data)

        uv_lay = bm.loops.layers.uv.active

        if uv_lay is not None:
            same_verts = {}
            same_verts_co = {}
            i = 0
            for face in bm.faces:
                for loop in face.loops:
                    uv = loop[uv_lay].uv
                    vert = loop.vert

                    res = self.gen_hash(vert.co, uv)
                    co_hash = res[0]
                    hash_key = res[1]
                    if hash_key in same_verts:
                        if vert not in same_verts[hash_key]:
                            same_verts[hash_key].append(vert)
                    else:
                        same_verts[hash_key] = []
                        same_verts[hash_key].append(vert)
                        same_verts_co[hash_key] = co_hash

            i = 0
            values_list = []
            hash_list = []
            keys = same_verts.keys()
            print("")
            for hash_key in keys:
                hash_len = len(hash_list)
                added = False
                for enum in range(0, hash_len):
                    if same_verts_co[hash_key] not in hash_list[enum]:
                        values_list[enum].extend(same_verts[hash_key])
                        hash_list[enum][same_verts_co[hash_key]] = True
                        added = True
                        break
                if not added:
                    values_list.append([])
                    values_list[hash_len].extend(same_verts[hash_key])
                    hash_list.append({})
                    hash_list[hash_len][same_verts_co[hash_key]] = True

                i += 1
                print("\rPreprocess", i, "/", len(keys), end="")

            i = 0
            print("")
            for values in values_list:
                k = 0
                arr_len = len(values)
                while k < arr_len:
                    if values[k] not in bm.verts:
                        del values[k]
                        arr_len -= 1
                    else:
                        k += 1
                bmesh.ops.remove_doubles(bm, verts=values, dist=0.0001)
                i += 1
                print("\rMerging", i, "/", len(values_list), end="")
            bpy.ops.object.scs_remove_nested_vertices()
        else:
            self.report({'INFO'}, "No active UV layer for selected object!")

        bm.to_mesh(ob.data)
        print("\nMerge took:", str(time.clock() - t)[:4] + "s")
        return {'FINISHED'}

    def gen_hash(self, co, uv):
        fact = 1000
        co_hash = ""
        co_hash += str(int(co.x * fact))
        co_hash += str(int(co.y * fact))
        co_hash += str(int(co.z * fact))

        uv_hash = ""
        uv_hash += str(int(uv.x * fact))
        uv_hash += str(int(uv.y * fact))

        return [co_hash, co_hash + uv_hash]


class SCS_OP_reload_mat_library(bpy.types.Operator):
    bl_idname = "scene.scs_reload_mat_library"
    bl_label = "Reload Material Library"
    bl_description = "Reload material library from given blender filepath"
    bl_options = {'REGISTER'}

    path = StringProperty()

    def execute(self, context):
        context_ob = bpy.context.object

        new_mats = None
        try:
            with bpy.data.libraries.load(self.path, link=True) as (data_from, data_to):
                data_to.materials = data_from.materials
                new_mats = data_to.materials
        except OSError:
            self.report({'ERROR'}, "Given path is not a Blend file or the file does not exist!")
            return {'FINISHED'}


        if 'scs_mat_library_object' not in bpy.data.objects:
            mesh = bpy.data.meshes.new('scs_mat_library_mesh')
            mat_ob = bpy.data.objects.new('scs_mat_library_object', object_data=mesh)
        else:
            mat_ob = bpy.data.objects['scs_mat_library_object']

        bpy.context.scene.objects.link(mat_ob)
        bpy.data.scenes[bpy.context.scene.name].objects.active = mat_ob

        objs = [ob for ob in bpy.data.objects]
        for material in bpy.data.materials:
            if material in new_mats:
                if len(mat_ob.material_slots) <= 0:
                    bpy.ops.object.material_slot_add()
                # mat_ob.material_slots[0].material = material
            elif material.library is not None:
                for ob in objs:
                    mat_slots = [mat_slot for mat_slot in ob.material_slots if mat_slot.material is not None and mat_slot.material.name == material.name]
                    for mat_slot in mat_slots:
                        mat_slot.material = None

                material.user_clear()
                material.use_fake_user = False
                bpy.data.materials.remove(material)

        # if len(bpy.data.materials) > 0:
        #     mat_ob.material_slots[0].material = bpy.data.materials[0]
        bpy.context.scene.objects.unlink(mat_ob)

        bpy.data.scenes[bpy.context.scene.name].objects.active = context_ob
        self.report({'INFO'}, "Reload successful! " + str(len(new_mats)) +" materials reloaded.")
        return {'FINISHED'}


class SCS_OP_assign_material_to_slot(bpy.types.Operator):
    bl_idname = "object.scs_assign_material_to_slot"
    bl_label = "Assign material to slot"
    bl_description = "Assign given material to active material slot of selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    new_material = StringProperty()

    def execute(self, context):
        mat = bpy.data.materials[self.new_material]

        objs = [ob for ob in bpy.data.objects if ob.select == True and ob.type == 'MESH']
        err_objs = []
        for ob in objs:
            if len(ob.material_slots) > 0:
                ob.material_slots[ob.active_material_index].material = mat
            else:
                err_objs.append(ob.name)
        if len(err_objs) > 0:
            self.report({'INFO'}, "No change applied to objects: " + str(err_objs) + ". They don't have any material slots!")
        return {'FINISHED'}


class SCS_OP_assign_material_to_all_slots(bpy.types.Operator):
    bl_idname = "object.scs_assign_material_to_all_slots"
    bl_label = "Assign material to all slots"
    bl_description = "Assign given material to all material slots of selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    new_material = StringProperty()

    def execute(self, context):
        mat = bpy.data.materials[self.new_material]

        objs = [ob for ob in bpy.data.objects if ob.select == True and ob.type == 'MESH']
        err_objs = []
        for ob in objs:
            for mat_slot in ob.material_slots:
                mat_slot.material = mat
            if len(ob.material_slots) == 0:
                err_objs.append(ob.name)

        if len(err_objs) > 0:
            self.report({'INFO'}, "No change applied to objects: " + str(err_objs) + ". They don't have any material slots!")
        return {'FINISHED'}

class SCS_OP_create_mat_slot_and_assign_mat(bpy.types.Operator):
    bl_idname = "object.scs_create_mat_slot_and_assign_mat"
    bl_label = "Create slot and assign material"
    bl_description = "Create new material slot and assign given material to that slot (for all selected objects)"
    bl_options = {'REGISTER', 'UNDO'}

    new_material = StringProperty()

    def execute(self, context):
        mat_ob = bpy.data.materials[self.new_material]

        objs = [ob for ob in bpy.data.objects if ob.select == True and ob.type == 'MESH']
        for ob in objs:
            bpy.data.scenes[bpy.context.scene.name].objects.active = ob
            bpy.ops.object.material_slot_add()

            ob.material_slots[ob.active_material_index].material = mat_ob
        return {'FINISHED'}

###############################
#Help functions for operators
###############################
def check_name(self, dic):
    """
    Check if name is valid SCS CRC name
    """
    if self.name in dic.values():
        self.report({'INFO'}, 'Name already used!')
        return {'FINISHED'}
    valid, msg = help_funcs.IsWordValid(self.name)
    if valid > 0:
        self.report({'INFO'}, msg)
        return {'FINISHED'}
    return None


def redraw_properties(context):
    """
    Redraws properties
    """
    for area in context.screen.areas:
        if area.type == 'PROPERTIES':
            for region in area.regions:
                if region.type == 'WINDOW':
                    region.tag_redraw()
                    return {'FINISHED'}
    return {'FINISHED'}


###################################################################
#
# SCS tools panels
#
###################################################################
class SCS_texture_tools(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"
    bl_label = "SCS Texture Tool"

    @classmethod
    def poll(self, context):
        return context.texture is not None

    def draw(self, context):
        layout = self.layout

        if root_obj() is not None:
            tex = context.texture
            if tex != None and "scs_tex_base" not in tex:
                props = layout.operator("material.scs_add_custom_prop", text="Convert to SCS texture")
                props.key = "scs_tex_base"
            else:
                layout.label(text="SCS texture type: ")
                box = layout.box()
                box.prop(context.texture, '["scs_tex_base"]', text="")

                if "scs_extra_tex" not in tex:
                    #show texture settings
                    layout.label(text="SCS texture settings: ")
                    box = layout.box()
                    box.prop(context.texture, "scs_map_type")

                layout.label(text="Rewritten tobj path:")
                box = layout.box()
                if "scs_extra_tex" in tex:
                    row = box.row()
                    row = row.split(percentage=0.8)
                    row.prop(context.texture, '["scs_extra_tex"]', text="")
                    props = row.operator("material.scs_del_custom_prop", text="Del")
                    props.key = "scs_extra_tex"
                else:
                    props = box.operator("material.scs_add_custom_prop", text="Add Custom TOBJ Value")
                    props.key = "scs_extra_tex"
        else:
            row = layout.row()
            row.label(text="Until there is no SCS root object", icon='INFO')
            row = layout.row()
            row.separator()
            row.label(text="no SCS texture can be created!")


class SCS_material_shelf(Panel):
    bl_space_type = 'VIEW_3D'
    bl_category = 'Blender2SCS'
    bl_region_type = 'TOOLS'
    bl_label = "SCS Material Shelf"
    bl_context = "objectmode"

    @classmethod
    def poll(self, context):
        if 'scs_mat_library_object' not in bpy.data.objects:
            mesh = bpy.data.meshes.new('scs_mat_library_mesh')
            bpy.data.objects.new('scs_mat_library_object', object_data=mesh)
        return True

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Selected material:")
        if 'scs_mat_library_object' in bpy.data.objects:
            col.template_ID_preview(bpy.data.objects['scs_mat_library_object'], "active_material", rows=3, cols=8)
            col = col.column(align=True)
            if bpy.data.objects['scs_mat_library_object'].active_material is not None:
                props = col.operator("object.scs_create_mat_slot_and_assign_mat", text="Create Slot & Set Material")
                props.new_material = bpy.data.objects['scs_mat_library_object'].active_material.name
                props = col.operator("object.scs_assign_material_to_slot", text="Set To Current Slot")
                props.new_material = bpy.data.objects['scs_mat_library_object'].active_material.name
                props = col.operator("object.scs_assign_material_to_all_slots", text="Set To All Slots")
                props.new_material = bpy.data.objects['scs_mat_library_object'].active_material.name
        else:
            box = col.box()
            box.label(text="Library not yet loaded!", icon='ERROR')

        col = layout.column(align=True)
        col.label(text="Material Library File:")
        row = col.row(align=True)
        row.prop(bpy.context.scene, "scs_mat_library_path", text="")
        props = row.operator("scene.scs_reload_mat_library", text="Reload")
        props.path = bpy.context.scene.scs_mat_library_path


class SCS_material_tools(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_label = "SCS Material Tool"

    def draw(self, context):
        layout = self.layout

        ob = context.object
        #Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
        # if context.material is not None and "scs_mat_options" not in context.material:
        #     props = layout.operator("material.scs_add_custom_prop", text="Convert to SCS material")
        #     props.key = "scs_mat_options"
        # el
        root_object = root_obj()
        if root_object is not None:
            looks = root_object["scs_looks"]
            keys = sorted(looks.keys(), key=lambda x: int(x))

            actual_mats_len = len([mat_slot for mat_slot in ob.material_slots if mat_slot.material is not None])
            if len(keys) > len(ob.material_slots) or len(keys) > actual_mats_len:
                row = layout.row()
                row.label(text="Export Warning:")
                box = layout.box()
                row = box.row()
                row.label(text="Object must have assigned: " + str(len(keys)) + " materials.",
                          icon="ERROR")
                row = box.row()
                row.label(text="SCS model won't be properly exported!",
                          icon="ERROR")

            if len(ob.material_slots) > 0:
                row = layout.row()
                row.label(text="Active object material slot info:")
                box = layout.box()
                row = box.row()
                if ob.active_material_index < len(looks):
                    row = row.split(percentage=0.7)
                    row.label(text="Material Slot Belongs to:")
                    look_name = looks[str(ob.active_material_index)]
                    row.label(text=look_name)

                    if len(keys) > 1:
                        row = box.row()
                        row.label(text="Quick Look Toggler:")
                        col = box.column(align=True)
                        row = col.row(align=True)
                        i = 0
                        for key in keys:
                            props = row.operator("object.scs_switch_look",
                                                 text=str(looks[key]))
                            props.look_indx = int(key)
                            i += 1
                            if i % 3 == 0:
                                row = col.row(align=True)
                else:
                    row.label(text="Slot index is greater then number of looks,",
                              icon="INFO")
                    row = box.row()
                    row.separator()
                    row.label(text="so this material slot doesn't belong to any look!")
                    row = box.row()
                    row.label(text="This material slot won't effect exported model!",
                              icon="ERROR")

                    #Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
                    #if context.material.scs_look_idx == -1:
                    #    row.label(text="Active object material belongs to:")
                    #row = layout.row()
                    #props = row.operator("material.scs_convert", "Convert To Multi Look")
                    #props.changable_look = True
                    #else:
                    #    row.label(text="Active object material belongs to:")
                    #    look_name = looks[str(ob.active_material_index)]
                    #    row.label(text=look_name)
                    #row = layout.row()
                    #props = row.operator("material.scs_convert", "Convert To Single Look")
                    #props.changable_look = False

                if not ob.active_material is None and "scs_mat_options" in context.material:
                    row = layout.row()
                    row.label(text="Shading Type:")
                    box = layout.box()
                    row = box.row()
                    row = row.split(percentage=0.7)
                    row.label(text=context.material.scs_shading)
                    props = row.operator("material.scs_edit_shading", text="Edit")
                    props.value = context.material.scs_shading
                    scs_options = context.material["scs_mat_options"]
                    keys = sorted(scs_options.keys())
                    row = layout.row()
                    row.label(text="SCS Options:")
                    box = layout.box()
                    for option in keys:
                        row = box.row()
                        row = row.split(percentage=0.6)
                        row.label(text=option + ": " + str(scs_options[option]))
                        props = row.operator("material.scs_edit_option", text="Edit")
                        props.key = option
                        props.value = scs_options[option]
                        props = row.operator("material.scs_del_option", text="Del")
                        props.key = option
                    row = box.row()
                    row.operator("material.scs_add_option", text="Add New Option")
                else:
                    props = layout.operator("material.scs_add_custom_prop", text="Convert to SCS material")
                    props.key = "scs_mat_options"
        else:
            row = layout.row()
            row.label(text="Until there is no SCS root object", icon='INFO')
            row = layout.row()
            row.separator()
            row.label(text="no SCS material can be created!")


class SCS_collision_tool(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "SCS Collision Tool"


    def draw(self, context):
        layout = self.layout
        row = layout.row()
        if "scs_coll_type" in context.object:
            row.prop(context.object, "scs_coll_type",
                     text="Type")
            if context.object.scs_coll_type == "box":
                col = layout.column()
                col.prop(context.object, 'scale', text="Size Of Box")
            elif context.object.scs_coll_type == "cylinder":
                col = layout.column()
                col.prop(context.object, 'scale', text="Size Of Cylinder")
                row = layout.row()
                row.label(text="Note: size X and Y defines radius,", icon='INFO')
                row = layout.row()
                row.separator()
                row.label(text="size Z defines depth")
            col = layout.column()
            col.prop(context.object, 'location', text="Location Of Collision")
        else:
            if ("collisions" in bpy.data.objects and
                        context.object in bpy.data.objects["collisions"].children):
                row.label(text="Collision type doesn't exist!")
                row = layout.row()
                prop = row.operator("object.scs_add_custom_prop", text="Set Default Type")
                prop.key = "scs_coll_type"
            else:
                row.label(text="Select collision object to edit", icon='INFO')
                row = layout.row()
                row.separator()
                row.label(text="collision properties!")


class SCS_objectmode_visi_tools(Panel):
    bl_space_type = 'VIEW_3D'
    bl_category = 'Blender2SCS'
    bl_region_type = 'TOOLS'
    bl_label = "SCS Look Toggler"
    bl_context = "objectmode"

    @classmethod
    def poll(self, context):
        return root_obj() is not None

    def draw(self, context):
        root_object = root_obj()
        if root_object is not None:
            layout = self.layout
            looks = root_object["scs_looks"]
            keys = sorted(looks.keys(), key=lambda x: int(x))
            col = layout.column(align=True)
            row = col.row(align=True)
            for key in keys:
                props = row.operator("object.scs_switch_look",
                                     text=str(looks[key]))
                props.look_indx = int(key)
                row = col.row(align=True)


class SCS_objectmode_tools(Panel):
    bl_space_type = 'VIEW_3D'
    bl_category = 'Blender2SCS'
    bl_region_type = 'TOOLS'
    bl_label = "SCS Object Tools"
    bl_context = "objectmode"

    @classmethod
    def poll(self, context):
        return context.object is not None and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)

        col.label(text="Tools Via UV")

        col.operator("mesh.scs_rip_by_uv")
        col.operator("mesh.scs_merge_by_uv")


class SCS_root_variant_visi_tools(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "SCS Section/Collision Visibility Tools"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        row = layout.row()
        root_ob = root_obj()
        if root_ob is not None:
            var_dic = root_ob["scs_variants"]
            if "scs_variant_visib" in ob:
                if ob.parent.name == "collisions":
                    prefix = "Collision '"
                else:
                    prefix = "Section '"
                row.label(text=prefix + ob.name + "' visible in:")
                box = layout.box()
                if len(var_dic) == 0:
                    row = box.row()
                    row.label(text="No variants! First add variants.")
                    return
                variants = ob["scs_variant_visib"]
                keys = var_dic.keys()
                keys.sort()
                for var_key in keys:
                    row = box.row()
                    row.label(text=var_key + ": " + var_dic[var_key])
                    if var_key in variants:
                        props = row.operator("scene.scs_del_section_visib", "",
                                             icon='CHECKBOX_HLT',
                                             emboss=False)
                        props.var_key = var_key
                    else:
                        props = row.operator("scene.scs_add_section_visib", "",
                                             icon='CHECKBOX_DEHLT',
                                             emboss=False)
                        props.var_key = var_key

            else:
                if ob in root_ob.children:
                    if ob.name != "collisions":
                        prop = row.operator("object.scs_add_custom_prop", text="Set object as SCS section")
                        prop.key = "scs_variant_visib"
                elif ("collisions" in bpy.data.objects and
                              ob in bpy.data.objects["collisions"].children):
                    prop = row.operator("object.scs_add_custom_prop", text="Set as SCS collision object")
                    prop.key = "scs_variant_visib"
                else:
                    row.label(text="Select section/collision to edit", icon='INFO')
                    row = layout.row()
                    row.separator()
                    row.label(text="section visibility in variants!")
        else:
            row = layout.row()
            row.label(text="Select root object to edit", icon='INFO')
            row = layout.row()
            row.separator()
            row.label(text="collision and variants visibility!")


class SCS_root_variant_looks_tools(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "SCS Variant/Look Tools"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        if context.object == root_obj():
            row.label(text="Variant List:")
            box = layout.box()
            var_dic = context.object["scs_variants"]
            keys = sorted(var_dic.keys())
            for var_key in keys:
                row = box.row()
                row = row.split(percentage=0.6)
                row.label(text=var_key + ": " + var_dic[var_key])
                props = row.operator("scene.scs_rename_variant", "Edit")
                props.key = var_key
                props.name = var_dic[var_key]
                props = row.operator("scene.scs_delete_variant", "Del")
                props.key = var_key
            row = box.row()
            row.operator("scene.scs_add_variant", "Add New Variant")

            row = layout.row()
            row.label(text="Look List:")
            box = layout.box()
            look_dic = context.object["scs_looks"]
            keys = sorted(look_dic.keys(), key=lambda x: int(x))
            for look_key in keys:
                row = box.row()
                row = row.split(percentage=0.6)
                row.label(text=look_key + ": " + look_dic[look_key])
                props = row.operator("scene.scs_rename_look", "Edit")
                props.key = look_key
                props.name = look_dic[look_key]
                props = row.operator("scene.scs_del_look", "Del")
                props.indx = look_key
            row = box.row()
            row.operator("scene.scs_add_look", "Add New Look")
        else:
            row.label(text="Select root object to edit", icon='INFO')
            row = layout.row()
            row.separator()
            row.label(text="looks and variants!")


class SCS_models_tools(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "SCS Visibility and Global Tools"

    def check_variant_toggle(self, context):
        layout = self.layout
        ob = context.active_object
        row = layout.row()
        #check if root object is selected which has variants properties
        if context.object == root_obj():
            row = layout.row()
            row.label(text="Show variant:")
            box = layout.box()
            column = box.column(align=True)
            row = column.row(align=True)
            row.operator("scene.scs_reset_variant_toggler", text="Reset Variant Toggler")
            row = column.row(align=True)
            txt = "Include collisions:  "
            if context.scene.scs_incl_col:
                txt += "ON"
                icon = "RADIOBUT_ON"
            else:
                txt += "OFF"
                icon = "RADIOBUT_OFF"

            row.operator("scene.scs_switch_incl_col", text=txt, icon=icon)
            row = box.row()
            i = 0
            variants = ob["scs_variants"]
            keys = variants.keys()
            keys.sort()
            for key in keys:
                props = row.operator("object.scs_toggle_variant",
                                     text=str(variants[key]))
                props.variant = key
                if i % 2 == 1:
                    row = box.row()
                i += 1
            row = layout.row()
            row.label(text="Toggle look:")
            box = layout.box()
            row = box.row()
            i = 0
            looks = ob["scs_looks"]
            keys = looks.keys()
            keys.sort()
            for key in keys:
                props = row.operator("object.scs_switch_look",
                                     text=str(looks[key]))
                props.look_indx = int(key)
                if i % 2 == 1:
                    row = box.row()
                i += 1
        else:
            row.label("Transformation reset:")
            box = layout.box()
            row = box.row()
            props = row.operator("object.scs_reset_transform", text="Apply Location & Rotation")
            props.type = 0
            row = box.row()
            props = row.operator("object.scs_reset_transform", text="Apply Parent Transform")
            props.type = 1

            row = layout.row()
            row.label("Mesh tools:")
            box = layout.box()
            row = box.row()
            props = row.operator("object.scs_remove_nested_vertices", text="Remove Nested Verts")

            row = layout.row()
            row.label(text="Select root object to toggle", icon='INFO')
            row = layout.row()
            row.separator()
            row.label(text="variants and looks!")

    def draw(self, context):
        layout = self.layout

        if not (context.active_object is None):
            column = layout.column(align=True)
            row = column.row(align=True)
            row.operator("scene.clear", text="Clear Scene")

            row = column.row(align=True)
            row.operator("object.delete_node", text="Delete Node")

            column = layout.column(align=True)
            row = column.row(align=True)
            props = row.operator("object.toggle_node", text="Toggle Node Visibility")
            props.hide = not context.active_object.hide
            props.node = context.active_object.name

            if "scs_hide_shading" in context.scene:
                row = column.row(align=True)
                if not context.scene["scs_hide_shading"]["shadow"]:
                    on_off = "ON"
                    icn = 'RADIOBUT_ON'
                else:
                    on_off = "OFF"
                    icn = 'RADIOBUT_OFF'
                props = row.operator("object.toggle_by_shading", text="Shadows Visibility: " + on_off, icon=icn)
                props.shading = "shadow"

                row = column.row(align=True)
                if not context.scene["scs_hide_shading"]["glass"]:
                    on_off = "ON"
                    icn = 'RADIOBUT_ON'
                else:
                    on_off = "OFF"
                    icn = 'RADIOBUT_OFF'
                props = row.operator("object.toggle_by_shading", text="Glass Visibility: " + on_off, icon=icn)
                props.shading = "glass"

        self.check_variant_toggle(context)


###################################################################
#
# Import/Export classes
#
###################################################################
'''
class ImportSCS_PMA(bpy.types.Operator, ImportHelper):
    """Importer for SCS PMA files"""
    bl_idname = "import_anim.scs"
    bl_label = "Import SCS animations"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".pma"
    filter_glob = StringProperty(
        default="*.pma",
        options={'HIDDEN'}
    )

    use_all = BoolProperty(
        name="Import all",
        description="Import all PMA files found in choosen directory",
        default=False
    )

    def execute(self, context):
        t = time.clock()
        help_funcs.PrintDeb("\nImporting PMA -----------------\n")

        imp.load_source('import_pma', f_path + 'import_pma.py')
        import import_pma
        #from . import import_pma

        if root_obj() is None:
            self.report({'ERROR'}, "No SCS root object yet! Make sure that SCS model is properly imported.")
            return {'FINISHED'}

        if not 'anim_armature_object' in bpy.data.objects:
            self.report({'ERROR'},
                        "No SCS armature object yet! Make sure that animated SCS model is properly imported.")
            return {'FINISHED'}

        bpy.data.scenes[bpy.context.scene.name].objects.active = bpy.data.objects['anim_armature_object']
        bpy.ops.object.mode_set(mode='EDIT')
        bones_obj_li = bpy.data.armatures['anim_armature'].edit_bones

        bones_indxes_dic = {}
        for bone in bones_obj_li:
            bones_indxes_dic[bone["scs_b_indx"]] = bone.name

        if self.use_all:
            #import all files in selected directory
            dir = os.path.dirname(self.filepath)
            for file in os.listdir(dir):
                if file.endswith(".pma"):
                    result = import_pma.load(os.path.join(dir, file), bpy.data.objects['anim_armature_object'],
                                             bones_indxes_dic)
                    if result is None:
                        help_funcs.PrintDeb("Error:", file, "has wrong PMA format!")
        else:
            result = import_pma.load(self.filepath, bpy.data.objects['anim_armature_object'], bones_indxes_dic)
            if result is None:
                help_funcs.PrintDeb("Error:", os.path.basename(self.filepath), "has wrong PMA format!")

        help_funcs.PrintDeb("\nImport of animations took:", str(time.clock() - t)[:4] + "s\n")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="PMA selection:")
        row = box.row()
        row.prop(self, "use_all")
'''


class ImportSCS(bpy.types.Operator, ImportHelper):
    """Importer for SCS models"""
    bl_idname = "import_scene.scs"
    bl_label = "Import SCS model"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".pmd"
    filter_glob = StringProperty(
        default="*.pmd",
        options={'HIDDEN'}
    )
    base_path = StringProperty(
        name="Mod base",
        description="Paste path to base of your extracted mod eg. 'C:\\mods\\some_mod'",
        default="C:\\"
    )
    scs_base = StringProperty(
        name="SCS base",
        description="Paste path to SCS base eg. 'C:\\ETS2\\base'",
        default="C:\\Program Files (x86)\\Euro Truck Simulator 2\\base"
    )
    use_pmd = BoolProperty(
        name="Use PMD",
        description="Include PMD file by importing",
        default=True
    )
    use_pmc = BoolProperty(
        name="Use PMC",
        description="Include PMC file by importing",
        default=True
    )
    use_mats = BoolProperty(
        name="Use MAT",
        description="Generate materials from MAT files",
        default=True
    )
    # use_pma = BoolProperty(
    #     name="Use PMA",
    #     description="Include all PMA animation files found in directory",
    #     default=False
    # )

    show_textured = BoolProperty(
        name="Textured mode",
        description="Show 3D view in textured mode on import (might be slower for some PCs)",
        default=True
    )

    optimize = BoolProperty(
        name="Merge duplicates",
        description="Try to optimize and merge model if vertices has same coordinate, normal and all uvs",
        default=True
    )

    basepath_mode = BoolProperty(
        default=False,
        description="Set currently selected directory as basepath")

    scsbase_mode = BoolProperty(
        default=False,
        description="Set currently selected directory as basepath")

    def check(self, context):
        #if in right mode then set current path for basepath
        if self.basepath_mode:
            self.base_path = os.path.dirname(self.filepath)
            self.basepath_mode = False
        elif self.scsbase_mode:
            self.scs_base = os.path.dirname(self.filepath)
            self.scsbase_mode = False
        return True

    def execute(self, context):
        t = time.clock()
        cls()

        from . import import_pmg, import_pmd, import_pmc, import_scs

        self.base_path = self.base_path.rstrip("\\")
        self.base_path = self.base_path.rstrip("/")

        self.scs_base = self.scs_base.rstrip("\\")
        self.scs_base = self.scs_base.rstrip("/")

        if not os.path.exists(self.base_path):
            msg = "Mod base path doesn't exist! Please fix it!"
            self.report({'WARNING'}, msg)
            return {'FINISHED'}

        if not os.path.exists(self.scs_base):
            msg = "SCS base path doesn't exist! Please fix it!"
            self.report({'WARNING'}, msg)
            return {'FINISHED'}

        if self.use_pmd:
            pmd = import_pmd.load(self.filepath)
            if pmd is None:
                self.report({'ERROR'}, "Wrong PMD file version!")
                return {'FINISHED'}
        else:
            pmd = None

        if self.use_pmc:
            pmc_path = self.filepath[:-1] + 'c'
            if os.path.exists(pmc_path):
                pmc = import_pmc.load(pmc_path)
                if pmc is None:
                    self.report({'ERROR'}, "Wrong PMC file version!")
                    return {'FINISHED'}
            else:
                pmc = None
                msg = "PMC file not found! Collisions won't be loaded"
                self.report({'WARNING'}, msg)
        else:
            pmc = None

        pmg = import_pmg.load(self.filepath[:-1] + 'g')
        if pmg is None:
            self.report({'ERROR'}, "Wrong PMG file version!")
            return {'FINISHED'}

        status, ob = import_scs.load(self.filepath, self.base_path, self.scs_base, pmd, pmg, pmc,
                                     self.use_mats, self.show_textured, self.optimize)
        if status == -1:
            print("\nImport error:", ob)
            self.report({'ERROR'}, ob)
            return {'CANCELLED'}

        root_name = ob
        root_obj = bpy.data.objects[root_name]
        bpy.data.scenes[context.scene.name].objects.active = root_obj
        #assign root_obj of scs model for later use
        root_obj["scs_is_root"] = True

        # if self.use_pma and pmg.header.no_bones > 0:
        #     bpy.ops.import_anim.scs(filepath=self.filepath, filter_glob="*.pma", use_all=True)

        #for switching by shading technique
        bpy.context.scene["scs_hide_shading"] = {"shadow": False, "glass": False}

        help_funcs.PrintDeb("\nImport took:", str(time.clock() - t)[:4] + "s\n")
        return {'FINISHED'}


    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Mod base path:")
        row = box.row()
        row.prop(self, "base_path", text="")
        row = box.row()
        row.prop(self, "basepath_mode", toggle=True, text="Set As Mod path")

        box = layout.box()
        row = box.row()
        row.label(text="SCS base path:")
        row = box.row()
        row.prop(self, "scs_base", text="")
        row = box.row()
        row.prop(self, "scsbase_mode", toggle=True, text="Set As SCS Base path")

        box = layout.box()
        row = box.row()
        row.label(text="Import Options:")
        row = box.row()
        row.prop(self, "optimize")
        row = box.row()
        row.prop(self, "use_pmd")
        row = box.row()
        row.prop(self, "use_pmc")
        row = box.row()
        row.prop(self, "use_mats")
        # row = box.row()
        # row.prop(self, "use_pma")
        if not self.use_pmd:
            row.enabled = False

        box = layout.box()
        col = box.column_flow()
        col.label(text="3D View Options:")
        col.prop(self, "show_textured")


class ExportSCS(bpy.types.Operator, ExportHelper):
    """Exporter for SCS models"""
    bl_idname = "export_scene.scs"
    bl_label = "Export SCS model"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".pmd"

    origin_path = StringProperty(
        name="Export origin directory",
        description="Type path to model eg. '/vehicle/truck/daf_xf'",
        default="/model/blender_export"
    )

    copy_textures = BoolProperty(
        name="Copy textures",
        description="By export copy textures to export path",
        default=True
    )

    pmg_version = EnumProperty(
        items=[
            ('1349347090', 'until v1.3.1', 'Save PMG version for game versions until 1.3.1'),
            ('1349347091', 'v1.4.x', 'Save PMG version for game versions 1.4.x')],
        name="PMG version",
        description="Defines which PMG version to use"
    )

    def execute(self, context):
        cls()

        from . import export_pmg, export_pmd, export_pmc, export_scs

        origin_path = self.origin_path.strip("/").strip("\\")
        filepath = self.filepath.rstrip("/").rstrip("\\")
        indx = filepath.rfind('/')
        if indx == -1:
            indx = filepath.rfind('\\')
            if indx == -1:
                self.report({'ERROR'}, "File path is not in right format!")
                return {'FINISHED'}
        filepath = filepath[:indx]

        root_object = root_obj()
        error = None
        if root_object is None:
            error = "There is no SCS root obj make sure that model was imported properly!"
            self.report({"ERROR"}, error)
            return {'FINISHED'}

        #switch to first look that materials can be created in right order
        bpy.ops.object.scs_switch_look(look_indx=0)
        #switch to object mode so reading vertexes is enabled
        if bpy.context.object is not None and bpy.context.object.type == 'MESH' and not bpy.context.object.hide:
            bpy.ops.object.mode_set(mode='OBJECT')

        if not os.path.exists(filepath + '/' + origin_path):
            os.makedirs(filepath + '/' + origin_path)

        if error is None:
            error = export_scs.save(filepath, origin_path, root_object, self.copy_textures, int(self.pmg_version))
            if error is None:
                help_funcs.PrintDeb("Export succesfully finished!")
            else:
                print("\nExport error:", error)
                self.report({'ERROR'}, error)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Export origin directory:")
        row = box.row()
        row.prop(self, "origin_path", text="")
        row = box.row()
        row.label(text="PMG version:")
        row = box.row()
        row.prop(self, "pmg_version", text="")


def menu_func_import(self, context):
    self.layout.operator(ImportSCS.bl_idname, text="SCSoft Model ETS2 (.pmd)")
    # self.layout.operator(ImportSCS_PMA.bl_idname, text="SCSoft Anims ETS2 (.pma)")


def menu_func_export(self, context):
    self.layout.operator(ExportSCS.bl_idname, text="SCSoft Model ETS2 (.pmd)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
    unregister()

bpy.types.Scene.scs_mat_library_path = StringProperty(
    name="Material library path",
    description="Path to blend file which includes only materials",
    default="C:/mat_library.blend",
    subtype="FILE_PATH")

bpy.types.Scene.scs_incl_col = BoolProperty(name="Include collisions",
                                            description="By showing variant show also it's collisions",
                                            default=True)

#Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
# bpy.types.Material.scs_look_idx = IntProperty( name="Material look index",
#         description = "Look index which belongs to this material",
#         default=0
#         )

bpy.types.Material.scs_shading = StringProperty(name="Shading Type",
                                                description="Shading type used in game",
                                                default="eut2.dif.spec")

bpy.types.Object.scs_coll_type = EnumProperty(items=[('box', 'Box', 'Box collision'),
                                                     ('cylinder', 'Cylinder', 'Cylinder collision'),
                                                     ('geometry', 'Geometry', 'Geometry collision')],
                                              name="Collision Type",
                                              description="Defines SCS collision type",
                                              get=get_coll_type,
                                              set=set_coll_type)

bpy.types.Texture.scs_map_type = EnumProperty(items=[
    ('(1, 33685507, 0)', 'Clip-1', 'Faces outside original texture will be clipped to edge pixel (1,33685507,0)'),
    ('(131073, 33685507, 0)', 'Clip-2',
     'Faces outside original texture will be clipped to edge pixel (131073,33685507,0)'),
    ('(1, 33685507, 256)', 'Clip-3', 'Faces outside original texture will be clipped to edge pixel (1,33685507,256)'),
    ('(1, 33685506, 2)', 'Clip-4-Refl', 'Type of mapping used for reflections (1,33685506,2)'),
    ('(1, 33685506, 0)', 'Clip-5', 'Unknown type (1,33685506,0)'),
    ('(1, 3, 0)', 'Repeat-1', 'Repeat texture outside original boundaries (1,3,0)'),
    ('(131073, 3, 0)', 'Repeat-2', 'Repeat texture outside original boundaries (131073,3,0)'),
    ('(1, 131075, 0)', 'Repeat-Y', 'Unknown type (1,131075,0)'),
    ('(0, 3, 0)', 'Repeat-Grounds', 'Repeat texture used for grass, pavements, prefab grounds (0,3,0)'),
    ('(1, 3, 256)', 'Repeat-NM', 'Normal16 (1,3,256)'),
    ('(65537, 3, 256)', 'Repeat-NM', 'Normal16 (65537,3,256)'),
    ('(131073, 2, 0)', 'Repeat-Details', 'Dashboard details (131073, 2, 0)'),
    ('(1, 16842755, 0)', 'Lights-Color', 'New lights color mapping for DAF XF EU6 (1,16842755,0)'),
    ('(1, 33554435, 0)', 'Skybox', 'Used on textures for skybox'),
    ('(1, 33685506, 256)', 'Skybox-Invisible', 'Used for invisible texture of skybox'),
    ('(1, 2, 0)', 'Dashboard-New', 'Used for new dashboards (DAF XF EU6)'),
    ('(0, 0, 0)', 'Default', 'Default type repeat texture (0,0,0)')],
                                              name="Mapping",
                                              description="Defines SCS texture mapping type")