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

feedback = []

class ShowAdvancedSettings(bpy.types.Operator):
    TAG_REGISTER = True
    bl_idname = "tesselator.show_advanced"
    bl_label = "Advanced Settings"
    bl_description = ""
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = context.scene.tesselator_addon_settings
        settings.show_advanced = not settings.show_advanced
        return {"FINISHED"}

class TesselatorSettings(bpy.types.PropertyGroup):
    TAG_REGISTER = True
    resolution : bpy.props.FloatProperty(
        name="Resolution",
        description="The amount of particles, (Caution: Values above 200 may crash blender.)",
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
        default=15,
        min=0
    )
    seeds : bpy.props.IntProperty(
        name="Seeds",
        description="How many initial sample points to grow the whole mesh (If no grease pencil be found)",
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
        description="Take grease pencil strokes as topology guides (it depends on the resolution to get good flow)",
        default=True
    )
    allow_triangles : bpy.props.BoolProperty(
        name="Quads and Triangles",
        description="Remesh mixing triangles and squares (better suitable for sculpting)"
    )
    triangle_mode : bpy.props.BoolProperty(
        name="Pure Triangles",
        description="Remesh with triangles instead of squares (Creates highly Smooth triangles)"
    )
    particle_placement : bpy.props.EnumProperty(
        name="Particle Placement",
        description="How to place initial particles before relaxing it",
        items=[("INTEGER_LATTICE", "Integer Lattice", "Creates a uniform grid."),
               ("FAST_MARCHING", "Fast Marching", "Spread Particles following the curvature."),
               ("ANOTHER_MESH", "Another Mesh", "Use vertices from another mesh as starting particles")],
        default="FAST_MARCHING"
    )
    show_advanced : bpy.props.BoolProperty(
        name="Advanced Settings",
        description="Show advanced settigns."
    )

def register():
    bpy.types.Scene.tesselator_addon_settings = bpy.props.PointerProperty(type=TesselatorSettings)
    pass


def unregister():
    del bpy.types.Scene.tesselator_addon_settings
    pass


class TesselatorPanel(bpy.types.Panel):
    TAG_REGISTER = True
    bl_idname = "tesselator.panel"
    bl_label = "Particle Remesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tesselator"

    @classmethod
    def poll(self, context):
        if context.active_object:
            if context.active_object.mode in {"OBJECT", "SCULPT"}:
                return context.active_object.type == "MESH"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.tesselator_addon_settings
        layout.label(text="Particle Remesh")

        if feedback:
            box = layout.box()
            for line in feedback:
                box.label(text=line)
            return

        op = layout.operator("tesselator.remesh_particles", icon="MOD_PARTICLES")
        col = layout.column(align=True)
        col.prop(settings, "resolution")
        col.prop(settings, "mask_resolution")
        col.prop(settings, "steps")
        col.prop(settings, "subdivisions")
        col.separator()
        col.prop(settings, "x_mirror", toggle=True,icon="MOD_MIRROR")
        col.prop(settings, "use_gp", toggle=True,icon="GREASEPENCIL")
        col.prop(settings, "triangle_mode", toggle=True,icon="MESH_DATA")
        col1 = col.column()
        if settings.triangle_mode:
            col1.enabled = False
        col1.prop(settings, "allow_triangles", toggle=True, icon="MOD_REMESH")

        box = col.box()
        box.operator("tesselator.show_advanced", emboss=False,
                     icon="TRIA_DOWN" if settings.show_advanced else "TRIA_RIGHT")
        if settings.show_advanced:
            box.prop(settings, "predecimation", slider=True)
            box.prop(settings, "step_scale", slider=True)
            col = box.column(align=True)
            col.label("Particle Placement")
            col.prop(settings, "particle_placement", text = "")
            if settings.particle_placement == "FAST_MARCHING":
                col.prop(settings, "seeds")

        op.resolution = settings.resolution
        op.mask_resolution = settings.mask_resolution
        op.predecimation = settings.predecimation
        op.subdivisions = settings.subdivisions
        op.steps = settings.steps
        op.step_scale = settings.step_scale
        op.x_mirror = settings.x_mirror
        op.use_gp = settings.use_gp
        op.allow_triangles = settings.allow_triangles
        op.triangle_mode = settings.triangle_mode
        op.seeds = settings.seeds
        op.particle_placement = settings.particle_placement
