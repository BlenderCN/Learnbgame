# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Original Author = Jacob Morris
# URL = github.com/BlendingJake

bl_info = {
    "name": "CubeSter",
    "author": "Jacob Morris",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View 3D > Toolbar > CubeSter",
    "description": "Take an image, image sequence, or audio file and use it to generate a cube-based mesh.",
    "category": "Learnbgame",
}

from bpy.types import Scene, PropertyGroup, Object, Panel, Image, Operator
from bpy.props import PointerProperty, EnumProperty, BoolProperty, StringProperty, CollectionProperty, IntProperty, \
    FloatProperty, FloatVectorProperty
from bpy.utils import register_class, unregister_class
from bpy import app
from os import walk
from bpy.path import abspath
from pathlib import Path
from typing import List
import bpy
import bmesh


def build_block_mesh_from_heights(context, props, heights: List[list]):
    bpy.ops.mesh.primitive_cube_add()
    bm = bmesh.new()
    bs = props.grid_size
    y = -(len(heights)*bs) / 2

    verts, faces = [], []
    for row in heights:
        x = -(len(heights[0])*bs) / 2

        for height in row:
            p = len(verts)

            verts += [
                (x, y, 0), (x+bs, y, 0), (x+bs, y+bs, 0), (x, y+bs, 0),
                (x, y, height), (x+bs, y, height), (x+bs, y+bs, height), (x, y+bs, height)
            ]

            faces += [
                (p, p+4, p+5, p+1), (p, p+3, p+7, p+4), (p+3, p+2, p+6, p+7), (p+2, p+1, p+5, p+6),
                (p+4, p+7, p+6, p+5), (p, p+1, p+2, p+3)
            ]

            x += bs
        y += bs

    for vert in verts:
        bm.verts.new(vert)
    bm.verts.ensure_lookup_table()

    for face in faces:
        bm.faces.new([bm.verts[i] for i in face])
    bm.faces.ensure_lookup_table()

    bm.to_mesh(context.object.data)
    bm.free()


def build_plane_mesh_from_heights(context, props, heights: List[list]):
    bpy.ops.mesh.primitive_cube_add()
    bm = bmesh.new()
    bs = props.grid_size
    y = -((len(heights)-1) * bs) / 2

    verts, faces = [], []
    for row in heights:
        x = -((len(heights[0])-1) * bs) / 2

        for height in row:
            verts.append((x, y, height))

            x += bs
        y += bs

    rl = len(heights[0])
    for i in range(len(heights) - 1):
        for j in range(len(heights[0]) - 1):
            pos = (i * rl) + j
            faces.append((pos, pos + 1, pos + 1 + rl, pos + rl))

    for vert in verts:
        bm.verts.new(vert)
    bm.verts.ensure_lookup_table()

    for face in faces:
        bm.faces.new([bm.verts[i] for i in face])
    bm.faces.ensure_lookup_table()

    bm.to_mesh(context.object.data)
    bm.free()


def create_vertex_material():
    mat = bpy.data.materials.new("CubeSter")
    mat.use_nodes = True

    nodes = mat.node_tree.nodes

    att = nodes.new("ShaderNodeAttribute")
    att.location = (-275, 275)
    att.attribute_name = "Col"

    mat.node_tree.links.new(att.outputs[0], nodes["Principled BSDF"].inputs[0])


def color_block_mesh(context, props, colors: List[list]):
    bpy.ops.mesh.vertex_color_add()
    layer = context.object.data.vertex_colors[0].data

    i = 0
    for row in colors:
        for color in row:
            for _ in range(24):  # 6 faces, 4 vertices each
                layer[i].color = color
                i += 1


def color_plane_mesh(context, props, colors: List[list]):
    bpy.ops.mesh.vertex_color_add()
    layer = context.object.data.vertex_colors[0].data

    i = 0
    # there is one less row and column of faces then the number of rows and columns of vertices, so stop one short
    for r in range(len(colors) - 1):
        for c in range(len(colors[0]) - 1):
            for _ in range(4):
                layer[i].color = colors[r][c]
                i += 1


def frame_handler(scene):
    """
    Update all image sequence CubeSter objects to have the correct colors for the current frame
    :param scene: the current scene
    """
    layer = bpy.context.object.data.vertex_colors[0].data

    for ob in scene.objects:
        ob_props = ob.cs_properties
        frame = scene.frame_current

        if ob_props.cs_type == "sequence" and 0 <= frame < len(ob_props.color_data):
            i = 0
            if ob_props.mesh_type == "blocks":
                for row in ob_props.color_data[frame].rows:
                    for color in row.colors:
                        for _ in range(24):  # 6 faces, 4 vertices each
                            layer[i].color = color.color
                            i += 1
            else:
                # stop one short as there is one less row and column of vertices when the type is plane
                rows = ob_props.color_data[frame].rows
                for r in range(len(rows)-1):
                    for c in range(len(rows[0].colors)-1):
                        for _ in range(4):
                            layer[i].color = rows[r].colors[c].color
                            i += 1


def image_update(_, context):
    props = context.scene.cs_properties

    if "." in props.image.name:
        name = props.image.name[0:props.image.name.rindex(".")]
    else:
        name = props.image.name

    props.image_base_name = name


class CSImageProperties(PropertyGroup):
    filepath: StringProperty()


class CSVertexColor(PropertyGroup):
    color: FloatVectorProperty(
        size=4
    )


class CSRowColors(PropertyGroup):
    colors: CollectionProperty(
        type=CSVertexColor
    )


class CSFrameColorRows(PropertyGroup):
    rows: CollectionProperty(
        type=CSRowColors
    )


class CSObjectProperties(PropertyGroup):
    cs_type: EnumProperty(
        name="CubeSter type",
        items=(("none", "None", ""), ("single", "Single", ""), ("sequence", "Sequence", "")),
        default="none"
    )

    color_data: CollectionProperty(
        type=CSFrameColorRows
    )

    mesh_type: EnumProperty(
        name="Mesh Type",
        items=(("blocks", "Blocks", ""), ("plane", "Plane", "")),
        description="Whether the mesh is a plane or composed of many blocks"
    )


class CSSceneProperties(PropertyGroup):
    image: PointerProperty(
        name="Image",
        type=Image,
        update=image_update
    )

    # image sequence options
    is_image_sequence: BoolProperty(
        name="Image Sequence?", default=False
    )

    image_base_name: StringProperty(
        name="Base Image Name"
    )

    image_sequence: CollectionProperty(
        type=CSImageProperties, name="Image Sequence"
    )

    start_image_index: IntProperty(
        name="Start Image Index", min=0, description="Of the images found, start this many in from the first",
        default=0
    )

    step_image_index: IntProperty(
        name="Step Image Index", min=1, description="Of the images found, only keep ones at multiples of this value",
        default=1
    )

    skip_pixels: IntProperty(
        name="Skip Pixels",
        min=0, default=64,
        description="Skip this many pixels in each row and column"
    )

    height: FloatProperty(
        name="Height",
        unit="LENGTH", min=0, default=0.5,
        description="The height of pure white"
    )

    grid_size: FloatProperty(
        name="Grid Size",
        unit="LENGTH", min=0, default=0.01,
        description="The length and width of each block, or the spacing between vertices in the plane"
    )

    invert: BoolProperty(
        name="Invert Heights?", default=False, description="Make black the highest value, not white"
    )

    mesh_type: EnumProperty(
        name="Mesh Type",
        items=(("blocks", "Blocks", ""), ("plane", "Plane", "")),
        description="Whether the mesh is a plane or composed of many blocks"
    )

    # advanced
    show_advanced: BoolProperty(
        name="Show Advanced", default=False
    )

    remove_images: BoolProperty(
        name="Remove Images On Creation", default=False,
        description="Remove images as quickly as possible to save memory. Useful with image sequences."
    )


class CSPanel(Panel):
    bl_idname = "OBJECT_PT_cs_panel"
    bl_label = "CubeSter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout
        props = context.scene.cs_properties

        layout.template_ID(props, "image", open="image.open")

        layout.separator()
        box = layout.box()
        box.prop(props, "is_image_sequence", icon="RENDER_RESULT")
        if props.is_image_sequence:
            box.prop(props, "image_base_name")
            box.operator("object.cs_load_image_sequence")

            box.separator()
            box.prop(props, "start_image_index")
            box.prop(props, "step_image_index")
            box.label(text="Images Found: {}".format(len(props.image_sequence)))

        layout.separator()
        box = layout.box()
        box.prop(props, "skip_pixels")
        box.prop(props, "height")
        box.prop(props, "grid_size")

        layout.separator()
        layout.prop(props, "invert", icon="DECORATE_OVERRIDE")

        layout.separator()
        layout.prop(props, "mesh_type")

        layout.separator()
        layout.operator("object.cs_create_object", icon="MESH_CUBE")

        layout.separator()
        box = layout.box()
        box.prop(props, "show_advanced", icon="TRIA_DOWN" if props.show_advanced else "TRIA_RIGHT")

        if props.show_advanced:
            box.separator()
            box.prop(props, "remove_images", icon="FAKE_USER_OFF")


class CSLoadImageSequence(Operator):
    bl_idname = "object.cs_load_image_sequence"
    bl_label = "Load Image Sequence"
    bl_description = "Load CubeSter Image Sequence"

    def execute(self, context):
        props = context.scene.cs_properties
        dir_path = Path(abspath(props.image.filepath)).parent
        props.image_sequence.clear()

        image_files = []
        for _, _, files in walk(dir_path):
            for file in files:
                if file.startswith(props.image_base_name):
                    image_files.append(file)

            break  # only get top-level

        image_files.sort()

        for fi in range(props.start_image_index, len(image_files), props.step_image_index):
            file = image_files[fi]
            img = props.image_sequence.add()
            img.filepath = str(dir_path / file)

        return {"FINISHED"}


class CSCreateObject(Operator):
    bl_idname = "object.cs_create_object"
    bl_label = "Create Object"
    bl_description = "Create CubeSter Object"

    def execute(self, context):
        props = context.scene.cs_properties
        images = []
        image_data = []

        if props.is_image_sequence:
            for path in props.image_sequence:
                name = Path(path.filepath).name
                if name in bpy.data.images:
                    images.append(bpy.data.images[name])
                else:
                    images.append(bpy.data.images.load(path.filepath))

            self.report({"INFO"}, "Image sequence loaded.")
        else:
            images.append(props.image)

        sp = props.skip_pixels
        for image in images:
            w, h = image.size
            channels = image.channels
            channels_index = channels if channels <= 4 else 4
            padding = [1] * (4 - image.channels)
            pixels = list(image.pixels)  # 0 = bottom-left corner of image

            height_factor = props.height / channels

            heights = []
            colors = []
            for r in range(0, h, sp):
                heights.append([])
                colors.append([])
                for c in range(0, w, sp):
                    pos = ((r * w) + c) * channels
                    total = 0

                    for i in range(channels):
                        total += pixels[pos + i]

                    colors[-1].append(pixels[pos:pos+channels_index] + padding)

                    if props.invert:
                        heights[-1].append((channels-total) * height_factor)
                    else:
                        heights[-1].append(total * height_factor)

            image_data.append((heights, colors))

            # if cleaning up images immediately
            if props.remove_images:
                bpy.data.images.remove(image)

        self.report({"INFO"}, "Image data collected.")

        # build and color mesh based on first/only image
        if props.mesh_type == "blocks":
            build_block_mesh_from_heights(context, props, image_data[0][0])
            color_block_mesh(context, props, image_data[0][1])
        else:
            build_plane_mesh_from_heights(context, props, image_data[0][0])
            color_plane_mesh(context, props, image_data[0][1])

        self.report({"INFO"}, "Mesh built.")

        # materials
        if "CubeSter" not in bpy.data.materials:
            create_vertex_material()
        context.object.data.materials.append(bpy.data.materials["CubeSter"])

        self.report({"INFO"}, "Material added.")

        # generated needed data from image sequence if one applicable
        if props.is_image_sequence:
            context.object.cs_properties.cs_type = "sequence"
            mesh = context.object.data

            # animate mesh
            action = bpy.data.actions.new("CubeSter Animation: {}".format(context.object.name))

            mesh.animation_data_create()
            mesh.animation_data.action = action

            vertex_index = 4 if props.mesh_type == "blocks" else 0  # index of first vertex
            vertex_count = 4 if props.mesh_type == "blocks" else 1  # number of vertices the need changed

            rows, columns = len(image_data[0][0]), len(image_data[0][0][0])
            for r in range(rows):
                for c in range(columns):
                    for _ in range(vertex_count):
                        for frame in range(len(images)):
                            mesh.vertices[vertex_index].co.z = image_data[frame][0][r][c]
                            mesh.vertices[vertex_index].keyframe_insert('co', index=2, frame=frame)

                        vertex_index += 1

                    if props.mesh_type == "blocks":  # skip vertices for bottom of block
                        vertex_index += 4

            # store color data
            ob_props = context.object.cs_properties
            for _, colors in image_data:
                frame = ob_props.color_data.add()
                for row in colors:
                    color_row = frame.rows.add()

                    for color in row:
                        item = color_row.colors.add()
                        item.color = color

            self.report({"INFO"}, "Vertex colors stored.")
        else:
            context.object.cs_properties.cs_type = "single"

        context.object.cs_properties.mesh_type = props.mesh_type
        return {"FINISHED"}


classes = [
    CSImageProperties,
    CSVertexColor,
    CSRowColors,
    CSFrameColorRows,
    CSObjectProperties,
    CSSceneProperties,
    CSPanel, 
    CSLoadImageSequence,
    CSCreateObject
]


def register():
    for cls in classes:
        register_class(cls)

    Scene.cs_properties = PointerProperty(
        name="cs_properties",
        type=CSSceneProperties,
        description="All the scene properties needed for the add-on CubeSter"
    )

    Object.cs_properties = PointerProperty(
        name="cs_properties",
        type=CSObjectProperties,
        description="All the object properties needed for the add-on CubeSter"
    )

    app.handlers.frame_change_pre.append(frame_handler)


def unregister():
    del Scene.cs_properties
    del Object.cs_properties

    for cls in classes:
        unregister_class(cls)

    app.handlers.frame_change_pre.remove(frame_handler)


if __name__ == "__main__":
    register() 