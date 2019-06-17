__reload_order_index__ = 0

import bpy
from bpy.app.handlers import persistent
from .utils.copy import copy_modifiers, copy_constraints
from .utils.camera import in_frustum


global render_event
render_event = False


def update_lod_mesh(obj, group, index):
    index = max(-1, min(len(group.lod) - 1, index))
    # The LOD object to copy the mesh from.
    lod = bpy.data.objects.get(group.lod[index].object, None)

    if lod is not None:
        obj.data = lod.data


def update_lod_modifiers(obj, group, index):
    index = max(-1, min(len(group.lod) - 1, index))
    # The LOD object to copy the modifiers from.
    lod = bpy.data.objects.get(group.lod[index].object, None)

    if lod is not None:
        copy_modifiers(lod, obj)


def update_lod_constraints(obj, group, index):
    index = max(-1, min(len(group.lod) - 1, index))
    # The LOD object to copy the constraints from.
    lod = bpy.data.objects.get(group.lod[index].object, None)

    if lod is not None:
        copy_constraints(lod, obj)


def update_objects_lod(scene, event):
    for obj in scene.objects:
        group = bpy.data.groups.get(obj.lod.group, None)
        if obj.lod.use_active_camera:
            offset = scene.camera
        else:
            offset = scene.objects.get(obj.lod.offset, None)

        # If group and offset are set.
        if group is not None and offset is not None and len(group.lod) > 0:
            # region Update using distance.
            if (event == 'viewport' and obj.lod.viewport_active) or (event == 'render' and obj.lod.render_active):
                # If frustum is enabled, update using frustum level.
                if obj.lod.use_frustum:
                    camera = scene.camera
                    if camera is not None:
                        if not in_frustum(camera, obj, radius=obj.lod.frustum_radius * max(obj.scale)):
                            index = obj.lod.frustum_level - 1
                            if obj.lod.use_mesh:
                                update_lod_mesh(obj, group, index)
                            if obj.lod.use_modifiers:
                                update_lod_modifiers(obj, group, index)
                            if obj.lod.use_constraints:
                                update_lod_constraints(obj, group, index)

                            continue

                # Calculate distance between the objects.
                distance = (obj.location - offset.location).length
                # If distance is larger than highest distance, use highest level.
                if distance >= group.lod[-1].distance:
                    if obj.lod.use_mesh:
                        update_lod_mesh(obj, group, -1)
                    if obj.lod.use_modifiers:
                        update_lod_modifiers(obj, group, -1)
                    if obj.lod.use_constraints:
                        update_lod_constraints(obj, group, -1)
                else:
                    for index, level in enumerate(group.lod):
                        if distance <= level.distance:
                            if obj.lod.use_mesh:
                                update_lod_mesh(obj, group, index)
                            if obj.lod.use_modifiers:
                                update_lod_modifiers(obj, group, index)
                            if obj.lod.use_constraints:
                                update_lod_constraints(obj, group, index)
                            break
            # endregion
            # region Update using constant viewport settings.
            elif event == 'viewport' and not obj.lod.viewport_active:
                if obj.lod.use_mesh:
                    update_lod_mesh(obj, group, obj.lod.viewport_level - 1)
                if obj.lod.use_modifiers:
                    update_lod_modifiers(obj, group, obj.lod.viewport_level - 1)
                if obj.lod.use_constraints:
                    update_lod_constraints(obj, group, obj.lod.viewport_level - 1)
            # endregion
            # region Update using constant render settings.
            elif event == 'render' and not obj.lod.render_active:
                if obj.lod.use_mesh:
                    update_lod_mesh(obj, group, obj.lod.render_level - 1)
                if obj.lod.use_modifiers:
                    update_lod_modifiers(obj, group, obj.lod.render_level - 1)
                if obj.lod.use_constraints:
                    update_lod_constraints(obj, group, obj.lod.render_level - 1)
            # endregion


@persistent
def handler_frame_change(scene):
    global render_event
    if not render_event:
        update_objects_lod(scene, event='viewport')


@persistent
def handler_render(scene):
    global render_event
    render_event = True
    update_objects_lod(scene, event='render')


@persistent
def handler_render_post(scene):
    global render_event
    render_event = False


def register():
    bpy.app.handlers.frame_change_post.append(handler_frame_change)
    bpy.app.handlers.render_pre.append(handler_render)
    bpy.app.handlers.render_post.append(handler_render_post)


def unregister():
    bpy.app.handlers.frame_change_post.remove(handler_frame_change)
    bpy.app.handlers.render_pre.remove(handler_render)
    bpy.app.handlers.render_post.remove(handler_render_post)
