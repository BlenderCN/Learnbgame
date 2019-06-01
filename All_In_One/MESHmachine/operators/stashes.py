import bpy
import blf
from bpy.props import BoolProperty, StringProperty, FloatProperty
import bgl
from .. utils.ui import draw_init, draw_end, draw_title, draw_prop, step_collection, popup_message
from .. utils.stash import create_stash, retrieve_stash, transfer_stashes
from .. utils import MACHIN3 as m3



class CreateStash(bpy.types.Operator):
    bl_idname = "machin3.create_stash"
    bl_label = "MACHIN3: Create Stash"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Stash the current state of an object"

    countdown = FloatProperty(name="Countdown (s)", default=2)

    remove_sources = BoolProperty(name="Remove Sources", default=False)

    def check(self, context):
        return True

    def draw_VIEW3D(self, args):
        stashingtype = self.stashret[0]
        if stashingtype == "ACTIVE":
            meshes = [self.active.data]
            color = (1, 1, 1)

        elif stashingtype == "OTHER":
            meshes = [obj.data for obj in self.stashret[2]]
            color = (1, 1, 0)

        alpha = self.countdown / self.time

        for mesh in meshes:
            mx = self.active.matrix_world

            # offset amount depends on size of active object
            offset = sum([d for d in self.active.dimensions]) / 3 * 0.001

            edgecolor = (*color, alpha)
            edgewidth = 2

            bgl.glEnable(bgl.GL_BLEND)

            # if self.xray:
                # bgl.glDisable(bgl.GL_DEPTH_TEST)

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

        # title
        alpha = self.countdown / self.time

        stashingtype = self.stashret[0]

        if stashingtype == "ACTIVE":
            title = "Created %s" % self.stashret[3]
        elif stashingtype == "OTHER":
            stashnames = self.stashret[3]
            if len(stashnames) == 1:
                title = "Created %s" % self.stashret[3][0]
            else:
                title = "Created %s..%s" % (self.stashret[3][0], self.stashret[3][-1])

        HUDcolor = m3.MM_prefs().modal_hud_color
        bgl.glColor4f(*HUDcolor, alpha)

        blf.position(self.font_id, self.HUDx - 7, self.HUDy, 0)
        blf.size(self.font_id, 16, 72)
        blf.draw(self.font_id, "» " + title)

        # stashes

        offset = self.offset + 0
        self.offset = offset
        blf.size(self.font_id, 11, 72)


        if stashingtype == "ACTIVE":
            bgl.glColor4f(1, 1, 1, alpha)

            msg = "from object %s" % (self.active.name)

            blf.position(self.font_id, self.HUDx + 20, self.HUDy - 20 - offset, 0)
            blf.draw(self.font_id, msg)

        elif stashingtype == "OTHER":
            bgl.glColor4f(1, 1, 0, alpha)

            stashobjnames = self.stashret[1]

            for name in stashobjnames:
                msg = "from object %s" % (name)

                blf.position(self.font_id, self.HUDx + 20, self.HUDy - 20 - offset, 0)
                blf.draw(self.font_id, msg)

                self.offset += 18
                offset = self.offset

            draw_prop(self, "Remove Sources", self.remove_sources, offset=18, key="press D")


        draw_end()

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "remove_sources")

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y


        if event.type == "D" and event.value == "PRESS":
            # don't do anything
            if event.shift or event.alt or event.ctrl or not self.sources:
                return {'PASS_THROUGH'}

            # hide/unhide sources to pretend they are removed already, when they only actually get removed once the counter ran out
            else:
                self.remove_sources = not self.remove_sources

                for obj in self.sources:
                    obj.hide = self.remove_sources

                return {'RUNNING_MODAL'}

        # FINISH when countdown is 0

        if self.countdown < 0:
            # print("Countdown of %d seconds finished" % (self.time))

            # remove time handler
            context.window_manager.event_timer_remove(self.TIMER)

            # remove draw handlers
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')

            # remove sources
            if self.remove_sources:
                for obj in self.sources:
                    bpy.data.objects.remove(obj, do_unlink=True)

            return {'FINISHED'}

        # COUNT DOWN

        if event.type == 'TIMER':
            self.countdown -= 0.1

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.active = m3.get_active()

        # create the stash
        self.stashret = self.main(context, self.active)

        # get source objects
        if self.stashret[0] == "OTHER":
            sourcenames = self.stashret[1]

            self.sources = [bpy.data.objects.get(name) for name in sourcenames]

            # hide them based on the remove_sources prop
            for obj in self.sources:
                obj.hide = self.remove_sources
        else:
            self.sources = []

        self.time = self.countdown

        # # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        # draw handler
        args = (self, context)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')

        # time handler
        self.TIMER = context.window_manager.event_timer_add(0.1, context.window)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.active = m3.get_active()

        # create the stash
        self.main(context, self.active)

        return {'FINISHED'}

    def main(self, context, active):
        mode = active.mode
        sel = context.selected_objects

        print()
        print("%s's stashes" % (active.name))
        for s in active.MM.stashes:
            print(" »", s.name)


        if mode == "EDIT" or (mode == "OBJECT" and len(sel) == 1):
            if mode == "EDIT":
                # make sure the current edit mode state is saved to active.data
                active.update_from_editmode()


            # create the stash and stashobj
            stash = create_stash(active=active, source=active)

            return "ACTIVE", None, None, stash.name

        elif mode == "OBJECT":
            sel.remove(active)

            sourceobjsnames= []
            stashobjs = []
            stashnames = []

            for obj in sel:
                stash = create_stash(active=active, source=obj)

                sourceobjsnames.append(obj.name)
                stashobjs.append(stash.obj)
                stashnames.append(stash.name)

            print()

            return "OTHER", sourceobjsnames, stashobjs, stashnames


class ViewStashes(bpy.types.Operator):
    bl_idname = "machin3.view_stashes"
    bl_label = "MACHIN3: View Stashes"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "View stashes of an object and retrieve them"

    xray = BoolProperty(name="X-Ray", default=False)

    retrievedname = StringProperty()

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active.MM.stashes

    def draw_VIEW3D(self, args):
        # NOTE: its possible the objs no longer exist
        # this can happen when a duplicate of on object with stashes was created and the stashes have been cleared on theduplicate
        # the original will still have the stashes, but the obj pointers will return None as the stashobjs are gone
        if self.stash.obj:
            mesh = self.stash.obj.data

            mx = self.active.matrix_world

            # offset amount depends on size of active object
            offset = sum([d for d in self.active.dimensions]) / 3 * 0.001

            # draw edges as lines
            # NOTE you can also draw quads, perhaps even ngons:
            # https://blender.stackexchange.com/questions/71980/modal-operator-to-highlight

            alpha = 0.5
            color = (1.0, 1.0, 1.0)

            edgecolor = (*color, alpha)
            edgewidth = 2

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

        draw_title(self, "View Stashes", subtitle=self.active.name, subtitleoffset=200)

        draw_prop(self, "Stash", "%d/%d" % (self.stash.index + 1, len(self.active.MM.stashes)), key="scroll UP/DOWN")
        self.offset += 10

        if self.stash.obj:
            draw_prop(self, "X-Ray", self.xray, offset=18, key="toggle X")
            self.offset += 10

            if self.retrievedname:
                draw_prop(self, "Retrieved", self.retrievedname, offset=18, key="press R")
            else:
                draw_prop(self, "Retrieve", self.retrievedname, offset=18, key="press R")
        else:
            draw_prop(self, "INVALID", "Stash Object Not Found", offset=18, HUDcolor=(1, 0, 0))


        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        if event.type in {'WHEELUPMOUSE', 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
            self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", 1)
            self.retrievedname = ""

        elif event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
            self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", -1)
            self.retrievedname = ""


        if self.stash.obj:
            # TOGGLE stash x-ray

            if event.type == 'X' and event.value == 'PRESS':
                self.xray = not self.xray

            # RETRIEVe stash obj

            elif event.type == 'R' and event.value == 'PRESS':
                # retrieve stash
                r = retrieve_stash(self.active, self.stash.obj)
                self.retrievedname = r.name

                # tranfer active's stashes to the retrieved
                if self.stash.obj.MM.stashmx == self.stash.obj.MM.stashtargetmx:
                    transfer_stashes(self.active, r)

        # VIEWPORT control

        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            # self.cancel_modal()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.active = m3.get_active()

        self.stash = self.active.MM.stashes[self.active.MM.active_stash_idx]

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        args = (self, context)
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ClearStashes(bpy.types.Operator):
    bl_idname = "machin3.clear_stashes"
    bl_label = "MACHIN3: Clear Stashes"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear stashes of an object"

    clear_all = BoolProperty(name="Clear All", default=False)

    xray = BoolProperty(name="X-Ray", default=False)

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active.MM.stashes

    def draw_VIEW3D(self, args):
        if not self.clear_all:
            if self.stash.obj:
                mesh = self.stash.obj.data

                mx = self.active.matrix_world

                # offset amount depends on size of active object
                offset = sum([d for d in self.active.dimensions]) / 3 * 0.001

                alpha = 0.5
                if self.stash.mark_delete:
                    color = (1.0, 0.0, 0.0)
                else:
                    color = (1.0, 1.0, 1.0)

                edgecolor = (*color, alpha)
                edgewidth = 2

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

        marked = sum([stash.mark_delete for stash in self.active.MM.stashes])
        title = "Clear Stashes (%d)" % (len(self.active.MM.stashes)) if self.clear_all else "Clear Stashes (%d)" % (marked) if marked != 0 else "Clear Stashes"
        suboffset = 250 if self.clear_all or marked != 0 else 200

        title = "Clear Stashes (%d)" % (len(self.active.MM.stashes)) if self.clear_all else "Clear Stashes (%d)" % (marked) if marked != 0 else "Clear Stashes"

        draw_title(self, title, subtitle=self.active.name, subtitleoffset=suboffset, HUDcolor=(1, 0, 0), HUDalpha=1)

        draw_prop(self, "Clear All", self.clear_all, key="toggle A")
        self.offset += 10

        if self.clear_all:
            draw_prop(self, "Stashes", "All %d" % len(self.active.MM.stashes), offset=18, key="")
        else:
            draw_prop(self, "Stash", "%d/%d" % (self.stash.index + 1, len(self.active.MM.stashes)), offset=18, key="scroll UP/DOWN")
            draw_prop(self, "Delete", self.stash.mark_delete, offset=18, key="toggle D")
            self.offset += 10

            if self.stash.obj:
                draw_prop(self, "X-Ray", self.xray, offset=18, key="toggle X")
            else:
                draw_prop(self, "INVALID", "Stash Object Not Found", offset=18, HUDcolor=(1, 0, 0))

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        # STASH selection

        if not self.clear_all:
            if event.type in {'WHEELUPMOUSE', 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
                self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", 1)

            elif event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
                self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", -1)

            elif event.type == 'D' and event.value == 'PRESS':
                self.stash.mark_delete = not self.stash.mark_delete


        # TOGGLE clear_all and x-ray

        if event.type == 'A' and event.value == 'PRESS':
            self.clear_all = not self.clear_all

        if self.stash.obj:
            if event.type == 'X' and event.value == 'PRESS':
                self.xray = not self.xray

        # VIEWPORT control

        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

            if self.clear_all:
                # get stashobj list
                delete_objs = []

                for stash in self.active.MM.stashes:
                    delete_objs.append(stash.obj)

                # clear the collection
                self.active.MM.stashes.clear()

            else:
                # removing stashes is done via the index in the collection
                # the index changes as items are remoeved and will invalidate the index prop we set ourselfs
                # so first create a list of all stash names and objs that are marked for deletion

                delete = []
                for stash in self.active.MM.stashes:
                    if stash.mark_delete:
                        delete.append((stash.name, stash.obj))

                # then use the names to get the current index from the keys()
                for name, obj in delete:
                    index = self.active.MM.stashes.keys().index(name)

                    # remove stash
                    self.active.MM.stashes.remove(index)

                # update props of remaining stashes
                for idx, stash in enumerate(self.active.MM.stashes):
                    stash.name = "stash_%d" % (idx)
                    stash.index = idx
                    stash.obj.name = "%s_%s" % (self.active.name, stash.name)

                # set new active stash index
                self.active.MM.active_stash_idx = len(self.active.MM.stashes) - 1

            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.active = m3.get_active()

        # self.stash = self.active.MM.stashes[self.active.MM.active_stash_idx]
        self.stash = self.active.MM.stashes[-1]

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        args = (self, context)
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class TransferStashes(bpy.types.Operator):
    bl_idname = "machin3.transfer_stashes"
    bl_label = "MACHIN3: Transfer Stashes"
    bl_options = {'REGISTER', 'UNDO'}

    restash = BoolProperty(name="Retrieve and Re-Stash", default=False)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "restash")

    @classmethod
    def poll(cls, context):
        sel = context.selected_objects
        active = context.active_object
        if len(sel) == 2 and active in sel:
            sel.remove(active)
            source =sel[0]
            return source.MM.stashes

    def execute(self, context):
        sel = context.selected_objects
        active = context.active_object

        if len(sel) == 2 and active in sel:
            sel.remove(active)
            source = sel[0]

            transfer_stashes(source, active, restash=self.restash)

        return {'FINISHED'}


class ViewOrphanStashes(bpy.types.Operator):
    bl_idname = "machin3.view_orphan_stashes"
    bl_label = "MACHIN3: View Orphan Stashes"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "View Oprhan Stashes"

    xray = BoolProperty(name="X-Ray", default=False)

    retrievedname = StringProperty()

    @classmethod
    def poll(cls, context):
        return [obj for obj in bpy.data.objects if obj.MM.isstashobj and obj.use_fake_user and obj.users == 1]


    def draw_VIEW3D(self, args):
        stashobj = self.orphans[self.idx]

        mesh = stashobj.data
        mx = stashobj.MM.stashtargetmx

        # draw edges as lines
        # NOTE you can also draw quads, perhaps even ngons:
        # https://blender.stackexchange.com/questions/71980/modal-operator-to-highlight

        alpha = 0.5
        color = (1.0, 1.0, 1.0)

        edgecolor = (*color, alpha)
        edgewidth = 2

        bgl.glEnable(bgl.GL_BLEND)

        if self.xray:
            bgl.glDisable(bgl.GL_DEPTH_TEST)

        for edge in mesh.edges:
            v1 = mesh.vertices[edge.vertices[0]]
            v2 = mesh.vertices[edge.vertices[1]]

            # bring the coordinates into world space, and push the verts out a bit
            v1co = mx * v1.co
            v2co = mx * v2.co

            bgl.glLineWidth(edgewidth)
            bgl.glColor4f(*edgecolor)

            bgl.glBegin(bgl.GL_LINES)

            bgl.glVertex3f(*v1co)
            bgl.glVertex3f(*v2co)

        draw_end()

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "View Orphan Stashes")

        draw_prop(self, "Stash", "%d/%d" % (self.idx + 1, len(self.orphans)), key="scroll UP/DOWN")
        self.offset += 10

        draw_prop(self, "X-Ray", self.xray, offset=18, key="toggle X")
        self.offset += 10

        if self.retrievedname:
            draw_prop(self, "Retrieved", self.retrievedname, offset=18, key="press R")
        else:
            draw_prop(self, "Retrieve", self.retrievedname, offset=18, key="press R")


        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        if event.type in {'WHEELUPMOUSE', 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
            self.idx = min([self.idx + 1, len(self.orphans) - 1])
            self.retrievedname = ""

        elif event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
            self.idx = max([0, self.idx - 1])
            self.retrievedname = ""


        # TOGGLE stash x-ray

        if event.type == 'X' and event.value == 'PRESS':
            self.xray = not self.xray

        # RETRIEVe stash obj

        elif event.type == 'R' and event.value == 'PRESS':
            # retrieve stash
            r = retrieve_stash(None, self.orphans[self.idx])
            self.retrievedname = r.name

        # VIEWPORT control

        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            # self.cancel_modal()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.orphans = [obj for obj in bpy.data.objects if obj.MM.isstashobj and obj.use_fake_user and obj.users == 1]
        self.idx = 0

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        args = (self, context)
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class RemoveOrphanStashes(bpy.types.Operator):
    bl_idname = "machin3.remove_orphan_stashes"
    bl_label = "MACHIN3: Remove Orphan Stashes"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Permanently remove orphan stashes"

    remove_all = BoolProperty(name="Clear All", default=False)

    xray = BoolProperty(name="X-Ray", default=False)


    @classmethod
    def poll(cls, context):
        return [obj for obj in bpy.data.objects if obj.MM.isstashobj and obj.use_fake_user and obj.users == 1]


    def draw_VIEW3D(self, args):
        if not self.remove_all:
            stashobj = self.orphans[self.idx]

            mesh = stashobj.data
            mx = stashobj.MM.stashtargetmx

            alpha = 0.5
            if self.mark_delete[self.idx]:
                color = (1.0, 0.0, 0.0)
            else:
                color = (1.0, 1.0, 1.0)

            edgecolor = (*color, alpha)
            edgewidth = 2

            bgl.glEnable(bgl.GL_BLEND)

            if self.xray:
                bgl.glDisable(bgl.GL_DEPTH_TEST)

            for edge in mesh.edges:
                v1 = mesh.vertices[edge.vertices[0]]
                v2 = mesh.vertices[edge.vertices[1]]

                # bring the coordinates into world space, and push the verts out a bit
                v1co = mx * v1.co
                v2co = mx * v2.co

                bgl.glLineWidth(edgewidth)
                bgl.glColor4f(*edgecolor)

                bgl.glBegin(bgl.GL_LINES)

                bgl.glVertex3f(*v1co)
                bgl.glVertex3f(*v2co)

            draw_end()

    def draw_HUD(self, args):
        draw_init(self, args)

        marked = sum([md for md in self.mark_delete])
        title = "Remove Orphan Stashes (%d)" % (len(self.orphans)) if self.remove_all else "Remove Orphan Stashes (%d)" % (marked) if marked != 0 else "Remove Orphan Stashes"

        draw_title(self, title, HUDcolor=(1, 0, 0), HUDalpha=1)

        draw_prop(self, "Remove All", self.remove_all, key="toggle A")
        self.offset += 10

        if self.remove_all:
            draw_prop(self, "Stashes", "All %d" % len(self.orphans), offset=18, key="")
        else:
            # draw_prop(self, "Stash", self.stash.index, offset=18, key="scroll UP/DOWN")
            draw_prop(self, "Stash", "%d/%d" % (self.idx + 1, len(self.orphans)), offset=18, key="scroll UP/DOWN")

            draw_prop(self, "Delete", self.mark_delete[self.idx], offset=18, key="toggle D")
            self.offset += 10

            draw_prop(self, "X-Ray", self.xray, offset=18, key="toggle X")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        # STASH selection

        if not self.remove_all:
            if event.type in {'WHEELUPMOUSE', 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
                self.idx = min([self.idx + 1, len(self.orphans) - 1])

            elif event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
                self.idx = max([0, self.idx - 1])

            elif event.type == 'D' and event.value == 'PRESS':
                self.mark_delete[self.idx] = not self.mark_delete[self.idx]


        # TOGGLE remove_all and x-ray

        if event.type == 'A' and event.value == 'PRESS':
            self.remove_all = not self.remove_all

        if event.type == 'X' and event.value == 'PRESS':
            self.xray = not self.xray

        # VIEWPORT control

        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

            if self.remove_all:
                delete_objs = self.orphans
            else:
                delete_objs = [obj for (obj, md) in zip(self.orphans, self.mark_delete) if md]

            count = len(delete_objs)

            for do in delete_objs:
                bpy.data.objects.remove(do, do_unlink=True)

            if count:
                popup_message("Removed %d Orphan Stashes!" % (count))

            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.orphans = [obj for obj in bpy.data.objects if obj.MM.isstashobj and obj.use_fake_user and obj.users == 1]
        self.mark_delete = [False for obj in self.orphans]
        self.idx = 0

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        args = (self, context)
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
