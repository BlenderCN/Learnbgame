import bpy
import bgl
from bpy.props import FloatProperty, EnumProperty, BoolProperty
import bmesh
import math
import mathutils
from ..utils.developer import output_traceback
from ..utils.graph import build_mesh_graph
from ..utils.core import get_2_rails, get_selection_islands
from ..utils.normal import normal_clear, normal_transfer_from_stash, loopmapping, normal_clear_across_sharps
from ..utils.support import get_edge_normal, add_vgroup
from ..utils.ui import wrap_mouse, draw_init, draw_title, draw_prop, draw_end, popup_message, step_collection, step_enum
from ..utils import MACHIN3 as m3


thresholdpresetsitems = [("CUSTOM", "Custom", ""),
                         ("5", "5", ""),
                         ("15", "15", ""),
                         ("30", "30", ""),
                         ("60", "60", ""),
                         ("90", "90", "")]


# TODO: Mirror custom normals tool?

class FlattenSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'allowmodalthreshold']:
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


class NormalFlatten(bpy.types.Operator, FlattenSettings):
    bl_idname = "machin3.normal_flatten"
    bl_label = "MACHIN3: Normal Flatten"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Flatten uneven shading on (mostly) ngons"

    normalthreshold = FloatProperty(name="Angle Threshold", default=15, min=0)
    normalthreshold_preset = EnumProperty(name="Angle Threshold Presets", items=thresholdpresetsitems, default="CUSTOM")

    clear = BoolProperty(name="Clear Existing Normals", default=False)

    # modal
    allowmodalthreshold = BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "normalthreshold")

        row = column.row()
        row.prop(self, "normalthreshold_preset", expand=True)

        # column.separator()
        # column.prop(self, "clear")

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        return len([f for f in bm.faces if f.select]) >= 1

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Normal Flatten")

        draw_prop(self, "Angle Threshold", self.normalthreshold, active=self.allowmodalthreshold, key="move LEFT/RIGHT, toggle A, reset ALT + A, presets %s, X, C, V, B" % ("Z" if m3.MM_prefs().keyboard_layout == "QWERTY" else "Y"))
        # self.offset += 10

        # draw_prop(self, "Clear Existing", self.clear, offset=18, key="toggle R")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['A', 'R', 'Y', 'Z', 'X', 'C', 'V', 'B']

        # only consider MOUSEMOVE as a trigger for main(), when modalthreshold is actually active
        if self.allowmodalthreshold:
            events.append('MOUSEMOVE')

        if event.type in events:

            # CONTROL width and tension

            if event.type == 'MOUSEMOVE':
                delta_x = self.mouse_x - self.init_mouse_x  # bigger if going to the right

                if self.allowmodalthreshold:
                    wrap_mouse(self, context, event, x=True)

                    self.normalthreshold_preset = "CUSTOM"
                    self.normalthreshold = delta_x * 0.1 + self.init_threshold

            # SET threshold presets

            elif (event.type == 'Y' and event.value == "PRESS") or (event.type == 'Z' and event.value == "PRESS"):
                self.normalthreshold_preset = "5"

            elif event.type == 'X' and event.value == "PRESS":
                self.normalthreshold_preset = "15"

            elif event.type == 'C' and event.value == "PRESS":
                self.normalthreshold_preset = "30"

            elif event.type == 'V' and event.value == "PRESS":
                self.normalthreshold_preset = "60"

            elif event.type == 'B' and event.value == "PRESS":
                self.normalthreshold_preset = "90"

            # TOGGLE modal normal threshold and clear

            elif event.type == 'A' and event.value == "PRESS":
                if event.alt:
                    self.allowmodalthreshold = False
                    self.normalthreshold = self.init_threshold
                else:
                    self.allowmodalthreshold = not self.allowmodalthreshold

            elif event.type == 'R' and event.value == "PRESS":
                self.clear = not self.clear

            # modal normal flatten
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
                mode = m3.get_mode()
                if mode == "OBJECT":
                    m3.set_mode("EDIT")
                return {'FINISHED'}

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in {'LEFTMOUSE', 'SPACE'}:
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
        self.load_settings()

        self.active = m3.get_active()

        # make sure the current edit mode state is saved to obj.data
        self.active.update_from_editmode()

        # save this initial mesh state, this will be used when canceling the modal
        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        self.init_threshold = self.normalthreshold

        # first run, as there's no MOUSEMOVE event right away
        try:
            self.ret = self.main(self.active, modal=True)
            if self.ret:
                self.save_settings()
            else:
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
        if self.normalthreshold_preset != "CUSTOM":
            self.normalthreshold = float(self.normalthreshold_preset)

        debug = True
        debug = False

        if debug:
            m3.clear()
            m3.debug_idx()

        m3.set_mode("OBJECT")

        # reset the mesh the initial state
        if modal:
            self.initbm.to_mesh(active.data)

        mesh = active.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()

        # get existing loop normals
        mesh.calc_normals_split()

        loop_normals = []
        for loop in mesh.loops:
            loop_normals.append(loop.normal)

        # then change the ones we actually want to adjust
        faces = [f for f in bm.faces if f.select]

        if self.clear:
            for v in (v for v in bm.verts if v.select):
                for loop in v.link_loops:
                    loop_normals[loop.index] = mathutils.Vector()

        for f in faces:
            # print("face:", f.index, "normal:", f.normal)

            # first, get all bordering faces
            border_faces = []
            for v in f.verts:
                for face in v.link_faces:
                    if face not in border_faces and face != f:
                        border_faces.append(face)

            # do the faces directly connected to the selected face by an edge first
            edge_faces = []
            for bf in border_faces:
                for e in bf.edges:
                    if e in f.edges:
                        edge_faces.append(bf)
                        # if an edge is smooth and the angle is below the threshold, the edge face normals will be adjusted
                        if e.smooth and math.degrees(e.calc_face_angle()) < self.normalthreshold:
                            for loop in e.link_loops:
                                loop_normals[loop.index] = f.normal
                                loop_normals[loop.link_loop_next.index] = f.normal

            # then do the corner polygons, which are connected by a vert only
            for bf in border_faces:
                if bf not in edge_faces:
                    cf = bf
                    # if the corner polygon has no sharp edges and the face normal angle is below the threadshold...
                    if all([e.smooth for e in cf.edges]) and math.degrees(cf.normal.angle(f.normal)) < self.normalthreshold:
                        cv = [v for v in cf.verts if v in f.verts][0]
                        # print("corner face:", cf.index, "vert:", cv.index)
                        loop = [l for l in cv.link_loops if l in cf.loops][0]
                        loop_normals[loop.index] = f.normal

        # set the new normals
        mesh.normals_split_custom_set(loop_normals)
        mesh.use_auto_smooth = True

        m3.set_mode("EDIT")

        return True


class NormalStraighten(bpy.types.Operator):
    bl_idname = "machin3.normal_straighten"
    bl_label = "MACHIN3: Normal Straighten"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Straighten uneven shading on straight fuse surface sections"

    # TODO: make it work on cylinders/cyclic selections

    def draw(self, context):
        layout = self.layout

        column = layout.column()

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        return len([f for f in bm.faces if f.select]) >= 2

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

        # reset the mesh the initial state
        if modal:
            self.initbm.to_mesh(active.data)

        m3.set_mode("OBJECT")

        # get existing loop normals
        mesh = active.data
        mesh.calc_normals_split()

        loop_normals = []
        for loop in mesh.loops:
            loop_normals.append(loop.normal)

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()

        selected = [f for f in bm.faces if f.select]

        # get selection islands
        islands = get_selection_islands(bm, debug=debug)

        for verts, edges, faces in islands:
            # select only the current island
            for f in selected:
                if f in faces:
                    f.select_set(True)
                else:
                    f.select_set(False)

            mg = build_mesh_graph(bm, debug=debug)

            # get the rails of the selection, these are of course sweeps of the fuse
            ret = get_2_rails(bm, mg, verts, faces, False, debug=debug)

            if ret:
                rails, cyclic = ret

                for rail in rails:
                    # print()
                    # print(" » ".join([str(v.index) for v in rail[1:-1]]))

                    for idx, rv in enumerate(rail[1:-1]):
                        # print(" » rail vert", rv.index)
                        re = bm.edges.get([rv, rail[idx + 2]])  # + 1 because we start witht the second vert, and + 1 becuase we want the next vert
                        # print("  » rail edge", re.index)
                        if re.smooth:
                            fe = be = None
                            for e in rv.link_edges:
                                if e.other_vert(rv) in rail:
                                    continue
                                if e.select:
                                    fe = e
                                else:
                                    be = e
                            if fe and be:
                                # print("  » fuse edge", fe.index)
                                # print("  » border edge", be.index)
                                edge_normal = get_edge_normal(fe)

                                for loop in rv.link_loops:
                                    loop_normals[loop.index] = edge_normal

        # set the new normals
        mesh.normals_split_custom_set(loop_normals)
        mesh.use_auto_smooth = True
        # """

        # bm.to_mesh(active.data)

        m3.set_mode("EDIT")

        return True


mappingitems = [("NEAREST FACE", "Nearest Face Interpolated", ""),
                ("PROJECTED", "Projected Face Interpolated", ""),
                ("NEAREST NORMAL", "Nearest Corner and Best Matching Normal", ""),
                ("NEAREST POLY NORMAL", "Nearest Corner and Best Matching Face Normal", "")]


class NormalTransferSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type']:
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


class NormalTransfer(bpy.types.Operator, NormalTransferSettings):
    bl_idname = "machin3.normal_transfer"
    bl_label = "MACHIN3: Normal Transfer"
    bl_options = {'REGISTER'}
    bl_description = "Transfer Normals from Stash"

    mapping = EnumProperty("Mapping", items=mappingitems, default="NEAREST FACE")

    xray = BoolProperty(name="X-Ray", default=False)
    alpha = FloatProperty(name="Alpha", default=0.2, min=0.1, max=1)

    apply_data_transfer = BoolProperty(name="Apply Normal Transfer", default=True)
    remove_vgroup = BoolProperty(name="Remove Vertex Group", default=True)
    limit_by_sharps = BoolProperty(name="Limit by Sharps", default=True)

    # hidden
    debug = BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        active = bpy.context.active_object
        if active.MM.stashes:
            if active.mode == "EDIT":
                bm = bmesh.from_edit_mesh(active.data)
                return len([v for v in bm.verts if v.select]) >= 1

    def draw_VIEW3D(self, args):
        if self.stash.obj:
            mesh = self.stash.obj.data

            mx = self.active.matrix_world

            # offset amount depends on size of active object
            offset = sum([d for d in self.active.dimensions]) / 3 * 0.001

            alpha = self.alpha
            color = (1.0, 1.0, 1.0)

            edgecolor = (*color, alpha)
            edgewidth = 1

            bgl.glEnable(bgl.GL_BLEND)

            if self.xray:
                bgl.glDisable(bgl.GL_DEPTH_TEST)

            for edge in mesh.edges:
                v1 = mesh.vertices[edge.vertices[0]]
                v2 = mesh.vertices[edge.vertices[1]]

                # bring the coordinates into world space, and push the verts out a bit
                v1co = mx * (v1.co + v1.normal * offset)
                v2co = mx * (v2.co + v1.normal * offset)

                bgl.glLineWidth(edgewidth)
                bgl.glColor4f(*edgecolor)

                bgl.glBegin(bgl.GL_LINES)

                bgl.glVertex3f(*v1co)
                bgl.glVertex3f(*v2co)

            draw_end()

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Normal Transfer")

        draw_prop(self, "Stash", "%d/%d" % (self.stash.index + 1, len(self.active.MM.stashes)), key="scroll UP/DOWN")
        self.offset += 10

        if self.stash.obj:
            draw_prop(self, "Alpha", self.alpha, offset=18, key="ALT scroll UP/DOWN")
            draw_prop(self, "X-Ray", self.xray, offset=18, key="toggle X")
            self.offset += 10

            draw_prop(self, "Flipped", self.stash.flipped, offset=18, key="toggle F")
            # draw_prop(self, "Smooth", self.stash.flipped, offset=18, key="toggle S")
            self.offset += 10

            draw_prop(self, "Display", self.data_transfer.show_viewport, offset=18, key="toggle D")

            self.offset += 10
            draw_prop(self, "Mapping", self.mapping, offset=18, key="shift scroll UP/DOWN")
            draw_prop(self, "Apply Mod", self.apply_data_transfer, offset=18, key="toggle A")
            if self.apply_data_transfer:
                draw_prop(self, "Remove VGroup", self.remove_vgroup, offset=18, key="toggle R")
                draw_prop(self, "Limit by Sharps", self.limit_by_sharps, offset=18, key="toggle L")

        else:
            draw_prop(self, "INVALID", "Stash Object Not Found", offset=18, HUDcolor=(1, 0, 0))

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        # SELECT stash, CHANGE alpha

        if event.type in {'WHEELUPMOUSE', 'ONE'} and event.value == 'PRESS':
            if event.alt:
                self.alpha += 0.1
            elif event.shift:
                self.mapping = step_enum(self.mapping, mappingitems, 1)
                self.data_transfer.loop_mapping = loopmapping[self.mapping]
            else:
                self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", 1)
                self.data_transfer.object = self.stash.obj

        elif event.type in {'WHEELDOWNMOUSE', 'TWO'} and event.value == 'PRESS':
            if event.alt:
                self.alpha -= 0.1
            elif event.shift:
                self.mapping = step_enum(self.mapping, mappingitems, -1)
                self.data_transfer.loop_mapping = loopmapping[self.mapping]
            else:
                self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", -1)
                self.data_transfer.object = self.stash.obj

        # STASH OBJ

        if self.stash.obj:

            # TOGGLE normal flip

            if event.type == 'F' and event.value == 'PRESS':
                mesh = self.stash.obj.data

                bm = bmesh.new()
                bm.from_mesh(mesh)
                bm.normal_update()

                bmesh.ops.reverse_faces(bm, faces=bm.faces)
                bm.to_mesh(mesh)
                bm.free()

                # update stashobj's flipped prop
                self.stash.flipped = not self.stash.flipped

            if event.type == 'S' and event.value == 'PRESS':
                mesh = self.stash.obj.data

                bm = bmesh.new()
                bm.from_mesh(mesh)
                bm.normal_update()

                for face in bm.faces:
                    face.smooth = True

                if self.debug:
                    print(" » Applied smoothing to stash object")

                bm.to_mesh(mesh)
                bm.free()

            # TOGGLE display mod and xray

            elif event.type == 'X' and event.value == 'PRESS':
                self.xray = not self.xray

            elif event.type == 'D' and event.value == 'PRESS':
                self.data_transfer.show_viewport = not self.data_transfer.show_viewport

            # TOGGLE apply mod and remove vgroup

            elif event.type == 'A' and event.value == 'PRESS':
                self.apply_data_transfer = not self.apply_data_transfer

            elif event.type == 'R' and event.value == 'PRESS':
                self.remove_vgroup = not self.remove_vgroup

            elif event.type == 'L' and event.value == 'PRESS':
                self.limit_by_sharps = not self.limit_by_sharps

        # VIEWPORT control

        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

            if self.stash.obj:
                if self.apply_data_transfer:
                    if self.debug:
                        print(" » Applying modifier '%s' to object '%s'." % (self.data_transfer.name, self.active.name))

                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=self.data_transfer.name)

                    if self.remove_vgroup:
                        if self.debug:
                            print(" » Removing vertex group: %s" % (self.vgroup.name))
                        self.active.vertex_groups.remove(self.vgroup)

                    # clear normals across sharp edges
                    if self.limit_by_sharps:
                        normal_clear_across_sharps(self.active)

            else:
                if self.debug:
                    print(" » Removing modifier '%s' from object '%s'." % (self.data_transfer.name, self.active.name))
                self.active.modifiers.remove(self.data_transfer)

                if self.debug:
                    print(" » Removing vertex group: %s" % (self.vgroup.name))
                self.active.vertex_groups.remove(self.vgroup)


            m3.set_mode("EDIT")

            self.save_settings()
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

            if self.debug:
                print(" » Removing modifier '%s' from object '%s'." % (self.data_transfer.name, self.active.name))
            self.active.modifiers.remove(self.data_transfer)

            if self.debug:
                print(" » Removing vertex group: %s" % (self.vgroup.name))
            self.active.vertex_groups.remove(self.vgroup)

            m3.set_mode("EDIT")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.load_settings()

        self.active = m3.get_active()

        self.vgroup, self.data_transfer = normal_transfer_from_stash(self.active, mapping=self.mapping)
        self.stash = self.active.MM.stashes[self.active.MM.active_stash_idx]

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        args = (self, context)
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class NormalClear(bpy.types.Operator):
    bl_idname = "machin3.normal_clear"
    bl_label = "MACHIN3: Normal Clear"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Reset normals of the selected geometry, keep unselected geo as is"

    limit_to_selection = BoolProperty(name="Limit to Selection", default=False)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "limit_to_selection")

    @classmethod
    def poll(cls, context):
        mesh = context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)
        return mesh.has_custom_normals and len([v for v in bm.verts if v.select]) >= 1

    def execute(self, context):
        active = m3.get_active()

        try:
            normal_clear(active, limit=self.limit_to_selection)
        except:
            output_traceback(self)

        return {'FINISHED'}
