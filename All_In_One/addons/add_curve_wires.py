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

#==============================================================================
# Ideas to expand/improve this addon:
#    - 'clean' the "use_mat" option. >> what to do if a material isn't found on
#        the second object or in selected faces; do nothing, give error, ignore
#        setting?
#    - option to assign the material of a face of ob1 to the connected wire.
#    - connect end points to objects (with hooks) and parent hooks to objects
#        (is more flexible then using objects directly)
#    - add hook in middle and contrain this to both objects/end hooks
#    - add goal weight 1 to end points and 0 to mid points for softbody
#    - choose a bevel object
#==============================================================================

bl_info = {
    "name": "Create wires",
    "author": "jasperge",
    "version": (0, 1),
    "blender": (2, 6, 4),
    "location": "View3D > Add > Curve ",
    "description": "Creates wires between two objects.",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame"
}


# Import modules.
import bpy
from bpy.props import (StringProperty,
                       IntProperty,
                       FloatProperty,
                       BoolProperty,
                       EnumProperty)
from mathutils import Vector
import random

"""

create_wires is a module to create wires between two object.

Usage:
    On both objects you have to select the faces to use. If you do not select
    faces it will use all faces of the object (which may result in weird
    connections). On these faces it selects two random points to connect
    the wire to. There are several settings to tweak the wires.

"""


def check_materials(ob1, ob2):
    """

    check_materials(ob1, ob2)

    Check if and which materials of ob1 are also on ob2.

        Parameters:
            ob1 - The first object.
            ob2 - The second object.

        Returns:
            A list with the material names that are both in ob1 and ob2.
            (An empty list if no matching materials are found.)

    """

    if len(ob1.material_slots) > 0:
        match_mats = [m.material for m in ob1.material_slots
                      if m.material in ob2.material_slots]
    else:
        match_mats = []

    return match_mats


def get_random_point(ob, self, material=None):
    """

    get_random_point(ob)

    Get a random point in space on the (selected) faces of an object.

        Parameters:
            ob - The object to work on.
            self - The class instance.
            material - A material.

        Returns:
            The coordinate of the random point in world space as a vector and
            the material of the face on which the point lies.

    """

    faces_opt = self.faces
    use_mat = self.use_mat
    mat_index = None

    if faces_opt == 'SELECTED':
        # Get the selected faces.
        faces = [f for f in ob.data.polygons if f.select]
    if faces_opt == 'ALL' or not faces:
        # If no faces are selected use all faces.
        faces = ob.data.polygons
    # Get a random face.
    face = faces[random.randrange(len(faces))]

    # If no material is passed, this means either we have a face on object 1
    # and want to pass the material of the face or we have a face on object 2
    # and no material was found on the face on object 1.
    if not material and use_mat == True:
        if len(ob.material_slots) > 0:
            mat_index = face.material_index
            material = ob.material_slots[mat_index].material

    # If a material is passed, this means we are on object 2 and have to get a
    # face which also has this material.
    if material and use_mat == True:
        # First check if the object has the passed material.
        if len(ob.material_slots) > 0:
            for slot in ob.material_slots:
                if slot.material == material:
                    # If the material is found on the object, check if the
                    # face has this material.
                    i = 1
                    while ob.material_slots[face.material_index].material != material:
                        face = faces[random.randrange(len(faces))]
                        i += 1
                        if i > 100: # Just to make sure we don't get stuck in this while loop.
                            #raise ValueError("Didn't find a face in object '%s' with material '%s'." % (ob.name, material.name))
                            break
        else:
            #raise ValueError("Didn't find a face in object '%s' with material '%s'." % (ob.name, material.name))
            pass

    vert1_index = face.vertices[0]    # Returns index number of vertex.
    # Get the two connected vertices.
    conn_verts = []
    for e in face.edge_keys:
        # edge_keys returns a list of tuples with the index numbers of the
        # vertices that are on the edges of the face.
        # e.g.: [(6, 7), (3, 7), (2, 3), (2, 6)]
        if vert1_index in e:
            # 1 - 0 = 1; 1 - 1 = 0
            conn_verts.append(e[1 - e.index(vert1_index)])
    vert2_index, vert3_index = conn_verts
    vert1 = ob.data.vertices[vert1_index]
    vert2 = ob.data.vertices[vert2_index]
    vert3 = ob.data.vertices[vert3_index]

    # Now create two vectors from vert1 to vert2 and vert3.
    face_vec1 = (vert2.co) - (vert1.co)
    face_vec2 = (vert3.co) - (vert1.co)
    # Get a random point on the face.
    random_point = vert1.co + ((random.random() * face_vec1)
                               + (random.random() * face_vec2))
    # Multiply the point coordinates by the world matrix of the object
    # to have them in world space instead of local space.
    wmtx = ob.matrix_world
    random_point = wmtx * random_point

    return random_point, material, mat_index


def wire_points(**kwargs):
    """

    wire_points(**kwargs)

    Creates one or more wires (bezier curves) between two points.

        Keyword arguments:
            start_point - Coordinates of start point.
                          Default is Vector((-1, 0, 0)).
            end_point - Coordinates of end point.
                        Default is Vector((1, 0, 0))
            start_drape - How much the curve starts hanging at the end points.
                          Default is 0.
            start_drape_random - How much the curve starts hanging randomly at the end points.
                                 Default is 0.
            drape - How much the midpoint hangs downwards.
                    Default is 0.
            drape_random - How much the midpoint hangs randomly downwards.
                           Default is 0.
            midpoint_u - The offset of the midpoint along the u 'axis'.
                         Default is 0.
            midpoint_random_u - The random offset of the midpoint along the u 'axis'.
                                Default is 0.
            midpoint_v - The offset of the midpoint along the v 'axis'.
                         Default is 0.
            midpoint_random_v - The random offset of the midpoint along the v 'axis'.
                                Default is 0.

        Returns:
            A list with lists of x,y,z coordinates for curve points, [[x,y,z],[x,y,z],...n]

    """

    # Pull out the variables.
    start_point = kwargs.setdefault("start_point", Vector((-1, 0, 0)))
    end_point = kwargs.setdefault("end_point", Vector((1, 0, 0)))
    start_drape = kwargs.setdefault("start_drape", 0)
    start_drape_random = kwargs.setdefault("start_drape_random", 0)
    drape = kwargs.setdefault("drape", 0)
    drape_random = kwargs.setdefault("drape_random", 0)
    midpoint_u = kwargs.setdefault("midpoint_u", 0)
    midpoint_random_u = kwargs.setdefault("midpoint_random_u", 0)
    midpoint_v = kwargs.setdefault("midpoint_v", 0)
    midpoint_random_v = kwargs.setdefault("midpoint_random_v", 0)

    # Calculate the middle point according to the settings:
    # drape, drape_random, midpoint_random_u, midpoint_random_v.
    # Get the vector from start_point to end_point.
    curve_vec = end_point - start_point
    # Initial mid_point, just directly inbetween start_point and end_point.
    mid_point = start_point + (curve_vec * .5)
    # Add drape and drape_random
    mid_point[2] += (-drape)    # drape, on z-axis
    mid_point[2] += (random.random() * -drape_random)   # drape_random, on z-axis
    # Calculate the vector perpendicular to curve_vec and the z-axis (up).
    curve_vec_norm = curve_vec.normalized() # Get normalized curve_vec.
    z_vec = Vector((0.0, 0.0, 1.0))         # Vector for z-axis.
    perp_vec = curve_vec_norm.cross(z_vec)  # Perpendicular vector is cross product.
    # Random value between -1.0 and 1.0.
    rand = (.5 - random.random()) * 2
    # Add offset in curve u axis.
    mid_point += curve_vec_norm * midpoint_u
    # Add random offset in curve u axis.
    mid_point += curve_vec_norm * rand * midpoint_random_u
    # Add offset in curve v axis.
    mid_point += perp_vec * midpoint_v
    # Add random offset in curve v axis.
    mid_point += perp_vec * rand * midpoint_random_v

    # Calculate the positions of the start_point_right_handle and the
    # end_point_left_handle according to start_drape and start_drape_random.
    start_point_right = start_point + (curve_vec * start_drape)
    start_point_right += (curve_vec * start_drape_random * random.random())
    end_point_left = end_point - (curve_vec * start_drape)
    end_point_left += - (curve_vec * start_drape_random * random.random())

    curve_points = [
                    start_point,
                    mid_point,
                    end_point,
                    start_point_right,
                    end_point_left,
                    ]

    return curve_points


def create_wire(curve_points, num, self, curve_mat, curve_object=None):

    """

    create_wire(curve_points, self, curve_object=None)

    Creates one or more wires (bezier curves) between two points.

        Arguments:
            curve_points - The points for the curve (should be 3 points).
            self - The class instance.
            curve_object - (optional) The curve object to add the spline to.

        Returns:
            The (newly created) wire object.

    """

    midpoint_tangent = self.midpoint_tangent
    assign_mats = self.assign_mats

    # Options to variables.
    name = "%s%.3d_crv" % (self.name, num + 1)
    if not name:
        name = "wire%.3d_crv" % num + 1

    # Create the wire curve.
    scene = bpy.context.scene
    if curve_object:
        new_curve = curve_object.data
    else:
        new_curve = bpy.data.curves.new(name, type='CURVE')
        new_curve.dimensions = '3D'
        new_curve.fill_mode = 'FULL'
    new_spline = new_curve.splines.new(type='BEZIER')

    # Create the spline from curve_points.
    new_spline.bezier_points.add(int(len(curve_points)) - 3)
    for i, p in enumerate(new_spline.bezier_points):
        p.co = curve_points[i]

    # Set the curve options.
    new_curve.resolution_u = self.wire_resolution
    new_curve.render_resolution_u = self.wire_render_resolution
    new_curve.bevel_depth = self.wire_bevel_depth
    new_curve.bevel_resolution = self.wire_bevel_resolution

    # Create an object with new_curve
    if not curve_object:
        new_obj = bpy.data.objects.new(name, new_curve)  # object
        scene.objects.link(new_obj)  # place in active scene

        # Assign material to the wire if 'assign_mats' is checked.
        # TODO: Add material to curve object if needed.
        if assign_mats:
            # Check if curve_object has materials.
            if len(new_obj.material_slots) > 0:
                # Check if it already has the material assigned.
                for slot in new_obj.material_slots:
                    if slot.material == curve_mat:
                        new_spline.material_index = curve_mat
            #if mat_index:
            #    new_spline.material_index = mat_index

        # First check if the object has the passed material.
        #if len(new_obj.material_slots) > 0:
            #for slot in new_obj.material_slots:
                #if slot.material == curve_mat:
                    # If the material is found on the object, check if the
                    # face has this material.

    else:
        new_obj = curve_object
    bpy.ops.object.select_all(action='DESELECT')
    new_obj.select = True  # set as selected
    scene.objects.active = new_obj  # set as active

    bezier_points = new_spline.bezier_points

    # Set the type of all the points' handles to 'AUTO'.
    for i, p in enumerate(bezier_points):
        bezier_points[i].handle_left_type = 'AUTO'
        bezier_points[i].handle_right_type = 'AUTO'

    # Set the type of the end points handles to 'FREE'
    # and change their position.
    bezier_points[0].handle_right_type = 'FREE'
    bezier_points[-1].handle_left_type = 'FREE'
    bezier_points[0].handle_right = curve_points[-2]
    bezier_points[-1].handle_left = curve_points[-1]

    # Change the tangent of the mid_point(s).
    # Get the midpoint(s) (in case there will be more in the future).
    midpoints = []
    for i in range(1, len(bezier_points) - 1):
        midpoints.append(bezier_points[i])
    for mp in midpoints:
        # Get the vectors from the midpoint to it's handles.
        mp_left_vec = mp.handle_left - mp.co
        mp_right_vec = mp.handle_right - mp.co
        # Set the handles to 'ALLIGNED'.
        mp.handle_left_type = 'ALIGNED'
        mp.handle_right_type = 'ALIGNED'
        # Set the handles according to midpoint_tangent.
        mp.handle_left = mp.co + mp_left_vec * midpoint_tangent
        mp.handle_right = mp.co + mp_right_vec * midpoint_tangent

    return new_obj


def main(context, self):

    """

    main(context, self)

    The main function of add_curve_wires. This handles the real creation of the wire(s).

        Arguments:
            context - The context.
            self - The class instance.

        Returns:
            A list of the created wire object(s).

    """

    # Get the selected objects.
    #try:
    # Make sure exactly TWO objects are selected.
    #    ob1, ob2 = bpy.context.selected_objects
    #except ValueError:
    #    raise ValueError("You have to select exactly TWO mesh objects.")
    if len(bpy.context.selected_objects) != 2:
        raise ValueError("You have to select exactly TWO mesh objects.")
    ob1 = bpy.context.active_object
    ob2 = [ob for ob in bpy.context.selected_objects if ob != ob1][0]
    # Make sure the objects are 'MESH' objects.
    if ob1.type != 'MESH' or ob2.type != 'MESH':
        raise TypeError("You have to select exactly two MESH objects.")

    # Get the options.
    num_wires = self.num_wires
    seed = self.seed
    one_object = self.one_object
    use_mat = self.use_mat
    start_drape = self.start_drape
    start_drape_random = self.start_drape_random
    drape = self.drape
    drape_random = self.drape_random
    midpoint_u = self.midpoint_u
    midpoint_random_u = self.midpoint_random_u
    midpoint_v = self.midpoint_v
    midpoint_random_v = self.midpoint_random_v

    # If use_mat, check if objects have matching materials.
    # If not, ignore this setting.
    #match_mats = check_materials(ob1, ob2)

    # Make num_wires amount of wires, so put this in a for loop.
    curve_object = None
    new_objects = []
    random.seed(seed)
    for i in range(num_wires):
        # Get the points for the curve.
        start_point, material, mat_index = get_random_point(ob1, self)
        curve_mat = material
        end_point, material, mat_index = get_random_point(ob2, self, material)
        curve_points = wire_points(
                                   start_point=start_point,
                                   end_point=end_point,
                                   start_drape=start_drape,
                                   start_drape_random=start_drape_random,
                                   drape=drape,
                                   drape_random=drape_random,
                                   midpoint_u=midpoint_u,
                                   midpoint_random_u=midpoint_random_u,
                                   midpoint_v=midpoint_v,
                                   midpoint_random_v=midpoint_random_v,
                                  )

        # Create the object.
        if self.one_object:
            curve_object = create_wire(
                                       curve_points,
                                       0,
                                       self,
                                       curve_mat,
                                       curve_object,
                                       )
        else:
            curve_object = create_wire(
                                       curve_points,
                                       i,
                                       self,
                                       curve_mat,
                                       )
        if not curve_object in new_objects:
            new_objects.append(curve_object)

    return new_objects


class Wires(bpy.types.Operator):
    """Add (a) wire(s) between the selected objects"""
    bl_idname = "curve.wires"
    bl_label = "Create wire(s)"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    def __init__(self):
        # Because creating a lot of wires can take some time and slow down the
        # viewport, set the initial amount of wires to 50 if it is higher.
        if self.num_wires > 50:
            self.num_wires = 50

    name = StringProperty(
                          name="Name",
                          description="The (base)name of the wire object(s)",
                          default="wire",
                          )
    seed = IntProperty(
                       name="Seed",
                       description="The seed to drive the random values",
                       default=2105,
                       min=1
                       )
    num_wires = IntProperty(
                            name="Amount",
                            description="The number of wires to create",
                            default=1,
                            min=1,
                            max=1000,
                            soft_max=100,
                           )
    one_object = BoolProperty(
                              name="One object",
                              description="Create the wires in one object instead of one object per wire",
                              default=True,
                              )
    assign_mats = BoolProperty(
                               name="Assign materials",
                               description="Assign the material from the connected face of the active object to the wire(s)",
                               default=False,
                               )
    faces_items = [
                   ("SELECTED", "Selected", "Use only the selected faces (all faces if nothing is selected)"),
                   ("ALL", "All", "Use all the faces of the object."),
                   ]
    faces = EnumProperty(
                         name="Use faces",
                         description="Choose which faces to use",
                         items=faces_items,
                         )
    use_mat = BoolProperty(
                           name="Use materials",
                           description="Connect the wire(s) to faces with the same material (if possible)",
                           default=False
                           )
    start_drape = FloatProperty(
                                name="Start drape",
                                description="How much the wire(s) start(s) hanging at the end points",
                                default=0.0,
                                min=-10.0,
                                max=10.0,
                                soft_min=0.0,
                                soft_max=0.5,
                                step=1,
                                )
    start_drape_random = FloatProperty(
                                 name="Random start drape",
                                 description="The amount of random start drape",
                                 default=0.0,
                                 min=-10.0,
                                 max=10.0,
                                 soft_min=0.0,
                                 soft_max=0.5,
                                 step=1,
                                 )
    drape = FloatProperty(
                          name="Drape",
                          description="The drape of the wire(s) (how much the wire(s) hang(s)",
                          default=1.0,
                          soft_min=-10.0,
                          soft_max=10.0,
                          step=10,
                          )
    drape_random = FloatProperty(
                                 name="Random drape",
                                 description="The amount of random drape",
                                 default=0.5,
                                 soft_min=-10.0,
                                 soft_max=10.0,
                                 step=1,
                                 )
    midpoint_tangent = FloatProperty(
                                     name="Tangent",
                                     description="The 'shallowness' of the curve of the midpoint",
                                     default=1.0,
                                     min=-10.0,
                                     max=10.0,
                                     soft_min=0.0,
                                     soft_max=2.0,
                                     step=1,
                                     )
    midpoint_u = FloatProperty(
                               name="Offset U",
                               description="The offset of the midpoint along the wire(s)",
                               default=0.0,
                               soft_min=-10.0,
                               soft_max=10.0,
                               step=1,
                               )
    midpoint_random_u = FloatProperty(
                                      name="Random U",
                                      description="The random offset of the midpoint along the wire(s)",
                                      default=0.0,
                                      min=0.0,
                                      soft_max=10.0,
                                      step=1,
                                      )
    midpoint_v = FloatProperty(
                               name="Offset V",
                               description="The offset of the midpoint perpendicular to the wire(s)",
                               default=0.0,
                               soft_min=-10.0,
                               soft_max=10.0,
                               step=1,
                               )
    midpoint_random_v = FloatProperty(
                                      name="Random V",
                                      description="The random offset of the midpoint perpendicular to the wire(s)",
                                      default=0.0,
                                      min=0.0,
                                      soft_max=10.0,
                                      step=1,
                                      )
    wire_bevel_depth = FloatProperty(
                                     name="Thickness",
                                     description="The thickness of the wire(s)",
                                     default=0.01,
                                     min=0.0001,
                                     soft_max=1.0,
                                     step=1,
                                     )
    wire_bevel_resolution = IntProperty(
                                        name="V resolution",
                                        description="The resolution of the cross section(s)",
                                        default=1,
                                        min=0,
                                        max=32,
                                        soft_max=10,
                                        )
    wire_resolution = IntProperty(
                                  name="Preview U",
                                  description="The preview resolution of the wire(s)",
                                  default=12,
                                  min=1,
                                  max=64,
                                  soft_max=32,
                                  )
    wire_render_resolution = IntProperty(
                                         name="Render U",
                                         description="The render resolution of the wire(s) (0 means: is the same as Preview U",
                                         default=0,
                                         min=0,
                                         max=64,
                                         soft_max=32,
                                         )

    # Draw
    def draw(self, context):
        layout = self.layout

        # Options
        box = layout.box()
        box.prop(self, 'name')
        box.prop(self, 'num_wires')
        box.prop(self, 'seed')
        if self.num_wires > 1:
            box.prop(self, 'one_object')
        #box.prop(self, 'assign_mats')
        box = layout.box()
        box.label(text="Connection options:")
        box.row().prop(self, 'faces', expand=True)
        box.prop(self, 'use_mat')
        box = layout.box()
        box.label(text="Endpoints settings:")
        box.prop(self, 'start_drape')
        box.prop(self, 'start_drape_random')
        box = layout.box()
        box.label(text="Midpoint settings:")
        box.prop(self, 'drape')
        box.prop(self, 'drape_random')
        box.prop(self, 'midpoint_tangent')
        box.prop(self, 'midpoint_u')
        box.prop(self, 'midpoint_random_u')
        box.prop(self, 'midpoint_v')
        box.prop(self, 'midpoint_random_v')
        box = layout.box()
        box.label(text="Resolution settings:")
        box.prop(self, 'wire_bevel_depth')
        box.prop(self, 'wire_bevel_resolution')
        box.prop(self, 'wire_resolution')
        box.prop(self, 'wire_render_resolution')

    # Poll
    @classmethod
    def poll(cls, context):
        return context.scene != None

    # Execute
    def execute(self, context):
        # Turn off undo. Copied this from curveaceous_galore. Don't know why this is.
        #bpy.context.user_preferences.edit.use_global_undo = True
        #bpy.context.user_preferences.edit.use_global_undo = False

        # Run main function.
        main(context, self)

        # Restore pre-operator undo state.
        #bpy.context.user_preferences.edit.use_global_undo = True

        return {'FINISHED'}

    # Invoke
    def invoke(self, context, event):
        self.execute(context)

        return {'FINISHED'}


# Register
def Wires_button(self, context):
    self.layout.operator(Wires.bl_idname, text="Create wire(s)", icon="PLUGIN")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_curve_add.append(Wires_button)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_curve_add.remove(Wires_button)


if __name__ == "__main__":
    register()
