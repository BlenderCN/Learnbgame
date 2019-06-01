import bpy
import bmesh
from bpy.props import (
    BoolProperty,
    PointerProperty,
    CollectionProperty,
    StringProperty
)
from math import (
    radians
)
from mathutils import (
    Vector,
    Quaternion
)

from . piece_properties import (
    WorkpiecePropertyGroup,
    WorkpieceDescription,
    WorkpieceSize,
    WorkpiecePosition,
    WorkpieceCount
)


class GroupItem(bpy.types.PropertyGroup):
    name = StringProperty(name="", default="")
    selected = BoolProperty(name="", default=False)


class WorkpieceOperator(bpy.types.Operator):
    bl_description = "Creates a new workpiece"
    bl_idname = "mesh.woodwork_workpiece"
    bl_label = "Workpiece"
    bl_category = 'Woodwork'
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    #
    # Class variables
    #
    expand_description_properties = BoolProperty(name="Expand",
                                                 default=True)
    expand_size_properties = BoolProperty(name="Expand",
                                          default=True)
    expand_position_properties = BoolProperty(name="Expand",
                                              default=True)
    expand_count_properties = BoolProperty(name="Expand",
                                           default=True)

    piece_properties = PointerProperty(type=WorkpiecePropertyGroup)

    group_items = CollectionProperty(type=GroupItem)

    origin_corner_to_origin_offset_scale = {
        "xminyminzmin": Vector((1.0, 1.0, 1.0)),
        "xmaxyminzmin": Vector((-1.0, 1.0, 1.0)),
        "xminymaxzmin": Vector((1.0, -1.0, 1.0)),
        "xmaxymaxzmin": Vector((-1.0, -1.0, 1.0)),
        "xminyminzmax": Vector((1.0, 1.0, -1.0)),
        "xmaxyminzmax": Vector((-1.0, 1.0, -1.0)),
        "xminymaxzmax": Vector((1.0, -1.0, -1.0)),
        "xmaxymaxzmax": Vector((-1.0, -1.0, -1.0))
    }

    origin_edge_to_origin_offset_scale = {
        "top-face-xmin": Vector((1.0, 0.0, -1.0)),
        "top-face-xmax": Vector((-1.0, 0.0, -1.0)),
        "top-face-ymin": Vector((0.0, 1.0, -1.0)),
        "top-face-ymax": Vector((0.0, -1.0, -1.0)),
        "bottom-face-xmin": Vector((1.0, 0.0, 1.0)),
        "bottom-face-xmax": Vector((-1.0, 0.0, 1.0)),
        "bottom-face-ymin": Vector((0.0, 1.0, 1.0)),
        "bottom-face-ymax": Vector((0.0, -1.0, 1.0)),
        "front-edge-xmin": Vector((1.0, 1.0, 0.0)),
        "front-edge-xmax": Vector((-1.0, 1.0, 0.0)),
        "front-edge-zmin": Vector((0.0, 1.0, 1.0)),
        "front-edge-zmax": Vector((0.0, 1.0, -1.0)),
        "back-edge-xmin": Vector((1.0, -1.0, 0.0)),
        "back-edge-xmax": Vector((-1.0, -1.0, 0.0)),
        "back-edge-zmin": Vector((0.0, -1.0, 1.0)),
        "back-edge-zmax": Vector((0.0, -1.0, -1.0)),
        "left-end-ymin": Vector((1.0, 1.0, 0.0)),
        "left-end-ymax": Vector((1.0, -1.0, 0.0)),
        "left-end-zmin": Vector((1.0, 0.0, 1.0)),
        "left-end-zmax": Vector((1.0, 0.0, -1.0)),
        "right-end-ymin": Vector((-1.0, 1.0, 0.0)),
        "right-end-ymax": Vector((-1.0, -1.0, 0.0)),
        "right-end-zmin": Vector((-1.0, 0.0, 1.0)),
        "right-end-zmax": Vector((-1.0, 0.0, -1.0))
    }

    origin_face_to_origin_offset_scale = {
        "face-top": Vector((0.0, 0.0, -1.0)),
        "face-bottom": Vector((0.0, 0.0, 1.0)),
        "edge-front": Vector((0.0, 1.0, 0.0)),
        "edge-back": Vector((0.0, -1.0, 0.0)),
        "end-left": Vector((1.0, 0.0, 0.0)),
        "end-right": Vector((-1.0, 0.0, 0.0))
    }

    @staticmethod
    def create_piece(piece_size: WorkpieceSize,
                     origin_offset_scale: Vector) -> bmesh.types.BMesh:
        mesh = bmesh.new()

        len_offset = piece_size.length / 2.0
        width_offset = piece_size.width / 2.0
        thickness_offset = piece_size.thickness / 2.0

        origin_offset = Vector((origin_offset_scale[0] * len_offset,
                                origin_offset_scale[1] * width_offset,
                                origin_offset_scale[2] * thickness_offset))

        coords = (Vector((-len_offset, -width_offset, -thickness_offset)),
                  Vector((len_offset, -width_offset, -thickness_offset)),
                  Vector((-len_offset, width_offset, -thickness_offset)),
                  Vector((len_offset, width_offset, -thickness_offset)),
                  Vector((-len_offset, -width_offset, thickness_offset)),
                  Vector((len_offset, -width_offset, thickness_offset)),
                  Vector((-len_offset, width_offset, thickness_offset)),
                  Vector((len_offset, width_offset, thickness_offset)))

        verts = []
        for co in coords:
            vert_co = co + origin_offset
            verts.append(mesh.verts.new(vert_co.to_tuple()))

        sides = ((0, 2, 3, 1),
                 (4, 5, 7, 6),
                 (0, 4, 5, 1),
                 (1, 3, 7, 5),
                 (3, 7, 6, 2),
                 (2, 0, 4, 6))
        faces = []
        for side in sides:
            side_verts = [verts[i] for i in side]
            faces.append(mesh.faces.new(side_verts))

        bmesh.ops.recalc_face_normals(mesh, faces=faces)

        return mesh

    # Adapted from blender code "rotation_between_quats_to_quat"
    @staticmethod
    def quaternion_rotation(quat0: Quaternion, quat1: Quaternion):
        conj = quat0.conjugated()
        saved_conj = conj.copy()
        val = 1.0 / conj.dot(conj)
        saved_conj *= val
        return saved_conj.cross(quat1)

    @staticmethod
    def visible_surface_rotation(visible_surface: str) -> list:
        # bring visible surface in x/z axis (front view)
        rotations = []
        if visible_surface == "face grain":
            rotations.append(Quaternion((1.0, 0.0, 0.0), radians(90.0)))
        elif visible_surface == "end grain":
            rotations.append(Quaternion((0.0, 0.0, 1.0), radians(90.0)))
        return rotations

    @staticmethod
    def orientation_rotation(context, orientation: str, view: str) -> list:
        rotations = []
        if orientation == "vertical":
            if view == "top":
                rotations.append(Quaternion((0.0, 0.0, 1.0), radians(90.0)))
            elif view == "right":
                rotations.append(Quaternion((1.0, 0.0, 0.0), radians(90.0)))
            elif view == "front":
                rotations.append(Quaternion((0.0, 1.0, 0.0), radians(90.0)))
            elif view == "align":
                space_data = context.space_data
                if space_data and space_data.type != 'VIEW_3D':
                    space_data = None
                if space_data:
                    to_user_view = space_data.region_3d.view_rotation
                    z_axis = Vector((0.0, 0.0, 1.0))
                    z_axis.rotate(to_user_view)
                    rotation_in_user_view = Quaternion(z_axis, radians(90.0))
                    rotations.append(rotation_in_user_view)

        return rotations

    @staticmethod
    def view_rotation(context, view: str) -> list:
        rotations = []
        if view == "top":
            rotations.append(Quaternion((1.0, 0.0, 0.0), radians(90.0)))
        elif view == "right":
            rotations.append(Quaternion((0.0, 0.0, 1.0), radians(90.0)))
        elif view == "align":
            space_data = context.space_data
            if space_data and space_data.type != 'VIEW_3D':
                space_data = None
            if space_data:
                # put in top view before user view
                rotations.append(Quaternion((1.0, 0.0, 0.0), radians(90.0)))
                rotations.append(space_data.region_3d.view_rotation.inverted())
        return rotations

    @staticmethod
    def origin_offset_scale(position_properties: WorkpiecePosition) -> Vector:
        if position_properties.origin_type == "center":
            origin_offset_scale = Vector((0.0, 0.0, 0.0))
        elif position_properties.origin_type == "corner":
            origin_offset_scale = \
                WorkpieceOperator.origin_corner_to_origin_offset_scale[
                    position_properties.origin_corner]
        elif position_properties.origin_type == "edge-centered":
            origin_offset_scale = \
                WorkpieceOperator.origin_edge_to_origin_offset_scale[
                    position_properties.origin_edge]
        elif position_properties.origin_type == "face-centered":
            origin_offset_scale = \
                WorkpieceOperator.origin_face_to_origin_offset_scale[
                    position_properties.origin_face]
        return origin_offset_scale

    @staticmethod
    def is_object_in_group(scene_object: bpy.types.Object,
                           group: bpy.types.Group) -> bool:
        found = False
        obj_name = scene_object.name
        group_objects = group.objects
        if obj_name in group_objects and scene_object in group_objects[:]:
            found = True
        return found

    def handle_workpiece_group(self,
                               description_properties: WorkpieceDescription,
                               scene_object: bpy.types.Object):
        if description_properties.is_in_group:

            for group in bpy.data.groups:
                found = False
                for displayed_group in self.group_items:
                    if displayed_group.name == group.name:
                        found = True
                if not found:
                    new_item = self.group_items.add()
                    new_item.name = group.name

                    if WorkpieceOperator.is_object_in_group(scene_object, group):
                        new_item.selected = True

            # create new group if needed
            if description_properties.create_new_group:
                if description_properties.group_name:
                    description_properties.create_new_group = False
                    new_item = self.group_items.add()
                    new_item.name = description_properties.group_name
                    new_item.selected = True

            # add / remove object from groups
            for group_item in self.group_items:
                if group_item.selected:
                    # add object to group
                    if not group_item.name in bpy.data.groups:
                        bpy.ops.group.create(name=group_item.name)
                    bpy.ops.object.group_link(group=group_item.name)
                else:
                    # remove selected objects from group
                    if group_item.name in bpy.data.groups:
                        group = bpy.data.groups.get(group_item.name)
                        if WorkpieceOperator.is_object_in_group(scene_object, group):
                            bpy.ops.group.objects_remove(group=group_item.name)
        else:
            # remove selected objects from every group
            for group in bpy.data.groups:
                if WorkpieceOperator.is_object_in_group(scene_object, group):
                    bpy.ops.group.objects_remove(group=group.name)
        description_properties.group_name = ""

    @staticmethod
    def set_object_rotation(context,
                            position_properties: WorkpiecePosition,
                            scene_object: bpy.types.Object):
        rotations = WorkpieceOperator.visible_surface_rotation(
            position_properties.visible_surface)
        rotations.extend(WorkpieceOperator.view_rotation(
            context,
            position_properties.view))
        rotations.extend(WorkpieceOperator.orientation_rotation(
            context,
            position_properties.orientation,
            position_properties.view))
        scene_object.rotation_mode = 'QUATERNION'
        object_rotations = scene_object.rotation_quaternion.copy()
        for rotation in rotations:
            object_rotations = WorkpieceOperator.quaternion_rotation(
                rotation, object_rotations)
        scene_object.rotation_quaternion = object_rotations

    def set_object_location(self,
                            position_properties: WorkpiecePosition,
                            scene: bpy.types.Scene,
                            scene_object: bpy.types.Object,
                            selected_objects):
        if position_properties.origin_location == "3D cursor":
            scene_object.location = scene.cursor_location
        elif position_properties.origin_location == "position":
            scene_object.location = position_properties.location_coordinates
        elif position_properties.origin_location == "selected":
            if len(selected_objects) == 1:
                selected = selected_objects[0]
                scene_object.location = selected.location + \
                                        Vector(position_properties.distance)
            else:
                self.report({'WARNING'},
                            "Woodworking: One object should be selected")

    def execute(self, context):
        if bpy.context.mode == "OBJECT":

            scene = context.scene

            piece_properties = self.piece_properties
            description_properties = piece_properties.description_properties
            position_properties = piece_properties.position_properties
            count_properties = piece_properties.count_properties

            # save selected object
            selected_objects = context.selected_objects
            if len(selected_objects) > 0:
                for ob in scene.objects:
                    ob.select = False

            if not description_properties.piece_name:
                description_properties.piece_name = description_properties.cutting_list_type
            piece_name = description_properties.piece_name

            mesh = bpy.data.meshes.new(piece_name + 'Mesh')
            scene_object = bpy.data.objects.new(piece_name, mesh)

            # save custom properties
            scene_object.woodwork.cutting_list_type = \
                description_properties.cutting_list_type
            scene_object.woodwork.comments = description_properties.comments

            base = scene.objects.link(scene_object)
            base.select = True

            origin_offset_scale = WorkpieceOperator.origin_offset_scale(
                position_properties)
            piece_mesh = WorkpieceOperator.create_piece(
                piece_properties.size_properties,
                origin_offset_scale)

            WorkpieceOperator.set_object_rotation(context,
                                                  position_properties,
                                                  scene_object)

            self.set_object_location(position_properties, scene, scene_object,
                                     selected_objects)

            piece_mesh.to_mesh(mesh)
            piece_mesh.free()

            mesh.update()
            scene.objects.active = scene_object

            # create group list
            self.handle_workpiece_group(description_properties, scene_object)

            # create copies
            if count_properties.count > 1:
                distance = Vector(count_properties.distance)
                for counter in range(count_properties.count - 1):
                    if count_properties.use_same_mesh:
                        bpy.ops.object.duplicate_move_linked(
                            TRANSFORM_OT_translate={
                                "value": (distance[0], distance[1], distance[2])
                            }
                        )
                    else:
                        bpy.ops.object.duplicate_move(
                            TRANSFORM_OT_translate={
                                "value": (distance[0], distance[1], distance[2])
                            }
                        )


            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "Woodworking: Option only valid in Object mode")
            return {'CANCELLED'}

    @staticmethod
    def __draw_size_properties(layout: bpy.types.UILayout,
                               size_properties: WorkpieceSize):
        size_box = layout.box()

        size_box.label(text="Thickness", icon="SETTINGS")
        size_box.prop(size_properties, "thickness", text="")
        size_box.label(text="Length", icon="SETTINGS")
        size_box.prop(size_properties, "length", text="")
        size_box.label(text="Width", icon="SETTINGS")
        size_box.prop(size_properties, "width", text="")

    @staticmethod
    def __draw_location_properties(position_box: bpy.types.UILayout,
                                   position_properties: WorkpiecePosition):
        position_box.label(text="Origin type")
        position_box.prop(position_properties, "origin_type", text="")

        if position_properties.origin_type == "corner":
            position_box.label(text="Selected corner (local)")
            position_box.prop(position_properties, "origin_corner", text="")
        elif position_properties.origin_type == "edge-centered":
            position_box.label(text="Selected edge")
            position_box.prop(position_properties, "origin_edge", text="")
        elif position_properties.origin_type == "face-centered":
            position_box.label(text="Selected face")
            position_box.prop(position_properties, "origin_face", text="")

        position_box.label(text="Origin location")
        position_box.prop(position_properties, "origin_location", text="")

        if position_properties.origin_location == "position":
            position_box.label(text="Coordinates")
            position_box.prop(position_properties, "location_coordinates",
                              text="")
        elif position_properties.origin_location == "selected":
            position_box.label(text="Distance", icon='ARROW_LEFTRIGHT')
            position_box.prop(position_properties, "distance", text="")

    @staticmethod
    def __draw_position_properties(layout: bpy.types.UILayout,
                                   position_properties: WorkpiecePosition):
        position_box = layout.box()

        position_box.label(text="Visible face", icon="SNAP_FACE")
        position_box.prop(position_properties, "visible_surface", text="")
        position_box.label(text="Orientation", icon="FILE_REFRESH")
        position_box.prop(position_properties, "orientation", text="")
        position_box.label(text="View", icon="RESTRICT_VIEW_OFF")
        position_box.prop(position_properties, "view", text="")
        WorkpieceOperator.__draw_location_properties(position_box,
                                                     position_properties)

    def __draw_description_properties(self,
                                      layout: bpy.types.UILayout,
                                      description_properties: WorkpieceDescription):
        description_box = layout.box()

        description_box.label(text="Type", icon="OOPS")
        description_box.prop(description_properties, "cutting_list_type", text="")
        description_box.label(text="Piece name", icon="SORTALPHA")
        description_box.prop(description_properties, "piece_name", text="")
        description_box.label(text="Comments", icon="TEXT")
        description_box.prop(description_properties, "comments", text="")

        description_box.prop(description_properties, "is_in_group")
        if description_properties.is_in_group:
            if not description_properties.create_new_group:
                if len(self.group_items) > 0:
                    description_box.template_list(
                        "GroupUIList",
                        "",
                        self,
                        "group_items",
                        description_properties,
                        "active_group_index",
                        rows=4,
                        maxrows=4)
                description_box.prop(description_properties, "create_new_group",
                                     emboss=True)
            else:
                description_box.prop(description_properties, "create_new_group",
                                     emboss=True)
                description_box.prop(description_properties, "group_name")

    @staticmethod
    def __draw_count_properties(layout: bpy.types.UILayout,
                                count_properties: WorkpieceCount):
        count_box = layout.box()

        count_box.label(text="Count", icon="ORTHO")
        count_box.prop(count_properties, "count", text="")
        if count_properties.count > 1:
            count_box.prop(count_properties, "use_same_mesh",
                           text="Use same mesh", icon="LINKED", toggle=True)

            count_box.label(text="Distance", icon='ARROW_LEFTRIGHT')
            count_box.prop(count_properties, "distance", text="")

    def draw(self, context):
        layout = self.layout

        piece_properties = self.piece_properties
        description_properties = piece_properties.description_properties
        size_properties = piece_properties.size_properties
        position_properties = piece_properties.position_properties
        count_properties = piece_properties.count_properties

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        if not self.expand_description_properties:
            row.prop(self, "expand_description_properties", icon="TRIA_RIGHT",
                     icon_only=True, text="Description",
                     emboss=False)
        else:
            row.prop(self, "expand_description_properties", icon="TRIA_DOWN",
                     icon_only=True, text="Description",
                     emboss=False)
            WorkpieceOperator.__draw_description_properties(self,
                                                            layout,
                                                            description_properties)

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        if not self.expand_size_properties:
            row.prop(self, "expand_size_properties", icon="TRIA_RIGHT",
                     icon_only=True, text="Size",
                     emboss=False)
        else:
            row.prop(self, "expand_size_properties", icon="TRIA_DOWN",
                     icon_only=True, text="Size",
                     emboss=False)
            WorkpieceOperator.__draw_size_properties(layout,
                                                     size_properties)

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        if not self.expand_position_properties:
            row.prop(self, "expand_position_properties", icon="TRIA_RIGHT",
                     icon_only=True, text="Position",
                     emboss=False)
        else:
            row.prop(self, "expand_position_properties", icon="TRIA_DOWN",
                     icon_only=True, text="Position",
                     emboss=False)
            WorkpieceOperator.__draw_position_properties(layout,
                                                         position_properties)

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        if not self.expand_count_properties:
            row.prop(self, "expand_count_properties", icon="TRIA_RIGHT",
                     icon_only=True, text="Count",
                     emboss=False)
        else:
            row.prop(self, "expand_count_properties", icon="TRIA_DOWN",
                     icon_only=True, text="Count",
                     emboss=False)
            WorkpieceOperator.__draw_count_properties(layout,
                                                      count_properties)


class GroupUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(item.name)
        layout.prop(item, "selected")


def register():
    bpy.utils.register_class(GroupItem)
    bpy.utils.register_class(GroupUIList)
    bpy.utils.register_class(WorkpieceOperator)


def unregister():
    bpy.utils.unregister_class(WorkpieceOperator)
    bpy.utils.unregister_class(GroupUIList)
    bpy.utils.unregister_class(GroupItem)