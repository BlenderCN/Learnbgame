bl_info = {
    "name": "Heavypoly Operators",
    "description": "Operators that make for smooth blending",
    "author": "Vaughan Ling",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }

import bpy
import bmesh
from bpy.types import Menu
from bpy.types import Operator
from bpy.props import BoolProperty

class HP_OT_loopcut(bpy.types.Operator):
    bl_idname = "mesh.hp_loopcut"         # unique identifier for buttons and menu items to reference.
    bl_label = "Loopcut with tablet modals"       # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.


    def modal(self, context, event):
        if event.type == 'MOUSEMOVE' and event.value == 'PRESS':
            print('Mousemove...')
            bpy.ops.mesh.loopcut_slide('INVOKE_DEFAULT')
            return {'RUNNING_MODAL'}
        if event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            return {'CANCELLED'}
        elif event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
            bpy.context.scene.tool_settings.mesh_select_mode = (False, True, False)
            print('Release...')
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}
    def invoke(self, context, event):

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class HP_OT_smart_snap_cursor(bpy.types.Operator):
    bl_idname = "view3d.smart_snap_cursor"        # unique identifier for buttons and menu items to reference.
    bl_label = ""         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    def invoke(self, context, event):
        try:
            if context.active_object.mode == 'EDIT':
                if  context.object.data.total_vert_sel > 0:
                    bpy.ops.view3d.snap_cursor_to_selected()
                else:
                    bpy.ops.view3d.snap_cursor_to_center()
            elif len(bpy.context.selected_objects) > 0:
                bpy.ops.view3d.snap_cursor_to_selected()
            else:
                bpy.ops.view3d.snap_cursor_to_center()
        except:
            bpy.ops.view3d.snap_cursor_to_center()
            #bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        return {'FINISHED'}

class HP_OT_smart_snap_origin(bpy.types.Operator):
    bl_idname = "view3d.smart_snap_origin"        # unique identifier for buttons and menu items to reference.
    bl_label = ""         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    def invoke(self, context, event):
        try:
            if context.active_object.mode == 'EDIT':
                if context.object.data.total_vert_sel > 0:
                    bpy.ops.view3d.snap_cursor_to_selected()
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                    bpy.ops.object.mode_set(mode='EDIT')
                else:
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            elif len(bpy.context.selected_objects) > 0:
                bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')
            else:
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        except:
            return {'FINISHED'}
        return {'FINISHED'}

class PushAndSlide(bpy.types.Operator):
    bl_idname = "mesh.push_and_slide"        # unique identifier for buttons and menu items to reference.
    bl_label = "Push And Slide"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
            bpy.ops.transform.vert_slide('INVOKE_DEFAULT', mirror=False, correct_uv=True)
        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT', use_even_offset=True, mirror=False)
        else:
            bpy.ops.transform.edge_slide('INVOKE_DEFAULT', mirror=False, correct_uv=True)
        return {'FINISHED'}


class HP_OT_extrude(Operator):
    """Context Sensitive Extrude"""
    bl_label = "Context Sensitive Extrude"
    bl_idname = "mesh.hp_extrude"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None and obj.mode == 'EDIT')

    
    def modal(self, context, event):
       
        if event.type == 'MOUSEMOVE':
            bpy.ops.mesh.select_linked()
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.vertex_group_select()
            bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            print('rightmouse')
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}
        
    def invoke(self, context, event):
        if bpy.context.object.type == 'CURVE':
            bpy.ops.curve.extrude()
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_orientation='GLOBAL')
            print('EXTRUDING CURVES')
            return {'FINISHED'}
        mesh = context.object.data
        selface = mesh.total_face_sel
        seledge = mesh.total_edge_sel
        selvert = mesh.total_vert_sel
        # Nothing Selected
        if selvert == 0:
            bpy.ops.mesh.select_mode(type = 'VERT')
            bpy.ops.mesh.dupli_extrude_cursor('INVOKE_DEFAULT')
            print('PLACING VERT')
            return {'FINISHED'}
        if selvert > 0 and seledge == 0:
            print('EXTRUDING VERTS')
            bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT')
            return {'FINISHED'}
        if seledge > 0 and selface == 0:
            print('EXTRUDING EDGES')
            bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT')
            return {'FINISHED'}
            
        
        # Save Selection
        bpy.ops.object.face_map_add()
        bpy.ops.object.face_map_assign()
        bpy.ops.mesh.select_linked(delimit={'SEAM'})

        print('SAVING SELECTION')
        linkedface = mesh.total_face_sel
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.face_map_select()
        bpy.ops.object.face_map_remove()

        bpy.ops.mesh.extrude_region_move('EXEC_DEFAULT')
        print('EXTRUDING FACES')

        if linkedface != selface:
            bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT')
            return {'FINISHED'}

        context.window_manager.modal_handler_add(self)
        
        if selface > 0:
            bpy.ops.object.vertex_group_add()
            bpy.ops.object.vertex_group_assign()
            bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT')
            print('FIXING NORMALS')
            return {'RUNNING_MODAL'}                    
        return {'RUNNING_MODAL'}

class SmartBevel(bpy.types.Operator):
    bl_idname = "mesh.smart_bevel"        # unique identifier for buttons and menu items to reference.
    bl_label = "Smart Bevel"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
            bpy.ops.mesh.bevel('INVOKE_DEFAULT',vertex_only=True)
            return {'FINISHED'}
        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            bpy.ops.mesh.select_mode(type = 'EDGE')
            print('edge mode...')
            bpy.ops.mesh.region_to_loop('INVOKE_DEFAULT')
            print('selecting border...')            
        
        bpy.ops.mesh.bevel('INVOKE_DEFAULT',vertex_only=False)
        return {'FINISHED'}



class SeparateAndSelect(bpy.types.Operator):
    bl_idname = "mesh.separate_and_select"        # unique identifier for buttons and menu items to reference.
    bl_label = "Separate and Select"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    def execute(self, context):

        base = bpy.context.active_object
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.editmode_toggle()
        base.select_set(state=False)
        selected = bpy.context.selected_objects
        for sel in selected:
            bpy.context.view_layer.objects.active = sel
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        return {'FINISHED'}

class SmartShadeSmooth(bpy.types.Operator):
    bl_idname = "view3d.smart_shade_smooth_toggle"        # unique identifier for buttons and menu items to reference.
    bl_label = "Smart Shade Smooth"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.shade_smooth()
            bpy.context.object.data.use_auto_smooth = True
            bpy.context.object.data.auto_smooth_angle = 0.436332
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        else:
            bpy.ops.object.shade_smooth()
            bpy.context.object.data.use_auto_smooth = True
            bpy.context.object.data.auto_smooth_angle = 0.436332
        return {'FINISHED'}

class toggle_render_material(bpy.types.Operator):
    bl_idname = "view3d.toggle_render_material"        # unique identifier for buttons and menu items to reference.
    bl_label = ""         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        if bpy.context.space_data.viewport_shade != 'MATERIAL':
            bpy.context.space_data.viewport_shade = 'MATERIAL'
        elif bpy.context.space_data.viewport_shade == 'MATERIAL':
            bpy.context.space_data.viewport_shade = 'RENDERED'
        return {'FINISHED'}


class Smart_Delete(bpy.types.Operator):
    bl_idname = "view3d.smart_delete"        # unique identifier for buttons and menu items to reference.
    bl_label = ""         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        obj = context.object
        objType = getattr(obj, 'type', '')
        act = bpy.context.active_object
        try:
            if not act:
                for o in bpy.context.selected_objects:
                    bpy.context.view_layer.objects.active = o
                    act = bpy.context.active_object
            actname = act.name
            if context.active_object.mode == 'OBJECT':
                if 'Bool_Cutter' in act.name and context.active_object.mode == 'OBJECT':
                    bpy.ops.object.delete(use_global=False)
#                    bpy.ops.object.select_all(action='SELECT')
#                    for o in bpy.context.selected_objects:
                    for buttsniffers in bpy.context.view_layer.objects:
                        bpy.context.view_layer.objects.active = buttsniffers
                        bpy.ops.object.modifier_remove(modifier=actname)
                else:
                    bpy.ops.object.delete(use_global=False)
                #bpy.ops.object.select_all(action='DESELECT')
            elif objType == 'CURVE':
                if context.active_object.mode != 'OBJECT':
                    bpy.ops.curve.delete(type='VERT')
            elif objType == 'GPENCIL':
                if context.active_object.mode != 'OBJECT':
                    bpy.ops.gpencil.delete(type='POINTS')

            elif objType == 'META':
                if context.active_object.mode != 'OBJECT':
                    bpy.ops.mball.delete_metaelems()
            elif objType == 'MESH':
                if context.active_object.mode != 'OBJECT':
                    if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
                        bpy.ops.mesh.delete(type='FACE')
                    else:
                        bpy.ops.mesh.delete(type='VERT')
        except:
            pass
        return {'FINISHED'}

class Subdivision_Toggle(bpy.types.Operator):
    bl_idname = "view3d.subdivision_toggle"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):

        for o in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = o
            if 0 < len([m for m in bpy.context.object.modifiers if m.type == "SUBSURF"]):
                if bpy.context.object.modifiers["Subsurf_Base"].show_viewport == False:
                    bpy.context.object.modifiers["Subsurf_Base"].show_render = True
                    bpy.context.object.modifiers["Subsurf_Base"].show_viewport = True
                else:
                    bpy.context.object.modifiers["Subsurf_Base"].show_render = False
                    bpy.context.object.modifiers["Subsurf_Base"].show_viewport = False

            else:
                o.modifiers.new("Subsurf_Base", "SUBSURF")
                bpy.context.object.modifiers["Subsurf_Base"].name = "Subsurf_Base"
                bpy.context.object.modifiers["Subsurf_Base"].render_levels = 3
                bpy.context.object.modifiers["Subsurf_Base"].levels = 3
                bpy.context.object.modifiers["Subsurf_Base"].show_in_editmode = True
                bpy.context.object.modifiers["Subsurf_Base"].show_on_cage = True
                bpy.context.object.modifiers["Subsurf_Base"].subdivision_type = 'CATMULL_CLARK'

        return {'FINISHED'}

class SaveWithoutPrompt(bpy.types.Operator):
    bl_idname = "wm.save_without_prompt"
    bl_label = "Save without prompt"

    def execute(self, context):
        bpy.ops.wm.save_mainfile()
        return {'FINISHED'}
class RevertWithoutPrompt(bpy.types.Operator):
    bl_idname = "wm.revert_without_prompt"
    bl_label = "Revert without prompt"

    def execute(self, context):
        bpy.ops.wm.revert_mainfile()
        return {'FINISHED'}
class DeleteWithoutPrompt(bpy.types.Operator):
    bl_idname = "wm.delete_without_prompt"
    bl_label = "Delete without prompt"

    def execute(self, context):
        bpy.ops.object.delete()
        return {'FINISHED'}

classes = (
    SaveWithoutPrompt,
    RevertWithoutPrompt,
    DeleteWithoutPrompt,
    Subdivision_Toggle,
    Smart_Delete,
    SmartShadeSmooth,
    SeparateAndSelect,
    PushAndSlide,
    SmartBevel,
    HP_OT_smart_snap_cursor,
    HP_OT_smart_snap_origin,
    HP_OT_extrude,
    HP_OT_loopcut
)
register, unregister = bpy.utils.register_classes_factory(classes)  
    
if __name__ == "__main__":
    register() 