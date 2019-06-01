import bpy
import numpy as np


def snapCursorToBoudingBox(context, report, *, mode="MIDDLE"):
    vertices = []
    selected_objects = context.selected_objects

    for ob in selected_objects:
        try:
            obj_data = ob.to_mesh(context.scene, True, "PREVIEW")
            vertices.extend([ob.matrix_world * v.co for v in obj_data.vertices])
            bpy.data.meshes.remove(obj_data)
        except RuntimeError:
            report({"WARNING"}, "Unsupported Object: `{}' [{}]".format(ob.name, ob.type))

    if len(vertices) == 0:
        return {"CANCELLED"}

    context.scene.cursor_location = (np.max(vertices, axis=0) + np.min(vertices, axis=0)) / 2

    if mode == "TOP":
        context.scene.cursor_location.z = np.max(vertices, axis=0)[2]
    elif mode == "BOTTOM":
        context.scene.cursor_location.z = np.min(vertices, axis=0)[2]

    return {"FINISHED"}


def addBoundingBoxEmptyCube(context, report):
    vertices = []
    selected_objects = context.selected_objects

    for ob in selected_objects:
        try:
            obj_data = ob.to_mesh(context.scene, True, "PREVIEW")
            vertices.extend([ob.matrix_world * v.co for v in obj_data.vertices])
            bpy.data.meshes.remove(obj_data)
        except RuntimeError:
            report({"WARNING"}, "Unsupported Object: `{}' [{}]".format(ob.name, ob.type))

    if len(vertices) == 0:
        return {"CANCELLED"}

    bbox_empty = bpy.data.objects.new("Bounding Box", None)
    bpy.context.scene.objects.link(bbox_empty)
    bbox_empty.empty_draw_size = 1
    bbox_empty.empty_draw_type = "CUBE"
    bbox_empty.location = (np.max(vertices, axis=0) + np.min(vertices, axis=0)) / 2
    bbox_empty.scale = (np.max(vertices, axis=0) - np.min(vertices, axis=0)) / 2

    return {"FINISHED"}


class AddBoundingBoxEmptyCube(bpy.types.Operator):
    bl_idname = "view3d.add_bounding_box_empty_cube"
    bl_label = "Add Bounding Box Empty Cube of selected item(s)"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return addBoundingBoxEmptyCube(context, self.report)


class SnapCursorToBoundingBoxTop(bpy.types.Operator):
    bl_idname = "view3d.snap_cursor_to_bounding_box_top"
    bl_label = "Snap cursor to the Bounding Box Top of selected item(s)"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return snapCursorToBoudingBox(context, self.report, mode="TOP")


class SnapCursorToBoundingBoxCenter(bpy.types.Operator):
    bl_idname = "view3d.snap_cursor_to_bounding_box_center"
    bl_label = "Snap cursor to the Bounding Box Center of selected item(s)"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return snapCursorToBoudingBox(context, self.report, mode="MIDDLE")


class SnapCursorToBoundingBoxBottom(bpy.types.Operator):
    bl_idname = "view3d.snap_cursor_to_bounding_box_bottom"
    bl_label = "Snap cursor to the Bounding Box Bottom of selected item(s)"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return snapCursorToBoudingBox(context, self.report, mode="BOTTOM")


def snap_menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(SnapCursorToBoundingBoxTop.bl_idname,    text="Cursor to Bounding Box Top")
    layout.operator(SnapCursorToBoundingBoxCenter.bl_idname, text="Cursor to Bounding Box Center")
    layout.operator(SnapCursorToBoundingBoxBottom.bl_idname, text="Cursor to Bounding Box Bottom")


def special_menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(AddBoundingBoxEmptyCube.bl_idname, text="Add Bounding Box Empty Cube of selected item(s)")
