#  ***** BEGIN GPL LICENSE BLOCK *****
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
#  ***** END GPL LICENSE BLOCK *****


bl_info = {
    "name": "Texture Buddy",
    "author": "Matt Lucas",
    "version": (1, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Tools",
    "description": "Adds some helpful UV tools to the edit mesh tools window.",
    "warning": "",
    "wiki_url": "https://matt-lucas.itch.io/level-buddy",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
import bmesh


# PROPERTIES
bpy.types.Scene.texel_density = bpy.props.IntProperty(name="Texel Density", default=128, step=128, min=8, max=512)
bpy.types.Scene.offset_x = bpy.props.FloatProperty(name="Offset X", default=0)
bpy.types.Scene.offset_y = bpy.props.FloatProperty(name="Offset Y", default=0)
bpy.types.Scene.nudge_amount = bpy.props.FloatProperty(name="Nudge Amount", default=0.125)


# TEXTURE BUDDY PANEL CLASS
class TextureBuddyPanel(bpy.types.Panel):
    bl_label = "Texture Buddy"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Buddy Tools"

    # DRAW TEXTURE BUDDY UI
    def draw(self, context):
        ob = context.active_object
        layout = self.layout
        col = layout.column(align=True)
        col.label(icon="LATTICE_DATA", text="Texel Density")
        col.prop(context.scene, "texel_density", text="")
        if context.mode == 'EDIT_MESH' or context.mode == 'OBJECT':
            col = layout.column(align=True)
            col.label(icon="FACESEL_HLT", text="Mapping")
            row = layout.row(align=True)
            row.operator("object.texture_buddy_uv", text="Auto").axis = "AUTO"
            row = layout.row(align=True)
            row.operator("object.texture_buddy_uv", text="X").axis = "X"
            row.operator("object.texture_buddy_uv", text="Y").axis = "Y"
            row.operator("object.texture_buddy_uv", text="Z").axis = "Z"
            row = layout.row(align=True)
            row.operator("object.texture_buddy_uv", text="-X").axis = "-X"
            row.operator("object.texture_buddy_uv", text="-Y").axis = "-Y"
            row.operator("object.texture_buddy_uv", text="-Z").axis = "-Z"
            if context.mode == 'EDIT_MESH':
                row = layout.row(align=True)
                row.operator("object.texture_buddy_pin", text="Pin UVs").p = False
                row.operator("object.texture_buddy_pin", text="Un-Pin UVs").p = True
                col = layout.column(align=True)
                col.label(icon="FULLSCREEN_ENTER", text="Offset")
                row = layout.row(align=True)
                row.prop(context.scene, "offset_x", text="X")
                row.prop(context.scene, "offset_y", text="Y")
                col = layout.column(align=True)
                col.label(icon="FORWARD", text="Nudge UVs")
                row = layout.row(align=True)
                row.operator("object.texture_buddy_nudge", text="Left").dir = "LEFT"
                row.operator("object.texture_buddy_nudge", text="Right").dir = "RIGHT"
                row = layout.row(align=True)
                row.operator("object.texture_buddy_nudge", text="Up").dir = "UP"
                row.operator("object.texture_buddy_nudge", text="Down").dir = "DOWN"
                row = layout.row(align=True)
                row.prop(context.scene, "nudge_amount", text="Amount")
                col = layout.column(align=True)
                col.label(icon="LOOP_BACK", text="Flip")
                row = layout.row(align=True)
                row.operator("object.texture_buddy_nudge", text="Horizontal").dir = "HORIZONTAL"
                row.operator("object.texture_buddy_nudge", text="Vertical").dir = "VERTICAL"


# TEXTURE BUDDY UV OPERATOR CLASS        
class TextureBuddyUV(bpy.types.Operator):
    bl_idname = "object.texture_buddy_uv"
    bl_label = "Texture Buddy UV"

    axis = bpy.props.StringProperty(name="Axis", default="AUTO")

    # EXECUTE OPERATOR
    def execute(self, context):
        obj = context.active_object
        me = obj.data
        objectLocation = context.active_object.location
        objectScale = context.active_object.scale
        texelDensity = context.scene.texel_density
        textureWidth = 64
        textureHeight = 64
        if bpy.context.mode == 'EDIT_MESH' or bpy.context.mode == 'OBJECT':
            was_obj_mode = False
            if bpy.context.mode == 'OBJECT':
                was_obj_mode = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
            bm = bmesh.from_edit_mesh(me)
            uv_layer = bm.loops.layers.uv.verify()
            bm.faces.layers.tex.verify()  # currently blender needs both layers.
            for f in bm.faces:
                if f.select:
                    bpy.ops.uv.select_all(action='SELECT')
                    matIndex = f.material_index
                    if len(obj.data.materials) > matIndex:
                        if obj.data.materials[matIndex] is not None:
                            if context.active_object.data.materials[matIndex].active_texture:
                                try:
                                    textureWidth = context.active_object.data.materials[matIndex].active_texture.image.size[0]
                                    textureHeight = context.active_object.data.materials[matIndex].active_texture.image.size[1]
                                except:
                                    pass
                                nX = f.normal.x
                                nY = f.normal.y
                                nZ = f.normal.z
                                if nX < 0:
                                    nX = nX * -1
                                if nY < 0:
                                    nY = nY * -1
                                if nZ < 0:
                                    nZ = nZ * -1
                                faceNormalLargest = nX
                                faceDirection = "x"
                                if faceNormalLargest < nY:
                                    faceNormalLargest = nY
                                    faceDirection = "y"
                                if faceNormalLargest < nZ:
                                    faceNormalLargest = nZ
                                    faceDirection = "z"
                                if faceDirection == "x":
                                    if f.normal.x < 0:
                                        faceDirection = "-x"
                                if faceDirection == "y":
                                    if f.normal.y < 0:
                                        faceDirection = "-y"
                                if faceDirection == "z":
                                    if f.normal.z < 0:
                                        faceDirection = "-z"
                                if self.axis == "X":
                                    faceDirection = "x"
                                if self.axis == "Y":
                                    faceDirection = "y"
                                if self.axis == "Z":
                                    faceDirection = "z"
                                if self.axis == "-X":
                                    faceDirection = "-x"
                                if self.axis == "-Y":
                                    faceDirection = "-y"
                                if self.axis == "-Z":
                                    faceDirection = "-z"
                                for l in f.loops:
                                    luv = l[uv_layer]
                                    if luv.select and l[uv_layer].pin_uv is not True:
                                        if faceDirection == "x":
                                            luv.uv.x = ((l.vert.co.y * objectScale[1]) + objectLocation[
                                                1]) * texelDensity / textureWidth
                                            luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[
                                                2]) * texelDensity / textureWidth
                                        if faceDirection == "-x":
                                            luv.uv.x = (((l.vert.co.y * objectScale[1]) + objectLocation[
                                                1]) * texelDensity / textureWidth) * -1
                                            luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[
                                                2]) * texelDensity / textureWidth
                                        if faceDirection == "y":
                                            luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[
                                                0]) * texelDensity / textureWidth) * -1
                                            luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[
                                                2]) * texelDensity / textureWidth
                                        if faceDirection == "-y":
                                            luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[
                                                0]) * texelDensity / textureWidth
                                            luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[
                                                2]) * texelDensity / textureWidth
                                        if faceDirection == "z":
                                            luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[
                                                0]) * texelDensity / textureWidth
                                            luv.uv.y = ((l.vert.co.y * objectScale[1]) + objectLocation[
                                                1]) * texelDensity / textureWidth
                                        if faceDirection == "-z":
                                            luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[
                                                0]) * texelDensity / textureWidth) * 1
                                            luv.uv.y = (((l.vert.co.y * objectScale[1]) + objectLocation[
                                                1]) * texelDensity / textureWidth) * -1
                                        luv.uv.x = luv.uv.x - context.scene.offset_x
                                        luv.uv.y = luv.uv.y - context.scene.offset_y
            bmesh.update_edit_mesh(me)
            if was_obj_mode:
                bpy.ops.object.editmode_toggle()
        return {"FINISHED"}


# TEXTURE BUDDY PIN OPERATOR CLASS       
class TextureBuddyPin(bpy.types.Operator):
    bl_idname = "object.texture_buddy_pin"
    bl_label = "Texture Buddy Pin"

    p = bpy.props.BoolProperty(name="tp", default=True)

    # EXECUTE THE OPERATOR
    def execute(self, context):
        obj = bpy.context.object
        if obj.mode == "EDIT":
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            uv_layer = bm.loops.layers.uv.verify()
            bm.faces.layers.tex.verify()
            bpy.ops.uv.pin(clear=self.p)
            bmesh.update_edit_mesh(me)
        return {"FINISHED"}


# TEXTURE BUDDY NUDGE OPERATOR CLASS        
class TextureBuddyNudge(bpy.types.Operator):
    bl_idname = "object.texture_buddy_nudge"
    bl_label = "Texture Buddy Nudge"

    dir = bpy.props.StringProperty(name="Some Floating Point", default="LEFT")

    # EXECUTE THE OPERATOR
    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()
        bm.faces.layers.tex.verify()  # currently blender needs both layers.

        # adjust UVs on all selected faces
        for f in bm.faces:

            # is this face currently selected?
            if f.select:
                # make sure that all the uvs for the face are selected
                bpy.ops.uv.select_all(action='SELECT')

                # loop through the face uvs
                for l in f.loops:
                    luv = l[uv_layer]
                    # only work on the selected UV layer
                    if luv.select:
                        if self.dir == "LEFT":
                            luv.uv.x = luv.uv.x + context.scene.nudge_amount
                        if self.dir == "RIGHT":
                            luv.uv.x = luv.uv.x - context.scene.nudge_amount
                        if self.dir == "UP":
                            luv.uv.y = luv.uv.y - context.scene.nudge_amount
                        if self.dir == "DOWN":
                            luv.uv.y = luv.uv.y + context.scene.nudge_amount
                        if self.dir == "HORIZONTAL":
                            luv.uv.x = luv.uv.x * -1
                        if self.dir == "VERTICAL":
                            luv.uv.y = luv.uv.y * -1

        # update the mesh
        bmesh.update_edit_mesh(me)
        return {"FINISHED"}


'''===================================================='''
''' REGISTER CLASSES                                   '''
'''===================================================='''


def register():
    bpy.utils.register_class(TextureBuddyPanel)
    bpy.utils.register_class(TextureBuddyUV)
    bpy.utils.register_class(TextureBuddyNudge)
    bpy.utils.register_class(TextureBuddyPin)


'''===================================================='''
''' UNREGISTER CLASSES                                '''
'''===================================================='''


def unregister():
    bpy.utils.unregister_class(TextureBuddyPanel)
    bpy.utils.unregister_class(TextureBuddyUV)
    bpy.utils.unregister_class(TextureBuddyNudge)
    bpy.utils.unregister_class(TextureBuddyPin)


if __name__ == "__main__":
    register()
