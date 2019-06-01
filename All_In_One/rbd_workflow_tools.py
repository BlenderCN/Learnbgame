# -*- coding: utf-8 -*-
bl_info = {
    "name": "Suite of Tools to abet RBD Workflow",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "Operator Search Menu (Tools start with RBD)",
    "description": "Suite of Tools to abet RBD Workflow",
    "warning": "",
    "category": "Learnbgame",
}   

"""Suite of Tools to abet RBD Workflow"""

import bpy
from bpy.props import IntProperty, BoolProperty, EnumProperty

def _update_attr(self, context, name):
    scene = context.scene
    point_cache = scene.rigidbody_world.point_cache
    value = getattr(self, name)
    for bobject in (scene, point_cache):
        setattr(bobject, name, value)
    bpy.ops.time.view_all()

def _update_frame_start(self, context):
    _update_attr(self, context, 'frame_start')

def _update_frame_end(self, context):
    _update_attr(self, context, 'frame_end')

class RBDChangeFrangeOperator(bpy.types.Operator):
    """Modify the frame range for the RBD simulation"""
    bl_idname = "object.rbd_change_frange"
    bl_label = "RBD Change Frange"

    frame_start = IntProperty(name="Start Frame", update=_update_frame_start,
                              default=1,
                              min=1,
                              soft_min=1,
                              step=1
                              )
    frame_end = IntProperty(name="End Frame", update=_update_frame_end,
                              default=1,
                              min=1,
                              soft_min=1,
                              step=1
                              )

    @classmethod
    def poll(cls, context):
        rbdworld = context.scene.rigidbody_world
        predicates = (context.area.type == 'TIMELINE',
                      rbdworld,
                      not rbdworld.point_cache.is_baking,
                      not rbdworld.point_cache.is_baked)
        return all(predicates)

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        self.frame_start = scene.frame_start
        self.frame_end = scene.frame_end
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        return {'FINISHED'}

class RBDView3DPoll():
    @classmethod
    def poll(cls, context):
        predicates = (context.area.type == 'VIEW_3D',)
        return all(predicates)

class RBDSelectMacro(bpy.types.Macro, RBDView3DPoll):
    """TODO"""
    bl_idname = "object.rbd_select"
    bl_label = "RBD Select"
    bl_options = {'REGISTER', 'UNDO'}


class RBDSelectAndHideMacro(bpy.types.Macro, RBDView3DPoll):
    """TODO"""
    bl_idname = "object.rbd_select_hide"
    bl_label = "RBD Select and Hide"
    bl_options = {'REGISTER', 'UNDO'}

class View3DQuadViewCustom(bpy.types.Operator):
    """Toggle the quad view and also set lock and sync properties"""
    bl_idname = "view3d.quad_view"
    bl_label = "V3D Quad View"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        predicates = (context.area.spaces.active.type == 'VIEW_3D',)
        return all(predicates)

    def execute(self, context):
        space_data = context.area.spaces.active
        quad_view = space_data.region_quadview
        bpy.ops.screen.region_quadview()
        if quad_view is None:
            for attr in ('lock_rotation', 'show_sync_view'):
                setattr(space_data.region_quadview, attr, True)
        return {'FINISHED'}

class DisplayAxis(bpy.types.Operator):
    """Turn on/off display"""
    bl_idname = "object.display_axis"
    bl_label = "DSP Axis"
    bl_description = bpy.types.Object.bl_rna.properties['show_axis'].description
    bl_options = {'REGISTER', 'UNDO'}

    show_axis = EnumProperty(items=(('TOGGLE', 'Toggle', 'Toggle the axis display'),
                                    ('ENABLE', 'Enable', 'Display the axis'),
                                    ('DISABLE', 'Disable', 'Hide the acis')),
                            name="Axis",
                            description=bl_description,
                            default='TOGGLE')

    @classmethod
    def poll(cls, context):
        predicates = (
            context.selected_editable_objects,
            len(context.selected_editable_objects),
        )
        return all(predicates)

    def draw(self, context):
        layout = self.layout
        layout.operator_menu_enum(self.bl_idname, 'show_axis')

    def execute(self, context):
        kwargs = {
                'data_path_iter': 'selected_editable_objects',
                'data_path_item': 'show_axis',
                'type': self.show_axis
            }
        
        return bpy.ops.wm.context_collection_boolean_set(**kwargs)

def _cameralist(self, context):
    data = context.blend_data
    scene = context.scene
    group = data.groups.get('PlayblastCameras', None)
    if not group:
        return []
    else:
        cameras = group.objects
        camera_list = [(camera.name, camera.name, "{0} {1}".format(scene.name, camera.name)) for camera in cameras]
        return camera_list

class PlayblastFromCamerasMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_playblast_from_cameras"
    bl_label = "Playblast from"

    def draw(self, context):
        layout = self.layout
        cameras = _cameralist(self, context)
        if not cameras:
            layout.label("Group PlayblastCameras is missing or empty")
        else:
            layout.operator_context = 'EXEC_DEFAULT'
            #layout.operator_menu_enum('render.playblast_from_camera', 'camera')
            #layout.operator_enum('render.playblast_from_camera', 'camera')
            for camera in sorted(cameras, key=lambda cam: cam[0]):
                row = layout.row()
                op = row.operator('render.playblast_from_camera', text=camera[0])
                op.camera = camera[0]
                row.enabled = not (camera[0] == context.scene.camera.name and 
                                   context.region_data.view_perspective in ('CAMERA',))

class PlayblastMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_playblast"
    bl_label = "Playblast"

    def draw(self, context):
        layout = self.layout
        column1 = layout.column()
        column1.menu('VIEW3D_MT_playblast_from_cameras', text="Set")
        column2 = layout.column()
        column2.operator('render.play_rendered_anim', text='View')
        cameras = _cameralist(self, context)
        if not cameras:
            column1.enabled = False
            column2.enabled = False

class PlayblastFromCameras(bpy.types.Operator):
    """Playblast from chosen camera"""
    bl_idname = "render.playblast_from_camera"
    bl_label = "REN Playblast from Camera"
    bl_description = "Playblast from the chosen camera in the scene"
    bl_options = {'REGISTER', 'UNDO'}

    camera = EnumProperty(items=_cameralist, name="Choose Camera")

    @classmethod
    def poll(cls, context):
        data = context.blend_data
        predicates = (
            context.area.spaces.active.type == 'VIEW_3D',
            data.filepath,
            data.groups.get('PlayblastCameras') is not None,
        )
        return all(predicates)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_popup(self, event)

    def execute(self, context):
        kwargs = {
                'data_path_iter': 'selected_editable_objects',
                'data_path_item': 'select',
                'type': 'DISABLE'
        }
        bpy.ops.wm.context_collection_boolean_set(**kwargs)

        #kwargs['data_path_iter'] = 'blend_data.groups["PlayblastCameras"].objects'
        #kwargs['data_path_item'] = 'hide'
        #kwargs['type'] = 'ENABLE'
        #bpy.ops.wm.context_collection_boolean_set(**kwargs)

        playblast_cameras = context.blend_data.groups.get('PlayblastCameras').objects

        playblast_cameras.foreach_set('hide', [True]*len(playblast_cameras))

        scene = context.scene

        scene.camera = playblast_cameras.get(self.camera)
        scene.objects.active = context.scene.camera
        scene.camera.select = True
        scene.camera.hide = False

        if 'playblast_settings' in scene.camera:
            code = scene.camera.get('playblast_settings')
            custom_preview_settings = eval(code)
            scene.use_preview_range = True
            for key, value in custom_preview_settings.items():
                setattr(scene, key, value)
        else:
            scene.use_preview_range = False
            pairs = zip(('frame_preview_start', 'frame_preview_end'), 
                        ('frame_start', 'frame_end')
                        )
            for preview, normal in pairs:
                setattr(scene, preview, getattr(scene, normal))

        render = context.scene.render
        render.resolution_percentage = 100
        render.filepath = '//' + bpy.path.display_name(bpy.data.filepath) + '_' + self.camera + '.'
        render.image_settings.file_format = 'H264'
        render.ffmpeg.format = 'MPEG4'
        render.display_mode = 'NONE'
        render.use_lock_interface = True

        space_data = context.space_data
        space_data.show_relationship_lines = False
        
        bpy.ops.view3d.viewnumpad(type='CAMERA')
        if space_data.region_3d.view_perspective in ('PERSP', 'ORTHO'):
            bpy.ops.view3d.viewnumpad(type='CAMERA')

        return {'FINISHED'}

#class DisplayShadowProperties(bpy.types.Operator)

def register():
    bpy.utils.register_class(RBDChangeFrangeOperator)
    bpy.utils.register_class(View3DQuadViewCustom)
    bpy.utils.register_class(DisplayAxis)
    bpy.utils.register_class(PlayblastFromCameras)
    bpy.utils.register_class(PlayblastFromCamerasMenu)
    bpy.utils.register_class(PlayblastMenu)
    
    bpy.utils.register_class(RBDSelectMacro)
    op = RBDSelectMacro.define("OBJECT_OT_select_linked")
    op.properties.type = 'OBDATA'

    bpy.utils.register_class(RBDSelectAndHideMacro)
    op = RBDSelectAndHideMacro.define("OBJECT_OT_select_linked")
    op.properties.type = 'OBDATA'
    op = RBDSelectAndHideMacro.define("OBJECT_OT_hide_view_set")
    op.properties.unselected = False


def unregister():
    bpy.utils.unregister_class(RBDChangeFrangeOperator)
    bpy.utils.unregister_class(View3DQuadViewCustom)
    bpy.utils.unregister_class(DisplayAxis)
    bpy.utils.unregister_class(PlayblastMenu)
    bpy.utils.unregister_class(PlayblastFromCamerasMenu)
    bpy.utils.unregister_class(PlayblastFromCameras)
    bpy.utils.unregister_class(RBDSelectAndHideMacro)
    bpy.utils.unregister_class(RBDSelectMacro)

if __name__ == '__main__':
    register()