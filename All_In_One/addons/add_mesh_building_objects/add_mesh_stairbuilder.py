# Stairs and railing creator script for Blender
#
# Creates a straight-run staircase with railings and stringer
# All components are optional and can be turned on and off by setting e.g. makeTreads=True or makeTreads=False
# Current values assume 1 blender unit = 1 metre
#
# Stringer will rest on lower landing and hang from upper landing
# Railings start on the lowest step and end on the upper landing
#
# Note: I'm not sure how to use recalcNormals so not all normals points ouwards.
#       Perhaps someone else can contribute this.
#
#-----------------------------------------------------------
#
#   @todo:
#   - Join separate stringer objects and then clean up the mesh.
#   - Generate left/right posts/railings/retainers separately with
#       option to disable just the left/right.
#   - Add wall railing type as an option for left/right
#   - Add different rail styles (profiles).  Select with enum.
#   - Would like to add additional staircase types.
#       - "L" staircase
#       - "T" staircase
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Stairbuilder is for quick stair generation.
#  Copyright (C) 2010  Nick van Adium
#  Copyright (C) 2011  Paul Marshall
#  Copyright (C) 2017 Lawrence D'Oliveiro
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import math
import enum
from copy import \
    copy
import bpy
from bpy.props import \
    BoolProperty, \
    EnumProperty, \
    IntProperty, \
    FloatProperty
import mathutils
from mathutils.geometry import \
    intersect_line_plane, \
    intersect_line_line

#+
# Useful stuff
#-

# deg = math.pi / 180 # degrees/radians conversion factor # not needed
circle = 2 * math.pi # circles/radians conversion factor

vec = lambda x, y, z : mathutils.Vector([x, y, z])
  # save some extra brackets
z_rotation = lambda angle : mathutils.Matrix.Rotation(angle, 3, "Z")
  # all my rotation matrices are of this form

class EnumPropItems(enum.Enum) :
    "base class for enumerations that can be passed to Blender’s EnumProperty" \
    " to construct a menu of the enumeration values. Subclasses need only contain" \
    " one or more enumeration item definitions in the form\n" \
    "\n" \
    "    «name» = («title», «description»)\n" \
    "\n" \
    " in order for the all_items() method to return a tuple of tuples that can be" \
    " passed directly to EnumProperty."

    def __init__(self, label, description) :
        self._value_ = (label, description)
        self.label = label
        self.description = description
    #end __init__

    @classmethod
    def all_items(celf) :
        return \
            tuple((item.name, item.label, item.description) for item in celf.__members__.values())
    #end all_items

#end EnumPropItems

#+
# Building the parts
#-

class STAIRTYPE(EnumPropItems) :
    "overall types of stairs."
    FREESTANDING = ("Freestanding", "Generate a freestanding staircase.")
    HOUSED_OPEN = ("Housed-Open", "Generate a housed-open staircase.")
    BOX = ("Box", "Generate a box staircase.")
    CIRCULAR = ("Circular", "Generate a circular or spiral staircase.")
#end STAIRTYPE

class TREADTYPE(EnumPropItems) :
    "types of stair treads."
    CLASSIC = ("Classic", "Generate wooden style treads")
    BASIC_STEEL = ("Basic Steel", "Generate common steel style treads")
    BAR_1 = ("Bar 1", "Generate bar/slat steel treads")
    BAR_2 = ("Bar 2", "Generate bar-grating steel treads")
    BAR_3 = ("Bar 3", "Generate bar-support steel treads")
#end TREADTYPE

class FREESTANDING_STRINGERTYPE(EnumPropItems) :
    "types of stair stringers."
    CLASSIC = ("Classic", "Generate a classic style stringer")
    I_BEAM = ("I-Beam", "Generate a steel I-beam stringer")
#end FREESTANDING_STRINGERTYPE

class HOUSED_STRINGERTYPE(EnumPropItems) :
    "types of stair stringers."
    CLASSIC = ("Classic", "Generate a classic style stringer")
    I_BEAM = ("I-Beam", "Generate a steel I-beam stringer")
    C_BEAM = ("C-Beam", "Generate a C-channel style stringer")
#end HOUSED_STRINGERTYPE

class MeshMaker :
    "utility class for creating meshes given the verts and faces."

    def __init__(self, rise, run, nr_treads, rotation, sections_per_slice, do_left_side, do_right_side) :
        # rise -- height of each tread
        # run -- depth of each tread
        self.rise = rise
        self.run = run
        self.nr_treads = nr_treads
        self.rotation = rotation
        self.sections_per_slice = sections_per_slice
        self.do_left_side = do_left_side
        self.do_right_side = do_right_side
        self.stop = nr_treads * vec(run, 0, rise)
        self.slope = rise / run
        # identical quads for all objects which are parallelepipeds (except stringers and treads)
        self.ppd_faces = \
            [
                [1, 0, 2, 3],
                [0, 1, 5, 4],
                [2, 0, 4, 6],
                [4, 5, 7, 6],
                [3, 2, 6, 7],
                [1, 3, 7, 5],
            ]
        self.made_objects = []
    #end __init__

    def make_mesh(self, verts, faces, name, flip = False) :
        # MeshMaker, MeshMaker, make me a mesh...
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata \
          (
            verts,
            [],
            (lambda : faces, lambda : list(list(reversed(f)) for f in faces))[flip]()
          )
        mesh.use_auto_smooth = True
        mesh.update()
        mesh_obj = bpy.data.objects.new(name = name, object_data = mesh)
        bpy.context.scene.objects.link(mesh_obj)
        mesh_obj.location = (0, 0, 0) # relative to root
        self.made_objects.append(mesh_obj)
    #end make_mesh

    def make_ppd_mesh(self, verts, name) :
        # special case of make_mesh for parallelepiped shapes
        assert len(verts) == 8
        self.make_mesh(verts, self.ppd_faces, name)
    #end make_ppd_mesh

    def start_sectioned(self) :
        # returns an object suitable for constructing a mesh consisting
        # of a succession of quad cross-sections. Call the object’s
        # add_quad(«verts») method to add another cross section consisting
        # of four Vectors, and call finish(«name») to finish off the
        # mesh and create the object with the given name.

        class Sectioned :

            def __init__(self, parent) :
                self.parent = parent
                self.verts = []
                self.faces = [[0, 1, 3, 2]]
                self.nr_sections = 0
            #end __init__

            def add_quad(self, verts) :
                # positions of verts elements should be
                #   2 3
                #   0 1
                assert len(verts) == 4
                self.verts.extend(verts)
                if self.nr_sections != 0 :
                    # add side faces joining to previous section
                    k = self.nr_sections * 4
                    self.faces.extend \
                      (
                        [
                            [k, k + 1, k - 3, k - 4],
                            [k + 1, k + 3, k - 1, k - 3],
                            [k + 3, k + 2, k - 2, k - 1],
                            [k + 2, k, k - 4, k - 2],
                        ]
                      )
                #end if
                self.nr_sections += 1
            #end add_quad

            def finish(self, name) :
                assert self.nr_sections != 0
                # close off end
                k = self.nr_sections * 4
                self.faces.append([k - 3, k - 4, k - 2, k - 1])
                self.parent.make_mesh(self.verts, self.faces, name)
            #end finish

        #end Sectioned

    #begin start_sectioned
        return \
            Sectioned(self)
    #end start_sectioned

#end MeshMaker

def posts(mm, post_depth, post_width, tread_width, nr_posts, rail_height, rail_thickness) :
    "generates posts for the stairs. These are the vertical elements holding up the railings."
    p1 = vec(0, 0, rail_height - rail_thickness) # first post
    p2 = p1 + mm.stop  # last post
    # note that first and last posts are not counted in nr_posts
    post_spacing_x = (p2.x - p1.x) / (nr_posts + 1)
    for i in range(nr_posts + 2) :
        verts = []
        # meet bottom of rail
        delta_x = i * post_spacing_x
        x1 = p1.x + delta_x
        x2 = x1 + post_depth
        z1 = p1.z + delta_x * mm.slope
        z2 = p1.z + (delta_x + post_depth) * mm.slope
        verts.append(vec(x1, 0, z1))
        verts.append(vec(x2, 0, z2))
        #intersections with tread
        verts.append(vec(
                x1,
                0,
                math.floor(verts[0].x / mm.run) * mm.rise # meet top of tread
            ))
        verts.append(verts[2] + vec(post_depth, 0, 0))
        #inner face
        for j in range(4) :
            verts.append(verts[j] + vec(0, post_width, 0))
        #end for
        if mm.do_right_side :
            mm.make_ppd_mesh(verts, 'posts')
        #end if
        if mm.do_left_side :
            #make post on other side of steps as well
            for j in verts :
                j += vec(0, tread_width - post_width, 0)
            #end for
            mm.make_ppd_mesh(verts, 'posts')
        #end if
    #end for
#end posts

def posts_circular(mm, post_depth, post_width, nr_posts, rail_height, rail_thickness, inner_radius, outer_radius) :
    p1 = vec(0, 0, rail_height - rail_thickness) # top of first post
    p2 = p1 + vec(0, 0, mm.stop.z) # top of last post, ignoring rotation
    # note that first and last posts are not counted in nr_posts
    post_spacing = (p2 - p1) / (nr_posts + 1)
    post_spacing_angle = mm.rotation / (nr_posts + 1)
    offset_angle = - math.pi # so posts end up on same side as treads
    for i in range(nr_posts + 2) :
        for radius, do_side in ((outer_radius - post_width, mm.do_right_side), (inner_radius, mm.do_left_side)) :
            if do_side :
                slope_adjust = mm.rise * mm.nr_treads / mm.rotation * math.atan(post_depth / radius / 2)
                verts = []
                orient = z_rotation(i * post_spacing_angle + offset_angle)
                for width in (0, post_width) :
                    top1 = orient * (p1 + vec(0, radius + width, slope_adjust) + post_spacing * i)
                    bottom1 = vec \
                      (
                        top1.x,
                        top1.y,
                        math.floor(i / (nr_posts + 2) * mm.nr_treads) * mm.rise
                      )
                    top2 = orient * (p1 + vec(post_depth, radius + width, - slope_adjust) + post_spacing * i)
                    bottom2 = vec(top2.x, top2.y, bottom1.z)
                    verts.append(top1)
                    verts.append(top2)
                    verts.append(bottom1)
                    verts.append(bottom2)
                #end for
                mm.make_ppd_mesh(verts, 'posts')
            #end if
        #end for
    #end for
#end posts_circular

def railings(mm, rail_width, rail_thickness, rail_height, tread_toe, post_width, post_depth, tread_width) :
    "generates railings for the stairs. These go across the tops of the posts."
    start = vec(0, 0, rail_height - rail_thickness) # rail bottom start
    stop = mm.stop + vec(0, 0, rail_height - rail_thickness) # rail bottom stop
    # determine offset to include railing toe
    offset = vec(tread_toe, 0, tread_toe * mm.slope)
    verts = []
    verts.append(start - offset)
    verts.append(stop + offset + vec(post_depth, 0, post_depth * mm.slope))
    verts.append(start - offset + vec(0, rail_width, 0))
    verts.append(stop + offset + vec(post_depth, rail_width, post_depth * mm.slope))
    for j in range(4) :
        verts.append(verts[j] + vec(0, 0, rail_thickness))
    #end for
    # centre over posts
    for j in verts :
        j += vec(0, 0.5 * (- rail_width + post_width), 0)
    #end for
    if mm.do_right_side :
        mm.make_ppd_mesh(verts, 'rails')
    #end if
    if mm.do_left_side :
        # make rail on other side
        for j in verts :
            j += vec(0, tread_width - post_width, 0)
        #end for
        mm.make_ppd_mesh(verts, 'rails')
    #end if
#end railings

def railings_circular(mm, rail_width, rail_thickness, adjust_thickness, rail_height, tread_toe, post_width, post_depth, tread_width, inner_radius, outer_radius) :
    nr_sections = mm.sections_per_slice * mm.nr_treads
    offset_angle = - math.pi # so railings end up on same side as treads
    for radius, do_side in ((outer_radius, mm.do_right_side), (inner_radius, mm.do_left_side)) :
        if do_side :
            if adjust_thickness :
                slope_adjust = 1 / math.cos(math.atan(mm.rise * mm.nr_treads / (radius * mm.rotation)))
            else :
                slope_adjust = 1
            #end if
            start = vec(0, 0, rail_height - rail_thickness * slope_adjust) # rail bottom start
            section_verts = \
                [
                    start + vec(0, - rail_width / 2, 0),
                    start + vec(0, rail_width / 2, 0),
                    start + vec(0, - rail_width / 2, rail_thickness * slope_adjust),
                    start + vec(0, rail_width / 2, rail_thickness * slope_adjust),
                ]
            angle_adjust = tread_toe / radius
            total_rise = mm.rise * mm.nr_treads * (1 + 2 * angle_adjust / mm.rotation)
            rise_adjust = mm.rise * mm.nr_treads * angle_adjust / mm.rotation
            section_spacing_angle = (mm.rotation + 2 * angle_adjust) / nr_sections
            sections = mm.start_sectioned()
            for i in range(nr_sections + 1) :
                orient = z_rotation(i * section_spacing_angle + offset_angle - angle_adjust)
                sections.add_quad \
                  (
                    [
                            orient * (pt + vec(0, radius, 0))
                        +
                            vec(0, 0, i / nr_sections * total_rise - rise_adjust)
                        for pt in section_verts
                    ]
                  )
            #end for
            sections.finish("rails")
        #end if
    #end for
#end railings_circular

def retainers(mm, retainer_width, retainer_height, nr_retainers, post_width, tread_width, rail_height) :
    "generates retainers for the stairs. These are the additional pieces parallel" \
    " to, and below, the railings."
    retainer_spacing = rail_height / (nr_retainers + 1)
    for i in range(nr_retainers) :
        verts = []
        offset = (i + 1) * vec(0, 0, retainer_spacing)
        verts.append(offset)
        verts.append(mm.stop + offset)
        verts.append(offset + vec(0, retainer_width, 0))
        verts.append(mm.stop + offset + vec(0, retainer_width, 0))
        for j in range(4) :
            verts.append(verts[j] + vec(0, 0, retainer_height))
        #end for
        # centre in posts
        for j in verts :
            j += vec(0, 0.5 * (post_width - retainer_width), 0)
        #end for
        if mm.do_right_side :
            mm.make_ppd_mesh(verts, 'retainers')
        #end if
        if mm.do_left_side :
            # make retainer on other side
            for j in verts :
                j += vec(0, tread_width - post_width, 0)
            #end for
            mm.make_ppd_mesh(verts, 'retainers')
        #end if
    #end for
#end retainers

def retainers_circular(mm, retainer_width, retainer_height, nr_retainers, post_width, tread_width, rail_height, inner_radius, outer_radius) :
    retainer_spacing = rail_height / (nr_retainers + 1)
    nr_sections = mm.sections_per_slice * mm.nr_treads
    section_spacing_angle = mm.rotation / nr_sections
    offset_angle = - math.pi # so retainers end up on same side as treads
    for radius, do_side in ((outer_radius - post_width / 2, mm.do_right_side), (inner_radius + post_width / 2, mm.do_left_side)) :
        if do_side :
            for i in range(nr_retainers) :
                offset = (i + 1) * vec(0, 0, retainer_spacing)
                section_verts = \
                    [
                        offset,
                        offset + vec(0, retainer_width, 0),
                        offset + vec(0, 0, retainer_height),
                        offset + vec(0, retainer_width, retainer_height),
                    ]
                sections = mm.start_sectioned()
                for j in range(nr_sections + 1) :
                    orient = z_rotation(j * section_spacing_angle + offset_angle)
                    sections.add_quad \
                      (
                        [
                                orient * (pt + vec(0, radius, 0))
                            +
                                vec(0, 0, j / nr_sections * mm.rise * mm.nr_treads)
                            for pt in section_verts
                        ]
                      )
                #end for
                sections.finish("retainers")
            #end for
        #end if
    #end for
#end retainers_circular

def stringer(mm, stair_type, stringer_type, w, stringer_height, tread_height, tread_width, tread_toe, tread_overhang, tw, stringer_flange_thickness, tp, stringer_intersects_ground,
    nr_stringers = 1, distributed_stringers = False, notMulti = True) :
    "generates stringers for the stairs. These are the supports that go under" \
    " the stairs."

    if notMulti :
        stringer_width = w / 100
    else :
        stringer_width = (tread_width * (w / 100)) / nr_stringers
    #end if
    stringer_web_thickness = stringer_width * (tw / 100)
    stringer_flange_taper = 1 - tp / 100

    def freestanding_classic() :
        if distributed_stringers or nr_stringers == 1 :
            offset = tread_width / (nr_stringers + 1) - stringer_width / 2
        else :
            offset = 0
        #end if
        faces = \
            [
                [0, 1, 3, 2],
                [1, 5, 3],
                [3, 5, 4],
                [7, 6, 8, 9],
                [7, 9, 11],
                [9, 10, 11],
                [0, 2, 8, 6],
                [1, 0, 6, 7],
                [5, 1, 7, 11],
                [2, 3, 9, 8],
                [3, 4, 10, 9],
                [4, 5, 11, 10],
            ]
        for i in range(nr_stringers) :
            for j in range(mm.nr_treads) :
                verts = \
                    [
                        vec(0, offset, - mm.rise),
                        vec(mm.run, offset, - mm.rise),
                        vec(0, offset, - tread_height),
                        vec(mm.run, offset, - tread_height),
                        vec(mm.run, offset, 0),
                        vec(mm.run * 2, offset, 0),
                    ]
                for k in range(6) :
                    verts.append(verts[k] + vec(0, stringer_width, 0))
                #end for
                for k in verts :
                    k += j * vec(mm.run, 0, mm.rise)
                #end for
                mm.make_mesh(verts, faces, 'stringer')
            #end for
            if distributed_stringers or nr_stringers == 1 :
                offset += tread_width / (nr_stringers + 1)
            else :
                offset += (tread_width - stringer_width) / (nr_stringers - 1)
            #end if
        #end for
    #end freestanding_classic

    def housed_open_classic() :
        verts = \
            [
                vec(- tread_toe, - stringer_width, - mm.rise),
                vec(tread_height / mm.slope, - stringer_width, - mm.rise),
                vec(- tread_toe, - stringer_width, 0),
                vec
                  (
                    mm.nr_treads * mm.run,
                    - stringer_width,
                    (mm.nr_treads - 1) * mm.rise - tread_height
                  ),
                vec(mm.nr_treads * mm.run, - stringer_width, mm.nr_treads * mm.rise),
                vec
                  (
                    mm.nr_treads * mm.run - tread_toe,
                    - stringer_width,
                    mm.nr_treads * mm.rise
                  ),
            ]
        for i in range(6) :
            verts.append(verts[i] + vec(0, stringer_width, 0))
        #end for
        faces = \
            [
                [1, 0, 6, 7],
                [3, 1, 7, 9],
                [4, 3, 9, 10],
                [4, 10, 11, 5],
                [5, 11, 8, 2],
                [2, 8, 6, 0],
                [0, 1, 2],
                [2, 1, 3, 5],
                [3, 4, 5],
                [7, 6, 8],
                [7, 8, 11, 9],
                [10, 9, 11],
            ]
        mm.make_mesh(verts, faces, 'stringer')
        for i in verts :
            i += vec(0, stringer_width + tread_width, 0)
        #end for
        mm.make_mesh(verts, faces, 'stringer')
    #end housed_open_classic

    def i_beam() :
        mid = stringer_width / 2
        web = stringer_web_thickness / 2
        tread_step = tread_width / (nr_stringers + 1)
        # Bottom of the stringer:
        base_z = - mm.rise - tread_height - stringer_height
        # Top of the stringer:
        top_z = - mm.rise - tread_height
        # Vertical taper amount:
        taper = stringer_flange_thickness * stringer_flange_taper
        if distributed_stringers or nr_stringers == 1 :
            offset = tread_step - mid
        else :
            offset = 0
        #end if
        # taper < 100%:
        if stringer_flange_taper > 0 :
            faces = \
                [
                    [1, 0, 16, 17],
                    [2, 1, 17, 18],
                    [3, 2, 18, 19],
                    [4, 3, 19, 20],
                    [5, 4, 20, 21],
                    [6, 5, 21, 22],
                    [7, 6, 22, 23],
                    [8, 7, 23, 24],
                    [9, 8, 24, 25],
                    [10, 9, 25, 26],
                    [11, 10, 26, 27],
                    [12, 11, 27, 28],
                    [13, 12, 28, 29],
                    [14, 13, 29, 30],
                    [15, 14, 30, 31],
                    [0, 15, 31, 16],
                    [0, 1, 2, 15],
                    [2, 11, 14, 15],
                    [11, 12, 13, 14],
                    [2, 3, 10, 11],
                    [3, 4, 5, 6],
                    [3, 6, 7, 10],
                    [7, 8, 9, 10],
                    [17, 16, 31, 18],
                    [27, 18, 31, 30],
                    [28, 27, 30, 29],
                    [19, 18, 27, 26],
                    [20, 19, 22, 21],
                    [22, 19, 26, 23],
                    [24, 23, 26, 25],
                ]
            for i in range(nr_stringers) :
                verts = \
                    [
                        vec(0, offset, base_z),
                        vec(0, offset, base_z + taper),
                        vec(0, offset + (mid - web), base_z + stringer_flange_thickness),
                        vec(0, offset + (mid - web), top_z - stringer_flange_thickness),
                        vec(0, offset, top_z - taper),
                        vec(0, offset, top_z),
                        vec(0, offset + (mid - web), top_z),
                        vec(0, offset + (mid + web), top_z),
                        vec(0, offset + stringer_width, top_z),
                        vec(0, offset + stringer_width, top_z - taper),
                        vec(0, offset + (mid + web), top_z - stringer_flange_thickness),
                        vec(0, offset + (mid + web), base_z + stringer_flange_thickness),
                        vec(0, offset + stringer_width, base_z + taper),
                        vec(0, offset + stringer_width, base_z),
                        vec(0, offset + (mid + web), base_z),
                        vec(0, offset + (mid - web), base_z),
                    ]
                for j in range(16) :
                    verts.append(verts[j] + vec(mm.run * mm.nr_treads, 0, mm.rise * mm.nr_treads))
                #end for
                # If the bottom meets the ground:
                #   Bottom be flat with the xy plane, but shifted down.
                #   Either project onto the plane along a vector (hard) or use the built in
                #       interest found in mathutils.geometry (easy).  Using intersect:
                if stringer_intersects_ground :
                    for j in range(16) :
                        verts[j] = intersect_line_plane \
                          (
                            verts[j],
                            verts[j + 16],
                            vec(0, 0, top_z),
                            vec(0, 0, 1)
                          )
                    #end for
                #end if
                mm.make_mesh(verts, faces, 'stringer')
                if distributed_stringers or nr_stringers == 1 :
                    offset += tread_step
                else :
                    offset += (tread_width - stringer_width) / (nr_stringers - 1)
                #end if
            #end for
        # taper = 100%:
        else :
            faces = \
                [
                    [1, 0, 8, 9],
                    [2, 1, 9, 10],
                    [3, 2, 10, 11],
                    [4, 3, 11, 12],
                    [5, 4, 12, 13],
                    [6, 5, 13, 14],
                    [7, 6, 14, 15],
                    [0, 7, 15, 8],
                    [0, 1, 6, 7],
                    [1, 2, 5, 6],
                    [2, 3, 4, 5],
                    [9, 8, 15, 14],
                    [10, 9, 14, 13],
                    [11, 10, 13, 12],
                ]
            for i in range(nr_stringers) :
                verts = \
                    [
                        vec(0, offset, base_z),
                        vec(0, offset + (mid - web), base_z + stringer_flange_thickness),
                        vec(0, offset + (mid - web), top_z - stringer_flange_thickness),
                        vec(0, offset, top_z),
                        vec(0, offset + stringer_width, top_z),
                        vec(0, offset + (mid + web), top_z - stringer_flange_thickness),
                        vec(0, offset + (mid + web), base_z + stringer_flange_thickness),
                        vec(0, offset + stringer_width, base_z),
                    ]
                for j in range(8) :
                    verts.append(verts[j] + vec(mm.run * mm.nr_treads, 0, mm.rise * mm.nr_treads))
                #end for
                mm.make_mesh(verts, faces, 'stringer')
                offset += tread_step
            #end for
        #end if
    #end i_beam

    def housed_beam_common(i_beam) :
        # common mesh construction for both housed_i_beam and housed_c_beam
        verts = []
        web_normal = vec(mm.rise, 0, - mm.run).normalized() # perpendicular to slope of beam
        web_height = vec(mm.run + tread_toe, 0, - tread_height).project(web_normal).length
        flange_y = (stringer_width - stringer_web_thickness) / 2
          # depth of flange
        outer = - tread_overhang - stringer_web_thickness - flange_y
          # outer side of left beam
        # Upper-Outer flange:
        # positions of following vertices (outer part of flange):
        #                            6   5
        #
        #                            3   4
        #
        #
        #                           14  13
        #
        # 7                         11  12
        #    2
        #
        #           15
        #               10
        #
        # 0  1       8   9
        verts.extend \
          (
            [
                vec(- tread_toe - stringer_flange_thickness, outer, - mm.rise),
                vec(- tread_toe, outer, - mm.rise),
                vec(- tread_toe, outer, 0),
                vec
                  (
                    mm.run * (mm.nr_treads - 1) - tread_toe,
                    outer,
                    mm.rise * (mm.nr_treads - 1)
                  ),
                vec
                  (
                    mm.run * mm.nr_treads,
                    outer,
                    mm.rise * (mm.nr_treads - 1)
                  ),
                vec
                  (
                    mm.run * mm.nr_treads,
                    outer,
                    mm.rise * (mm.nr_treads - 1) + stringer_flange_thickness
                  ),
                vec
                  (
                    mm.run * (mm.nr_treads - 1) - tread_toe,
                    outer,
                    mm.rise * (mm.nr_treads - 1) + stringer_flange_thickness
                  ),
                vec
                  (
                    - tread_toe - stringer_flange_thickness,
                    outer,
                    stringer_flange_thickness - stringer_flange_thickness * mm.slope
                      # adjust vertical point placement for slope
                  ),
            ]
          )
        # Lower-Outer flange:
        verts.extend \
          (
            [
                verts[0] + vec(stringer_flange_thickness + web_height, 0, 0),
                verts[1] + vec(stringer_flange_thickness + web_height, 0, 0),
            ]
          )
        verts.extend \
          (
            [
                intersect_line_line
                  (
                    verts[9],
                    verts[9] - vec(0, 0, 1), # straight up from verts[9]
                    vec(mm.run, 0, - tread_height - stringer_flange_thickness),
                    vec(mm.run * 2, 0, mm.rise - tread_height - stringer_flange_thickness)
                      # forward from bottom of where horizontal flange would go
                )[0],
                vec
                  (
                    mm.run * mm.nr_treads - (web_height - tread_height) / mm.slope,
                    outer,
                    mm.rise * (mm.nr_treads - 1) - (web_height + stringer_flange_thickness)
                      # same as z-coord of following vert!
                  ),
                verts[4] - vec(0, 0, stringer_flange_thickness + web_height),
                verts[5] - vec(0, 0, stringer_flange_thickness + web_height),
            ]
          )
        verts.extend \
          (
            [
                verts[11] + vec(0, 0, stringer_flange_thickness),
                intersect_line_line
                  (
                    verts[8],
                    verts[8] - vec(0, 0, 1), # straight down(?) from verts[8]
                    vec(mm.run, 0, - tread_height),
                    vec(mm.run * 2, 0, mm.rise - tread_height)
                  )[0],
            ]
          )
        # Outer web: (interior corners of flange)
        # Positions of following vertices:
        #
        #
        #                          22  21
        #
        #
        #                          19  20
        #
        #
        #
        #
        #
        #    23
        #            18
        #
        #    16      17
        for i in [1, 8, 15, 14, 13, 4, 3, 2] :
            verts.append(verts[i] + vec(0, flange_y, 0))
        #end for
        if i_beam :
            # Upper-Inner flange and lower-inner flange:
            # Positions of following vertices (outer part of flange):
            #                            30  29
            #
            #                            27  28
            #
            #
            #                            38  37
            #
            # 31                         35  36
            #     26
            #
            #            39
            #                34
            #
            # 24  25     32  33
            for i in range(16) :
                verts.append(verts[i] + vec(0, stringer_width, 0))
            #end for
            # Inner web:
            # Positions of following vertices:
            #
            #
            #                          46  45
            #
            #
            #                          43  44
            #
            #
            #
            #
            #
            #    47
            #            42
            #
            #    40      41
            for i in range(8) :
                verts.append(verts[i + 16] + vec(0, stringer_web_thickness, 0))
            #end for
        #end if
        # Outer corner nodes:
        # Positions of following vertices (housed I-beam):
        #                          50  51
        #
        #
        #
        #
        #                          54  55
        #
        # 49
        #              53
        #
        # 48           52
        #
        # or (housed C-beam):
        #                          26  27
        #
        #
        #
        #
        #                          29  28
        #
        # 25
        #              30
        #
        # 24           31
        if i_beam :
            for i in [0, 7, 6, 5, 9, 10, 11, 12] :
                verts.append(verts[i] + vec(0, flange_y + (stringer_web_thickness, 0)[i_beam], 0))
            #end for
            # Outer corner nodes again:
            # Positions of following vertices:
            #                          58  59
            #
            #
            #
            #
            #                          62  63
            #
            # 57
            #              61
            #
            # 56           60
            for i in range(8) :
                verts.append(verts[i + 48] + vec(0, stringer_web_thickness, 0))
            #end for
        else :
            for i in [0, 7, 6, 5, 12, 11, 10, 9] :
                verts.append(verts[i] + vec(0, flange_y + (stringer_web_thickness, 0)[i_beam], 0))
            #end for
        #end if
        faces = \
            [
                [1, 0, 7, 2],
                [3, 2, 7, 6],
                [4, 3, 6, 5],
                [1, 2, 23, 16],
                [2, 3, 22, 23],
                [3, 4, 21, 22],
                [17, 16, 23, 18],
                [19, 18, 23, 22],
                [20, 19, 22, 21],
                [8, 17, 18, 15],
                [15, 18, 19, 14],
                [14, 19, 20, 13],
                [9, 8, 15, 10],
                [11, 10, 15, 14],
                [12, 11, 14, 13],
            ]
        if i_beam :
            faces.extend \
              (
                [
                    [9, 10, 53, 52],
                    [10, 11, 54, 53],
                    [11, 12, 55, 54],
                    [52, 53, 61, 60],
                    [53, 54, 62, 61],
                    [54, 55, 63, 62],
                    [60, 61, 34, 33],
                    [61, 62, 35, 34],
                    [62, 63, 36, 35],
                    [32, 33, 34, 39],
                    [34, 35, 38, 39],
                    [35, 36, 37, 38],
                    [41, 32, 39, 42],
                    [42, 39, 38, 43],
                    [43, 38, 37, 44],
                    [40, 41, 42, 47],
                    [42, 43, 46, 47],
                    [43, 44, 45, 46],
                    [26, 25, 40, 47],
                    [27, 26, 47, 46],
                    [28, 27, 46, 45],
                    [24, 25, 26, 31],
                    [26, 27, 30, 31],
                    [27, 28, 29, 30],
                    [24, 31, 57, 56],
                    [31, 30, 58, 57],
                    [30, 29, 59, 58],
                    [49, 48, 56, 57],
                    [50, 49, 57, 58],
                    [51, 50, 58, 59],

                    [7, 0, 48, 49],
                    [6, 7, 49, 50],
                    [5, 6, 50, 51],

                    [16, 40, 56, 48],
                    [25, 24, 56, 40],
                    [16, 17, 41, 40],
                    [8, 9, 52, 17],
                    [17, 52, 60, 41],
                    [33, 32, 41, 60],
                    [12, 13, 20, 55],
                    [20, 44, 63, 55],
                    [44, 37, 36, 63],
                    [0, 1, 16, 48],
                    [20, 21, 45, 44],
                    #[28, 29, 51, 21],
                    [21, 51, 59, 45],
                    [28, 45, 59, 29],
                    [4, 5, 51, 21],
                ]
              )
        else :
            faces.extend \
              (
                [
                    [0, 24, 25, 7],
                    [7, 25, 26, 6],
                    [6, 26, 27, 5],

                    [31, 9, 10, 30],
                    [30, 10, 11, 29],
                    [29, 11, 12, 28],
                    [25, 24, 31, 30],
                    [26, 25, 30, 29],
                    [27, 26, 29, 28],
                    [0, 1, 16, 24],
                    [24, 16, 17, 31],
                    [8, 9, 31, 17],
                    [4, 5, 27, 21],
                    [20, 21, 27, 28],
                    [12, 13, 20, 28],
                ]
              )
        #end if
        return \
            verts, faces, outer, flange_y
    #end housed_beam_common

    def housed_i_beam() :
        verts, faces = housed_beam_common(True)[:2]
        mm.make_mesh(verts, faces, 'stringer', flip = True)
        for i in verts :
            i += vec(0, tread_width + stringer_web_thickness, 0)
        #end for
        mm.make_mesh(verts, faces, 'stringer', flip = True)
    #end housed_i_beam

    def housed_c_beam() :
        verts, faces, outer, flange_y = housed_beam_common(False)
        mm.make_mesh(verts, faces, 'stringer', flip = True)
        # flip the flange around
        for i in range(16) :
            verts[i] += vec(0, - outer * 2, 0)
        #end for
        for i in range(8) :
            verts[i + 16] += vec(0, (- outer - flange_y) * 2, 0)
        #end for
        for i in verts :
            i += vec(0, tread_overhang * 2 + tread_width, 0)
        #end for
        mm.make_mesh(verts, faces, 'stringer', flip = False)
    #end housed_c_beam

    def box() :
        h = - tread_height #height of top section
        for i in range(mm.nr_treads) :
            verts = []
            verts.append(vec((i + 1) * mm.run, 0, - mm.rise))
            verts.append(vec(i * mm.run, 0, - mm.rise))
            verts.append(vec((i + 1) * mm.run, 0, h + i * mm.rise))
            verts.append(vec(i * mm.run, 0, h + i * mm.rise))
            for j in range(4) :
                verts.append(verts[j] + vec(0, tread_width, 0))
            #end for
            mm.make_ppd_mesh(verts, 'stringer')
        #end for
    #end box

    def circular() :
        if distributed_stringers or nr_stringers == 1 :
            offset = tread_width / (nr_stringers + 1) - stringer_width / 2
        else :
            offset = 0
        #end if
        for s in range(nr_stringers) :
            base = tread_overhang + offset
            start = \
                [
                    vec(0, - base, - tread_height),
                    vec(0, - base, - tread_height - mm.rise),
                    vec(0, - base - stringer_width, - tread_height),
                    vec(0, - base - stringer_width, - tread_height - mm.rise),
                ]
            tread_arc = mm.rotation / mm.nr_treads
            for i in range(mm.nr_treads) :
                verts = []
                faces = [[0, 1, 3, 2]]
                tread_angle = z_rotation(tread_arc * i)
                for j in range(4) :
                    verts.append(tread_angle * start[j] + vec(0, 0, mm.rise * i))
                #end for
                for j in range(mm.sections_per_slice) :
                    k = j * 4 + 4
                    faces.extend \
                      (
                        [
                            [k, k + 1, k - 3, k - 4],
                            [k + 1, k + 3, k - 1, k - 3],
                            [k - 2, k - 1, k + 3, k + 2],
                            [k, k - 4, k - 2, k + 2],
                        ]
                      )
                    rot = z_rotation(tread_arc * (j + 1) / mm.sections_per_slice + tread_arc * i)
                    for v in start :
                        verts.append(rot * v + vec(0, 0, mm.rise * i))
                    #end for
                #end for
                if i + 1 < mm.nr_treads :
                    # part that overlaps stringer for next tread
                    for j in range(mm.sections_per_slice - 1) :
                        k = (j + mm.sections_per_slice) * 4 + 4
                        faces.extend \
                          (
                            [
                                [k, k + 1, k - 3, k - 4],
                                [k + 1, k + 3, k - 1, k - 3],
                                [k - 2, k - 1, k + 3, k + 2],
                                [k, k - 4, k - 2, k + 2],
                            ]
                          )
                        rot = z_rotation \
                          (
                                tread_arc * (j + mm.sections_per_slice + 1) / mm.sections_per_slice
                            +
                                tread_arc * i
                          )
                        for v in range(4) :
                            if v in [1, 3] :
                                incline = mm.rise * i + mm.rise / mm.sections_per_slice * (j + 1)
                                verts.append(rot * start[v] + vec(0, 0, incline))
                            else :
                                verts.append(rot * start[v] + vec(0, 0, mm.rise * i))
                            #end if
                        #end for
                    #end for
                    # pointy end
                    j = mm.sections_per_slice - 1
                    k = (j + mm.sections_per_slice) * 4 + 4
                    faces.extend \
                      (
                        [
                            [k, k - 3, k - 4],
                            [k, k + 1, k - 1, k - 3],
                            [k - 2, k - 1, k + 1],
                            [k, k - 4, k - 2, k + 1],
                        ]
                      )
                    rot = z_rotation \
                      (
                            tread_arc * (j + mm.sections_per_slice + 1) / mm.sections_per_slice
                        +
                            tread_arc * i
                      )
                    verts.extend \
                      (
                        [
                            rot * start[0] + vec(0, 0, mm.rise * i),
                            rot * start[2] + vec(0, 0, mm.rise * i),
                        ]
                      )
                else :
                    # close off end
                    k = mm.sections_per_slice * 4 + 4
                    faces.append([k - 3, k - 4, k - 2, k - 1])
                #end if
                mm.make_mesh(verts, faces, 'stringer')
            #end for
            if distributed_stringers or nr_stringers == 1 :
                offset += tread_width / (nr_stringers + 1)
            else :
                offset += (tread_width - stringer_width) / (nr_stringers - 1)
            #end if
        #end for
    #end circular

#begin stringer
    if stair_type == STAIRTYPE.FREESTANDING :
        if stringer_type == FREESTANDING_STRINGERTYPE.CLASSIC :
            freestanding_classic()
        elif stringer_type == FREESTANDING_STRINGERTYPE.I_BEAM :
            i_beam()
        #end if
    elif stair_type == STAIRTYPE.HOUSED_OPEN :
        if stringer_type == HOUSED_STRINGERTYPE.CLASSIC :
            housed_open_classic()
        elif stringer_type == HOUSED_STRINGERTYPE.I_BEAM :
            housed_i_beam()
        elif stringer_type == HOUSED_STRINGERTYPE.C_BEAM :
            housed_c_beam()
        #end if
    elif stair_type == STAIRTYPE.BOX :
        box()
    elif stair_type == STAIRTYPE.CIRCULAR :
        circular()
    #end if
#end stringer

def treads(mm, stair_type, tread_type, tread_width, tread_height, tread_toe, tread_side_overhang, tread_metal_thickness, nr_tread_sections, spacing, nr_cross_sections) :
    "generates treads for non-circular stairs."

    if nr_tread_sections != 1 and tread_type not in [TREADTYPE.BAR_2, TREADTYPE.BAR_3] :
        section_spacing = (mm.run + tread_toe) * (spacing / 100) / (nr_tread_sections - 1)
          # spacing between sections (% of depth)
    elif tread_type in [TREADTYPE.BAR_2, TREADTYPE.BAR_3] :
        section_spacing = spacing / 100 # keep % value
    else :
        section_spacing = 0
    #end if

    # Setup the coordinates:
    treads_verts = []
    bars_verts = []
    crosses_verts = []
    cross_spacing = 0
    cross_width = 0
    section_depth = 0
    section_offset = 0
    assert stair_type in [STAIRTYPE.FREESTANDING, STAIRTYPE.HOUSED_OPEN, STAIRTYPE.BOX]

    def make_treads_verts() :
        # calculates coordinates for the pieces of the treads.
        nonlocal section_spacing, section_offset, cross_spacing, cross_width, section_depth
        if tread_type == TREADTYPE.CLASSIC :
            treads_verts.extend \
              (
                [
                    vec(mm.run, - tread_side_overhang, 0),
                    vec(- tread_toe, - tread_side_overhang, 0),
                    vec(mm.run, tread_width + tread_side_overhang, 0),
                    vec(- tread_toe, tread_width + tread_side_overhang, 0),
                ]
              )
            for i in range(4) :
                treads_verts.append(treads_verts[i] + vec(0, 0, - tread_height))
            #end for
        elif tread_type == TREADTYPE.BASIC_STEEL :
            # sequence of C-beam sections without crossbars
            section_depth = \
                (
                        (mm.run + tread_toe - (nr_tread_sections - 1) * section_spacing)
                    /
                        nr_tread_sections
                )
            end_x = section_depth - tread_toe # end of first section
            # Positions of following vertices:
            # 7                   6
            #
            #      2        3
            #
            # 0    1        4     5
            treads_verts.extend \
              (
                [
                    vec(- tread_toe, - tread_side_overhang, - tread_height),
                    vec
                      (
                        tread_metal_thickness - tread_toe,
                        - tread_side_overhang,
                        - tread_height
                      ),
                    vec
                      (
                        tread_metal_thickness - tread_toe,
                        - tread_side_overhang,
                        - tread_metal_thickness
                      ),
                    vec
                      (
                        end_x - tread_metal_thickness,
                        - tread_side_overhang,
                        - tread_metal_thickness
                      ),
                    vec
                      (
                        end_x - tread_metal_thickness,
                        - tread_side_overhang,
                        - tread_height
                      ),
                    vec(end_x, - tread_side_overhang, - tread_height),
                    vec(end_x, - tread_side_overhang, 0),
                    vec(- tread_toe, - tread_side_overhang, 0),
                ]
              )
            for i in range(8) :
                treads_verts.append \
                  (
                    treads_verts[i] + vec(0, tread_width + 2 * tread_side_overhang, 0)
                  )
            #end for
        elif tread_type in [TREADTYPE.BAR_1, TREADTYPE.BAR_2, TREADTYPE.BAR_3] :
            # These ones have crossbars
            # Frame:
            # Positions of following vertices:
            # at right edge:
            # 2             3
            # 0             1
            # inset by tread_metal_thickness:
            #    6       7
            #    4       5
            # (relative positions flipped on other side.)
            treads_verts.extend \
              ( # outer right edge of frame
                [
                    vec(- tread_toe, - tread_side_overhang, - tread_height),
                    vec(mm.run, - tread_side_overhang, - tread_height),
                    vec(- tread_toe, - tread_side_overhang, 0),
                    vec(mm.run, - tread_side_overhang, 0),
                ]
              )
            for i in range(4) :
                # inset right edge of frame
                if i % 2 == 0 :
                    treads_verts.append \
                      (
                        treads_verts[i] + vec(tread_metal_thickness, tread_metal_thickness, 0)
                      )
                else :
                    treads_verts.append \
                      (
                        treads_verts[i] + vec(- tread_metal_thickness, tread_metal_thickness, 0)
                      )
                #end if
            #end for
            for i in range(4) :
                # outer left edge of frame
                treads_verts.append(treads_verts[i] + vec(0, tread_width + tread_side_overhang, 0))
            #end for
            for i in range(4) :
                # inset left edge of frame
                treads_verts.append \
                  (
                        treads_verts[i + 4]
                    +
                        vec(0, tread_width + tread_side_overhang - 2 * tread_metal_thickness, 0)
                  )
            #end for
            # Tread sections:
            if tread_type == TREADTYPE.BAR_1 :
                section_offset = tread_metal_thickness * math.sqrt(0.5)
                topset = tread_height - section_offset
                section_spacing = \
                    (
                            (
                                (mm.run + tread_toe - 2 * tread_metal_thickness)
                            -
                                (section_offset * nr_tread_sections + topset)
                            )
                        /
                            (nr_tread_sections + 1)
                    )
                base_x = - tread_toe + section_spacing + tread_metal_thickness
                bars_verts.extend \
                  ( # left face of tread bar
                    [
                        vec
                          (
                            base_x + section_offset,
                            tread_metal_thickness - tread_side_overhang,
                            - tread_height
                          ),
                        vec
                          (
                            base_x,
                            tread_metal_thickness - tread_side_overhang,
                            section_offset - tread_height
                          ),
                    ]
                  )
                for i in range(2) :
                    bars_verts.append(bars_verts[i] + vec(topset, 0, topset))
                #end for
                for i in range(4) :
                    bars_verts.append \
                      (
                            bars_verts[i]
                        +
                            vec
                              (
                                0,
                                (tread_width + tread_side_overhang) - 2 * tread_metal_thickness,
                                0
                              )
                      )
                #end for
            elif tread_type in [TREADTYPE.BAR_2, TREADTYPE.BAR_3] :
                section_offset = \
                    (
                        ((mm.run + tread_toe) * section_spacing)
                    /
                        (nr_tread_sections + 1)
                    )
                topset = \
                    (
                        (
                            (mm.run + tread_toe) * (1 - section_spacing)
                        -
                            2 * tread_metal_thickness
                        )
                    /
                        nr_tread_sections
                    )
                base_x = - tread_toe + tread_metal_thickness + section_offset
                base_y = tread_width + tread_side_overhang - 2 * tread_metal_thickness
                bars_verts.extend \
                  ( # left face of tread bar
                    [
                        vec
                          (
                            base_x + topset,
                            - tread_side_overhang + tread_metal_thickness,
                            - tread_height / 2
                          ),
                        vec
                          (
                            base_x,
                            - tread_side_overhang + tread_metal_thickness,
                            - tread_height / 2
                          ),
                        vec(base_x + topset, - tread_side_overhang + tread_metal_thickness, 0),
                        vec(base_x, - tread_side_overhang + tread_metal_thickness, 0),
                    ]
                  )
                for i in range(4) :
                    # right face of tread bar
                    bars_verts.append(bars_verts[i] + vec(0, base_y, 0))
                #end for
            #end if
            # Tread cross-sections:
            if tread_type in [TREADTYPE.BAR_1, TREADTYPE.BAR_2] :
                cross_width = tread_metal_thickness
                cross_spacing = \
                    (
                            (
                                tread_width
                            +
                                2 * tread_side_overhang
                            -
                                (nr_cross_sections + 2) * tread_metal_thickness
                            )
                        /
                            (nr_cross_sections + 1)
                    )
                if tread_type == TREADTYPE.BAR_2 :
                    section_spacing = topset
                #end if
                cross_height = 0
            else : # TREADTYPE.BAR_3
                spacing = section_spacing ** (1 / 4)
                cross_spacing = \
                    (
                        (2 * tread_side_overhang + tread_width)
                    *
                        spacing
                    /
                        (nr_cross_sections + 1)
                    )
                cross_width = \
                    (
                            (
                                - 2 * tread_metal_thickness
                            +
                                (2 * tread_side_overhang + tread_width) * (1 - spacing)
                            )
                        /
                            nr_cross_sections
                    )
                section_spacing = topset
                cross_height = - tread_height / 2
            #end if
            base_y = - tread_side_overhang + tread_metal_thickness + cross_spacing
            crosses_verts.extend \
              ( # left face of cross piece
                [
                    vec(mm.run - tread_metal_thickness, base_y, - tread_height),
                    vec(- tread_toe + tread_metal_thickness, base_y, - tread_height),
                    vec(mm.run - tread_metal_thickness, base_y, cross_height),
                    vec(- tread_toe + tread_metal_thickness, base_y, cross_height),
                ]
              )
            for i in range(4) :
                # right face of cross piece
                crosses_verts.append(crosses_verts[i] + vec(0, cross_width, 0))
            #end for
        #end if
    #end make_treads_verts

    def make_treads() :
        # actually creates the objects for the tread components.
        for i in range(mm.nr_treads) :
            if tread_type == TREADTYPE.CLASSIC :
                mm.make_ppd_mesh(treads_verts, 'treads')
            elif tread_type == TREADTYPE.BASIC_STEEL :
                faces = \
                    [
                        # Positions of following vertices:
                        # 7                   6
                        #
                        #      2        3
                        #
                        # 0    1        4     5
                      # near-end faces:
                        [0, 1, 2, 7],
                        [7, 2, 3, 6],
                        [3, 4, 5, 6],
                      # bottom faces:
                        [1, 0, 8, 9],
                        [5, 4, 12, 13],
                      # inner faces:
                        [2, 1, 9, 10],
                        [3, 2, 10, 11],
                        [4, 3, 11, 12],
                      # side faces:
                        [0, 7, 15, 8],
                        [6, 5, 13, 14],
                      # top face:
                        [7, 6, 14, 15],
                      # far-end faces:
                        [9, 8, 15, 10],
                        [10, 15, 14, 11],
                        [14, 13, 12, 11],
                    ]
                temp = []
                for j in treads_verts :
                    temp.append(copy(j))
                #end for
                for j in range(nr_tread_sections) :
                    mm.make_mesh(temp, faces, 'treads')
                    for k in temp :
                        k += vec(section_depth + section_spacing, 0, 0)
                    #end for
                #end for
            elif tread_type in [TREADTYPE.BAR_1, TREADTYPE.BAR_2, TREADTYPE.BAR_3] :
                faces = \
                    [
                        # right side of frame
                        [2, 0, 1, 3],
                        [2, 3, 7, 6],
                        [1, 0, 4, 5],
                        [5, 4, 6, 7],

                        # width of frame -- outside
                        [0, 2, 10, 8],
                        [9, 11, 3, 1],
                        [2, 6, 14, 10],
                        [7, 3, 11, 15],
                        [4, 0, 8, 12],
                        [1, 5, 13, 9],

                        # width of frame -- inside
                        [6, 4, 12, 14],
                        [5, 7, 15, 13],

                        # left side of frame
                        [8, 10, 11, 9],
                        [11, 10, 14, 15],
                        [8, 9, 13, 12],
                        [12, 13, 15, 14],
                    ]
                mm.make_mesh(treads_verts, faces, 'treads')
                temp = []
                for j in bars_verts :
                    temp.append(copy(j))
                #end for
                for j in range(nr_tread_sections) :
                    mm.make_ppd_mesh(temp, 'tread_bars')
                    for k in temp :
                        k += vec(section_offset + section_spacing, 0, 0)
                    #end for
                #end for
                for j in bars_verts :
                    j += vec(mm.run, 0, mm.rise)
                #end for
                temp = []
                for j in crosses_verts :
                    temp.append(copy(j))
                #end for
                for j in range(nr_cross_sections) :
                    mm.make_ppd_mesh(temp, 'tread_crosses')
                    for k in temp :
                        k += vec(0, cross_width + cross_spacing, 0)
                    #end for
                #end for
                for j in crosses_verts :
                    j += vec(mm.run, 0, mm.rise)
                #end for
            #end if
            for j in treads_verts :
                j += vec(mm.run, 0, mm.rise)
            #end for
        #end for
    #end make_treads

#begin treads
    make_treads_verts()
    make_treads()
#end treads

def treads_circular(mm, tread_type, outer_radius, tread_height, tread_toe, inner_radius) :
    "generates treads for circular stairs."
    start = \
        [
            vec(0, - inner_radius, 0),
            vec(0, - inner_radius, - tread_height),
            vec(0, - outer_radius, 0),
            vec(0, - outer_radius, - tread_height),
        ]
    tread_arc = mm.rotation / mm.nr_treads
    for i in range(mm.nr_treads) :
        verts = []
        # Base faces.  Should be able to append more sections:
        faces = [[0, 1, 3, 2]]
        t_inner = z_rotation(- tread_toe / inner_radius + tread_arc * i)
        verts.append(t_inner * start[0] + vec(0, 0, mm.rise * i))
        verts.append(t_inner * start[1] + vec(0, 0, mm.rise * i))
        t_outer = z_rotation(- tread_toe / outer_radius + tread_arc * i)
        verts.append(t_outer * start[2] + vec(0, 0, mm.rise * i))
        verts.append(t_outer * start[3] + vec(0, 0, mm.rise * i))
        for j in range(mm.sections_per_slice + 1) :
            k = j * 4 + 4
            faces.append([k - 4, k, k + 1, k - 3])
            faces.append([k - 2, k - 1, k + 3, k + 2])
            faces.append([k - 3, k + 1, k + 3, k - 1])
            faces.append([k, k - 4, k - 2, k + 2])
            rot = z_rotation(tread_arc * j / mm.sections_per_slice + tread_arc * i)
            for v in start :
                verts.append(rot * v + vec(0, 0, mm.rise * i))
            #end for
        #end for
        faces.append([k + 1, k, k + 2, k + 3])
        mm.make_mesh(verts, faces, 'treads')
    #end for
#end treads_circular

def central_pillar(mm, tread_height, rail_height, inner_radius) :
    "central pillar for circular stairs."
    stringer_height = mm.rise # height of circular stringers
    height = mm.rise * mm.nr_treads + rail_height + tread_height + stringer_height
    tread_arc = mm.rotation / mm.nr_treads
    nr_sections = math.ceil(mm.sections_per_slice * circle / tread_arc)
    verts = []
    faces = []
    bottom_face = []
    top_face = []
    for i in range(nr_sections) :
        orient = z_rotation(circle * i / nr_sections)
        bottom_face.append(len(verts))
        top_face.append(len(verts) + 1)
        verts.extend \
          (
            [
                orient * vec(0, inner_radius, - tread_height - stringer_height),
                orient * vec(0, inner_radius, height - tread_height - stringer_height),
            ]
          )
        k = i * 2
        faces.append(list(k % (2 * nr_sections) for k in [k + 1, k, k + 2, k + 3]))
    #end for
    bottom_face.reverse() # get normal the right way
    faces.append(bottom_face)
    faces.append(top_face)
    mm.make_mesh(verts, faces, "central pillar")
#end central_pillar

#+
# Putting it all together
#-

class Stairs(bpy.types.Operator) :
    "actual generation of stairs."

    bl_idname = "mesh.stairs"
    bl_label = "Add Stairs"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Add stairs"

    stair_type = EnumProperty \
      (
        name = "Type",
        description = "Type of staircase to generate",
        items = STAIRTYPE.all_items()
      )

    rise = FloatProperty \
      (
        name = "Rise",
        description = "Single tread rise",
        min = 0.0,
        max = 1024.0,
        default = 0.20
      )
    run = FloatProperty \
      (
        name = "Run",
        description = "Single tread run",
        min = 0.0,
        max = 1024.0,
        default = 0.30
      )

    #for circular
    rad1 = FloatProperty \
      (
        name = "Inner Radius",
        description = "Inner radius for circular staircase",
        min = 0.0,
        max = 1024.0,
        soft_max = 10.0,
        default = 0.25
      )
    rad2 = FloatProperty \
      (
        name = "Outer Radius",
        description = "Outer radius for circular staircase",
        min = 0.0,
        max = 1024.0,
        soft_min = 0.015625,
        soft_max = 32.0,
        default = 1.0
      )
    rotation = FloatProperty \
      (
        subtype = "ANGLE",
        name = "Rotation",
        description = "How much the stairway rotates",
        min = 0.0,
        max = 256 * circle,
        step = 5 * 100,
        default = 1.25 * circle
      )
    central_pillar = BoolProperty \
      (
        name = "Central Pillar",
        description = "Generate a central pillar",
        default = False
      )

    #for treads
    make_treads = BoolProperty \
      (
        name = "Make Treads",
        description = "Enable tread generation",
        default = True
      )
    tread_w = FloatProperty \
      (
        name = "Tread Width",
        description = "Width of each generated tread",
        min = 0.0001,
        max = 1024.0,
        default = 1.2
      )
    tread_h = FloatProperty \
      (
        name = "Tread Height",
        description = "Height of each generated tread",
        min = 0.0001,
        max = 1024.0,
        default = 0.04
      )
    tread_t = FloatProperty \
      (
        name = "Tread Toe",
        description = "Toe (aka \"nosing\") of each generated tread",
        min = 0.0,
        max = 10.0,
        default = 0.03
      )
    tread_o = FloatProperty \
      (
        name = "Tread Overhang",
        description = "How much tread \"overhangs\" the sides",
        min = 0.0,
        max = 1024.0,
        default = 0.025
      )
    tread_n = IntProperty \
      (
        name = "Number of Treads",
        description = "How many treads to generate",
        min = 1,
        max = 1024,
        default = 10
      )
    tread_type = EnumProperty \
      (
        name = "Tread Type",
        description = "Type/style of treads to generate",
        items = TREADTYPE.all_items()
      )
    tread_tk = FloatProperty \
      (
        name = "Thickness",
        description = "Thickness of the treads",
        min = 0.0001, max = 10.0,
        default = 0.02
      )
    tread_sec = IntProperty \
      (
        name = "Sections",
        description = "Number of sections to use for tread",
        min = 1,
        max = 1024,
        default = 5
      )
    tread_sp = IntProperty \
      (
        subtype = "PERCENTAGE",
        name = "Spacing",
        description = "Total spacing between tread sections as a percentage of total tread width",
        min = 0,
        max = 80,
        default = 5
      )
    tread_sn = IntProperty \
      (
        name = "Crosses",
        description = "Number of cross section supports",
        min = 2,
        max = 1024,
        default = 4
      )
    #special circular tread properties:
    sections_per_slice = IntProperty \
      (
        name = "Slices",
        description = "Number of slices each tread is composed of",
        min = 1,
        max = 1024,
        soft_max = 16,
        default = 4
      )

    #for posts
    make_posts = BoolProperty \
      (
        name = "Make Posts",
        description = "Enable post generation",
        default = True
      )
    post_d = FloatProperty \
      (
        name = "Post Depth",
        description = "Depth of generated posts",
        min = 0.0001,
        max = 10.0,
        default = 0.04
      )
    post_w = FloatProperty \
      (
        name = "Post Width",
        description = "Width of generated posts",
        min = 0.0001,
        max = 10.0,
        default = 0.04
      )
    post_n = IntProperty \
      (
        name = "Number of Posts",
        description = "Number of posts to generated",
        min = 1,
        max = 1024,
        default = 5
      )

    #for railings
    make_railings = BoolProperty \
      (
        name = "Make Railings",
        description = "Generate railings",
        default = True
      )
    rail_w = FloatProperty \
      (
        name = "Railings Width",
        description = "Width of railings to generate",
        min = 0.0001,
        max = 10.0,
        default = 0.12
      )
    rail_t = FloatProperty \
      (
        name = "Railings Thickness",
        description = "Thickness of railings to generate",
        min = 0.0001,
        max = 10.0,
        default = 0.03
      )
    adjust_rail_thickness = BoolProperty \
      (
        name = "Adjust Thickness",
        description = "Compensate for different slopes on inner and outer railings",
        default = True
      )
    rail_h = FloatProperty \
      (
        name = "Railings Height",
        description = "Height of railings to generate",
        min = 0.0001,
        max = 10.0,
        default = 0.90
      )

    #for retainers
    make_retainers = BoolProperty \
      (
        name = "Make Retainers",
        description = "Generate retainers",
        default = True
      )
    ret_w = FloatProperty \
      (
        name = "Retainer Width",
        description = "Width of generated retainers",
        min = 0.0001,
        max = 10.0,
        default = 0.01
      )
    ret_h = FloatProperty \
      (
        name = "Retainer Height",
        description = "Height of generated retainers",
        min = 0.0001,
        max = 10.0,
        default = 0.01
      )
    ret_n = IntProperty \
      (
        name = "Number of Retainers",
        description = "Number of retainers to generated",
        min = 1,
        max = 1024,
        default = 3
      )

    #for stringer
    make_stringer = BoolProperty \
      (
        name = "Make Stringer",
        description = "Generate stair stringer",
        default = True
      )
    freestanding_stringer_type = EnumProperty \
      (
        name = "Stringer Type",
        description = "Type/style of freestanding stringer to generate",
        items = FREESTANDING_STRINGERTYPE.all_items()
      )
    housed_stringer_type = EnumProperty \
      (
        name = "Stringer Type",
        description = "Type/style of housed stringer to generate",
        items = HOUSED_STRINGERTYPE.all_items()
      )
    string_n = IntProperty \
      (
        name = "Number of Stringers",
        description = "Number of stringers to generate",
        min = 1,
        max = 10,
        default = 1
      )
    string_dis = BoolProperty \
      (
        name = "Distributed",
        description = "Use distributed stringers",
        default = False
      )
    string_w = FloatProperty \
      (
        subtype = "PERCENTAGE",
        name = "Stringer width",
        description = "Width of stringer as a percentage of tread width",
        min = 0.0001,
        max = 100.0,
        default = 15.0
      )
    string_h = FloatProperty \
      (
        name = "Stringer Height",
        description = "Height of the stringer",
        min = 0.0001,
        max = 100.0,
        default = 0.3
      )
    string_tw = FloatProperty \
      (
        subtype = "PERCENTAGE",
        name = "Web Thickness",
        description = "Thickness of the beam's web as a percentage of width",
        min = 0.0001,
        max = 100.0,
        default = 25.0
      )
    string_tf = FloatProperty \
      (
        name = "Flange Thickness",
        description = "Thickness of the flange",
        min = 0.0001,
        max = 100.0,
        default = 0.05
      )
    string_tp = FloatProperty \
      (
        subtype = "PERCENTAGE",
        name = "Flange Taper",
        description = "Flange thickness taper as a percentage",
        min = 0.0,
        max = 100.0,
        default = 0.0
      )
    string_g = BoolProperty \
      (
        name = "Floating",
        description = "Cut bottom of stringer to be a \"floating\" section",
        default = False
      )

    use_original = BoolProperty \
      (
        name = "Use legacy method",
        description = "Use the Blender 2.49 legacy method for stair generation",
        default = True
      )
    do_right_side = BoolProperty \
      (
        name = "Right Details",
        description = "Generate right side details (posts/rails/retainers)",
        default = True
      )
    do_left_side = BoolProperty \
      (
        name = "Left Details",
        description = "Generate left side details (posts/rails/retainers)",
        default = True
      )

    # Draw the GUI:
    def draw(self, context) :
        layout = self.layout
        box = layout.box()
        box.prop(self, 'stair_type')
        box = layout.box()
        box.prop(self, 'rise')
        if self.stair_type != STAIRTYPE.CIRCULAR.name :
            box.prop(self, 'run')
        else :
            box.prop(self, 'rotation')
            box.prop(self, 'rad1')
            box.prop(self, 'rad2')
            box.prop(self, 'central_pillar')
            box.prop(self, "sections_per_slice") # affects resolution of treads, railings, retainers and stringers
        #end if
        if self.stair_type in [STAIRTYPE.FREESTANDING.name, STAIRTYPE.CIRCULAR.name] :
            box.prop(self, 'use_original')
            if not self.use_original :
                box.prop(self, 'do_right_side')
                box.prop(self, 'do_left_side')
            #end if
        else :
            self.use_original = False
            box.prop(self, 'do_right_side')
            box.prop(self, 'do_left_side')
        #end if
        # Treads
        box = layout.box()
        box.prop(self, 'make_treads')
        if self.make_treads :
            if not self.use_original and self.stair_type != STAIRTYPE.CIRCULAR.name :
                box.prop(self, 'tread_type')
            else :
                self.tread_type = TREADTYPE.CLASSIC.name
            #end if
            if self.stair_type != STAIRTYPE.CIRCULAR.name :
                box.prop(self, 'tread_w')
            #end if
            box.prop(self, 'tread_h')
            box.prop(self, 'tread_t')
            if self.stair_type not in [STAIRTYPE.HOUSED_OPEN.name, STAIRTYPE.CIRCULAR.name] :
                box.prop(self, 'tread_o')
            else :
                self.tread_o = 0.0
            #end if
            box.prop(self, 'tread_n')
            if self.tread_type != TREADTYPE.CLASSIC.name :
                box.prop(self, 'tread_tk')
                box.prop(self, 'tread_sec')
                if self.tread_sec > 1 and self.tread_type not in [TREADTYPE.BAR_1.name, TREADTYPE.BAR_2.name] :
                    box.prop(self, 'tread_sp')
                #end if
                if self.tread_type in [TREADTYPE.BAR_1.name, TREADTYPE.BAR_2.name, TREADTYPE.BAR_3.name] :
                    box.prop(self, 'tread_sn')
                #end if
            #end if
        #end if
        # Posts
        box = layout.box()
        box.prop(self, 'make_posts')
        if self.make_posts :
            box.prop(self, 'post_d')
            box.prop(self, 'post_w')
            box.prop(self, 'post_n')
        #end if
        # Railings
        box = layout.box()
        box.prop(self, 'make_railings')
        if self.make_railings :
            box.prop(self, 'rail_w')
            box.prop(self, 'rail_t')
            if self.stair_type == STAIRTYPE.CIRCULAR.name :
                box.prop(self, "adjust_rail_thickness")
            #end if
        #end if
        box.prop(self, 'rail_h') # affects placement of posts and retainers too
        # Retainers
        box = layout.box()
        box.prop(self, 'make_retainers')
        if self.make_retainers :
            box.prop(self, 'ret_w')
            box.prop(self, 'ret_h')
            box.prop(self, 'ret_n')
        #end if
        # Stringers
        box = layout.box()
        if self.stair_type != STAIRTYPE.BOX.name :
            box.prop(self, 'make_stringer')
        else :
            self.make_stringer = True
        #end if
        if self.stair_type != STAIRTYPE.BOX.name and self.make_stringer :
            if not self.use_original and self.stair_type != STAIRTYPE.CIRCULAR.name :
                if self.stair_type == STAIRTYPE.HOUSED_OPEN.name :
                    box.prop(self, 'housed_stringer_type')
                else :
                    box.prop(self, 'freestanding_stringer_type')
                #end if
            else :
                self.freestanding_stringer_type = FREESTANDING_STRINGERTYPE.CLASSIC.name
                self.housed_stringer_type = HOUSED_STRINGERTYPE.CLASSIC.name
            #end if
            box.prop(self, 'string_w')
            if self.stair_type == STAIRTYPE.FREESTANDING.name :
                if self.freestanding_stringer_type == FREESTANDING_STRINGERTYPE.CLASSIC.name and not self.use_original :
                    box.prop(self, 'string_n')
                    box.prop(self, 'string_dis')
                elif self.freestanding_stringer_type == FREESTANDING_STRINGERTYPE.I_BEAM.name :
                    box.prop(self, 'string_n')
                    box.prop(self, 'string_dis')
                    box.prop(self, 'string_h')
                    box.prop(self, 'string_tw')
                    box.prop(self, 'string_tf')
                    box.prop(self, 'string_tp')
                    box.prop(self, 'string_g')
                #end if
            elif self.stair_type == STAIRTYPE.HOUSED_OPEN.name :
                if self.housed_stringer_type in [HOUSED_STRINGERTYPE.I_BEAM.name, HOUSED_STRINGERTYPE.C_BEAM.name] :
                    box.prop(self, 'string_tw')
                    box.prop(self, 'string_tf')
                #end if
            elif self.stair_type == STAIRTYPE.CIRCULAR.name :
                box.prop(self, 'string_n')
                box.prop(self, 'string_dis')
            #end if
        #end if
    #end draw

    def execute(self, context) :
        mm = MeshMaker(self.rise, self.run, self.tread_n, self.rotation, self.sections_per_slice, self.do_left_side, self.do_right_side)
        # convert strings to enums
        stair_type = STAIRTYPE[self.stair_type]
        freestanding_stringer_type = FREESTANDING_STRINGERTYPE[self.freestanding_stringer_type]
        housed_stringer_type = HOUSED_STRINGERTYPE[self.housed_stringer_type]
        tread_type = TREADTYPE[self.tread_type]
        if self.make_treads :
            if stair_type != STAIRTYPE.CIRCULAR :
                treads \
                  (
                    mm = mm,
                    stair_type = stair_type,
                    tread_type = tread_type,
                    tread_width = self.tread_w,
                    tread_height = self.tread_h,
                    tread_toe = self.tread_t,
                    tread_side_overhang = self.tread_o,
                    tread_metal_thickness = self.tread_tk,
                    nr_tread_sections = self.tread_sec,
                    spacing = self.tread_sp,
                    nr_cross_sections = self.tread_sn
                  )
            else :
                treads_circular \
                  (
                    mm = mm,
                    tread_type = tread_type,
                    outer_radius = self.rad2,
                    tread_height = self.tread_h,
                    tread_toe = self.tread_t,
                    inner_radius = self.rad1
                  )
            #end if
        #end if
        if self.do_right_side or self.do_left_side :
            if self.make_posts :
                if stair_type != STAIRTYPE.CIRCULAR :
                    posts \
                      (
                        mm = mm,
                        post_depth = self.post_d,
                        post_width = self.post_w,
                        tread_width = self.tread_w,
                        nr_posts = self.post_n,
                        rail_height = self.rail_h,
                        rail_thickness = self.rail_t
                      )
                else :
                    posts_circular \
                      (
                        mm = mm,
                        post_depth = self.post_d,
                        post_width = self.post_w,
                        nr_posts = self.post_n,
                        rail_height = self.rail_h,
                        rail_thickness = self.rail_t,
                        inner_radius = self.rad1,
                        outer_radius = self.rad2
                      )
                #end if
            #end if
            if self.make_railings :
                if stair_type != STAIRTYPE.CIRCULAR :
                    railings \
                      (
                        mm = mm,
                        rail_width = self.rail_w,
                        rail_thickness = self.rail_t,
                        rail_height = self.rail_h,
                        tread_toe = self.tread_t,
                        post_width = self.post_w,
                        post_depth = self.post_d,
                        tread_width = self.tread_w
                      )
                else :
                    railings_circular \
                      (
                        mm = mm,
                        rail_width = self.rail_w,
                        rail_thickness = self.rail_t,
                        adjust_thickness = self.adjust_rail_thickness,
                        rail_height = self.rail_h,
                        tread_toe = self.tread_t,
                        post_width = self.post_w,
                        post_depth = self.post_d,
                        tread_width = self.tread_w,
                        inner_radius = self.rad1,
                        outer_radius = self.rad2
                      )
                #end if
            #end if
            if self.make_retainers :
                if stair_type != STAIRTYPE.CIRCULAR :
                    retainers \
                      (
                        mm = mm,
                        retainer_width = self.ret_w,
                        retainer_height = self.ret_h,
                        nr_retainers = self.ret_n,
                        post_width = self.post_w,
                        tread_width = self.tread_w,
                        rail_height = self.rail_h
                      )
                else :
                    retainers_circular \
                      (
                        mm = mm,
                        retainer_width = self.ret_w,
                        retainer_height = self.ret_h,
                        nr_retainers = self.ret_n,
                        post_width = self.post_w,
                        tread_width = self.tread_w,
                        rail_height = self.rail_h,
                        inner_radius = self.rad1,
                        outer_radius = self.rad2
                      )
                #end if
            #end if
        #end if
        if self.make_stringer :
            if stair_type == STAIRTYPE.FREESTANDING and self.use_original :
                stringer \
                  (
                    mm = mm,
                    stair_type = stair_type,
                    stringer_type = freestanding_stringer_type,
                    w = self.string_w,
                    stringer_height = self.string_h,
                    tread_height = self.tread_h,
                    tread_width = self.tread_w,
                    tread_toe = self.tread_t,
                    tread_overhang = self.tread_o,
                    tw = self.string_tw,
                    stringer_flange_thickness = self.string_tf,
                    tp = self.string_tp,
                    stringer_intersects_ground = not self.string_g
                  )
            elif stair_type == STAIRTYPE.BOX :
                stringer \
                  (
                    mm = mm,
                    stair_type = stair_type,
                    stringer_type = freestanding_stringer_type,
                    w = 100,
                    stringer_height = self.string_h,
                    tread_height = self.tread_h,
                    tread_width = self.tread_w,
                    tread_toe = self.tread_t,
                    tread_overhang = self.tread_o,
                    tw = self.string_tw,
                    stringer_flange_thickness = self.string_tf,
                    tp = self.string_tp,
                    stringer_intersects_ground = not self.string_g,
                    nr_stringers = 1,
                    distributed_stringers = False,
                    notMulti = False
                  )
            elif stair_type == STAIRTYPE.CIRCULAR :
                stringer \
                  (
                    mm = mm,
                    stair_type = stair_type,
                    stringer_type = None,
                    w = self.string_w,
                    stringer_height = self.string_h,
                    tread_height = self.tread_h,
                    tread_width = self.rad2 - self.rad1,
                    tread_toe = self.tread_t,
                    tread_overhang = self.rad1,
                    tw = self.string_tw,
                    stringer_flange_thickness = self.string_tf,
                    tp = self.string_tp,
                    stringer_intersects_ground = not self.string_g,
                    nr_stringers = self.string_n,
                    distributed_stringers = self.string_dis,
                    notMulti = self.use_original
                  )
            else :
                stringer \
                  (
                    mm = mm,
                    stair_type = stair_type,
                    stringer_type = (freestanding_stringer_type, housed_stringer_type)[stair_type == STAIRTYPE.HOUSED_OPEN],
                    w = self.string_w,
                    stringer_height = self.string_h,
                    tread_height = self.tread_h,
                    tread_width = self.tread_w,
                    tread_toe = self.tread_t,
                    tread_overhang = self.tread_o,
                    tw = self.string_tw,
                    stringer_flange_thickness = self.string_tf,
                    tp = self.string_tp,
                    stringer_intersects_ground = not self.string_g,
                    nr_stringers = self.string_n,
                    distributed_stringers = self.string_dis,
                    notMulti = self.use_original
                  )
            #end if
        #end if
        if stair_type == STAIRTYPE.CIRCULAR and self.central_pillar :
            central_pillar \
              (
                mm = mm,
                tread_height = self.tread_h,
                rail_height = self.rail_h,
                inner_radius = self.rad1
              )
        #end if
        if len(mm.made_objects) != 0 :
            # cannot seem to create an empty with bpy.data.objects.new()
            bpy.ops.object.empty_add \
              (
                location = bpy.context.scene.cursor_location,
                layers = bpy.context.space_data.layers
              )
            root = bpy.context.active_object
            assert root.type == "EMPTY"
            root.name = "staircase root"
            for obj in mm.made_objects :
                obj.parent = root
                obj.parent_type = "OBJECT"
            #end if
        #end if
        return {'FINISHED'}
    #end execute

#end Stairs
