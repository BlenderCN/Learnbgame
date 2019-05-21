#############################################
# THUG1/2 COLLISION SETTINGS
#############################################
import bpy
import struct
import mathutils
import math
import bmesh
import os, sys
import statistics, random
import collections
from bpy.props import *
from . constants import *
from . helpers import *
from . autorail import *

# PROPERTIES
#############################################
update_triggered_by_ui_updater = False
BSPNode = collections.namedtuple("BSPNode", "split_point split_axis left right")
BSPLeaf = collections.namedtuple("BSPLeaf", "faces")


# METHODS
#############################################
def _resolve_face_terrain_type(ob, bm, face):
    ttl = bm.faces.layers.int.get("terrain_type")
    tt = 0
    if not ttl or face[ttl] == AUTORAIL_AUTO:
        if face.material_index >= 0 and len(ob.material_slots):
            face_material = ob.material_slots[face.material_index].material
            if face_material:
                tt = TERRAIN_TYPES.index(face_material.thug_material_props.terrain_type)
    else:
        tt = face[ttl]
    return tt

def make_bsp_tree(ob, faces, matrix):
    def vv(vert, matrix):
        return to_thug_coords(matrix * vert.co)

    def inner(faces, split_axis, level, cant_split=set()):
        # print(level)
        # split_axis = 0
        if len(faces) <= 50: # or split_axis in cant_split:
            return BSPLeaf(faces)

        best_duplis = float("inf")
        best_point = None
        best_left = None
        best_right = None
        best_axis = None

        for split_axis in range(3):
            if split_axis in cant_split: continue
            split_point = statistics.median(
                vv(vert, matrix)[split_axis] for face in random.sample(faces, min(20, len(faces))) for vert in face.verts)
            """
            split_point = statistics.median(
                vv(vert)[split_axis] for face in faces for vert in face.verts)
            """
            split_point = int(split_point * 16.0) * 0.0625

            left_faces = []
            right_faces = []

            duplis = 0
            for face in faces:
                assert len(face.verts) == 3
                left = False
                right = False
                for vert in face.verts:
                    if vv(vert, matrix)[split_axis] < split_point:
                        left = True
                    if vv(vert, matrix)[split_axis] >= split_point:
                        right = True
                if left:
                    left_faces.append(face)
                if right:
                    right_faces.append(face)
                if left and right:
                    duplis += 1

            if duplis < best_duplis:
                best_left = left_faces
                best_right = right_faces
                best_axis = split_axis
                best_duplis = duplis
                best_point = split_point

        left_faces = best_left
        right_faces = best_right
        split_axis = best_axis
        duplis = best_duplis
        split_point = best_point

        if duplis >= (len(faces) // 2):
            return BSPLeaf(faces)

        # print(len(faces), len(left_faces), len(right_faces), duplis, split_axis, level)

        return BSPNode(
            split_point,
            split_axis,
            inner(left_faces,
                (split_axis + 1) % 3,
                level + 1,
                (cant_split | set([split_axis]) if len(left_faces) == len(faces) else cant_split)),
            inner(right_faces,
                (split_axis + 1) % 3,
                level + 1,
                (cant_split | set([split_axis]) if len(right_faces) == len(faces) else cant_split))
             #,
        )

    return inner(faces, 0, 0)


def iter_tree(tree):
    yield tree
    if isinstance(tree, BSPLeaf):
        return
    yield from iter_tree(tree.left)
    yield from iter_tree(tree.right)


def tree_to_list(tree):
    index = 0
    indices = {id(tree): index}
    l = [tree]
    stack = [tree]
    while stack:
        tree = stack.pop(0)
        if isinstance(tree, BSPNode):
            index += 1
            indices[id(tree.left)] = index
            l.append(tree.left)
            stack.append(tree.left)
            index += 1
            indices[id(tree.right)] = index
            l.append(tree.right)
            stack.append(tree.right)
    return l, indices



def update_collision_flag_mesh(wm, context, flag):
    global update_triggered_by_ui_updater
    if update_triggered_by_ui_updater:
        return
    if not context.edit_object:
        return
    bm = bmesh.from_edit_mesh(context.edit_object.data)

    cfl = bm.faces.layers.int.get("collision_flags")
    if not cfl:
        cfl = bm.faces.layers.int.new("collision_flags")

    flag_set = getattr(wm, "thug_face_" + flag)
    for face in bm.faces:
        if not face.select:
            continue
        flags = face[cfl]
        #for ff in SETTABLE_FACE_FLAGS:
        if flag_set:
            flags |= FACE_FLAGS[flag]
        else:
            flags &= ~FACE_FLAGS[flag]
        face[cfl] = flags
    bmesh.update_edit_mesh(context.edit_object.data)

#----------------------------------------------------------------------------------
def update_terrain_type_mesh(wm, context):
    global update_triggered_by_ui_updater
    if update_triggered_by_ui_updater:
        return
    if not context.edit_object:
        return
    bm = bmesh.from_edit_mesh(context.edit_object.data)

    ttl = bm.faces.layers.int.get("terrain_type")
    if not ttl:
        ttl = bm.faces.layers.int.new("terrain_type")

    for face in bm.faces:
        if not face.select:
            continue

        if wm.thug_face_terrain_type == "Auto":
            face[ttl] = AUTORAIL_AUTO
        else:
            face[ttl] = TERRAIN_TYPES.index(wm.thug_face_terrain_type)


    bmesh.update_edit_mesh(context.edit_object.data)

#----------------------------------------------------------------------------------
@bpy.app.handlers.persistent
def update_collision_flag_ui_properties(scene):
    global update_triggered_by_ui_updater
    update_triggered_by_ui_updater = True
    try:
        ob = scene.objects.active
        if not ob or ob.mode != "EDIT" or ob.type != "MESH":
            return
        bm = bmesh.from_edit_mesh(ob.data)
        wm = bpy.context.window_manager

        arl = bm.edges.layers.int.get("thug_autorail")
        edge = bm.select_history.active
        if arl and edge and isinstance(edge, bmesh.types.BMEdge):
            new_value = "Auto" if edge[arl] == AUTORAIL_AUTO else \
                        "None" if edge[arl] == AUTORAIL_NONE else \
                        TERRAIN_TYPES[edge[arl]]
            if wm.thug_autorail_terrain_type != new_value:
                try:
                    wm.thug_autorail_terrain_type = new_value
                except TypeError:
                    wm.thug_autorail_terrain_type = "Auto"

        face = None
        if (("FACE" in bm.select_mode)
            and bm.select_history
            and isinstance(bm.select_history[-1], bmesh.types.BMFace)):
            face = bm.select_history[-1]
        if not face:
            face = next((face for face in bm.faces if face.select), None)
        if not face:
            return

        cfl = bm.faces.layers.int.get("collision_flags")
        for ff in SETTABLE_FACE_FLAGS:
            new_value = bool(cfl and (face[cfl] & FACE_FLAGS[ff]))
            if getattr(wm, "thug_face_" + ff) != new_value:
                setattr(wm, "thug_face_" + ff, new_value)

        ttl = bm.faces.layers.int.get("terrain_type")
        if ttl:
            if face[ttl] == AUTORAIL_AUTO:
                new_value = "Auto"
            else:
                new_value = TERRAIN_TYPES[face[ttl]]
        else:
            new_value = "Auto"
        if wm.thug_face_terrain_type != new_value:
            wm.thug_face_terrain_type = new_value
    finally:
        update_triggered_by_ui_updater = False


# PROPERTIES
#############################################
class THUGCollisionMeshTools(bpy.types.Panel):
    bl_label = "TH Collision Mesh Tools"
    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"
    bl_category = "THUG Tools"

    """
    @classmethod
    def poll(cls, context):
        # Only allow in edit mode for a selected mesh.
        return context.mode == "EDIT_MESH" and context.object is not None and context.object.type == "MESH"
    """

    def draw(self, context):
        self.layout.prop(context.window_manager, "thug_show_face_collision_colors")
        if not context.object: return
        #print(context.mode + " " + context.object.type)
        if context.mode == "EDIT_MESH" and context.object.type == "MESH":
            obj = context.object
            bm = bmesh.from_edit_mesh(obj.data)
            any_face_selected = any(face for face in bm.faces if face.select)
            collision_flag_layer = bm.faces.layers.int.get("collision_flags")
            terrain_type_layer = bm.faces.layers.int.get("terrain_type")
            if any_face_selected:
                box = self.layout.box().column(True)
                tmp_row = box.split()
                col = tmp_row.column()
                for idx, ff in enumerate(SETTABLE_FACE_FLAGS):
                    if idx == 5:
                        col = tmp_row.column()
                    col.prop(context.window_manager, "thug_face_" + ff, toggle=True)
                self.layout.prop(context.window_manager, "thug_face_terrain_type")
            else:
                self.layout.label("No faces selected.")

            if any_face_selected or any(edge for edge in bm.edges if edge.select):
                box = self.layout.box().column(True)
                tmp_row = box.split()
                col = tmp_row.column()
                col.operator(MarkAutorail.bl_idname)
                col = tmp_row.column()
                col.operator(ClearAutorail.bl_idname)
                box.row().prop(context.window_manager, "thug_autorail_terrain_type")
                box.row().operator(ExtractRail.bl_idname)
            else:
                self.layout.label("No edges selected.")
        elif False and context.mode == "OBJECT":
            self.layout.row().label("Object: {}".format(context.object.type))
            self.layout.row().label("Object flags: {}".format(context.object.thug_col_obj_flags))

        elif context.mode == "EDIT_CURVE" and context.object.type == "CURVE":
            if (context.object.type == "CURVE" and
                        context.object.data.splines and
                        context.object.data.splines[0].points):
        
                self.layout.prop(context.window_manager.thug_pathnode_props, "name")
                self.layout.prop_search(
                context.window_manager.thug_pathnode_props, "script_name",
                context.window_manager.thug_all_nodes, "scripts", icon='SCRIPT')
                #self.layout.prop(context.window_manager.thug_pathnode_props, "script_name")
                if context.object.thug_path_type == "Rail":
                    self.layout.prop(context.window_manager.thug_pathnode_props, "terrain")
                if context.object.thug_path_type == "Waypoint":
                    #self.layout.prop(context.window_manager.thug_pathnode_props, "waypt_type")
                    self.layout.prop_search(
                        context.window_manager.thug_pathnode_props, "spawnobjscript",
                        context.window_manager.thug_all_nodes, "scripts", icon='SCRIPTPLUGINS')
                    if context.object.thug_waypoint_props.waypt_type == "PedAI":
                        #self.layout.prop(context.window_manager.thug_pathnode_props, "PedType")
                        if context.object.thug_waypoint_props.PedType == "Skate":
                            #self.layout.prop(context.window_manager.thug_pathnode_props, "do_continue")
                            #self.layout.prop(context.window_manager.thug_pathnode_props, "ContinueWeight")
                            
                            # Once I implement branching paths, Priority will be important!
                            #self.layout.label(text="Priority")
                            #self.layout.prop(context.window_manager.thug_pathnode_props, "Priority", expand=True)
                            self.layout.prop(context.window_manager.thug_pathnode_props, "SkateAction")
                            self.layout.prop(context.window_manager.thug_pathnode_props, "JumpToNextNode")
                            if context.window_manager.thug_pathnode_props.SkateAction == "Jump" or \
                                context.window_manager.thug_pathnode_props.JumpToNextNode:
                                self.layout.prop(context.window_manager.thug_pathnode_props, "JumpHeight")
                                self.layout.prop(context.window_manager.thug_pathnode_props, "SpinAngle")
                                self.layout.prop(context.window_manager.thug_pathnode_props, "SpinDirection", expand=True)
                            
                            if context.window_manager.thug_pathnode_props.SkateAction == "Grind":
                                self.layout.prop(context.window_manager.thug_pathnode_props, "terrain")
                            #if context.window_manager.thug_pathnode_props.SkateAction == "Manual":
                                #self.layout.prop(context.window_manager.thug_pathnode_props, "ManualType")
                            #if context.window_manager.thug_pathnode_props.SkateAction == "Stop":
                                #self.layout.prop(context.window_manager.thug_pathnode_props, "Deceleration")
                                #self.layout.prop(context.window_manager.thug_pathnode_props, "StopTime")
                        
                        elif context.object.thug_waypoint_props.PedType == "Walk":
                            #self.layout.prop(context.window_manager.thug_pathnode_props, "do_continue")
                            #self.layout.prop(context.window_manager.thug_pathnode_props, "ContinueWeight")
                            self.layout.prop(context.window_manager.thug_pathnode_props, "Priority")
                            #self.layout.prop(context.window_manager.thug_pathnode_props, "SkateAction")
                
                