'''
Copyright (C) 2018 Jean Da Costa machado.
Jean3dimensional@gmail.com

Created by Jean Da Costa machado

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from .surface_particles import *
from mathutils import bvhtree
from . import ui
import traceback


def surface_snap(source_verts, tree):
    for vert in source_verts:
        final_co = None
        start = vert.co
        ray = vert.normal
        location1, normal, index, distance1 = tree.ray_cast(start, ray)
        location2, normal, index, distance2 = tree.ray_cast(start, -ray)
        location3, normal, index, distance3 = tree.find_nearest(vert.co)
        if location1 and location2:
            final_co = location2 if distance2 < distance1 else location1

        elif location1:
            final_co = location1
            if location3:
                if distance3 * 2 < distance1:
                    final_co = location3
        elif location2:
            final_co = location2
            if location3:
                if distance3 * 2 < distance2:
                    final_co = location3
        else:
            if location3:
                final_co = location3
        
        if final_co:
            vert.co = final_co


def triangle_quad_subdivide(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True, smooth=1)
    collapse_edges = set()
    for vert in bm.verts:
        if len(vert.link_edges) not in {5, 6}:
            continue
        if [len(face.verts) for face in vert.link_faces].count(3) == 1:
            for face in vert.link_faces:
                if len(face.verts) == 3:
                    for edge in face.edges:
                        if vert not in edge.verts:
                            collapse_edges.add(edge)

    bmesh.ops.collapse(bm, edges=list(collapse_edges))
    triangulate_faces = set()
    connect_verts = set()
    for vert in bm.verts:
        face_count = len(vert.link_faces)
        if face_count > 4:
            for face in vert.link_faces:
                triangulate_faces.add(face)
                for vert in face.verts:
                    if len(vert.link_edges) == 4:
                        connect_verts.add(vert)
        elif face_count == 3:
            for face in vert.link_faces:
                triangulate_faces.add(face)
                for vert in face.verts:
                    if len(vert.link_edges) in {3, 5}:
                        connect_verts.add(vert)

    bmesh.ops.connect_verts(bm, verts=list(connect_verts))
    # bmesh.ops.triangulate(bm, faces=list(triangulate_faces))
    bmesh.ops.join_triangles(bm, faces=bm.faces, angle_face_threshold=1.5, angle_shape_threshold=3.14)
    bmesh.ops.smooth_vert(bm, verts=bm.verts, use_axis_x=True, use_axis_y=True, use_axis_z=True, factor=1)

    bm.to_mesh(obj.data)


class ParticleTest(bpy.types.Operator):
    TAG_REGISTER = True
    bl_idname = "tesselator.remesh_particles"
    bl_label = "Particle Remesh"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    _timer = None
    _handle = None
    counter = 0
    bm = None
    tree = None
    initialized = False
    algorithm_steps = None
    solver = None

    resolution : bpy.props.FloatProperty(
        name="Resolution",
        description="The amount of particles in unmasked areas, (warning: Values above 200 may crash blender.)",
        min=0,
        default=60,
    )

    mask_resolution : bpy.props.FloatProperty(
        name="Mask Resolution",
        description="The amount of particles in masked areas, (warning: Values above 200 may crash blender.)",
        min=0,
        default=100,
    )

    predecimation : bpy.props.FloatProperty(
        name="Pre Decimation",
        description="simplify geometry before spawning the particles (low values makes pre-computation faster.)",
        min=0,
        max=1,
        default=0.1,
    )
    step_scale : bpy.props.FloatProperty(
        name="Step Scale",
        description="How fast the paticles move",
        min=0.0001,
        max=1,
        default=0.1,
    )
    subdivisions : bpy.props.IntProperty(
        name="Subdivisions",
        description="How many final subdivisions",
        default=2,
        min=0
    )
    steps : bpy.props.IntProperty(
        name="Relaxation Steps",
        description="The number of \"Smoothing\" steps.",
        default=25,
        min=0
    )
    seeds : bpy.props.IntProperty(
        name="Seeds",
        description="How many initial sample points to grow the whole mesh.",
        default=5,
        min=0
    )
    x_mirror : bpy.props.BoolProperty(
        name="X Mirror",
        description="Force symmetry around X axis. Disable if your object isn't near symmetric",
        default=True
    )
    use_gp : bpy.props.BoolProperty(
        name="Use grease pencil",
        description="Take grease pencil strokes as topology guides (it depends on the resolution to get good flow)"
    )
    allow_triangles : bpy.props.BoolProperty(
        name="Allow Triangles",
        description="Remesh with triangles and squares"
    )
    triangle_mode : bpy.props.BoolProperty(
        name="Pure Triangles",
        description="Remesh with triangles instead of squares"
    )
    particle_placement : bpy.props.EnumProperty(
        name="Particle Placement",
        description="How to place initial particles before relaxing it",
        items=[("INTEGER_LATTICE", "Integer Lattice", "Creates a uniform grid."),
               ("FAST_MARCHING", "Fast Marching", "Spread Particles following the curvature.")],
        default="FAST_MARCHING"
    )
    show_advanced : bpy.props.BoolProperty(
        name="Advanced Settings",
        description="Show advanced settigns."
    )

    def draw(self, context):
        return

    @classmethod
    def poll(cls, context):
        if context.active_object:
            if context.active_object.type == "MESH":
                return True

    def stepper(self, context, event):
        print("stepper")
        bpy.ops.object.transform_apply(scale=True)
        ui.feedback = ["Decimating domain."]
        yield {"RUNNING_MODAL"}
        yield {"RUNNING_MODAL"}

        self.bm = bmesh.new()
        self.bm.from_mesh(context.active_object.data)
        self.tree = bvhtree.BVHTree.FromBMesh(self.bm)
        print("Tree")

        mask_vg = context.active_object.vertex_groups.new()
        mask_layer = self.bm.verts.layers.paint_mask.verify()
        print('MASK')
        for vert in self.bm.verts:
            mask_vg.add([vert.index], vert[mask_layer], "REPLACE")
        context.active_object["Density Mask"] = mask_vg.name
        print("vg")

        md = context.active_object.modifiers.new(type="DECIMATE", name="Decimate")
        md.ratio = self.predecimation
        print("modifier apply")
        print(md)
        bpy.ops.object.modifier_apply(modifier=md.name)
        print("md")

        ui.feedback = ["Building Direction Field."]
        yield {"RUNNING_MODAL"}
        self.solver = ParticleManager(context.active_object)
        scale = max(context.active_object.dimensions)
        self.solver.min_resolution = scale / self.resolution
        self.solver.max_resolution = scale / self.mask_resolution
        print("field")

        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.solver.draw_obj, (), "WINDOW", "POST_VIEW")
        self.solver.build_field(context, self.use_gp, self.x_mirror)
        self.bm.verts.ensure_lookup_table()
        print("field")

        context.active_object.vertex_groups.remove(mask_vg)

        if self.triangle_mode:
            self.solver.triangle_mode = True
        self.bm.to_mesh(context.active_object.data)
        print("bm to mesh")

        if self.particle_placement == "FAST_MARCHING":
            new_particles = False
            if self.use_gp:
                new_particles = self.solver.initialize_particles_from_gp(self.resolution, context)
                if self.x_mirror:
                    self.solver.mirror_particles(any_side=True)
            if not new_particles:
                self.solver.initialize_from_features(self.bm.verts, self.resolution, self.seeds)
            while True:
                ui.feedback = ["Spreading particles.."]
                result = self.solver.spread_step()
                yield {"RUNNING_MODAL"}
                if not result:
                    break
            for i in range(2):
                self.solver.spread_step()


        elif self.particle_placement == "INTEGER_LATTICE":
            ui.feedback = ["Creating particles.."]
            yield {"RUNNING_MODAL"}
            self.solver.initialize_grid(self.bm.verts, self.resolution, self.x_mirror)

        elif self.particle_placement == "ANOTHER_MESH":
            objs = list(context.selected_objects)
            for obj in objs:
                if obj is not context.active_object:
                    break
            self.solver.initialize_from_verts(obj.data.vertices)
            if self.x_mirror:
                self.solver.mirror_particles()

        if self.x_mirror:
            self.solver.mirror_particles()

        for i in range(self.steps):
            self.solver.step(self.step_scale)
            ui.feedback = ["Relaxation step.",
                           str(int(i / self.steps * 100)) + "% Done.",
                           "Press Esc to stop."]
            yield {"RUNNING_MODAL"}

        ui.feedback = ["Extracting Mesh."]
        yield {"RUNNING_MODAL"}
        yield {"RUNNING_MODAL"}

        yield self.finish(context)

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode="OBJECT")
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.algorithm_steps = self.stepper(context, event)

        self.initialized = False
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        try:
            if event.type == "TIMER":
                context.area.tag_redraw()
                return next(self.algorithm_steps)

            if event.type == "ESC":
                return self.finish(context)

            return {"RUNNING_MODAL"}
        except:
            traceback.print_exc()
            ui.feedback = []
            context.window_manager.event_timer_remove(self._timer)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            self.report({"ERROR"}, message="Something went wrong, remeshing couldn't finish, open console for details.")
            return {"CANCELLED"}

    def finish(self, context):
        ui.feedback = []
        context.window_manager.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
        bm = self.solver.simplify_mesh(self.bm)

        for i in range(5):
            bmesh.ops.smooth_vert(bm, verts=bm.verts, use_axis_x=True, use_axis_y=True, use_axis_z=True, factor=0.5)
            surface_snap(bm.verts, self.tree)

        bm.to_mesh(context.active_object.data)
        new_obj = context.active_object

        for _ in range(self.subdivisions):
            if not self.triangle_mode:
                if self.allow_triangles:
                    triangle_quad_subdivide(new_obj)
                else:
                    md = new_obj.modifiers.new(type="SUBSURF", name="SUBSURF")
                    md.levels = 1
                    # md.subdivision_type = "SIMPLE"
                    bpy.ops.object.modifier_apply(modifier=md.name)
                surface_snap(new_obj.data.vertices, self.tree)
            else:
                bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
                surface_snap(bm.verts, self.tree)
                bmesh.ops.smooth_vert(bm, verts=bm.verts, use_axis_x=True, use_axis_y=True, use_axis_z=True, factor=1)

        if self.triangle_mode:
            surface_snap(bm.verts, self.tree)
            bm.to_mesh(new_obj.data)
        else:
            surface_snap(new_obj.data.vertices, self.tree)

        context.area.tag_redraw()
        return {"FINISHED"}
