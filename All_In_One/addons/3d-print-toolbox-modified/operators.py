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

# <pep8-80 compliant>

#----------------------------------------------------------
# File operators.py
# All Operator.
#----------------------------------------------------------

import bpy
import bmesh
from bpy.types import Operator
from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    EnumProperty,
    StringProperty
)

from . import (mesh_helpers, report, make_solid_helpers)


def clean_float(text):
    # strip trailing zeros: 0.000 -> 0.0
    index = text.rfind(".")
    if index != -1:
        index += 2
        head, tail = text[:index], text[index:]
        tail = tail.rstrip("0")
        text = head + tail
    return text

def get_text_value(text):
    value_index = text.rfind(":")
    if value_index != -1:
        value_index += 2
        text = text[value_index:]

        index = text.rfind(".")
        if index != -1:
            index += 9
            text = text[:index]
    return text

# get count of vertices, edges and faces in the mesh
def elem_count(context):
    bm = bmesh.from_edit_mesh(context.edit_object.data)
    return len(bm.verts), len(bm.edges), len(bm.faces)


# set the mode as edit, select mode as vertices, and reveal hidden vertices
def setup_environment():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.reveal()


# ---------
# Mesh Info

class Print3DInfoVolume(Operator):
    """Report the volume of the active mesh"""
    bl_idname = "mesh.print3d_info_volume"
    bl_label = "Print3D Info Volume"

    def execute(self, context):
        scene = context.scene
        unit = scene.unit_settings
        scale = 1.0 if unit.system == 'NONE' else unit.scale_length
        obj = context.active_object

        bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
        volume = bm.calc_volume()
        bm.free()

        info = []
        if unit.system == 'METRIC':
            info.append(("Volume: %s cm³" % clean_float("%.4f" %
                                                        ((volume * (scale ** 3.0)) / (0.01 ** 3.0))), None))
        elif unit.system == 'IMPERIAL':
            info.append(("Volume: %s \"³" % clean_float("%.4f" %
                                                        ((volume * (scale ** 3.0)) / (0.0254 ** 3.0))), None))
        else:
            info.append(("Volume: %s³" % clean_float("%.8f" % volume), None))

        report.update(*info)
        return {'FINISHED'}


class Print3DInfoArea(Operator):
    """Report the surface area of the active mesh"""
    bl_idname = "mesh.print3d_info_area"
    bl_label = "Print3D Info Area"

    def execute(self, context):
        scene = context.scene
        unit = scene.unit_settings
        scale = 1.0 if unit.system == 'NONE' else unit.scale_length
        obj = context.active_object

        bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
        area = mesh_helpers.bmesh_calc_area(bm)
        bm.free()

        info = []
        if unit.system == 'METRIC':
            info.append(("Area: %s cm²" % clean_float("%.4f" %
                                                      ((area * (scale ** 2.0)) / (0.01 ** 2.0))), None))
        elif unit.system == 'IMPERIAL':
            info.append(("Area: %s \"²" % clean_float("%.4f" %
                                                      ((area * (scale ** 2.0)) / (0.0254 ** 2.0))), None))
        else:
            info.append(("Area: %s²" % clean_float("%.8f" % area), None))

        report.update(*info)
        return {'FINISHED'}


# ---------------
# Geometry Checks

def execute_check(self, context):
    obj = context.active_object

    info = []
    self.main_check(obj, info)
    report.update(*info)

    return {'FINISHED'}


class Print3DCheckSolid(Operator):
    """Check for geometry is solid (has valid inside/outside) and correct normals"""
    bl_idname = "mesh.print3d_check_solid"
    bl_label = "Print3D Check Solid"

    @staticmethod
    def main_check(obj, info):
        import array

        bm = mesh_helpers.bmesh_copy_from_object(
            obj, transform=False, triangulate=False)

        edges_non_manifold = array.array('i', (i for i, ele in enumerate(bm.edges)
                                               if not ele.is_manifold))
        edges_non_contig = array.array('i', (i for i, ele in enumerate(bm.edges)
                                             if ele.is_manifold and (not ele.is_contiguous)))

        info.append(("Non Manifold Edge: %d" % len(edges_non_manifold),
                     (bmesh.types.BMEdge, edges_non_manifold)))

        info.append(("Bad Contig. Edges: %d" % len(edges_non_contig),
                     (bmesh.types.BMEdge, edges_non_contig)))

        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckIntersections(Operator):
    """Check geometry for self intersections"""
    bl_idname = "mesh.print3d_check_intersect"
    bl_label = "Print3D Check Intersections"

    @staticmethod
    def main_check(obj, info):
        faces_intersect = mesh_helpers.bmesh_check_self_intersect_object(obj)
        info.append(("Intersect Face: %d" % len(faces_intersect),
                     (bmesh.types.BMFace, faces_intersect)))

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckDegenerate(Operator):
    """Check for degenerate geometry that may not print properly """ \
        """(zero area faces, zero length edges)"""
    bl_idname = "mesh.print3d_check_degenerate"
    bl_label = "Print3D Check Degenerate"

    @staticmethod
    def main_check(obj, info):
        import array
        scene = bpy.context.scene
        print_3d = scene.print_3d
        threshold = print_3d.threshold_zero

        bm = mesh_helpers.bmesh_copy_from_object(
            obj, transform=False, triangulate=False)

        faces_zero = array.array('i', (i for i, ele in enumerate(
            bm.faces) if ele.calc_area() <= threshold))
        edges_zero = array.array('i', (i for i, ele in enumerate(
            bm.edges) if ele.calc_length() <= threshold))

        info.append(("Zero Faces: %d" % len(faces_zero),
                     (bmesh.types.BMFace, faces_zero)))

        info.append(("Zero Edges: %d" % len(edges_zero),
                     (bmesh.types.BMEdge, edges_zero)))

        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckDistorted(Operator):
    """Check for non-flat faces """
    bl_idname = "mesh.print3d_check_distort"
    bl_label = "Print3D Check Distorted Faces"

    @staticmethod
    def main_check(obj, info):
        import array

        scene = bpy.context.scene
        print_3d = scene.print_3d
        angle_distort = print_3d.angle_distort

        def face_is_distorted(ele):
            no = ele.normal
            angle_fn = no.angle
            for loop in ele.loops:
                if angle_fn(loop.calc_normal(), 1000.0) > angle_distort:
                    return True
            return False

        bm = mesh_helpers.bmesh_copy_from_object(
            obj, transform=True, triangulate=False)
        bm.normal_update()

        faces_distort = array.array(
            'i', (i for i, ele in enumerate(bm.faces) if face_is_distorted(ele)))

        info.append(("Non-Flat Faces: %d" % len(faces_distort),
                     (bmesh.types.BMFace, faces_distort)))

        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckThick(Operator):
    """Check geometry is above the minimum thickness preference """ \
        """(relies on correct normals)"""
    bl_idname = "mesh.print3d_check_thick"
    bl_label = "Print3D Check Thickness"

    @staticmethod
    def main_check(obj, info):
        scene = bpy.context.scene
        print_3d = scene.print_3d

        faces_error = mesh_helpers.bmesh_check_thick_object(
            obj, print_3d.thickness_min)

        info.append(("Thin Faces: %d" % len(faces_error),
                     (bmesh.types.BMFace, faces_error)))

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckSharp(Operator):
    """Check edges are below the sharpness preference"""
    bl_idname = "mesh.print3d_check_sharp"
    bl_label = "Print3D Check Sharp"

    @staticmethod
    def main_check(obj, info):
        scene = bpy.context.scene
        print_3d = scene.print_3d
        angle_sharp = print_3d.angle_sharp

        bm = mesh_helpers.bmesh_copy_from_object(
            obj, transform=True, triangulate=False)
        bm.normal_update()

        edges_sharp = [ele.index for ele in bm.edges
                       if ele.is_manifold and ele.calc_face_angle_signed() > angle_sharp]

        info.append(("Sharp Edge: %d" % len(edges_sharp),
                     (bmesh.types.BMEdge, edges_sharp)))
        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckOverhang(Operator):
    """Check faces don't overhang past a certain angle"""
    bl_idname = "mesh.print3d_check_overhang"
    bl_label = "Print3D Check Overhang"

    @staticmethod
    def main_check(obj, info):
        import math
        from mathutils import Vector

        scene = bpy.context.scene
        print_3d = scene.print_3d
        angle_overhang = (math.pi / 2.0) - print_3d.angle_overhang

        if angle_overhang == math.pi:
            info.append(("Skipping Overhang", ()))
            return

        bm = mesh_helpers.bmesh_copy_from_object(
            obj, transform=True, triangulate=False)
        bm.normal_update()

        z_down = Vector((0, 0, -1.0))
        z_down_angle = z_down.angle

        # 4.0 ignores zero area faces
        faces_overhang = [ele.index for ele in bm.faces
                          if z_down_angle(ele.normal, 4.0) < angle_overhang]

        info.append(("Overhang Face: %d" % len(faces_overhang),
                     (bmesh.types.BMFace, faces_overhang)))
        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckAll(Operator):
    """Run all checks"""
    bl_idname = "mesh.print3d_check_all"
    bl_label = "Print3D Check All"

    check_cls = (
        Print3DCheckSolid,
        Print3DCheckIntersections,
        Print3DCheckDegenerate,
        Print3DCheckDistorted,
        Print3DCheckThick,
        Print3DCheckSharp,
        Print3DCheckOverhang,
    )

    def execute(self, context):
        obj = context.active_object

        info = []
        for cls in self.check_cls:
            cls.main_check(obj, info)

        report.update(*info)

        return {'FINISHED'}


# ---------------
# Mesh Clean Up

class Print3DCleanDegenerates(Operator):
    """Dissolve zero area faces and zero length egdes"""
    bl_idname = "mesh.print3d_clean_degenerates"
    bl_label = "Degenerate Dissolve"
    bl_options = {'REGISTER', 'UNDO'}

    threshold = FloatProperty(
        name="Merge Distance",
        description="Minimum distance between elements to merge",
        default=0.0001,
        step=1
    )

    def execute(self, context):
        self.context = context
        mode_orig = context.mode

        setup_environment()

        bm_key_orig = elem_count(context)

        self.dissolve_degenerate(self.threshold)

        bm_key = elem_count(context)

        if mode_orig != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report(
            {'INFO'},
            "Modified Verts:%+d, Edges:%+d, Faces:%+d" %
            (bm_key[0] - bm_key_orig[0],
             bm_key[1] - bm_key_orig[1],
             bm_key[2] - bm_key_orig[2]
             ))

        return {'FINISHED'}

    @staticmethod
    def dissolve_degenerate(threshold):
        """dissolve zero area faces and zero length edges"""
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.dissolve_degenerate(threshold=threshold)


class Print3DCleanDoubles(Operator):
    """Remove duplicate vertices"""
    bl_idname = "mesh.print3d_clean_doubles"
    bl_label = "Remove Doubles"
    bl_options = {'REGISTER', 'UNDO'}

    threshold = FloatProperty(
        name="Merge Distance",
        description="Minimum distance between elements to merge",
        default=0.0001,
        step=1
    )

    def execute(self, context):
        self.context = context
        mode_orig = context.mode

        setup_environment()

        bm_key_orig = elem_count(context)

        self.remove_doubles(self.threshold)

        bm_key = elem_count(context)

        if mode_orig != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report(
            {'INFO'},
            "Modified Verts:%+d, Edges:%+d, Faces:%+d" %
            (bm_key[0] - bm_key_orig[0],
             bm_key[1] - bm_key_orig[1],
             bm_key[2] - bm_key_orig[2]
             ))

        return {'FINISHED'}

    @staticmethod
    def remove_doubles(threshold):
        """select all vertices and remove duplicated ones"""
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=threshold)


class Print3DCleanLoose(Operator):
    """Delete loose vertices, edges or faces"""
    bl_idname = "mesh.print3d_clean_loose"
    bl_label = "Delete Loose"
    bl_options = {'REGISTER', 'UNDO'}

    use_verts = BoolProperty(
        name="Vertices",
        description="Remove loose vertices",
        default=True
    )

    use_edges = BoolProperty(
        name="Edges",
        description="Remove loose edges",
        default=True
    )

    use_faces = BoolProperty(
        name="Faces",
        description="Remove loose faces",
        default=True
    )

    def execute(self, context):
        self.context = context
        mode_orig = context.mode

        setup_environment()

        bm_key_orig = elem_count(context)

        self.delete_loose(self.use_verts, self.use_edges, self.use_faces)

        bm_key = elem_count(context)

        if mode_orig != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report(
            {'INFO'},
            "Modified Verts:%+d, Edges:%+d, Faces:%+d" %
            (bm_key[0] - bm_key_orig[0],
             bm_key[1] - bm_key_orig[1],
             bm_key[2] - bm_key_orig[2]
             ))

        return {'FINISHED'}

    @staticmethod
    def delete_loose(use_verts, use_edges, use_faces):
        """delete loose vertices, edges or faces"""
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete_loose(
            use_verts=use_verts, use_edges=use_edges, use_faces=use_faces)


class Print3DCleanNonPlanars(Operator):
    """Split non-planar faces that exceed the angle threshold"""
    bl_idname = "mesh.print3d_clean_non_planars"
    bl_label = "Split Non Planar Faces"
    bl_options = {'REGISTER', 'UNDO'}

    angle_threshold = FloatProperty(
        name="Max Angle",
        description="Angle limit",
        default=0.174533,
        subtype="ANGLE",
        unit="ROTATION",
        step=10
    )

    def execute(self, context):
        self.context = context
        mode_orig = context.mode

        setup_environment()

        bm_key_orig = elem_count(context)

        self.clean_non_planars(self.angle_threshold)

        bm_key = elem_count(context)

        if mode_orig != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report(
            {'INFO'},
            "Modified Verts:%+d, Edges:%+d, Faces:%+d" %
            (bm_key[0] - bm_key_orig[0],
             bm_key[1] - bm_key_orig[1],
             bm_key[2] - bm_key_orig[2]
             ))

        return {'FINISHED'}

    @staticmethod
    def clean_non_planars(angle_limit):
        """split non-planar faces that exceed the angle threshold"""
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.vert_connect_nonplanar(angle_limit=angle_limit)
        # bpy.ops.ui.reports_to_textblock()


class Print3DCleanConcave(Operator):
    """Make all faces convex"""
    bl_idname = "mesh.print3d_clean_concaves"
    bl_label = "Split Concave Faces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.context = context
        mode_orig = context.mode

        setup_environment()

        bm_key_orig = elem_count(context)

        self.clean_concaves()

        bm_key = elem_count(context)

        if mode_orig != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report(
            {'INFO'},
            "Modified Verts:%+d, Edges:%+d, Faces:%+d" %
            (bm_key[0] - bm_key_orig[0],
             bm_key[1] - bm_key_orig[1],
             bm_key[2] - bm_key_orig[2]
             ))

        return {'FINISHED'}

    @staticmethod
    def clean_concaves():
        """make all faces convex"""
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.vert_connect_concave()


class Print3DCleanTriangulateFaces(Operator):
    """Triangulate selected faces"""
    bl_idname = "mesh.print3d_clean_triangulates"
    bl_label = "Triangulate Faces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.context = context
        mode_orig = context.mode

        setup_environment()

        bm_key_orig = elem_count(context)

        bpy.ops.mesh.quads_convert_to_tris()

        bm_key = elem_count(context)

        if mode_orig != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report(
            {'INFO'},
            "Modified Verts:%+d, Edges:%+d, Faces:%+d" %
            (bm_key[0] - bm_key_orig[0],
             bm_key[1] - bm_key_orig[1],
             bm_key[2] - bm_key_orig[2]
             ))

        return {'FINISHED'}


class Print3DCleanHoles(Operator):
    """Fill in holes (boundary edge loops)"""
    bl_idname = "mesh.print3d_clean_holes"
    bl_label = "Fill Holes"
    bl_options = {'REGISTER', 'UNDO'}

    sides = IntProperty(
        name="Sides",
        description="Number of sides in hole required to fill (zero fills all holes)",
        default=4,
        step=1
    )

    def execute(self, context):
        self.context = context
        mode_orig = context.mode

        setup_environment()

        bm_key_orig = elem_count(context)

        self.fill_holes(self.sides)

        bm_key = elem_count(context)

        if mode_orig != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report(
            {'INFO'},
            "Modified Verts:%+d, Edges:%+d, Faces:%+d" %
            (bm_key[0] - bm_key_orig[0],
             bm_key[1] - bm_key_orig[1],
             bm_key[2] - bm_key_orig[2]
             ))

        return {'FINISHED'}

    @staticmethod
    def fill_holes(sides):
        """fill in holes (boundary edge loops)"""
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.fill_holes(sides=sides)


class Print3DCleanLimited(Operator):
    """Dissolve selected edges and verts, limited by the angle of surrounding geometry"""
    bl_idname = "mesh.print3d_clean_limited"
    bl_label = "Limited Dissolve"
    bl_options = {'REGISTER', 'UNDO'}

    angle_threshold = FloatProperty(
        name="Max Angle",
        description="Angle limit",
        default=0.0872665,
        subtype="ANGLE",
        unit="ROTATION",
        step=10
    )

    use_boundaries = BoolProperty(
        name="All Boundaries",
        description="Dissolve all vertices inbetween face boundaries",
        default=False
    )

    def execute(self, context):
        self.context = context
        mode_orig = context.mode

        setup_environment()

        bm_key_orig = elem_count(context)

        self.limited_dissolve(self.angle_threshold, self.use_boundaries)

        bm_key = elem_count(context)

        if mode_orig != 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report(
            {'INFO'},
            "Modified Verts:%+d, Edges:%+d, Faces:%+d" %
            (bm_key[0] - bm_key_orig[0],
             bm_key[1] - bm_key_orig[1],
             bm_key[2] - bm_key_orig[2]
             ))

        return {'FINISHED'}

    @staticmethod
    def limited_dissolve(angle, use_boundaries):
        """dissolve selected edges and verts, limited by the angle of surrounding geometry"""
        bpy.ops.mesh.dissolve_limited(angle_limit=angle, use_dissolve_boundaries=use_boundaries, delimit={'NORMAL'})


# ------------------------------------
# Make Solid from selected objects

class MakeSolidFromSelected(Operator):
	"""Combine selected objects into one"""
	bl_idname = "object.make_solid"
	bl_label = "Make Solid"
	bl_options = {'REGISTER', 'UNDO'}

	mode = 'UNION'

	def execute(self, context):
		active = context.active_object
		selected = context.selected_objects

		if active is None or len(selected) < 2:
			self.report({'WARNING'}, "Select at least 2 objects")
			return {'CANCELLED'}
		else:
			make_solid_helpers.prepare_meshes()
			make_solid_helpers.make_solid_batch()
			make_solid_helpers.is_manifold(self)

		return {'FINISHED'}


# -------------
# Select Report
# ... helper function for info UI

class Print3DSelectReport(Operator):
    """Select the data associated with this report"""
    bl_idname = "mesh.print3d_select_report"
    bl_label = "Print3D Select Report"
    bl_options = {'INTERNAL'}

    index = IntProperty()

    _type_to_mode = {
        bmesh.types.BMVert: 'VERT',
        bmesh.types.BMEdge: 'EDGE',
        bmesh.types.BMFace: 'FACE',
    }

    _type_to_attr = {
        bmesh.types.BMVert: "verts",
        bmesh.types.BMEdge: "edges",
        bmesh.types.BMFace: "faces",
    }

    def execute(self, context):
        obj = context.edit_object
        info = report.info()
        text, data = info[self.index]
        bm_type, bm_array = data

        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type=self._type_to_mode[bm_type])

        bm = bmesh.from_edit_mesh(obj.data)
        elems = getattr(bm, Print3DSelectReport._type_to_attr[bm_type])[:]

        try:
            for i in bm_array:
                elems[i].select_set(True)
        except:
            # possible arrays are out of sync
            self.report({'WARNING'}, "Report is out of date, re-run check")

        # cool, but in fact annoying
        #~ bpy.ops.view3d.view_selected(use_all_regions=False)

        return {'FINISHED'}


class Print3DCopyVolumeToClipboard(Operator):
    """Copy the volume value to clipboard"""
    bl_idname = "mesh.print3d_copy_volume_to_clipboard"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    volume = StringProperty(name="Copied to Clipboard (Volume):")

    def execute(self, context):
        volume = self.volume
        if volume:
            text_value = get_text_value(volume)
            context.window_manager.clipboard = text_value
            self.volume = text_value

        return {'FINISHED'}


class Print3DCopyAreaToClipboard(Operator):
    """Copy the area value to clipboard"""
    bl_idname = "mesh.print3d_copy_area_to_clipboard"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    area = StringProperty(name="Copied to Clipboard (Area):")

    def execute(self, context):
        area = self.area
        if area:
            text_value = get_text_value(area)
            context.window_manager.clipboard = text_value
            self.area = text_value

        return {'FINISHED'}


# ------
# Export

class Print3DExport(Operator):
    """Export active object using print3d settings"""
    bl_idname = "mesh.print3d_export"
    bl_label = "Print3D Export"

    def execute(self, context):
        scene = bpy.context.scene
        print_3d = scene.print_3d
        from . import export

        info = []
        ret = export.write_mesh(context, info, self.report)
        report.update(*info)

        if ret:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
