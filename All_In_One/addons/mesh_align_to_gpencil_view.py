# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Align Selection To Gpencil Stroke",
    "description": "Aligns selection to a grease pencil stroke. Hold SHIFT and double-click LEFT MOUSE to execute.",
    "author": "Bjørnar Frøyse",
    "version": (1, 0, 7),
    "blender": (2, 7, 0),
    "location": "Tool Shelf",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
from bpy_extras import view3d_utils
import bmesh
import mathutils
from bpy.props import FloatProperty, BoolProperty
import math


# Preferences for the addon (Displayed "inside" the addon in user preferences)
class AlignSelectionToGpencilAddonPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    clear_strokes = bpy.props.BoolProperty(
            name = "Clear Strokes On Execute",
            description = "Clear grease pencil strokes after executing",
            default = False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "clear_strokes")
        if(self.clear_strokes):
            layout.label(text="Be warned: This will currently make the influence slider stop working", icon="ERROR")


class AlignUVsToGpencil(bpy.types.Operator):
    """Aligns UV selection to gpencil stroke"""
    bl_idname = "bear.uv_align_to_gpencil"
    bl_label = "Align UV Verts to Gpencil"
    bl_options = {'REGISTER', 'UNDO'}

    influence = FloatProperty(
            name="Influence",
            description="Influence",
            min=0.0, max=1.0,
            default=1.0,
            )

    def execute(self, context):
        align_uvs(context, self.influence)
        return {'FINISHED'}


def align_uvs(context, influence):
    editor = bpy.context.area.spaces[0]
    gps = editor.grease_pencil.layers[-1].active_frame.strokes[-1].points
    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.layers.tex.verify()

    selected_uv_verts = []
    for f in bm.faces:
        for l in f.loops:
            l_uv = l[uv_layer]
            if l_uv.select:
                selected_uv_verts.append(l_uv)

    selected_uv_verts_positions = []
    for vert in selected_uv_verts:
        selected_uv_verts_positions.append(vert.uv)

    gpencil_points = []
    for point in gps:
        gpencil_points.append(point.co)

    for i, v in enumerate(selected_uv_verts):
        nearest_point = get_nearest_interpolated_point_on_stroke(selected_uv_verts_positions[i], gpencil_points, context)
        # newcoord = obj.matrix_world.inverted() * region_to_location(nearest_point, obj.matrix_world * v.co)
        v.uv = v.uv.lerp(nearest_point, influence)

    bmesh.update_edit_mesh(me, True)

    if context.user_preferences.addons[__name__].preferences.clear_strokes:
       editor.grease_pencil.layers[-1].active_frame.clear()



class AlignSelectionToGPencil(bpy.types.Operator):
    """Aligns selection to gpencil stroke"""
    bl_idname = "bear.align_to_gpencil"
    bl_label = "Align Verts to Gpencil"
    bl_options = {'REGISTER', 'UNDO'}

    influence = FloatProperty(
            name="Influence",
            description="Influence",
            min=0.0, max=1.0,
            default=1.0,
            )

    def execute(self, context):

        # TODO: Make it able to project the selected vertices onto a surface (for retopo).
        # TODO: Option to lock axis?
        # TODO: More flexible "projection"? Currently only vertical & horizontal.
        #       Works in most cases, but can easily break.
        # TODO: Make it work with the mesh.use_mirror_x setting.
        # TODO: Proportional editing
        # TODO: Support for bones (pose mode)
        # TODO: Clear last drawn stroke only

        # Object mode
        if bpy.context.mode == 'OBJECT':
            align_objects(context, self.influence)
            clear_gpencil_strokes(context)
            return {'FINISHED'}

        # Proportional edit active
        if bpy.context.active_object.type == 'MESH' and bpy.context.active_object.data.is_editmode and bpy.data.scenes["Scene"].tool_settings.proportional_edit != 'DISABLED':
            align_vertices_proportional(context, self.influence)
            clear_gpencil_strokes(context)
            return {'FINISHED'}

        # The regular mesh mode. Aligns vertices.
        if bpy.context.active_object.type == 'MESH' and bpy.context.active_object.data.is_editmode:
            align_vertices(context, self.influence)

            clear_gpencil_strokes(context)
            return {'FINISHED'}

        # Aligns bones in edit mode. Simple enough.
        if bpy.context.active_object.type == 'ARMATURE' and bpy.context.active_object.data.is_editmode:
            align_bones_editmode(context, self.influence)

            clear_gpencil_strokes(context)
            return {'FINISHED'}

        # For bones in pose mode. Incomplete.
        if bpy.context.active_object.type == 'ARMATURE' and not bpy.context.active_object.data.is_editmode and bpy.context.active_object.pose is not None:
            align_bones_posemode(context, self.influence)

            clear_gpencil_strokes(context)
            return {'FINISHED'}

        # Aligns curve points
        if bpy.context.active_object.type == 'CURVE' and bpy.context.active_object.data.is_editmode:
            align_curves(context, self.influence)

            clear_gpencil_strokes(context)
            return {'FINISHED'}

        print("No valid cases found. Try again with another selection!")
        return{'FINISHED'}

    @classmethod
    def poll(cls, context):
       if len(bpy.data.grease_pencil) is 0:
           return False
       elif len(bpy.data.grease_pencil[-1].layers) is 0:
           return False
       elif bpy.data.grease_pencil[-1].layers[-1].active_frame is None:
           return False
       elif len(bpy.data.grease_pencil[-1].layers[-1].active_frame.strokes) is 0:
           return False
       else:
           return True


def align_bones_posemode(context, influence):
    print("\nAligning Pose Mode Bones\nThis is pretty 'experimental' at the moment. Don't expect good results!")
    # print("View Matrix:\n", bpy.context.space_data.region_3d.view_matrix)

    # Gets negative values, but it seems to work :)
    rotation_axis = bpy.context.space_data.region_3d.view_matrix.row[2].xyz

    # print("View Matrix Column 3:\n", rotation_axis)

    view_matrix = bpy.context.space_data.region_3d.view_matrix.to_3x3()

    obj = bpy.context.active_object

    selected_p_bones = bpy.context.selected_pose_bones

    p_bone_tails_3d = [p_bone.tail for p_bone in selected_p_bones]
    p_bone_tails_2d = vectors_to_screenpos(context, p_bone_tails_3d, obj.matrix_world)

    for p_bone in selected_p_bones:
        p_bone.bone.select = False


    for r in range(0,5):
        for i, p_bone in enumerate(selected_p_bones):
            p_bone.bone.select = True
            closest_segment = get_closest_segment(p_bone_tails_2d[i], gpencil_to_screenpos(context), context)

            side = is_left(closest_segment[0], closest_segment[1], p_bone_tails_2d[i])
            determinator = side
            
            nearest_point = get_nearest_interpolated_point_on_stroke(p_bone_tails_2d[i], gpencil_to_screenpos(context), context)

            # print("\nSide is", side)
            # print("Determinator is", determinator, "\n")
            iteration = 0
            while side is determinator and iteration < 50:
                if side == False:
                    bpy.ops.transform.rotate(value=-0.01, axis=rotation_axis)
                if side == True:
                    bpy.ops.transform.rotate(value=0.01, axis=rotation_axis)
                current_tail_pos = vectors_to_screenpos(context, p_bone_tails_3d[i], obj.matrix_world)
                side = is_left(closest_segment[0], closest_segment[1], current_tail_pos)
                iteration += 1
                # print("Side is", side)
            # print("\nCOMPLETE\n")
            p_bone.bone.select = False

    for p_bone in selected_p_bones:
        p_bone.bone.select = True

        #newcoord = obj.matrix_world.inverted() * region_to_location(nearest_point, obj.matrix_world * p_bone.tail)
        #p_bone.bone.tail = p_bone.tail.lerp(newcoord, influence)


def is_left(point_a, point_b, point_c):
    return ((point_b[0] - point_a[0]) * (point_c[1] - point_a[1]) - (point_b[1] - point_a[1]) * (point_c[0] - point_a[0])) > 0


def align_bones_editmode(context, influence):
    # Object currently in edit mode.
    obj = bpy.context.edit_object
    # Object's mesh datablock.
    bo = obj.data.edit_bones
    # Get all selected bones (in their local space).

    selected_bones = [bone for bone in bo if bone.select]

    bone_heads_3d = [bone.head for bone in selected_bones]
    bone_heads_2d = vectors_to_screenpos(context, bone_heads_3d, obj.matrix_world)

    bone_tails_3d = [bone.tail for bone in selected_bones]
    bone_tails_2d = vectors_to_screenpos(context, bone_tails_3d, obj.matrix_world)

    points_2d = gpencil_to_screenpos(context)

    for i, bone in enumerate(selected_bones):
        nearest_point_for_head = get_nearest_interpolated_point_on_stroke(bone_heads_2d[i], points_2d, context)
        newcoord_for_head = obj.matrix_world.inverted() * region_to_location(nearest_point_for_head, obj.matrix_world * bone.head)
        bone.head = bone.head.lerp(newcoord_for_head, influence)

        nearest_point_for_tail = get_nearest_interpolated_point_on_stroke(bone_tails_2d[i], points_2d, context)
        newcoord_for_tail = obj.matrix_world.inverted() * region_to_location(nearest_point_for_tail, obj.matrix_world * bone.tail)
        bone.tail = bone.tail.lerp(newcoord_for_tail, influence)


def align_vertices_proportional(context, influence):
    prop_size = bpy.data.scenes["Scene"].tool_settings.proportional_size
    prop_falloff = bpy.data.scenes["Scene"].tool_settings.proportional_edit_falloff

    if prop_falloff == 'SHARP':
        prop_falloff = 0
    if prop_falloff == 'SMOOTH':
        prop_falloff = 1
    if prop_falloff == 'ROOT':
        prop_falloff = 2
    if prop_falloff == 'LINEAR':
        prop_falloff = 3
    if prop_falloff == 'CONSTANT':
        prop_falloff = 4
    if prop_falloff == 'SPHERE':
        prop_falloff = 5
    if prop_falloff == 'RANDOM':
        prop_falloff = 6

    # Object currently in edit mode.
    obj = bpy.context.edit_object
    # Object's mesh datablock.
    me = obj.data
    # Convert mesh data to bmesh.
    bm = bmesh.from_edit_mesh(me)

    # Get all selected vertices (in their local space).
    selected_verts = [v for v in bm.verts if v.select]

    # print("\n ///////// \n")
    unselected_verts_within_radius = []
    for selected_vert in selected_verts:
        for vert in bm.verts:
            if not vert.select:
                dist = (vert.co - selected_vert.co).length 
                if dist <= prop_size:
                    # print("\nVertex:", vert.index, "\nDist: ", dist, "\nProp_size:", prop_size)
                    unselected_verts_within_radius.append(vert)

    unselected_verts_within_radius = list(set(unselected_verts_within_radius))

    # This can probably be merged with the above list
    unselected_verts_nearest_vert_distance = []
    for vert in unselected_verts_within_radius:
        maxdist = 999.0
        nearest_vert = None
        for selected_vert in selected_verts:
            vdist = (vert.co - selected_vert.co).length
            if vdist <= maxdist:
                maxdist = vdist
                nearest_vert = selected_vert
        unselected_verts_nearest_vert_distance.append([vert.index, nearest_vert.index, abs(maxdist)])

    # print("\nUnselected Verts Nearest Verts Distance\n", unselected_verts_nearest_vert_distance)

    verts_local_3d = [v.co for v in selected_verts]
    verts_world_2d = vectors_to_screenpos(context, verts_local_3d, obj.matrix_world)

    final_vert_positions = []
    distances_for_prop_edit = {}
    for i, v in enumerate(selected_verts):
        nearest_point = get_nearest_interpolated_point_on_stroke(verts_world_2d[i], gpencil_to_screenpos(context), context)
        distances_for_prop_edit[v.index] = ((mathutils.Vector(verts_world_2d[i]) - mathutils.Vector(nearest_point)))
        newcoord = obj.matrix_world.inverted() * region_to_location(nearest_point, obj.matrix_world * v.co)
        final_vert_positions.append(newcoord)

    # print("\nDistances For Prop edit\n", distances_for_prop_edit)

    unselected_verts_3d = [v.co for v in unselected_verts_within_radius]
    unselected_verts_2d = vectors_to_screenpos(context, unselected_verts_3d, obj.matrix_world)

    for i, v in enumerate(unselected_verts_within_radius):
        # print("i: ", i)
        # print("v: ", v)
        # Distance had to be inverted to work. Not sure why.
        distance = 1 - unselected_verts_nearest_vert_distance[i][2]
        # print("\nVertex", v.index, "\nDistance", distance)

        proportional_influence = 0
        
        # These are grabbed almost directly from the Blender source. Should work as expected.
        # SHARP
        if prop_falloff == 0:
            proportional_influence = distance * distance
        
        # SMOOTH
        if prop_falloff == 1:
            proportional_influence = 3.0 * distance * distance - 2.0 * distance * distance * distance
        
        # ROOT
        if prop_falloff == 2:
            proportional_influence = math.sqrt(distance)
        
        # LINEAR
        if prop_falloff == 3:
            proportional_influence = distance
        
        # CONSTANT
        if prop_falloff == 4:
            proportional_influence = 1.0
        
        # SPHERE
        if prop_falloff == 5:
            proportional_influence = math.sqrt(2 * distance - distance * distance)
        
        # RANDOM
        if prop_falloff == 6:
            proportional_influence = mathutils.noise.random() * distance

        # print("Prop_influence_BEFORE:", proportional_influence)

        # print("\nNearest Vert for This Vert: ", unselected_verts_nearest_vert_distance[i][1])
        # proportional_influence = clamp(0, 1, proportional_influence)g
        # proportional_influence = prop_size / proportional_influence
        # print("Prop_influence_AFTER", proportional_influence)
        nearest_point = mathutils.Vector(unselected_verts_2d[i]) - distances_for_prop_edit[unselected_verts_nearest_vert_distance[i][1]]
        # nearest_point = get_nearest_interpolated_point_on_stroke(unselected_verts_2d[i], gpencil_to_screenpos(context), context)

        newcoord = obj.matrix_world.inverted() * region_to_location(nearest_point, obj.matrix_world * v.co)
        v.co = v.co.lerp(newcoord, influence * proportional_influence)

    for i, v in enumerate(selected_verts):
        v.co = v.co.lerp(final_vert_positions[i], influence)

    # Recalculate mesh normals (so lighting looks right).
    for edge in bm.edges:
        edge.normal_update()


    # Push bmesh changes back to the actual mesh datablock.
    bmesh.update_edit_mesh(me, True)    


def align_vertices(context, influence):
    # Object currently in edit mode.
    obj = bpy.context.edit_object
    # Object's mesh datablock.
    me = obj.data
    # Convert mesh data to bmesh.
    bm = bmesh.from_edit_mesh(me)

    # Get all selected vertices (in their local space).
    selected_verts = [v for v in bm.verts if v.select]

    verts_local_3d = [v.co for v in selected_verts]

    # Convert selected vertices' positions to 2D screen space.
    # IMPORTANT: Multiply vertex coordinates with the world matrix to get their WORLD position, not local position.
    verts_world_2d = vectors_to_screenpos(context, verts_local_3d, obj.matrix_world)

    # For each vert, look up or to the side and find the nearest interpolated gpencil point for this vertex.
    for i, v in enumerate(selected_verts):
        nearest_point = get_nearest_interpolated_point_on_stroke(verts_world_2d[i], gpencil_to_screenpos(context), context)
        # Get new vertex coordinate by converting from 2D screen space to 3D world space. Must multiply depth coordinate
        # with world matrix and then final result by INVERTED world matrix to get a correct final value.
        newcoord = obj.matrix_world.inverted() * region_to_location(nearest_point, obj.matrix_world * v.co)
        # Apply the final position using an influence slider.
        v.co = v.co.lerp(newcoord, influence)

    # Recalculate mesh normals (so lighting looks right).
    for edge in bm.edges:
        edge.normal_update()

    # Push bmesh changes back to the actual mesh datablock.
    bmesh.update_edit_mesh(me, True)


def align_curves(context, influence):

    print("Aligning curves...\n")
    # Object currently in edit mode.
    obj = bpy.context.edit_object

    splines = bpy.context.active_object.data.splines

    spline_is_bezier = False

    if len(splines[0].bezier_points) > 0:
        spline_is_bezier = True

    # For each vert, look up or to the side and find the nearest interpolated gpencil point for this vertex.
    if not spline_is_bezier:
        selected_points = []
        for spline in splines:
            for point in spline.points:
               if point.select:
                   selected_points.append(point)

        points_local_3d = [p.co for p in selected_points]
        points_world_2d = vectors_to_screenpos(context, points_local_3d, obj.matrix_world)

        for i, p in enumerate(selected_points):
            nearest_point = get_nearest_interpolated_point_on_stroke(points_world_2d[i], gpencil_to_screenpos(context), context)
            # Get new vertex coordinate by converting from 2D screen space to 3D world space. Must multiply depth coordinate
            # with world matrix and then final result by INVERTED world matrix to get a correct final value.
            newcoord = obj.matrix_world.inverted() * region_to_location(nearest_point, obj.matrix_world * p.co)
            # Apply the final position using an influence slider.

            newcoord = newcoord.to_4d()
            p.co = p.co.lerp(newcoord, influence)

    if spline_is_bezier:
        selected_bezier_points = []
        for spline in splines:
            for point in spline.bezier_points:
               if point.select_control_point:
                   selected_bezier_points.append(point)

        bezier_points_local_3d = [p.co for p in selected_bezier_points]
        bezier_points_world_2d = vectors_to_screenpos(context, bezier_points_local_3d, obj.matrix_world)

        for i, p in enumerate(selected_bezier_points):
            nearest_point = get_nearest_interpolated_point_on_stroke(bezier_points_world_2d[i], gpencil_to_screenpos(context), context)
            newcoord = obj.matrix_world.inverted() * region_to_location(nearest_point, obj.matrix_world * p.co)
            if p.handle_left_type == 'FREE' or p.handle_left_type == 'ALIGNED' or p.handle_right_type == 'FREE' or p.handle_right_type == 'ALIGNED':
                print("Supported handle modes: 'VECTOR', 'AUTO'. Please convert. Sorry!")
                return{'CANCELLED'}

            p.co = p.co.lerp(newcoord.to_4d(), influence)
            p.handle_left = obj.matrix_world.inverted() * region_to_location(get_nearest_interpolated_point_on_stroke(p.handle_left, gpencil_to_screenpos(context), context), obj.matrix_world * p.handle_left) 
            p.handle_right = obj.matrix_world.inverted() * region_to_location(get_nearest_interpolated_point_on_stroke(p.handle_right, gpencil_to_screenpos(context), context), obj.matrix_world * p.handle_right) 


def align_objects(context, influence):
    selected_objs = bpy.context.selected_objects

    for i, obj in enumerate(selected_objs):
        obj_loc_2d = vectors_to_screenpos(context, obj.location, obj.matrix_world * obj.matrix_world.inverted())
        nearest_point = get_nearest_interpolated_point_on_stroke(obj_loc_2d, gpencil_to_screenpos(context), context)

        newcoord = region_to_location(nearest_point, obj.location)
        obj.location = obj.location.lerp(newcoord, influence)


def get_nearest_interpolated_point_on_stroke(vertex_2d, points_2d, context):
    # Define variables used for the two different axes (horizontal or vertical).
    # Doing it like this in order to use the same code for both axes.
    if is_vertical(vertex_2d, points_2d):
        a = 1
        b = 0
    if not is_vertical(vertex_2d, points_2d):
        a = 0
        b = 1

    # Variable for nearest point. Set to 9999 in order to guarantee a closer match.
    nearest_distance = 9999.0
    nearest_point = (0, 0)
    point_upper = 0.0
    point_lower = 0.0
    coord_interpolated = 0

    # I have a feeling this is not the best way to do this, but anyway;
    # This bit of code finds (in 2D) the point (on a line) closest to another point.

    # Works by finding the closest in one direction, then the other, then
    # calculating the interpolated position between these two outer points.
    for i, gpoint_2d in enumerate(points_2d):
        # Variables used to find points relative to the current point (i),
        # clamped to avoid out of range errors.
        previous_point = clamp(0, len(points_2d)-1, i - 1)
        next_point = clamp(0, len(points_2d)-1, i + 1)

        # Gets the absolute (non-negative) distance from the
        # current vertex to the current grease pencil point.
        distance = abs(vertex_2d[a] - gpoint_2d[a])

        # If the current gpencil point is the closest so far, calculate
        # everything and push the values to the variables defined earlier.
        if (distance < nearest_distance):
            nearest_distance = distance
            # If the nearest gpoint is ABOVE the current vertex,
            # find the nearest point BELOW as well.
            # TODO: Make this more readable/elegant? It works, so no need, but still.
            if (gpoint_2d[a] >= vertex_2d[a]):
                point_upper = gpoint_2d
                point_lower = points_2d[previous_point]

                # If the lower point is actually above the vertex,
                # we picked the wrong point and need to correct.
                if (point_lower[a] > point_upper[a]) or (point_upper == point_lower):
                    point_lower = points_2d[next_point]
            else:
                # The opposite of the previous lines
                point_lower = gpoint_2d
                point_upper = points_2d[previous_point]
                if (point_upper[a] <= point_lower[a]) or (point_upper == point_lower):
                    point_upper = points_2d[next_point]

            # Define min and max ranges to calculate the interpolated po<int from
            hrange = (point_upper[b], point_lower[b])
            vrange = (point_upper[a], point_lower[a])
            coord_interpolated = map_range(vrange, hrange, vertex_2d[a])

            # Push the interpolated coord to the correct axis
            if a == 1:
                nearest_point = (coord_interpolated, vertex_2d[1])
            if a == 0:
                nearest_point = (vertex_2d[0], coord_interpolated)

    return nearest_point


def get_closest_segment(vertex_2d, points_2d, context):
    if is_vertical(vertex_2d, points_2d):
        a = 1
        b = 0
    if not is_vertical(vertex_2d, points_2d):
        a = 0
        b = 1
    nearest_distance = 9999.0
    nearest_point = (0, 0)
    point_upper = 0.0
    point_lower = 0.0
    coord_interpolated = 0
    for i, gpoint_2d in enumerate(points_2d):
        previous_point = clamp(0, len(points_2d)-1, i - 1)
        next_point = clamp(0, len(points_2d)-1, i + 1)

        distance = abs(vertex_2d[a] - gpoint_2d[a])

        if (distance < nearest_distance):
            nearest_distance = distance
            if (gpoint_2d[a] >= vertex_2d[a]):
                point_upper = gpoint_2d
                point_lower = points_2d[previous_point]
                if (point_lower[a] > point_upper[a]) or (point_upper == point_lower):
                    point_lower = points_2d[next_point]
            else:
                point_lower = gpoint_2d
                point_upper = points_2d[previous_point]
                if (point_upper[a] <= point_lower[a]) or (point_upper == point_lower):
                    point_upper = points_2d[next_point]

    segment = (point_upper, point_lower)
    return segment


def clear_gpencil_strokes(context):
    if context.user_preferences.addons[__name__].preferences.clear_strokes:
        bpy.context.active_object.grease_pencil.layers[-1].active_frame.clear()


def gpencil_to_screenpos(context):
    gps = bpy.context.active_object.grease_pencil.layers[-1].active_frame
    points_2d = [location_to_region(point.co) for point in gps.strokes[-1].points if (len(gps.strokes) > 0)]
    return points_2d


def vectors_to_screenpos(context, list_of_vectors, matrix):
    if type(list_of_vectors) is mathutils.Vector:
        return location_to_region(matrix * list_of_vectors)
    else:
        return [location_to_region(matrix * vector) for vector in list_of_vectors]


# Generic clamp function
def clamp(a, b, v):
    if (v <= a):
        return a
    elif (v >= b):
        return b
    else:
        return v


# Function for determining if a sequence of 2D
# coordinates form a vertical or horizontal line.
def is_vertical(vertex, list_of_vec2):
    if len(list_of_vec2) == 1:
        if abs(list_of_vec2[0][0] - vertex[0]) > abs(list_of_vec2[0][1] - vertex[1]):
            return True
        else:
            return False

    minval = list(map(min, *list_of_vec2))
    maxval = list(map(max, *list_of_vec2))

    if (maxval[0] - minval[0] > maxval[1] - minval[1]):
        return False
    if (maxval[0] - minval[0] < maxval[1] - minval[1]):
        return True


# Generic map range function.
# grabbed from here: www.rosettacode.org/wiki/Map_range
def map_range(fromrange, torange, value):
    (a1, a2), (b1, b2) = fromrange, torange
    # WORKAROUND: If torange start and end is equal, division by zero occurs.
    # A tiny amount is added to one of them to avoid a zero value here.
    if (a1 == a2):
        a2 += 0.0001
    return b1 + ((value - a1) * (b2 - b1) / (a2 - a1))


import bpy_extras


# Utility functions for converting between 2D and 3D coordinates
def location_to_region(worldcoords):
    out = bpy_extras.view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.space_data.region_3d, worldcoords)
    return out


def region_to_location(viewcoords, depthcoords):
    return bpy_extras.view3d_utils.region_2d_to_location_3d(bpy.context.region, bpy.context.space_data.region_3d, viewcoords, depthcoords)


class AlignSelectionToGpencilBUTTON(bpy.types.Panel):
    bl_category = "Tools"
    bl_label = "Gpencil Align"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout
        layout.operator("bear.align_to_gpencil")

class AlignUVsToGpencilBUTTON(bpy.types.Panel):
    bl_category = "Tools"
    bl_label = "Gpencil Align"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout
        layout.operator("bear.uv_align_to_gpencil")


classes = [AlignSelectionToGpencilAddonPrefs, AlignSelectionToGPencil, AlignSelectionToGpencilBUTTON, AlignUVsToGpencil, AlignUVsToGpencilBUTTON]
addon_keymaps = []

def register():
    for c in classes:
        bpy.utils.register_class(c)

    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new("bear.align_to_gpencil", 'LEFTMOUSE', 'DOUBLE_CLICK', False, True)
    addon_keymaps.append((km, kmi))

    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='IMAGE_EDITOR')
    kmi = km.keymap_items.new("bear.uv_align_to_gpencil", 'LEFTMOUSE', 'DOUBLE_CLICK', False, True)
    addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
