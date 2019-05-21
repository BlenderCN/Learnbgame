import bpy
from bpy.app.handlers import persistent
from bpy_extras.object_utils import world_to_camera_view

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

# AUTHOR: Eugenio Pignataro (Oscurart) www.oscurart.com.ar


bl_info = {
    "name": "Automatic Render Border",
    "author": "Eugenio Pignataro (Oscurart)",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "Properties > Render > Automatic Render Border",
    "description": "Set Render Border Automatically",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
    }

bpy.types.Scene.automatic_render_border_margin = \
    bpy.props.FloatProperty(default=0, min=0, max=1)


class AutomaticRenderBorder(bpy.types.Panel):
    bl_label = "Automatic Render Border"
    bl_idname = "RENDER_PT_renderBorder"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("render.automatic_render_border",
                     text="Play / Stop", icon="TRIA_RIGHT")
        row.operator("render.automatic_render_border_set",
                     text="Manual Set", icon="STYLUS_PRESSURE")
        row = layout.row()
        row.prop(bpy.context.scene,
                 "automatic_render_border_margin", text="Margin")


def autoCrop(dummy):
    margin = bpy.context.scene.automatic_render_border_margin
    sc = bpy.context.scene
    sc.render.use_border = True
    x, y = [], []
    objetos = [bpy.context.visible_objects[:] if len(
        bpy.context.selected_objects) == 0 else
        bpy.context.selected_objects[:]]
    for ob in objetos[0]:
        if ob.type in ["MESH", "FONT", "CURVE", "META"] and ob.is_visible(sc):
            nmesh = ob.to_mesh(sc, True, "RENDER")
            for vert in nmesh.vertices:
                gl = ob.matrix_world * vert.co
                cc = world_to_camera_view(sc, sc.camera, gl)
                x.append(cc[0])
                y.append(cc[1])
            bpy.data.meshes.remove(nmesh)
        if ob.dupli_type == "GROUP" and ob.type == "EMPTY":
            for iob in ob.dupli_group.objects:
                if iob.type == "MESH" and ob.is_visible(sc):
                    nmesh = iob.to_mesh(sc, True, "RENDER")
                    for vert in nmesh.vertices:
                        gl = ob.matrix_world * iob.matrix_world * vert.co
                        cc = world_to_camera_view(sc, sc.camera, gl)
                        x.append(cc[0])
                        y.append(cc[1])
                    bpy.data.meshes.remove(nmesh)
    x.sort()
    y.sort()
    sc.render.border_min_x = x[0] - margin
    sc.render.border_max_x = x[-1] + margin
    sc.render.border_min_y = y[0] - margin
    sc.render.border_max_y = y[-1]+margin
    del x
    del y


@persistent
def AutomaticRenderToggle(context):
    global a
    try:
        bpy.app.handlers.scene_update_post.remove(
            bpy.app.handlers.scene_update_post[-1])
    except:
        bpy.app.handlers.scene_update_post.append(autoCrop)


class ClassAutomaticRenderBorder(bpy.types.Operator):
    """Set render border automatically."""
    bl_idname = "render.automatic_render_border"
    bl_label = "Automatic Render Border"

    def execute(self, context):
        AutomaticRenderToggle(context)
        return {'FINISHED'}


class ClassAutomaticRenderBorderSet(bpy.types.Operator):
    """Set render border manually. Good for heavy scenes."""
    bl_idname = "render.automatic_render_border_set"
    bl_label = "Automatic Render Border Set"

    def execute(self, context):
        autoCrop(1)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AutomaticRenderBorder)
    bpy.utils.register_class(ClassAutomaticRenderBorder)
    bpy.utils.register_class(ClassAutomaticRenderBorderSet)


def unregister():
    bpy.utils.unregister_class(AutomaticRenderBorder)
    bpy.utils.unregister_class(ClassAutomaticRenderBorder)
    bpy.utils.register_class(ClassAutomaticRenderBorderSet)

if __name__ == "__main__":
    register()

