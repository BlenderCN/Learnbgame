import bpy
import bmesh
import bpy.utils.previews
from ... preferences import get_preferences

# _____________________________________________________________clean mesh (OBJECT MODE)________________________


class HOPS_OT_CleanMeshOperator(bpy.types.Operator):
    bl_idname = "view3d.clean_mesh"
    bl_label = "Limited Dissolve"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Cleans mesh of Coplanar / Colinear / Degenerate / Duplicate FACES, EDGES and VERTS
Advanced selection options in F6"""

    text = "Limited Dissolve Removed"
    op_tag = "Limited Dissolve / Remove Doubles"
    op_detail = "Angled Doubles Dissolved"

    @classmethod
    def poll(cls, context):
        return context.active_object.mode in {'OBJECT', 'EDIT'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        row = box.row()
        row.prop(get_preferences(), 'meshclean_mode', expand=True)
        box.prop(get_preferences(), 'meshclean_dissolve_angle', text="Limited Disolve Angle")
        box.prop(get_preferences(), 'meshclean_remove_threshold', text="Remove Threshold")
        box.prop(get_preferences(), 'meshclean_unhide_behavior', text="Unhide Mesh")
        box.prop(get_preferences(), 'meshclean_delete_interior', text="Delete Interior Faces")

    def execute(self, context):

        self.object_mode = context.active_object.mode

        if get_preferences().meshclean_mode == 'SELECTED':
            if self.object_mode == 'OBJECT':

                original_active_object = context.view_layer.objects.active

                for object in context.selected_objects:
                    if object.type == 'MESH':

                        self.clean_mesh(context, object)

                context.view_layer.objects.active = original_active_object

            else:
                if context.active_object.type == 'MESH':

                    self.clean_mesh(context, context.active_object)

        elif get_preferences().meshclean_mode == 'VISIBLE':
            if self.object_mode == 'OBJECT':

                original_active_object = context.view_layer.objects.active

                for object in context.visible_objects:
                    if object.type == 'MESH':

                        self.clean_mesh(context, object)

                context.view_layer.objects.active = original_active_object

            else:
                if context.active_object.type == 'MESH':

                    mesh = bmesh.from_edit_mesh(context.active_object.data)

                    original_selected_geometry = {'verts': [vert for vert in mesh.verts if vert.select],
                                                  'edges': [edge for edge in mesh.edges if edge.select],
                                                  'faces': [face for face in mesh.faces if face.select]}

                    visible_geometry = {'verts': [vert for vert in mesh.verts if not vert.hide],
                                        'edges': [edge for edge in mesh.edges if not edge.hide],
                                        'faces': [face for face in mesh.faces if not face.hide]}

                    # unselect geometry
                    for type in original_selected_geometry:
                        for geo in original_selected_geometry[type]:
                            geo.select_set(state=False)

                    # select visible
                    for type in visible_geometry:
                        for geo in visible_geometry[type]:
                            geo.select_set(state=True)

                    # clean mesh
                    self.clean_mesh(context, context.active_object)

        else:
            if context.active_object.type == 'MESH':
                self.clean_mesh(context, context.active_object)

        bpy.ops.object.mode_set(mode=self.object_mode)

        return {'FINISHED'}

    def clean_mesh(self, context, object):

        context.view_layer.objects.active = object

        bpy.ops.object.mode_set(mode='EDIT')

        if get_preferences().meshclean_unhide_behavior:
            bpy.ops.mesh.reveal()

        context.tool_settings.mesh_select_mode = (False, True, False)

        if get_preferences().meshclean_mode == 'ACTIVE' or self.object_mode == 'OBJECT':
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='TOGGLE')

        bpy.ops.mesh.remove_doubles(threshold=get_preferences().meshclean_remove_threshold)

        bpy.ops.mesh.dissolve_limited(angle_limit=get_preferences().meshclean_dissolve_angle)

        if get_preferences().meshclean_delete_interior:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_interior_faces()
            bpy.ops.mesh.delete(type='FACE')

        if object.hops.status == "CSTEP":
            bpy.ops.mesh.hide(unselected=False)

        bpy.ops.object.mode_set(mode='OBJECT')
