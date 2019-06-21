import bpy
from bpy.props import IntProperty
import bmesh
import bgl
from .. utils.ui import draw_init, draw_end, draw_title, draw_prop
from .. utils.developer import output_traceback
from .. utils import MACHIN3 as m3


# TODO: vcreate


class VSelect(bpy.types.Operator):
    bl_idname = "machin3.vselect"
    bl_label = "MACHIN3: VSelect"
    bl_options = {'REGISTER', 'UNDO'}

    selidx = IntProperty(name="Selection Index")

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active.vertex_groups


    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Vertex Group Select")

        draw_prop(self, "Groups", "%d/%d" % (self.selidx + 1, len(self.groups["list"])), key="scroll UP/DOWN")
        self.offset += 10

        draw_prop(self, "Name", self.active.vertex_groups[self.gidx].name, offset=18)
        draw_prop(self, "Select", self.groups[self.gidx]["select"], offset=18, key="toggle individual S, toggle all A")
        # self.offset += 10

        draw_end()

    def draw_VIEW3D(self, args):
        white = (1, 1, 1)
        green = (0, 1, 0)
        alpha = 1
        pointcolor = (*white, alpha)
        greencolor = (*green, 1)

        mx = self.active.matrix_world


        bgl.glEnable(bgl.GL_BLEND)

        # if self.xray:
        bgl.glDisable(bgl.GL_DEPTH_TEST)


        # draw the vgroups groups marked as select in green
        bgl.glColor4f(*greencolor)
        bgl.glPointSize(8)
        bgl.glBegin(bgl.GL_POINTS)

        for group in self.green:
            for v in self.green[group]:
                # bring the coordinates into world space
                vco = mx * v.co

                bgl.glVertex3f(*vco)

        bgl.glEnd()

        # draw the currently selected/highlightes group of verts in white
        bgl.glColor4f(*pointcolor)
        bgl.glPointSize(4)
        bgl.glBegin(bgl.GL_POINTS)

        for v in self.groups[self.gidx]["verts"]:
            # bring the coordinates into world space
            vco = mx * v.co

            bgl.glVertex3f(*vco)


        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y


        if event.type in ['WHEELUPMOUSE', 'ONE', 'WHEELDOWNMOUSE', 'TWO']:

            # CHANGE vertex group selection

            if event.type in ['WHEELUPMOUSE', 'ONE'] and event.value == "PRESS":
                self.selidx += 1
            elif event.type in ['WHEELDOWNMOUSE', 'TWO'] and event.value == "PRESS":
                self.selidx -= 1

            # loop vertex groups
            if self.selidx > len(self.groups["list"]) - 1:
                self.selidx = 0
            elif self.selidx < 0:
                self.selidx = len(self.groups["list"]) - 1

            self.gidx = self.groups["list"][self.selidx]

        # TOGGLE per cgroup select state

        if event.type in ['S'] and event.value == "PRESS":
            self.groups[self.gidx]["select"] = not self.groups[self.gidx]["select"]

            if self.groups[self.gidx]["select"]:
                self.green[self.gidx] = self.groups[self.gidx]["verts"]
            else:
                self.green[self.gidx] = []

        # TOGGLE/INVERT all vgroups selected/unsellected

        elif event.type in ['A'] and event.value == "PRESS":
            for gidx in self.green:
                if self.green[gidx]:
                    self.green[gidx] = []
                    self.groups[gidx]["select"] = False
                else:
                    self.green[gidx] = self.groups[gidx]["verts"]
                    self.groups[gidx]["select"] = True


        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            self.select_vgroup(self.active)

            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.active = m3.get_active()

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        # get the selection, find the common vgroups, prepare self.groups dictionary
        try:
            self.ret = self.main(self.active)
        except:
            output_traceback(self)
            return {'FINISHED'}


        # if there's no vgroup, finish without doing anything
        if not self.ret:
            return {'FINISHED'}

        # if there's only one group, select an finish immedeately
        elif len(self.groups["list"]) == 1:
            self.green[self.gidx] = self.groups[self.gidx]["verts"]
            self.select_vgroup(self.active)
            return {'FINISHED'}

        # if there are multiple vgroups, run the modal, to select which ones should be selected
        else:
            args = (self, context)
            self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')
            self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

    def execute(self, context):
        active = m3.get_active()

        try:
            self.main(active)
        except:
            output_traceback(self)

        return {'FINISHED'}

    def main(self, active):
        debug = False
        # debug = True

        if debug:
            m3.clear()

        # all vgroup indices
        all_vgroups = set(range(len(active.vertex_groups)))

        # create bmesh
        self.bm = bmesh.from_edit_mesh(active.data)
        self.bm.normal_update()
        self.bm.verts.ensure_lookup_table()

        groups = self.bm.verts.layers.deform.verify()

        verts = [v for v in self.bm.verts if v.select]

        # get common vgroup indices of the selected verts
        if verts:
            # vgroups = self.get_common_vgroups(verts, all_vgroups, groups, debug=debug)
            vgroups = self.get_selected_vgroups(verts, groups, debug=debug)

        # if nothing is selected use all vgroup indices
        else:
            vgroups = list(all_vgroups)

        if vgroups:
            # loop vertex groups
            if self.selidx > len(vgroups) - 1:
                self.selidx = 0
            elif self.selidx < 0:
                self.selidx = len(vgroups) - 1


            # create a dict with group idx keys, and verts + select bool as attributes
            # also add a simple group list used with the selidx prop
            self.groups = {"list": vgroups}

            # create a similar dict for groups marked as select in the modal
            self.green = {}

            for vg in vgroups:
                self.groups[vg] = {}
                self.groups[vg]["verts"] = []
                self.groups[vg]["select"] = False
                self.green[vg] = []

            self.gidx = self.groups["list"][self.selidx]

            for v in self.bm.verts:
                for vg in vgroups:
                    if vg in v[groups]:
                        self.groups[vg]["verts"].append(v)


            # select
            # self.select_vgroup(active)

            return True
        else:
            return False

    def select_vgroup(self, active):
        for group in self.green:
            for v in self.green[group]:
                v.select = True

        self.bm.select_flush(True)

        bmesh.update_edit_mesh(active.data)


    def get_selected_vgroups(self, verts, deform_layer, debug=False):
        # update the set for each vert in the selection, only leaving the groups common to all of them
        selected = []
        for v in verts:
            selected.extend(v[deform_layer].keys())

        # make unique
        selected = list(set(selected))

        if debug:
            print(" » selected vgroups:", selected)

        return selected


    def get_common_vgroups(self, verts, vgroups, deform_layer, debug=False):
        if debug:
            print(" » all vgroups:", vgroups)

        # update the set for each vert in the selection, only leaving the groups common to all of them
        for v in verts:
            vgroups.intersection_update(set(v[deform_layer].keys()))

        if debug:
            print(" » common vgroups:", vgroups)

        return list(vgroups)
