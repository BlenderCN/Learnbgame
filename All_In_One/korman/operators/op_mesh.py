#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh
import math
import mathutils

class PlasmaMeshOperator:
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == "PLASMA_GAME"


class PlasmaAddLadderMeshOperator(PlasmaMeshOperator, bpy.types.Operator):
    bl_idname = "mesh.plasma_ladder_add"
    bl_label = "Add Ladder"
    bl_category = "Plasma"
    bl_description = "Adds a new Plasma Ladder"
    bl_options = {"REGISTER", "UNDO"}

    # Allows user to specify their own name stem
    ladder_name = bpy.props.StringProperty(name="Name",
                                           description="Ladder name stem",
                                           default="Ladder",
                                           options=set())
    # Basic stats
    ladder_height = bpy.props.FloatProperty(name="Height",
                                          description="Height of ladder in feet",
                                          min=6, max=1000, step=200, precision=0, default=6,
                                          unit="LENGTH", subtype="DISTANCE",
                                          options=set())
    ladder_width = bpy.props.FloatProperty(name="Width",
                                           description="Width of ladder in inches",
                                           min=30, max=42, step=100, precision=0, default=30,
                                           options=set())
    rung_height = bpy.props.FloatProperty(name="Rung height",
                                          description="Height of rungs in inches",
                                          min=1, max=6, step=100, precision=0, default=6,
                                          options=set())
    # Template generation
    gen_back_guide = bpy.props.BoolProperty(name="Ladder",
                                            description="Generates helper object where ladder back should be placed",
                                            default=True,
                                            options=set())
    gen_ground_guides = bpy.props.BoolProperty(name="Ground",
                                               description="Generates helper objects where ground should be placed",
                                               default=True,
                                               options=set())
    gen_rung_guides = bpy.props.BoolProperty(name="Rungs",
                                             description="Generates helper objects where rungs should be placed",
                                             default=True,
                                             options=set())
    rung_width_type = bpy.props.EnumProperty(name="Rung Width",
                                             description="Type of rungs to generate",
                                             items=[("FULL", "Full Width Rungs", "The rungs cross the entire width of the ladder"),
                                                    ("HALF", "Half Width Rungs", "The rungs only cross half the ladder's width, on the side where the avatar will contact them"),],
                                             default="FULL",
                                             options=set())
    # Game options
    has_upper_entry = bpy.props.BoolProperty(name="Has Upper Entry Point",
                                             description="Specifies whether the ladder has an upper entry",
                                             default=True,
                                             options=set())
    upper_entry_enabled = bpy.props.BoolProperty(name="Upper Entry Enabled",
                                                 description="Specifies whether the ladder's upper entry is enabled by default at Age start",
                                                 default=True,
                                                 options=set())
    has_lower_entry = bpy.props.BoolProperty(name="Has Lower Entry Point",
                                             description="Specifies whether the ladder has a lower entry",
                                             default=True,
                                             options=set())
    lower_entry_enabled = bpy.props.BoolProperty(name="Lower Entry Enabled",
                                                 description="Specifies whether the ladder's lower entry is enabled by default at Age start",
                                                 default=True,
                                                 options=set())

    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data

        if not space.local_view:
            box = layout.box()
            box.label("Ladder Name:")
            row = box.row()
            row.alert = not self.ladder_name
            row.prop(self, "ladder_name", text="")

            box = layout.box()
            box.label("Geometry:")
            row = box.row()
            row.alert = self.ladder_height % 2 != 0
            row.prop(self, "ladder_height")
            row = box.row()
            row.prop(self, "ladder_width")
            row = box.row()
            row.prop(self, "rung_height")

            box = layout.box()
            box.label("Template Guides:")
            col = box.column()
            col.prop(self, "gen_back_guide")
            col.prop(self, "gen_ground_guides")
            col.prop(self, "gen_rung_guides")
            if self.gen_rung_guides:
                col.separator()
                col.prop(self, "rung_width_type", text="")

            box = layout.box()
            row = box.row()
            col = row.column()
            col.label("Upper Entry:")
            col.row().prop(self, "has_upper_entry", text="Create")
            row = col.row()
            row.enabled = self.has_upper_entry
            row.prop(self, "upper_entry_enabled", text="Enabled")
            col.separator()
            col.label("Lower Entry:")
            col.row().prop(self, "has_lower_entry", text="Create")
            row = col.row()
            row.enabled = self.has_lower_entry
            row.prop(self, "lower_entry_enabled", text="Enabled")

        else:
            row = layout.row()
            row.label("Warning: Operator does not work in local view mode", icon="ERROR")

    def execute(self, context):
        if context.mode == "OBJECT":
            self.create_ladder_objects()
        else:
            self.report({"WARNING"}, "Ladder creation only valid in Object mode")
            return {"CANCELLED"}
        return {"FINISHED"}

    def create_guide_rungs(self):
        bpyscene = bpy.context.scene
        cursor_shift = mathutils.Matrix.Translation(bpy.context.scene.cursor_location)

        rung_height_ft = self.rung_height / 12
        rung_width_ft = self.ladder_width / 12

        if self.rung_width_type == "FULL":
            rung_width = rung_width_ft
            rung_yoffset = 0.0
        else:
            rung_width = rung_width_ft / 2
            rung_yoffset = rung_width_ft / 4

        rungs_scale = mathutils.Matrix(
            ((0.5, 0.0, 0.0),
             (0.0, rung_width, 0.0),
             (0.0, 0.0, rung_height_ft)))

        for rung_num in range(0, int(self.ladder_height)):
            side = "L" if (rung_num % 2) == 0 else "R"

            mesh = bpy.data.meshes.new("{}_Rung_{}_{}".format(self.name_stem, side, rung_num))
            rungs = bpy.data.objects.new("{}_Rung_{}_{}".format(self.name_stem, side, rung_num), mesh)
            rungs.hide_render = True
            rungs.draw_type = "BOUNDS"

            bpyscene.objects.link(rungs)
            bpyscene.objects.active = rungs
            rungs.select = True

            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=(1.0), matrix=rungs_scale)

            # Move each rung up, based on:
            # its place in the array, aligned to the top of the rung position, shifted up to start at the ladder's base
            if (rung_num % 2) == 0:
                rung_pos = mathutils.Matrix.Translation((0.5, -rung_yoffset, rung_num + (1.0 - rung_height_ft) + (rung_height_ft / 2)))
            else:
                rung_pos = mathutils.Matrix.Translation((0.5, rung_yoffset, rung_num + (1.0 - rung_height_ft) + (rung_height_ft / 2)))
            bmesh.ops.transform(bm, matrix=cursor_shift, space=rungs.matrix_world, verts=bm.verts)
            bmesh.ops.transform(bm, matrix=rung_pos, space=rungs.matrix_world, verts=bm.verts)
            bm.to_mesh(mesh)
            bm.free()

    def create_guide_back(self):
        bpyscene = bpy.context.scene
        cursor_shift = mathutils.Matrix.Translation(bpy.context.scene.cursor_location)

        # Create an empty mesh and the object.
        name = "{}_Back".format(self.name_stem)
        mesh = bpy.data.meshes.new(name)
        back = bpy.data.objects.new(name, mesh)
        back.hide_render = True
        back.draw_type = "BOUNDS"

        # Add the object into the scene.
        bpyscene.objects.link(back)
        bpyscene.objects.active = back
        back.select = True

        # Construct the bmesh and assign it to the blender mesh.
        bm = bmesh.new()
        ladder_scale = mathutils.Matrix(
            ((0.5, 0.0, 0.0),
             (0.0, self.ladder_width / 12, 0.0),
             (0.0, 0.0, self.ladder_height)))
        bmesh.ops.create_cube(bm, size=(1.0), matrix=ladder_scale)

        # Shift the ladder up so that its base is at the 3D cursor
        back_pos = mathutils.Matrix.Translation((0.0, 0.0, self.ladder_height / 2))
        bmesh.ops.transform(bm, matrix=cursor_shift, space=back.matrix_world, verts=bm.verts)
        bmesh.ops.transform(bm, matrix=back_pos, space=back.matrix_world, verts=bm.verts)
        bm.to_mesh(mesh)
        bm.free()

    def create_guide_ground(self):
        bpyscene = bpy.context.scene
        cursor_shift = mathutils.Matrix.Translation(bpy.context.scene.cursor_location)

        for pos in ("Upper", "Lower"):
            # Create an empty mesh and the object.
            name = "{}_Ground_{}".format(self.name_stem, pos)
            mesh = bpy.data.meshes.new(name)
            ground = bpy.data.objects.new(name, mesh)
            ground.hide_render = True
            ground.draw_type = "BOUNDS"

            # Add the object into the scene.
            bpyscene.objects.link(ground)
            bpyscene.objects.active = ground
            ground.select = True

            # Construct the bmesh and assign it to the blender mesh.
            bm = bmesh.new()
            ground_depth = 3.0
            ground_scale = mathutils.Matrix(
                ((ground_depth, 0.0, 0.0),
                 (0.0, self.ladder_width / 12, 0.0),
                 (0.0, 0.0, 0.5)))
            bmesh.ops.create_cube(bm, size=(1.0), matrix=ground_scale)

            if pos == "Upper":
                ground_pos = mathutils.Matrix.Translation((-(ground_depth / 2) + 0.25, 0.0, self.ladder_height + 0.25))
            else:
                ground_pos = mathutils.Matrix.Translation(((ground_depth / 2) + 0.25, 0.0, 0.25))
            bmesh.ops.transform(bm, matrix=cursor_shift, space=ground.matrix_world, verts=bm.verts)
            bmesh.ops.transform(bm, matrix=ground_pos, space=ground.matrix_world, verts=bm.verts)
            bm.to_mesh(mesh)
            bm.free()

    def create_upper_entry(self):
        bpyscene = bpy.context.scene
        cursor_shift = mathutils.Matrix.Translation(bpy.context.scene.cursor_location)

        # Create an empty mesh and the object.
        name = "{}_Entry_Upper".format(self.name_stem)
        mesh = bpy.data.meshes.new(name)
        upper_rgn = bpy.data.objects.new(name, mesh)
        upper_rgn.hide_render = True
        upper_rgn.draw_type = "WIRE"

        # Add the object into the scene.
        bpyscene.objects.link(upper_rgn)
        bpyscene.objects.active = upper_rgn
        upper_rgn.select = True
        upper_rgn.plasma_object.enabled = True

        # Construct the bmesh and assign it to the blender mesh.
        bm = bmesh.new()
        rgn_scale = mathutils.Matrix(
            ((self.ladder_width / 12, 0.0, 0.0),
             (0.0, 2.5, 0.0),
             (0.0, 0.0, 2.0)))
        bmesh.ops.create_cube(bm, size=(1.0), matrix=rgn_scale)

        rgn_pos = mathutils.Matrix.Translation((-1.80, 0.0, 1.5 + self.ladder_height))
        bmesh.ops.transform(bm, matrix=cursor_shift, space=upper_rgn.matrix_world, verts=bm.verts)
        bmesh.ops.transform(bm, matrix=rgn_pos, space=upper_rgn.matrix_world, verts=bm.verts)

        bm.to_mesh(mesh)
        bm.free()

        origin_to_bottom(upper_rgn)
        upper_rgn.rotation_euler[2] = math.radians(90.0)

        bpy.ops.object.plasma_modifier_add(types="laddermod")
        laddermod = upper_rgn.plasma_modifiers.laddermod
        laddermod.is_enabled = self.lower_entry_enabled
        laddermod.num_loops = (self.ladder_height - 6) / 2
        laddermod.direction = "DOWN"

    def create_lower_entry(self):
        bpyscene = bpy.context.scene
        cursor_shift = mathutils.Matrix.Translation(bpy.context.scene.cursor_location)

        # Create an empty mesh and the object.
        name = "{}_Entry_Lower".format(self.name_stem)
        mesh = bpy.data.meshes.new(name)
        lower_rgn = bpy.data.objects.new(name, mesh)
        lower_rgn.hide_render = True
        lower_rgn.draw_type = "WIRE"

        # Add the object into the scene.
        bpyscene.objects.link(lower_rgn)
        bpyscene.objects.active = lower_rgn
        lower_rgn.select = True
        lower_rgn.plasma_object.enabled = True

        # Construct the bmesh and assign it to the blender mesh.
        bm = bmesh.new()
        rgn_scale = mathutils.Matrix(
            ((self.ladder_width / 12, 0.0, 0.0),
             (0.0, 2.5, 0.0),
             (0.0, 0.0, 2.0)))
        bmesh.ops.create_cube(bm, size=(1.0), matrix=rgn_scale)

        rgn_pos = mathutils.Matrix.Translation((2.70, 0.0, 1.5))
        bmesh.ops.transform(bm, matrix=cursor_shift, space=lower_rgn.matrix_world, verts=bm.verts)
        bmesh.ops.transform(bm, matrix=rgn_pos, space=lower_rgn.matrix_world, verts=bm.verts)

        bm.to_mesh(mesh)
        bm.free()

        origin_to_bottom(lower_rgn)
        lower_rgn.rotation_euler[2] = math.radians(-90.0)

        bpy.ops.object.plasma_modifier_add(types="laddermod")
        laddermod = lower_rgn.plasma_modifiers.laddermod
        laddermod.is_enabled = self.lower_entry_enabled
        laddermod.num_loops = (self.ladder_height - 6) / 2
        laddermod.direction = "UP"

    def create_ladder_objects(self):
        for obj in bpy.data.objects:
            obj.select = False

        if self.gen_rung_guides:
            self.create_guide_rungs()
        if self.gen_back_guide:
            self.create_guide_back()
        if self.gen_ground_guides:
            self.create_guide_ground()

        bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")

        if self.has_upper_entry:
            self.create_upper_entry()
        if self.has_lower_entry:
            self.create_lower_entry()

        bpy.ops.group.create(name="LadderGroup")
        bpy.ops.group.objects_add_active()

    @property
    def name_stem(self):
        return self.ladder_name if self.ladder_name else "Ladder"

def origin_to_bottom(obj):
    # Modified from https://blender.stackexchange.com/a/42110/3055
    mw = obj.matrix_world
    local_verts = [mathutils.Vector(v[:]) for v in obj.bound_box]
    x, y, z = 0, 0, 0

    l = len(local_verts)
    y = sum((v.y for v in local_verts)) / l
    x = sum((v.x for v in local_verts)) / l
    z = min((v.z for v in local_verts))

    local_origin = mathutils.Vector((x, y, z))
    global_origin = mw * local_origin

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    for v in bm.verts:
        v.co = v.co - local_origin

    bm.to_mesh(obj.data)
    mw.translation = global_origin


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
