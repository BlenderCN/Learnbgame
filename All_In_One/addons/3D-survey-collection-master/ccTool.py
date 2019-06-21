import bpy
import os
import time
from .functions import *

import nodeitems_utils
from bpy.types import Header, Menu, Panel


class OBJECT_OT_removeccsetup(bpy.types.Operator):
    """Remove cc node for selected objects"""
    bl_idname = "removeccnode.material"
    bl_label = "Remove cycles cc node for selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                remove_cc_setup(mat)

        return {'FINISHED'}
    
class OBJECT_OT_applyccsetup(bpy.types.Operator):
    """Apply color correction images to materials and discard the originals (they will NOT be erased from the HD"""
    bl_idname = "applyccsetup.material"
    bl_label = "Apply color correction images to materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                diffusenode = node_retriever(mat, "diffuse")
                orimagenode = node_retriever(mat, "original")
                newimagenode = node_retriever(mat, "cc_image")
                cc_node = node_retriever(mat, "cc_node")
                print(orimagenode)
                nodes.remove(orimagenode)
                nodes.remove(cc_node)

                newimagenode.name = "original"
                newimagenode.location = (-1100, -50)

                links.new(newimagenode.outputs[0], diffusenode.inputs[0])
                bpy.ops.image.save_dirty()

        return {'FINISHED'}

#-------------------------------------------------------------
class OBJECT_OT_createccsetup(bpy.types.Operator):
    """Create a color correction node for selected objects"""
    bl_idname = "create.ccsetup"
    bl_label = "Create cycles materials for selected object"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.context.scene.render.engine = 'CYCLES'
        active_object_name = context.active_object.name
        cc_nodegroup = create_correction_nodegroup(active_object_name)
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                cc_node_to_mat(mat,cc_nodegroup)
                create_new_tex_set(mat,"cc_image")

                context.window_manager.ccToolViewVar.cc_view = "cc_node"
                #set_texset_obj(context)

        return {'FINISHED'}
#-------------------------------------------------------------
class OBJECT_OT_setccview(bpy.types.Operator):
    """Set view mode"""
    bl_idname = "set.cc_view"
    bl_label = "Set view mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_texset_obj(context)
 
        return {'FINISHED'}

#-------------------------------------------------------------

class OBJECT_OT_bakecyclesdiffuse(bpy.types.Operator):
    """Color correction to new texture set"""
    bl_idname = "bake.cyclesdiffuse"
    bl_label = "Transfer new color correction to a new texture set"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.window_manager.ccToolViewVar.cc_view = "cc_node"
        set_texset_obj(context)
        bake_tex_set("cc")
        context.window_manager.ccToolViewVar.cc_view = "cc_image"
        set_texset_obj(context)

        return {'FINISHED'}

####-----------------------------------------------------------