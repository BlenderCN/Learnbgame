# ##### BEGIN GPL LICENSE BLOCK #####
#
#  3dview_border_lines_bmesh_edition.py
#  Draw thicker lines for border edges - using bmesh in edit mode
#  Copyright (C) 2015 Quentin Wenger
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



bl_info = {"name": "Border Lines - BMesh Edition",
           "description": "Draw thicker lines for border edges; this is a version "\
                          "of the addon which should be faster than the original; "\
                          "it allows thick display of active edge color, but notof fancy "\
                          "edges (freestyle, crease, seam, sharp, etc.), which are "\
                          "nevertheless shown normally.",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 11),
           "blender": (2, 74, 0),
           "location": "3D View(s) -> Properties -> Shading",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "3D View"
           }



import bpy
from bpy_extras.mesh_utils import edge_face_count
from mathutils import Vector
from bgl import glBegin, glLineWidth, glColor3f, glColor4f, glVertex3f, glEnd, GL_LINES, glEnable, glDisable, GL_DEPTH_TEST
import bmesh

handle = []
bm_old = [None]


def drawColorSize(coords, color):
    glColor3f(*color[:3])
    for coord in coords:
        glVertex3f(*coord)

def drawCallback():
                    
    if bpy.context.mode == 'EDIT_MESH':

        obj = bpy.context.object

        bl = obj.border_lines
        if obj and obj.type == 'MESH' and obj.data:
            if bl.borderlines_use:
                mesh = obj.data
                matrix_world = obj.matrix_world
                settings = bpy.context.user_preferences.themes[0].view_3d

                transform = settings.transform
                edge_select = settings.edge_select
                wire_edit = settings.wire_edit
                wire = settings.wire
                object_active = settings.object_active

                glLineWidth(bl.borderlines_width)

                draw_with_test = True

                if bm_old[0] is None or not bm_old[0].is_valid:
                    bm = bm_old[0] = bmesh.from_edit_mesh(mesh)

                else:
                    bm = bm_old[0]


                no_depth = not bpy.context.space_data.use_occlude_geometry

                if no_depth:
                    glDisable(GL_DEPTH_TEST)

                    draw_with_test = False

                    if bl.finer_lines_behind_use:
                        glLineWidth(bl.borderlines_width/4.0)
                        draw_with_test = True

                    glBegin(GL_LINES)

                    if bl.custom_color_use:
                        glColor3f(*bl.custom_color)
                        for edge in bm.edges:
                            if edge.is_valid and edge.is_boundary:
                                coords = [matrix_world*vert.co for vert in edge.verts]
                                for coord in coords:
                                    glVertex3f(*coord)


                    else:
                        active = bm.select_history.active
                        for edge in bm.edges:
                            if edge.is_valid and edge.is_boundary and not edge.hide:
                                coords = [matrix_world*vert.co for vert in edge.verts]

                                if active == edge:
                                    drawColorSize(coords, transform)
                                elif edge.select:
                                    drawColorSize(coords, edge_select)
                                else:
                                    drawColorSize(coords, wire_edit)

                    glEnd()

                    glLineWidth(bl.borderlines_width)

                    glEnable(GL_DEPTH_TEST)


                if draw_with_test:

                    glBegin(GL_LINES)


                    if bl.custom_color_use:
                        glColor3f(*bl.custom_color)
                        for edge in bm.edges:
                            if edge.is_valid and edge.is_boundary:
                                coords = [matrix_world*vert.co for vert in edge.verts]
                                for coord in coords:
                                    glVertex3f(*coord)


                    else:
                        active = bm.select_history.active
                        for edge in bm.edges:
                            if edge.is_valid and edge.is_boundary:
                                coords = [matrix_world*vert.co for vert in edge.verts]

                                if active == edge:
                                    drawColorSize(coords, transform)
                                elif edge.select:
                                    drawColorSize(coords, edge_select)
                                else:
                                    drawColorSize(coords, wire_edit)

                    glEnd()

                        

    elif bpy.context.mode == 'OBJECT':
        for obj in bpy.context.visible_objects:
            if obj and obj.type == 'MESH' and obj.data:
                if (obj.show_wire or bpy.context.space_data.viewport_shade == 'WIREFRAME'):
                    bl = obj.border_lines

                    if bl.borderlines_use:
                        
                        mesh = obj.data
                        matrix_world = obj.matrix_world
                        settings = bpy.context.user_preferences.themes[0].view_3d

                        wire = settings.wire
                        object_selected = settings.object_selected

                        counts = edge_face_count(mesh)

                        glLineWidth(bl.borderlines_width)

                        glBegin(GL_LINES)

                        if bl.custom_color_use:
                            glColor3f(*bl.custom_color)
                        elif obj == bpy.context.active_object and obj.select:
                            glColor3f(*settings.object_active)
                        elif obj.select:
                            glColor3f(*settings.object_selected)
                        else:
                            glColor3f(*settings.wire)
                            
                        for edge, count in zip(mesh.edges, counts):
                            # border edges
                            if count == 1:
                                coords = [matrix_world*Vector(mesh.vertices[i].co) for i in edge.key]
                                for coord in coords:
                                    glVertex3f(*coord)
                            
                        glEnd()
        
    glLineWidth(1.0)


class BorderLinesCopyUseOperator(bpy.types.Operator):
    bl_idname = "object.border_lines_copy_use"
    bl_label = "Copy use"
    bl_description = "Copy 'use' setting to all objects in the scene"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        o = context.active_object
        for obj in context.scene.objects:
            # don't care about active object...
            obj.border_lines.borderlines_use = o.border_lines.borderlines_use
        context.area.tag_redraw()
        return {'FINISHED'}

class BorderLinesCopyWidthOperator(bpy.types.Operator):
    bl_idname = "object.border_lines_copy_width"
    bl_label = "Copy width"
    bl_description = "Copy 'width' setting to all objects in the scene"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        o = context.active_object
        for obj in context.scene.objects:
            # don't care about active object...
            obj.border_lines.borderlines_width = o.border_lines.borderlines_width
        context.area.tag_redraw()
        return {'FINISHED'}

class BorderLinesCopyFinerOperator(bpy.types.Operator):
    bl_idname = "object.border_lines_copy_finer"
    bl_label = "Copy finer lines"
    bl_description = "Copy 'finer lines' setting to all objects in the scene"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        o = context.active_object
        for obj in context.scene.objects:
            # don't care about active object...
            obj.border_lines.finer_lines_behind_use = o.border_lines.finer_lines_behind_use
        context.area.tag_redraw()
        return {'FINISHED'}

class BorderLinesCopyColorOperator(bpy.types.Operator):
    bl_idname = "object.border_lines_copy_color"
    bl_label = "Copy custom color"
    bl_description = "Copy 'custom color' setting to all objects in the scene"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        o = context.active_object
        for obj in context.scene.objects:
            # don't care about active object...
            obj.border_lines.custom_color = o.border_lines.custom_color
        context.area.tag_redraw()
        return {'FINISHED'}

class BorderLinesCopyCustomOperator(bpy.types.Operator):
    bl_idname = "object.border_lines_copy_custom"
    bl_label = "Copy custom color use"
    bl_description = "Copy 'custom color use' setting to all objects in the scene"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        o = context.active_object
        for obj in context.scene.objects:
            # don't care about active object...
            obj.border_lines.custom_color_use = o.border_lines.custom_color_use
        context.area.tag_redraw()
        return {'FINISHED'}

class BorderLinesCopySettingsOperator(bpy.types.Operator):
    bl_idname = "object.border_lines_copy_settings"
    bl_label = "Copy to all"
    bl_description = "Copy all Border Lines settings to all objects in the scene"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        o = context.active_object
        for obj in context.scene.objects:
            # don't care about active object...
            obj.border_lines.borderlines_use = o.border_lines.borderlines_use
            obj.border_lines.borderlines_width = o.border_lines.borderlines_width
            obj.border_lines.finer_lines_behind_use = o.border_lines.finer_lines_behind_use
            obj.border_lines.custom_color = o.border_lines.custom_color
            obj.border_lines.custom_color_use = o.border_lines.custom_color_use
        context.area.tag_redraw()
        return {'FINISHED'}


class BorderLinesCollectionGroup(bpy.types.PropertyGroup):
    borderlines_use = bpy.props.BoolProperty(
        name="Border Lines",
        description="Display border edges thicker",
        default=False)
    borderlines_width = bpy.props.FloatProperty(
        name="Width",
        description="Border lines width in pixels",
        min=1.0,
        max=10.0,
        default=3.0,
        subtype='PIXEL')
    finer_lines_behind_use = bpy.props.BoolProperty(
        name="Finer Lines behind",
        description="Display partially hidden border edges finer in non-occlude mode",
        default=True)
    custom_color = bpy.props.FloatVectorProperty(
        name="Custom Color",
        description="Unique Color to draw Border Lines with",
        min=0.0,
        max=1.0,
        default=(0.0, 1.0, 0.0),
        size=3,
        subtype='COLOR')
    custom_color_use = bpy.props.BoolProperty(
        name="Custom Color",
        description="Use a unique Color to draw Border Lines with",
        default=False)


def displayBorderLinesPanel(self, context):

    if context.active_object and context.active_object.type == 'MESH':
        border_lines = context.active_object.border_lines
    
        box = self.layout.box()

        split = box.split(percentage=0.8)

        col = split.column()
        col2 = split.column()

        col2.alignment = 'RIGHT'

        col.prop(border_lines, "borderlines_use")
        col2.operator("object.border_lines_copy_use", text="", icon='COPYDOWN')

        if border_lines.borderlines_use:
            
            col.prop(border_lines, "borderlines_width")
            col2.operator("object.border_lines_copy_width", text="", icon='COPYDOWN')
            col.prop(border_lines, "custom_color_use")
            col2.operator("object.border_lines_copy_custom", text="", icon='COPYDOWN')
            
            if border_lines.custom_color_use:
                split = col.split(percentage=0.1)    
                split.separator()
                split.prop(border_lines, "custom_color", text="")
                col2.operator("object.border_lines_copy_color", text="", icon='COPYDOWN')

            if context.mode == 'EDIT_MESH' and not context.space_data.use_occlude_geometry:
                col.prop(border_lines, "finer_lines_behind_use")
                col2.operator("object.border_lines_copy_finer", text="", icon='COPYDOWN')

        box.operator("object.border_lines_copy_settings", icon='COPYDOWN')
            
    

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.border_lines = bpy.props.PointerProperty(
        type=BorderLinesCollectionGroup)
    bpy.types.VIEW3D_PT_view3d_shading.append(displayBorderLinesPanel)
    if handle:
        bpy.types.SpaceView3D.draw_handler_remove(handle[0], 'WINDOW')
    handle[:] = [bpy.types.SpaceView3D.draw_handler_add(drawCallback, (), 'WINDOW', 'POST_VIEW')]

    

def unregister():
    bpy.types.VIEW3D_PT_view3d_shading.remove(displayBorderLinesPanel)
    del bpy.types.Object.border_lines
    if handle:
        bpy.types.SpaceView3D.draw_handler_remove(handle[0], 'WINDOW')
        handle[:] = []
    bpy.utils.unregister_module(__name__)
    

if __name__ == "__main__":
    register()
