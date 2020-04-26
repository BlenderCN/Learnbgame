import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
import bmesh
import mathutils
from .. utils.developer import output_traceback
from .. utils.ui import step_enum, draw_init, draw_end, draw_title, draw_prop
from .. utils import MACHIN3 as m3


flatten_mode_items = [("EDGE", "Along Edge", ""),
                      ("NORMAL", "Along Normal", "")]


class Flatten(bpy.types.Operator):
    bl_idname = "machin3.flatten"
    bl_label = "MACHIN3: Flatten"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Flatten Polygon(s) along Edges or Normal"

    flatten_mode = EnumProperty(name="Mode", items=flatten_mode_items, default="EDGE")

    dissolve = BoolProperty(name="Dissolve", default=True)

    # hidden
    face_mode = BoolProperty(name="Face Mode", default=False)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.prop(self, "flatten_mode", expand=True)

        if self.face_mode:
            column.prop(self, "dissolve")

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        return len([f for f in bm.faces if f.select]) >= 1 or len([v for v in bm.verts if v.select]) == 3  # it's >= so, redo works

    def draw_HUD(self, args):
        draw_init(self, args)

        subtitle = "Face mode" if self.face_mode else "Vert mode"

        draw_title(self, "Flatten", subtitle=subtitle, subtitleoffset=125)

        draw_prop(self, "Flatten Along", self.flatten_mode, key="scroll UP/DOWN")
        if self.face_mode:
            draw_prop(self, "Dissolve", self.dissolve, offset=18, key="toggle D")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'ONE', 'TWO', 'D']

        if event.type in events:

            if event.type in ['WHEELUPMOUSE', 'ONE'] and event.value == "PRESS":
                self.flatten_mode = step_enum(self.flatten_mode, flatten_mode_items, 1)

            elif event.type in ['WHEELDOWNMOUSE', 'TWO'] and event.value == "PRESS":
                self.flatten_mode = step_enum(self.flatten_mode, flatten_mode_items, -1)

            # TOGGLE dissolve

            elif event.type == 'D' and event.value == "PRESS":
                self.dissolve = not self.dissolve

            # modal flatten
            try:
                ret = self.main(self.active, modal=True)

                # caught and error
                if ret is False:
                    bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                    return {'FINISHED'}
            # unexpected error
            except:
                output_traceback(self)
                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                return {'FINISHED'}

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel_modal(self, removeHUD=True):
        if removeHUD:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

        m3.set_mode("OBJECT")
        self.initbm.to_mesh(self.active.data)
        m3.set_mode("EDIT")

    def invoke(self, context, event):
        self.active = m3.get_active()

        # make sure the current edit mode state is saved to obj.data
        self.active.update_from_editmode()

        # save this initial mesh state, this will be used when canceling the modal and to reset it for each mousemove event
        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        # initial run, because there's no mouse movement trigger
        try:
            self.ret = self.main(self.active, modal=True)
            if not self.ret:
                self.cancel_modal(removeHUD=False)
                return {'FINISHED'}
        except:
            output_traceback(self)
            mode = m3.get_mode()
            if mode == "OBJECT":
                m3.set_mode("EDIT")
            return {'FINISHED'}

        args = (self, context)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        active = m3.get_active()

        try:
            self.main(active)
        except:
            output_traceback(self)

        return {'FINISHED'}

    def main(self, active, modal=False):
        debug = True
        debug = False

        if debug:
            m3.clear()
            m3.debug_idx()

        m3.set_mode("OBJECT")

        # reset the mesh the initial state
        if modal:
            self.initbm.to_mesh(active.data)

        # create new bmesh
        bm = bmesh.new()
        bm.from_mesh(active.data)

        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]
        edges = [e for e in bm.edges if e.select]
        faces = [f for f in bm.faces if f.select]

        if len(faces) > 1:
            self.face_mode = True
            flatten_faces(bm, edges, self.flatten_mode, self.dissolve, debug=debug)
        else:
            self.face_mode = False
            flatten_verts(bm, verts, self.flatten_mode, debug=debug)

        bm.normal_update()
        bm.to_mesh(active.data)

        m3.set_mode("EDIT")
        return True


def flatten_verts(bm, verts, flatten_mode, debug=False):
    # find the face all 3 verts share
    face = [f for v in verts for f in v.link_faces if f in verts[0].link_faces and f in verts[1].link_faces and f in verts[2].link_faces][0]

    if debug:
        print("face:", face)

    # get the normal of the 3 verts:
    three_verts_normal = mathutils.geometry.normal(verts[0].co, verts[1].co, verts[2].co)

    # the other verts of the faces, the ones that aren't selected and should be flattened + their other verts
    vert_pairs = [(v, e.other_vert(v)) for v in face.verts if v not in verts for e in v.link_edges if e not in face.edges]

    if flatten_mode == "EDGE":
        # projection along edges
        flatten_along_edges(vert_pairs, verts[0].co, three_verts_normal, debug=debug)
    elif flatten_mode == "NORMAL":
        flatten_along_normal(bm, vert_pairs, verts[0].co, three_verts_normal, debug=debug)


def flatten_faces(bm, edges, flatten_mode, dissolve=True, debug=False):
    # get selction history
    hist = [f for f in bm.select_history]
    flat = hist[-1]
    faces = hist[0:-1]

    if debug:
        print("history:", hist)
        print("flat:", flat)
        print("faces:", faces)

    for face in faces:
        if debug:
            print("flat face:", flat)
            print("face to flatten:", face)

        vert_pairs = [(v, e.other_vert(v)) for v in face.verts for e in v.link_edges if e not in edges and v not in flat.verts]

        if flatten_mode == "EDGE":
            # projection along edges
            flatten_along_edges(vert_pairs, flat.verts[0].co, flat.normal, debug=debug)
        elif flatten_mode == "NORMAL":
            flatten_along_normal(bm, vert_pairs, flat.verts[0].co, flat.normal, debug=debug)


    if dissolve:
        newface = bmesh.ops.dissolve_faces(bm, faces=hist)["region"][0]
        newface.select = True


def flatten_along_normal(bm, vert_pairs, plane_co, plane_normal, debug=False):
    for v, otherv in vert_pairs:
        # create a verpendicula vector in each vert
        perpco = v.co + plane_normal

        if debug:
            perp = bm.verts.new()
            perp.co = perpco

        # intersect with the plane to get a point on it
        ico = mathutils.geometry.intersect_line_plane(v.co, perpco, plane_co, plane_normal)

        if debug:
            i = bm.verts.new()
            i.co = ico

        # adjust the vert position accordingly
        v.co = ico


def flatten_along_edges(vert_pairs, plane_co, plane_normal, debug=False):
    for v, otherv in vert_pairs:
        ico = mathutils.geometry.intersect_line_plane(v.co, otherv.co, plane_co, plane_normal)
        if ico:
            v.co = ico

        if debug:
            print(v.index, otherv.index, v.co)
            print(" » ", ico)
            print()
