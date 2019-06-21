# particle_tracer.py (c) 2011 Phil Cote (cotejrp1)
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

"""
How to use:
1.  Set up a scene object with an emitter particle system.
2.  Adjust for the unborn, alive, and dead particle lifecycle.
3.  Advance the timeline til the particles are in the desired position.
4.  MAKE SURE you select the emitter object AFTER you'vb
    advanced the timeline.
5.  In the tools menu in the 3D view, click "Make Curve" under
    the Particle Tracer Panel
6.  Adjust for what kind of what life state of particles to include
    as well as the curve thickness bevel.
"""

# BUG? : You do have to make sure you select the emitter object AFTER you've
# advanced the timeline.  If you don't, the current frame changes on you
# when you change the particle tracer options.

import bpy


bl_info = {
    'name': 'Particle Tracer',
    'author': 'Phil Cote, cotejrp1, (http://www.blenderaddons.com)',
    'version': (0, 1),
    "blender": (2, 5, 8),
    "api": 37702,
    'location': '',
    'description':
    'Makes curve based on particle locations at a point in time',
    'warning': '',  # used for warning icon and text in addons panel
    "category": "Learnbgame",
}


def get_particle_sys(ob):
    """
    Grab the first particle system available or None if there aren't any.
    """
    if ob is None:
        return None

    psys_list = [mod for mod in ob.modifiers if mod.type == 'PARTICLE_SYSTEM']
    if len(psys_list) == 0:
        return None

    psys = psys_list[0].particle_system
    return psys


def build_location_list(psys, include_alive, include_dead, include_unborn):
    """
    Build a flattened list of locations for each of the particles.
    Curve creation will act on this.
    Included particles dictated by the user choice
    of any combo of unborn, alive, or dead.
    """
    loc_list = []
    alive_list = []
    dead_list = []
    unborn_list = []

    def list_by_alive_state(psys, alive_arg):

        new_list = []
        for p in psys.particles:
            if p.alive_state == alive_arg:
                new_list.extend(list(p.location))

        return new_list

    alive_list = list_by_alive_state(psys, "ALIVE")
    dead_list = list_by_alive_state(psys, "DEAD")
    unborn_list = list_by_alive_state(psys, "UNBORN")

    if include_alive:
        loc_list = loc_list + alive_list
    if include_dead:
        loc_list = loc_list + dead_list
    if include_unborn:
        loc_list = loc_list + unborn_list

    return loc_list


class PTracerOp(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "curve.particle_tracer"
    bl_label = "Particle Tracer Options"
    bl_region_type = "VIEW_3D"
    bl_context = "tools"
    bl_options = {"REGISTER", "UNDO"}

    curve_name = bpy.props.StringProperty(name="Curve Name",
                                          default="ptracecurve")
    include_alive = bpy.props.BoolProperty(name="Alive Particles", default=True)
    include_dead = bpy.props.BoolProperty(name="Dead Particles", default=True)
    include_unborn = bpy.props.BoolProperty(name="Unborn Particles",
                                            default=True)
    thickness = bpy.props.FloatProperty(name="Thickness", min=0, max=1)

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        if get_particle_sys(ob) == None:
            return False
        return True

    def execute(self, context):

        ob = context.active_object
        psys = get_particle_sys(ob)
        loc_list = build_location_list(psys, self.include_alive,
                                       self.include_dead, self.include_unborn)

        crv = bpy.data.curves.new(self.curve_name, type="CURVE")
        spline = crv.splines.new(type="BEZIER")
        crv.bevel_depth = self.thickness

        pointCount = len(loc_list) / 3
        if pointCount > 0:
            spline.bezier_points.add(pointCount - 1)

        spline.bezier_points.foreach_set("co", loc_list)

        for point in spline.bezier_points:
            point.handle_left_type = "AUTO"
            point.handle_right_type = "AUTO"

        scn = context.scene
        crvob = bpy.data.objects.new(self.curve_name, crv)
        scn.objects.link(crvob)

        return {'FINISHED'}


class PTracerPanel(bpy.types.Panel):

    bl_label = "Particle Tracer"
    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        layout = self.layout
        layout.row().operator("curve.particle_tracer", text="Make Curve")


def register():
    bpy.utils.register_class(PTracerOp)
    bpy.utils.register_class(PTracerPanel)


def unregister():
    bpy.utils.unregister_class(PTracerOp)
    bpy.utils.unregister_class(PTracerPanel)


if __name__ == "__main__":
    register()
