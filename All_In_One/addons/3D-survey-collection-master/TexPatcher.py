import bpy
import os
from .functions import *
        
class OBJECT_OT_textransfer(bpy.types.Operator):
    """Select two meshes in order to transfer a clone layer"""
    bl_idname = "texture.transfer"
    bl_label = "Texture transfer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_ob = bpy.context.selected_objects
        active_ob = bpy.context.scene.objects.active
        for matslot in active_ob.material_slots:
            mat = matslot.material
            nodes = mat.node_tree.nodes
            mat.use_nodes = True
            source_paint_node = node_retriever(mat, "source_paint_node")
            if source_paint_node:
                nodes.remove(source_paint_node)
#                print("Removed old sp node")
            create_new_tex_set(mat, "source_paint_node")
        bake_tex_set("source")

#        aggiungere source paint slots
#        abiliater painting
#        set-up paint
#        PAINT
#        SAVE paint
        pass
        return {'FINISHED'}
    
class OBJECT_OT_applyoritexset(bpy.types.Operator):
    """Use original textures in mats"""
    bl_idname = "applyoritexset.material"
    bl_label = "Use original textures in mats"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'

        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                set_texset(mat, "original")
                
        return {'FINISHED'}
    
class OBJECT_OT_applysptexset(bpy.types.Operator):
    """Use sp textures in mats"""
    bl_idname = "applysptexset.material"
    bl_label = "Use sp textures in mats"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'

        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                set_texset(mat, "source_paint_node")
                
        return {'FINISHED'}

    
class OBJECT_OT_paintsetup(bpy.types.Operator):
    """Set up paint from source"""
    bl_idname = "paint.setup"
    bl_label = "Set up paint from source"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.render.engine = 'CYCLES'
        setupclonepaint()
        return {'FINISHED'}

class OBJECT_OT_exitsetup(bpy.types.Operator):
    """Exit paint from source"""
    bl_idname = "exit.setup"
    bl_label = "Exit paint from source"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.tool_settings.image_paint.use_clone_layer = False
        bpy.ops.object.mode_set ( mode = 'OBJECT' ) 
                
        return {'FINISHED'}

class OBJECT_OT_removepaintsetup(bpy.types.Operator):
    """Remove paint source"""
    bl_idname = "remove.sp"
    bl_label = "Remove paint source"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context = bpy.context
        context.scene.render.engine = 'CYCLES'

        for obj in context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                remove_node(mat, "source_paint_node")
                
        return {'FINISHED'}


