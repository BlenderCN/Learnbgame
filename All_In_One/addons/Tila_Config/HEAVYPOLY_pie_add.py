from mathutils import Matrix
from bpy.props import BoolProperty
from bpy.types import Operator
from bpy.types import Menu
import bpy
bl_info = {
    "name": "Pie Add",
    "description": "",
    "author": "Vaughan Ling",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}


class HP_MT_pie_add(Menu):
    bl_idname = "HP_MT_pie_add"
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        obj = context.active_object
        pie = layout.menu_pie()
        # Left
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1.1
        col.operator("view3d.hp_add_primitive", icon='MESH_PLANE', text="Big").type = 'Plane'
        col.operator("view3d.hp_add_primitive", icon='MESH_PLANE', text="Small").type = 'Plane_Small'
        col.operator("view3d.hp_add_primitive", icon='MESH_CUBE', text="Big").type = 'Cube'
        col.operator("view3d.hp_add_primitive", icon='MESH_CUBE', text="Small").type = 'Cube_Small'
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1
        col.operator("view3d.hp_add_primitive", icon='MESH_CIRCLE', text="6").type = 'Circle_6'
        col.operator("view3d.hp_add_primitive", icon='MESH_CIRCLE', text="8").type = 'Circle_8'
        col.operator("view3d.hp_add_primitive", icon='MESH_CIRCLE', text="12").type = 'Circle_12'
        col.operator("view3d.hp_add_primitive", icon='MESH_CIRCLE', text="24").type = 'Circle_24'
        col.operator("view3d.hp_add_primitive", icon='MESH_CIRCLE', text="32").type = 'Circle_32'
        # Right
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1
        col.operator("view3d.hp_add_primitive", icon='MESH_UVSPHERE', text="12").type = 'Sphere_12'
        col.operator("view3d.hp_add_primitive", icon='MESH_UVSPHERE', text="24").type = 'Sphere_24'
        col.operator("view3d.hp_add_primitive", icon='MESH_UVSPHERE', text="32").type = 'Sphere_32'
        # Top
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1
        col.operator("view3d.hp_add_primitive", icon='IPO_EASE_IN_OUT', text="Curve").type = 'Curve'
        col.operator("view3d.hp_add_primitive", icon='CURVE_NCIRCLE', text="Curve").type = 'Curve Circle'
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1
        col.operator("view3d.hp_add_primitive", icon='LIGHT', text="Light").type = 'Light'
        col.operator("view3d.hp_add_primitive", icon='GREASEPENCIL', text="GPencil").type = 'Grease_Pencil'
        # Bottom
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1
        col.operator("view3d.hp_add_primitive", icon='MESH_CYLINDER', text="6").type = 'Cylinder_6'
        col.operator("view3d.hp_add_primitive", icon='MESH_CYLINDER', text="8").type = 'Cylinder_8'
        col.operator("view3d.hp_add_primitive", icon='MESH_CYLINDER', text="12").type = 'Cylinder_12'
        col.operator("view3d.hp_add_primitive", icon='MESH_CYLINDER', text="24").type = 'Cylinder_24'
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1
        col.operator("view3d.hp_add_primitive", icon='MESH_CYLINDER', text="32").type = 'Cylinder_32'
        col.operator("view3d.hp_add_primitive", icon='MESH_CYLINDER', text="64").type = 'Cylinder_64'
        col.operator("view3d.hp_add_primitive", icon='MESH_CYLINDER', text="128").type = 'Cylinder_128'

        # Top Left

        split = pie.split()

        # Top Right
        split = pie.split()

        # Bottom Left

        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1

        # Bottom Right


class HP_OT_add_primitive(bpy.types.Operator):
    bl_idname = "view3d.hp_add_primitive"        # unique identifier for buttons and menu items to reference.
    bl_label = "HP Add Primitive"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO', }  # enable undo for the operator.
    type: bpy.props.StringProperty(name="Type")

    def invoke(self, context, event):
        cur = bpy.context.scene.cursor.location
        # cur = list(cur)
        addob = False
        orthomode = False
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        if space.region_3d.is_perspective:
                            print("Perspective")
                            pass
                        else:
                            print("Ortho")
                            orthomode = True

        def prim(self, type):
            if self.type == 'Cube':
                bpy.ops.mesh.primitive_cube_add(size=.5, view_align=orthomode)
            if self.type == 'Cube_Small':
                bpy.ops.mesh.primitive_cube_add(size=.05, view_align=orthomode)
            if self.type == 'Plane':
                bpy.ops.mesh.primitive_plane_add(view_align=orthomode)
            if self.type == 'Plane_Small':
                bpy.ops.mesh.primitive_plane_add(size=.1, view_align=orthomode)
            if self.type == 'Circle_6':
                bpy.ops.mesh.primitive_circle_add(vertices=6, radius=0.08, fill_type='NGON', view_align=orthomode)
            if self.type == 'Circle_8':
                bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=.25, vertices=8, view_align=orthomode)
            if self.type == 'Circle_12':
                bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=.25, vertices=12, view_align=orthomode)
            if self.type == 'Circle_24':
                bpy.ops.mesh.primitive_circle_add(fill_type='NGON', radius=.25, vertices=24, view_align=orthomode)
            if self.type == 'Circle_32':
                bpy.ops.mesh.primitive_circle_add(fill_type='NGON', vertices=32, view_align=orthomode)

            if self.type == 'Cylinder_6':
                bpy.ops.mesh.primitive_cylinder_add(radius=.08, depth=.1, vertices=6, view_align=orthomode)
            if self.type == 'Cylinder_8':
                bpy.ops.mesh.primitive_cylinder_add(radius=.25, depth=.5, vertices=8, view_align=orthomode)
            if self.type == 'Cylinder_12':
                bpy.ops.mesh.primitive_cylinder_add(radius=.25, depth=.5, vertices=12, view_align=orthomode)
            if self.type == 'Cylinder_24':
                bpy.ops.mesh.primitive_cylinder_add(radius=.25, depth=.5, vertices=24, enter_editmode=False, view_align=orthomode)
            if self.type == 'Cylinder_32':
                bpy.ops.mesh.primitive_cylinder_add(vertices=32, view_align=orthomode)
            if self.type == 'Cylinder_64':
                bpy.ops.mesh.primitive_cylinder_add(vertices=64, view_align=orthomode)
            if self.type == 'Cylinder_128':
                bpy.ops.mesh.primitive_cylinder_add(vertices=128, view_align=orthomode)
            if self.type == 'Sphere_12':
                bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=0.1, view_align=orthomode)
            if self.type == 'Sphere_24':
                bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, view_align=orthomode)
            if self.type == 'Sphere_32':
                bpy.ops.mesh.primitive_uv_sphere_add(view_align=orthomode)

            if self.type == 'Grease_Pencil':
                bpy.ops.object.gpencil_add()
                bpy.ops.gpencil.paintmode_toggle()
            if self.type == 'Curve':
                bpy.ops.curve.primitive_nurbs_path_add(view_align=orthomode)
                bpy.ops.object.editmode_toggle()
            if self.type == 'Light':
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.light_add(type='POINT', radius=.05)
                bpy.context.active_object.name = 'Light'
                bpy.context.object.data.energy = 5
                bpy.context.object.data.shadow_soft_size = 0.3
                bpy.context.object.data.shadow_buffer_soft = 0
                bpy.context.object.data.shadow_buffer_bias = 0.1
                bpy.context.object.data.shadow_buffer_exp = 500
                bpy.context.object.data.shadow_buffer_clip_start = 0.1

        t_axis = bpy.context.scene.transform_orientation_slots[0].type

        if self.type in {'Light', 'Grease_Pencil'}:
            addob = True
        if bpy.context.object:
            if bpy.context.object.data.total_vert_sel == 0:
                print('Creating at Cursor')
                prim(self, type)
                bpy.ops.machin3.align(mode='CURSOR')
            elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
                print('Creating Aligned to Faces')
                o = bpy.context.view_layer.objects.active
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.transform.create_orientation(name="AddAxis", use=True, overwrite=True)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                prim(self, type)
                bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), orient_axis='Z', constraint_axis=(False, False, False))
                if addob == False:
                    o.select_set(state=True)
                    bpy.context.view_layer.objects.active = o
                    bpy.ops.object.join()
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.object.face_map_add()
                    bpy.ops.object.face_map_select()
                    bpy.ops.object.face_map_remove_from()
                    bpy.ops.object.face_map_remove()
            else:
                bpy.ops.view3d.snap_cursor_to_selected()
                prim(self, type)
            bpy.context.scene.cursor.location = cur
            bpy.data.scenes[0].transform_orientation_slots[0].type = t_axis
        return {'FINISHED'}


classes = (
    HP_MT_pie_add,
    HP_OT_add_primitive,
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
