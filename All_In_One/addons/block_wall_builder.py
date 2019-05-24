# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License
# as published by the Free Software Foundation - either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, write to:
#
#	the Free Software Foundation Inc.
#	51 Franklin Street, Fifth Floor
#	Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Block Wall Builder",
    "author": "Jonathon Anderson",
    "version": (0, 2),
    "blender": (2, 6, 3),
    "location": "View3D > Add > Mesh > Block Wall",
    "description": "Builder for block walls.",
    "warning": "Beta",
    "wiki_url": "http://wiki.blender.org/index.php/User:BlueBlender42zu/"
                "Addons/block_wall_builder",
    "tracker_url": "http://projects.blender.org/tracker/"
                   "?func=detail&aid=31422",
    "category": "Learnbgame",
}

#Version History
#V0.4 2012/5/??  ...
#  TODO: Make fancy block panel
#V0.3 2012/5/17  Allowed multiple holes, made a panel system for orgenizing the settings
#V0.2 2012/5/14  Added offset_dir, changed hierarchy, new and improved overlap algerithom
#V0.1 2012/5/11  First release!


import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


class Rectangle():
    """I am a rectangle that is not turned"""
    def __init__(self, position, extent):
        self.position = position
        self.extent = extent
        self.points = [position,
                       Vector((position.x + extent.x, position.y)),
                       position + extent,
                       Vector((position.x, position.y + extent.y))]

    def is_proper(self):
        return (self.extent.x > 0) and (self.extent.y > 0)

    def overlaps(self, other):
        return self.intersect(other).is_proper()

    def intersect(self, other):
        ll = Vector((max(self.position.x, other.position.x),
                     max(self.position.y, other.position.y)))
        ur = Vector((min(self.position.x + self.extent.x, other.position.x + other.extent.x),
                     min(self.position.y + self.extent.y, other.position.y + other.extent.y)))
        return Rectangle(ll, ur - ll)


class Block(Rectangle):
    """I represent a single block in the wall"""
    def __init__(self, position=Vector((0, 0)), split2=False, op=None):
        if split2:
            self.extent = Vector((op.block.x / 2, op.block.y))
        else:
            self.extent = op.block
        super().__init__(position, self.extent)
        self.split2 = split2
        self.op = op

    def test_for_hole(self):
        """Test if I'm in the hole. True for OK to build, False for not,
        and a block to say build this"""
        op = self.op
        if not self.split2 and op.split2:
            l = [0, 1]
            b1 = Block(self.position, True, op)
            l[0] = b1.test_for_hole()
            b2 = Block(Vector((self.position.x + (op.block.x / 2),
                               self.position.y)), True, op)
            l[1] = b2.test_for_hole()
            if l == [False, False]:
                return False
            elif l == [True, False]:
                return b1
            elif l == [False, True]:
                return b2
            elif l == [True, True]:
                return True
        for hole in op.holes.holes:
            if self.overlaps(Rectangle(hole.hole_pos, hole.hole_size)):
                return False
        return True

    def build(self, vadd):
        op = self.op
        if op.holeb:
            t = self.test_for_hole()
            if type(t) == Block:
                return t.build(vadd)
            elif t == False:
                return [], []
        grout = Vector.Fill(2, op.grout / 2)
        ext = self.extent - Vector.Fill(2, op.grout)
        pos = self.position + grout
        v = [0, 1, 2, 3, 4, 5, 6, 7]
        v[0] = (pos).to_3d()
        v[1] = Vector((pos.x, pos.y + ext.y, 0))
        v[2] = (pos + ext).to_3d()
        v[3] = Vector((pos.x + ext.x, pos.y, 0))
        v[4] = v[0] + Vector((0, 0, op.depth))
        v[5] = v[1] + Vector((0, 0, op.depth))
        v[6] = v[2] + Vector((0, 0, op.depth))
        v[7] = v[3] + Vector((0, 0, op.depth))
        f = [[0, 1, 2, 3], [4, 5, 6, 7],
             [0, 1, 5, 4], [1, 2, 6, 5],
             [2, 3, 7, 6], [3, 0, 4, 7]]
        for l in f:
            for i in range(len(l)):
                l[i] += vadd
        return v, f


class BlockRow():
    """I represent a row of blocks"""

    def __init__(self, position=Vector((0, 0)), op=None):
        self.position = position
        self.op = op

    def build(self, offset, vadd):
        op = self.op
        block_num = int(op.wall.x // op.block.x)
        verts = []
        faces = []
        pos = self.position

        if op.split2 and offset:
            v, f = Block(pos, True, op).build(vadd + len(verts))
            verts.extend(v)
            faces.extend(f)

        if offset:
            pos += Vector((op.block.x / 2.0, 0))
            block_num -= 1

        for i in range(0, block_num):
            v, f = Block(pos, op=op).build(vadd + len(verts))
            verts.extend(v)
            faces.extend(f)
            pos += Vector((op.block.x, 0))

        if op.split2 and offset:
            v, f = Block(pos, True, op).build(vadd + len(verts))
            verts.extend(v)
            faces.extend(f)

        return (verts, faces)


def add_object(self, context):
    row_num = self.wall.y // self.block.y
    verts = []
    edges = []
    faces = []

    offset = self.offset_dir

    for i in range(0, int(row_num)):
        row = BlockRow(Vector((0, i * self.block.y)), self)
        v, f = row.build(offset, len(verts))
        verts.extend(v)
        faces.extend(f)
        if self.offset:
            offset = not offset

    mesh = bpy.data.meshes.new(name="Block Wall")
    mesh.from_pydata(verts, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh, operator=self)


class bwb_hole(bpy.types.PropertyGroup):
    hole_size = bpy.props.FloatVectorProperty(
                          name="Hole size",
                          default=(1, 1),
                          size=2,
                          subtype='XYZ',
                          description="Size of the hole"
                          )

    hole_pos = bpy.props.FloatVectorProperty(
                         name="Hole position",
                         default=(1, 1),
                         size=2,
                         subtype='XYZ',
                         description="Position of the hole (lower left corner)"
                         )



def index_update(self, context):
    if len(self.holes) == 0:
        self.holes.add()
    if self.active_index < 1:
        self.active_index = 1
    elif self.active_index > len(self.holes):
        self.active_index = len(self.holes)
    if self.last_index > 0:
        self.holes[self.last_index - 1].hole_size = self.active_hole_size
        self.holes[self.last_index - 1].hole_pos = self.active_hole_pos
    self.last_index = self.active_index
    self.active_hole_size = self.holes[self.active_index - 1].hole_size
    self.active_hole_pos = self.holes[self.active_index - 1].hole_pos


def active_size_update(self, context):
    self.holes[self.active_index - 1].hole_size = self.active_hole_size


def active_pos_update(self, context):
    self.holes[self.active_index - 1].hole_pos = self.active_hole_pos


def add_button_update(self, context):
    if self.add_button:
        self.holes.add()
        self.add_button = False


def remove_button_update(self, context):
    if self.remove_button:
        self.holes.remove(self.active_index - 1)
        self.last_index = -1
        index_update(self, context)
        self.remove_button = False


class bwb_holes(bpy.types.PropertyGroup):
    holes = bpy.props.CollectionProperty(type=bwb_hole)
    active_index = bpy.props.IntProperty(
                             name="Index",
                             default=1,
                             description="Which hole are we looking at?",
                             update=index_update
                             )
    last_index = bpy.props.IntProperty(default=-1)
    active_hole_size = bpy.props.FloatVectorProperty(
                                 name="Hole size",
                                 default=(1, 1),
                                 size=2,
                                 subtype='XYZ',
                                 description="Size of the hole",
                                 update=active_size_update
                                 )
    active_hole_pos = bpy.props.FloatVectorProperty(
                                name="Hole position",
                                default=(1, 1),
                                size=2,
                                subtype='XYZ',
                                description="Position of the hole (lower left corner)",
                                update=active_pos_update
                                )
    add_button = bpy.props.BoolProperty(
                           name="Add hole",
                           default=False,
                           description="A button to add another hole",
                           update=add_button_update
                           )
    remove_button = bpy.props.BoolProperty(
                              name="Remove hole",
                              default=False,
                              description="A button to remove the current hole",
                              update=remove_button_update
                              )


def holeb_update(self, context):
    if (self.old_holeb == False) and (self.holeb == True):
        index_update(self.holes, context)
    self.old_holeb = self.holeb


class add_mesh_block_wall_build(Operator, AddObjectHelper):
    """Build a block wall"""
    bl_idname = "mesh.block_wall_build"
    bl_label = "Block Wall"
    bl_description = "Build a new block wall"
    bl_options = set(['REGISTER', 'UNDO'])

    panel_selector = bpy.props.EnumProperty(
                               name="Panel",
                               description="Choose the settings panel you want to see",
                               items=[('W', "Wall", "Settings for the whole wall"),
                                      ('B', "Block", "Settings for the blocks"),
                                      ('H', "Holes", "Settings for making holes")]
                               )

    block = bpy.props.FloatVectorProperty(
                      name="Block size",
                      default=(1.0, 1.0),
                      subtype='XYZ',
                      description="Size of the blocks",
                      size=2
                      )
    offset = bpy.props.BoolProperty(
                       name="Offset",
                       description="Move each layer a little to the side",
                       default=True
                       )
    offset_dir = bpy.props.BoolProperty(
                           name="Inverse Offset",
                           description="Make the blocks shift in the other direction",
                           default=False
                           )
    split2 = bpy.props.BoolProperty(
                       name="Split",
                       description="Allow half blocks",
                       default=True
                       )
    wall = bpy.props.FloatVectorProperty(
                     name="Wall size",
                     default=(3.0, 3.0),
                     size=2,
                     subtype='XYZ',
                     description="Maximum bounds of the entire wall"
                     )
    depth = bpy.props.FloatProperty(
                      name="Depth",
                      default=0.5,
                      subtype='DISTANCE',
                      description="Thickness of the wall"
                      )
    grout = bpy.props.FloatProperty(
                      name="Grout",
                      default=0.25,
                      subtype='DISTANCE',
                      description="Space between the blocks of the wall"
                      )

    holeb = bpy.props.BoolProperty(
                      name="Holes",
                      description="Have one or more rectangular holes in the wall",
                      default=False,
                      update=holeb_update
                      )
    old_holeb = bpy.props.BoolProperty(default=False)
    holes = bpy.props.PointerProperty(type=bwb_holes)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'panel_selector')
        if self.panel_selector == 'W':
            box = layout.box()
            box.label("Wall Settings")

            row = box.row()
            box.prop(self, 'split2')
            box.prop(self, 'offset')
        
            row = box.row()
            if self.offset:
                row.prop(self, 'offset_dir')

            box.prop(self, 'wall')
            box.prop(self, 'depth')
            box.prop(self, 'grout')
        elif self.panel_selector == 'B':
            box = layout.box()
            box.label("Block Settings")
            box.prop(self, 'block')
        elif self.panel_selector == 'H':
            box = layout.box()
            box.prop(self, 'holeb')

            if self.holeb:
                box.prop(self.holes, 'active_index')
                box.prop(self.holes, 'add_button')
                box.prop(self.holes, 'remove_button')
                box.prop(self.holes, 'active_hole_size')
                box.prop(self.holes, 'active_hole_pos')

    def execute(self, context):
        if self.block.x > self.wall.x:
            return set(['CANCELLED'])
        elif self.block.y > self.wall.y:
            return set(['CANCELLED'])
        elif (self.grout > self.block.x) or (self.grout > self.block.y):
            return set(['CANCELLED'])

        add_object(self, context)

        return set(['FINISHED'])


# Registration

def add_object_button(self, context):
    self.layout.operator(
        add_mesh_block_wall_build.bl_idname,
        text=add_mesh_block_wall_build.bl_label,
        icon="MOD_BUILD")


def register():
    bpy.utils.register_class(bwb_hole)
    bpy.utils.register_class(bwb_holes)
    bpy.utils.register_class(add_mesh_block_wall_build)
    bpy.types.INFO_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(add_mesh_block_wall_build)
    bpy.utils.unregister_class(bwb_hole)
    bpy.utils.unregister_class(bwb_holes)
    bpy.types.INFO_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()