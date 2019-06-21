import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
import bmesh
import mathutils
from ..utils.support import get_distance_between_verts
from ..utils.ui import draw_init, draw_end, draw_title, draw_prop, wrap_mouse
from ..utils.developer import output_traceback
from ..utils import MACHIN3 as m3


# TODO: can you flatten the turned poly, maybe partly?
# TODO: chose new_c1 based on loops, not distance


class OperatorSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'count']:
                continue
            try:
                self.__class__._settings[d] = self.properties[d]
            except KeyError:
                # catches __doc__ etc.
                continue

    def load_settings(self):
        # what exception could occur here??
        for d in self.__class__._settings:
            self.properties[d] = self.__class__._settings[d]


class Turn_Corner(bpy.types.Operator, OperatorSettings):
    bl_idname = "machin3.turn_corner"
    bl_label = "MACHIN3: Turn Corner"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Redirect Chamfer Flow"

    width = FloatProperty(name="Width", default=0.1, min=0.01, step=0.1)

    sharps = BoolProperty(name="Set Sharps", default=True)
    bweights = BoolProperty(name="Set Bevel Weights", default=False)
    bweight = FloatProperty(name="Weight", default=1, min=0, max=1)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "width")

        column.prop(self, "sharps")

        row = column.row()
        row.prop(self, "bweights")
        row.prop(self, "bweight")

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        faces = [f for f in bm.faces if f.select]
        verts = [v for v in bm.verts if v.select]

        if len(faces) == 1 and len(verts) == 4:
            v3s = [v for v in verts if len(v.link_edges) == 3]
            v4s = [v for v in verts if len(v.link_edges) == 4]
            return len(v3s) == len(v4s) == 2

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Turn Corner")

        draw_prop(self, "Turn", self.count, key="scroll UP/DOWN")
        draw_prop(self, "Width", self.width, offset=18, key="move LEFT/RIGHT")
        self.offset += 10

        draw_prop(self, "Set Sharps", self.sharps, offset=18, key="toggle S")
        draw_prop(self, "Set BWeights", self.bweights, offset=18, key="toggle B")
        if self.bweights:
            draw_prop(self, "BWeight", self.bweight, offset=18, decimal=1, key="ALT scroll UP/DOWN")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        if event.type in ['MOUSEMOVE', 'WHEELUPMOUSE', 'UP_ARROW', 'ONE', 'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO', 'S', 'B']:

            # CONTROL width and corner/count

            if event.type == 'MOUSEMOVE':
                wrap_mouse(self, context, event, x=True)

                delta = self.mouse_x - self.init_mouse_x  # bigger if going to the right
                self.width = self.init_width + delta * 0.001

            elif event.type in {"WHEELUPMOUSE", 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
                if event.alt:
                    self.bweight += 0.1
                else:
                    self.count += 1
                    if self.count > 2:
                        self.count = 1

            elif event.type in {"WHEELDOWNMOUSE", 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
                if event.alt:
                    self.bweight -= 0.1
                else:
                    self.count -= 1
                    if self.count < 1:
                        self.count = 2

            # TOGGLE sharps and bweights

            elif event.type == 'S' and event.value == "PRESS":
                self.sharps = not self.sharps

            elif event.type == 'B' and event.value == "PRESS":
                self.bweights = not self.bweights

            # modal turn corner
            try:
                self.ret = self.main(self.active, modal=True)

                # success
                if self.ret:
                    self.save_settings()
                # caught an error
                else:
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

        elif event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel_modal(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

        m3.set_mode("OBJECT")
        self.initbm.to_mesh(self.active.data)
        m3.set_mode("EDIT")

    def invoke(self, context, event):
        self.load_settings()

        # make sure the current edit mode state is saved to obj.data
        context.object.update_from_editmode()

        # save this initial mesh state, this will be used when canceling the modal and to reset it for each mousemove event
        self.initbm = bmesh.new()
        self.initbm.from_mesh(context.object.data)

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        self.init_width = self.width
        self.count = 1

        self.active = m3.get_active()

        args = (self, context)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.count = 1
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

        if modal:
            self.initbm.to_mesh(active.data)

        # run the following 1 or 2 times
        for i in range(self.count):
            # create bmesh
            bm = bmesh.new()
            bm.from_mesh(active.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            bw = bm.edges.layers.bevel_weight.verify()

            verts = [v for v in bm.verts if v.select]
            # edges = [e for e in bm.edges if e.select]
            faces = [f for f in bm.faces if f.select]

            new_edges = turn_corner(bm, verts, faces, self.width, debug=debug)

            if any([self.sharps, self.bweights]):
                if self.sharps:
                    bpy.context.object.data.show_edge_sharp = True
                if self.bweights:
                    bpy.context.object.data.show_edge_bevel_weight = True

                for e in new_edges:
                    if self.sharps:
                        e.smooth = False
                    if self.bweights:
                        e[bw] = self.bweight

            bm.to_mesh(active.data)

        m3.set_mode("EDIT")
        # m3.set_mode("VERT")

        if new_edges:
            return True

        return False


def turn_corner(bm, verts, faces, width, debug=False):
    if debug:
        print()

    #     |       |
    #     |       |
    #    c3 ----- c4
    #   / \       / \
    #  /   c1 - c2   \
    #     /      \
    #    /        \

    # get the "inner edge", it doesnt have to be the shortest one, but its the one where both verts have 3 connecting edges

    # get the selected face
    sel_face = faces[0]

    # the verts on the "shorter edge"(they dont have to be physically shorert necessarily)
    inner_verts = [v for v in verts if len(v.link_edges) == 3]

    c1 = inner_verts[0]
    c2 = inner_verts[1]

    # this vertex selection is arbitary, as a result, the face rotation will be arbitary
    # so we need to ensure c1 is always the one on the bottom left
    # BMLoops seem to go counter clock wise, so check if the next vert in the c1_loop of sel_face is c2

    c1_loop = [l for l in c1.link_loops if l in sel_face.loops][0]

    if debug:
        print("c1 next loop vert:", c1_loop.link_loop_next.vert.index)

    # if the next vert is not c2, c1 is not the bottom right one and they both need to switch
    if not c1_loop.link_loop_next.vert == c2:
        c1, c2 = c2, c1
        if debug:
            print("switched c1 < > c2, to ensure clock-wise rotation")

    inner_edge = bm.edges.get([c1, c2])
    if debug:
        print("inner edge:", inner_edge.index)

    c1_edge = [e for e in c1.link_edges if e != inner_edge and e.select][0]
    c2_edge = [e for e in c2.link_edges if e != inner_edge and e.select][0]

    c3 = c1_edge.other_vert(c1)
    c4 = c2_edge.other_vert(c2)

    if debug:
        print("c1:", c1.index)
        print("c1_edge:", c1_edge.index)
        print("c3:", c3.index)

        print("c2:", c2.index)
        print("c2_edge:", c2_edge.index)
        print("c4:", c4.index)

    # we are now rebuilding the geo in a way that the shortest edge will be where currently c3 is
    c3_edges = [e for e in c3.link_edges if not e.select]

    # NOTE: these are chosen randomly, hence why we need to check for distances between coordinates based on these edges
    # TODO: you should try choosing these based on face loops as above
    c3_edge1 = c3_edges[0]
    c3_edge2 = c3_edges[1]

    # also get the "top edge"
    c3_c4_edge = bm.edges.get([c3, c4])

    if debug:
        c3_edge1.select = True
        c3_edge2.select = True
        print("c3 edge1:", c3_edge1.index)
        print("c3 edge2:", c3_edge2.index)
        print("c3 c4 edge:", c3_c4_edge.index)

    # rebuild all connected geo from scratch
    new_c1co = c3.co + (c3_edge1.other_vert(c3).co - c3.co).normalized() * width
    new_c2co = c3.co + (c3_edge2.other_vert(c3).co - c3.co).normalized() * width

    new_c1 = bm.verts.new()
    new_c1.co = new_c1co

    new_c2 = bm.verts.new()
    new_c2.co = new_c2co

    bm.verts.index_update()

    if debug:
        print("new_c1:", new_c1.index)
        print("new_c2:", new_c2.index)

    bm.edges.new([new_c1, new_c2])

    if get_distance_between_verts(c1, new_c1) < get_distance_between_verts(c1, new_c2):
        bm.edges.new([c1, new_c1])
        bm.edges.new([c4, new_c2])
    else:
        bm.edges.new([c1, new_c2])
        bm.edges.new([c4, new_c1])
        new_c1, new_c2 = new_c2, new_c1
        if debug:
            print("switched new_c1 < > new_c2")

    c1_remote_edge = [e for e in c1.link_edges if e != c1_edge and e != inner_edge][0]
    c2_remote_edge = [e for e in c2.link_edges if e != c2_edge and e != inner_edge][0]

    if debug:
        # c1_remote_edge.select = True
        # c2_remote_edge.select = True
        print("c1 remote edge:", c1_remote_edge.index)
        print("c2 remote edge:", c2_remote_edge.index)

    # get coordinates where c1 and c2 will be merged
    h = mathutils.geometry.intersect_line_line(c1.co, c1_remote_edge.other_vert(c1).co, c2.co, c2_remote_edge.other_vert(c2).co)

    # get the two bordering faces and the top face(connected to c3) as well, all three will be rebuilt
    # for consitency with QuadCorner() name them like this
    face_A = [f for f in c1_edge.link_faces if f != sel_face][0]
    face_B = [f for f in c3_c4_edge.link_faces if f != sel_face][0]
    face_N = [f for f in c3.link_faces if f not in [sel_face, face_A, face_B]][0]

    if debug:
        print("face_A face:", face_A.index)
        print("face_B face:", face_B.index)
        print("face_N:", face_N.index)

    # get the vert of these faces, that aren't connected to the sel_face
    new_sel_face_verts = [c1, new_c1, new_c2, c4]
    face_A_verts = [v for v in face_A.verts]
    face_B_verts = [v for v in face_B.verts]
    face_N_verts = [v for v in face_N.verts]

    if debug:
        print("old face A verts:", [v.index for v in face_A_verts])
        print("old face B verts:", [v.index for v in face_B_verts])
        print("old face N verts:", [v.index for v in face_N_verts])

    # replace c3 in face_A with tne new c1
    face_A_c3_index = face_A_verts.index(c3)

    face_A_verts.insert(face_A_c3_index, new_c1)
    face_A_verts.remove(c3)

    # replace c3 in face B with tne new c2
    face_B_c3_index = face_B_verts.index(c3)

    face_B_verts.insert(face_B_c3_index, new_c2)
    face_B_verts.remove(c3)

    # replace c3 in face N with [new_c1, new_c2]
    face_N_c3_index = face_N_verts.index(c3)

    face_N_verts[face_N_c3_index:face_N_c3_index] = [new_c1, new_c2]
    face_N_verts.remove(c3)

    if debug:
        print("new face A verts:", [v.index for v in face_A_verts])
        print("new face B verts:", [v.index for v in face_B_verts])
        print("new face N verts:", [v.index for v in face_N_verts])

    new_faces = []

    new_faces.append(bm.faces.new(new_sel_face_verts))
    new_faces.append(bm.faces.new(face_A_verts))
    new_faces.append(bm.faces.new(face_B_verts))
    new_faces.append(bm.faces.new(face_N_verts))

    # set the smoothing of the new faces
    for f in new_faces:
        f.smooth = sel_face.smooth

    # 1: DEL_VERTS, 2: DEL_EDGES, 3: DEL_ONLYFACES, 4: DEL_EDGESFACES, 5: DEL_FACES, 6: DEL_ALL, 7: DEL_ONLYTAGGED};
    # see https://blender.stackexchange.com/a/1542/33919 for context enum details
    bmesh.ops.delete(bm, geom=[sel_face, face_A, face_B, face_N], context=6)

    # merge c1 and c2
    bmesh.ops.pointmerge(bm, verts=[c1, c2], merge_co=h[0])

    bmesh.ops.recalc_face_normals(bm, faces=new_faces)

    # select the new corner polygon
    new_faces[0].select = True

    # get the new edges, so we can set sharps and beweights
    new_edges = [e for e in new_faces[0].edges]
    new_edges.extend([e for e in new_faces[1].edges if e in new_faces[-1].edges])
    new_edges.extend([e for e in new_faces[2].edges if e in new_faces[-1].edges])

    return new_edges
