bl_info = {
    "name": "Color Edges",
    "description": "Sample script for editing and displaying customlayer data.",
    "author": "Adam Newgas",
    "version": (1, 0, 0),
    "blender": (2, 74, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame"
}

import bpy
import bgl
import blf
import bmesh
import itertools
from bgl import  GL_LINES, GL_FLOAT

# Custom layer definitions

def get_edgecolor_layer(bm, create=False):
    r = bm.edges.layers.int.get("edgecolor")
    if r is None and create:
        r = bm.edges.layers.int.new("edgecolor")
    return r


color_enum = [("NONE","None","", 0),
              ("RED", "Red","Colors the given edge red", 1),
              ("GREEN", "Green","Colors the given edge green", 2),
              ("BLUE", "Blue","Colors the given edge blue", 3),
              ]

color_enum_to_int = {item[0]: item[3] for item in color_enum}

colors = [None, [1,0,0], [0,1,0],[0,0,1]]

# Drawing code

callback_handle = [None]

def tag_redraw_all_view3d():
    context = bpy.context

    # Py cant access notifers
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


def enable_color_draw_callback():
    if callback_handle[0]:
        return

    handle_view = bpy.types.SpaceView3D.draw_handler_add(draw_callback_view, (), 'WINDOW', 'POST_VIEW')
    callback_handle[0] = handle_view

    tag_redraw_all_view3d()


def disable_color_draw_callback():
    if not callback_handle[0]:
        return

    handle_view, = callback_handle
    bpy.types.SpaceView3D.draw_handler_remove(handle_view, 'WINDOW')
    callback_handle[0] = None

    tag_redraw_all_view3d()


def draw_callback_view():
    context = bpy.context
    if context.mode != "EDIT_MESH":
        return
    ob = context.active_object
    if ob is None:
        return
    if ob.type != "MESH":
        return
    if ob.mode != "EDIT":
        return
    if False:
        # Respects modifiers, but not hidden edges
        ob.update_from_editmode()
        bm = bmesh.new()
        bm.from_object(ob, context.scene)
    else:
        # Faster bmesh access, but doesn't respect modifiers
        bm = bmesh.from_edit_mesh(ob.data)
    layer = get_edgecolor_layer(bm)
    if layer is None:
        return
    bgl.glLineWidth(3.0)
    bgl.glPushMatrix()
    b = bgl.Buffer(GL_FLOAT, [16], list(itertools.chain(*ob.matrix_world.col)))
    bgl.glMultMatrixf(b)
    for edge in bm.edges:
        if edge.hide: continue
        color_int = edge[layer]
        if color_int == 0: continue
        bgl.glColor3f(*colors[color_int])
        bgl.glBegin(GL_LINES)
        for v in edge.verts:
            bgl.glVertex3f(*v.co)
        bgl.glEnd()
    bgl.glPointSize(1.0)
    bgl.glLineWidth(1.0)
    bgl.glPopMatrix()

def set_edge_color_visible_property(self, context):
    print("asdf",self.edge_color_visible)
    if self.edge_color_visible:
        enable_color_draw_callback()
    else:
        disable_color_draw_callback()



# Define operators

# A clone of WM_menu_invoke, which Blender doesn't expose to the UI
def menu_invoke(operator, context):
    def draw(self, context):
        self.layout.operator_context = "EXEC_REGION_WIN"
        self.layout.operator_enum(operator.bl_idname, "type")
    context.window_manager.popup_menu(draw, operator.bl_label)
    return {"INTERFACE"}

class ColorEdgesOperator(bpy.types.Operator):
    """Sets the edge color for selected edges"""
    bl_idname = "view3d.color_edges"
    bl_label = "Color Edges"
    bl_options = {'REGISTER', 'UNDO'}

    type = bpy.props.EnumProperty(items=color_enum,
                                  name="Color",
                                  description="Controls what color the edges will be colored")

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ((ob is not None) and
                (ob.mode == "EDIT") and
                (ob.type == "MESH") and
                (context.mode == "EDIT_MESH"))

    def execute(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        layer = get_edgecolor_layer(bm, create=True)
        has_selected_edges = False
        for edge in bm.edges:
            if edge.select:
                edge[layer] = color_enum_to_int[self.type]
                has_selected_edges = True
        if not has_selected_edges:
            self.report({"WARNING"}, "No edges selected")
        bmesh.update_edit_mesh(obj.data, destructive=False)
        return {"FINISHED"}

    def invoke(self, context, event):
        return menu_invoke(self, context)

class ColorEdgesPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Color Edges Panel"
    bl_idname = "OBJECT_PT_color_edges"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "edge_color_visible")
        layout.operator("view3d.color_edges")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.edge_color_visible = (
        bpy.props.BoolProperty(name = "Edge Color Visible",
                               description="If true, custom edge colors will be displayed in Edit Mode",
                               default=False,
                               update=set_edge_color_visible_property))
    # Probably not a good a good idea for a real script
    # But I want to get people on their feet quickly
    enable_color_draw_callback()

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.edge_color_visible
    disable_color_draw_callback()

if __name__ == "__main__":
    register()