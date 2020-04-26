import bpy
import bgl
from bpy.props import FloatProperty, EnumProperty, BoolProperty
import bmesh
from ..utils.developer import output_traceback
from ..utils.ui import wrap_mouse, draw_init, draw_title, draw_prop, draw_end, popup_message, step_collection, step_enum
from ..utils import MACHIN3 as m3


methoditems = [("SURFACEPOINT", "Surface Point", ""),
               ("PROJECT", "Project", ""),
               ("VERTEX", "Vertex", "")]


methodict = {"SURFACEPOINT": "NEAREST_SURFACEPOINT",
             "PROJECT": "PROJECT",
             "VERTEX": "NEAREST_VERTEX"}


class Conform(bpy.types.Operator):
    bl_idname = "machin3.conform"
    bl_label = "MACHIN3: Conform"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Transfer Normals from Stash"

    method = EnumProperty(name="Method", items=methoditems, default="SURFACEPOINT")

    shrink_wrap_offset = FloatProperty(name="Offset", default=0)

    xray = BoolProperty(name="X-Ray", default=False)
    alpha = FloatProperty(name="Alpha", default=0.2, min=0.1, max=1)

    apply_shrink_wrap = BoolProperty(name="Apply Shrink Wrap", default=True)
    remove_vgroup = BoolProperty(name="Remove Vertex Group", default=True)

    # modal
    allowmodaloffset = BoolProperty(default=False)

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

        draw_title(self, "Conform")

        draw_prop(self, "Stash", "%d/%d" % (self.stash.index + 1, len(self.active.MM.stashes)), key="scroll UP/DOWN")
        self.offset += 10

        if self.stash.obj:
            draw_prop(self, "Offset", self.shrink_wrap_offset, offset=18, active=self.allowmodaloffset, key="MOVE LEFT/RIGHT, toggle W")
            draw_prop(self, "Method", self.method, offset=18, key="CTRL scroll UP/DOWN")
            self.offset += 10

            draw_prop(self, "Alpha", self.alpha, offset=18, key="ALT scroll UP/DOWN")
            draw_prop(self, "X-Ray", self.xray, offset=18, key="toggle X")
            self.offset += 10

            draw_prop(self, "Display", self.shrink_wrap.show_viewport, offset=18, key="toggle D")

            self.offset += 10
            draw_prop(self, "Apply Mod", self.apply_shrink_wrap, offset=18, key="toggle A")
            if self.apply_shrink_wrap:
                draw_prop(self, "Remove VGroup", self.remove_vgroup, offset=18, key="toggle R")
        else:
            draw_prop(self, "INVALID", "Stash Object Not Found", offset=18, HUDcolor=(1, 0, 0))

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        # only consider MOUSEMOVE as a trigger for main(), when modaloffset is active
        if self.allowmodaloffset:
            if event.type == "MOUSEMOVE":
                delta_x = self.mouse_x - self.init_mouse_x
                wrap_mouse(self, context, event, x=True)

                self.shrink_wrap_offset = delta_x * 0.001
                self.shrink_wrap.offset = self.shrink_wrap_offset

        # SELECT stash, CHANGE alpha

        if event.type in {'WHEELUPMOUSE', 'ONE'} and event.value == 'PRESS':
            if event.alt:
                self.alpha += 0.1
            elif event.ctrl:
                self.method = step_enum(self.method, methoditems, 1)
                self.shrink_wrap.wrap_method = methodict[self.method]
            else:
                self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", 1)

                # check if the active object has moved, because shrinkwrap doesnt work in local space like data transfer, so the locations need to match
                if self.stash.obj.matrix_world != self.active.matrix_world:
                    self.stash.obj.matrix_world = self.active.matrix_world

                self.shrink_wrap.target = self.stash.obj

        elif event.type in {'WHEELDOWNMOUSE', 'TWO'} and event.value == 'PRESS':
            if event.alt:
                self.alpha -= 0.1
            elif event.ctrl:
                self.method = step_enum(self.method, methoditems, -1)
                self.shrink_wrap.wrap_method = methodict[self.method]
            else:
                self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", -1)

                # check if the active object has moved, because shrinkwrap doesnt work in local space like data transfer, so the locations need to match
                if self.stash.obj.matrix_world != self.active.matrix_world:
                    self.stash.obj.matrix_world = self.active.matrix_world

                self.shrink_wrap.target = self.stash.obj

        # STASH OBJ

        if self.stash.obj:

            # TOGGLE display mod and xray

            if event.type == 'X' and event.value == 'PRESS':
                self.xray = not self.xray

            elif event.type == 'D' and event.value == 'PRESS':
                self.shrink_wrap.show_viewport = not self.shrink_wrap.show_viewport

            # TOGGLE apply mod and remove vgroup

            elif event.type == 'A' and event.value == 'PRESS':
                self.apply_shrink_wrap = not self.apply_shrink_wrap

            elif event.type == 'R' and event.value == 'PRESS':
                self.remove_vgroup = not self.remove_vgroup

            elif event.type == 'W' and event.value == "PRESS":
                if event.alt:
                    self.shrink_wrap_offset = 0
                    self.shrink_wrap.offset = self.shrink_wrap_offset
                    self.allowmodaloffset = False
                else:
                    self.allowmodaloffset = not self.allowmodaloffset

        # VIEWPORT control

        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

            if self.stash.obj:
                if self.apply_shrink_wrap:
                    print(" » Applying modifier '%s' to object '%s'." % (self.shrink_wrap.name, self.active.name))
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=self.shrink_wrap.name)

                    if self.remove_vgroup:
                        print(" » Removing vertex group: %s" % (self.vgroup.name))
                        self.active.vertex_groups.remove(self.vgroup)
            else:
                print(" » Removing modifier '%s' from object '%s'." % (self.shrink_wrap.name, self.active.name))
                self.active.modifiers.remove(self.shrink_wrap)
                print(" » Removing vertex group: %s" % (self.vgroup.name))
                self.active.vertex_groups.remove(self.vgroup)

            m3.set_mode("EDIT")
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

            print(" » Removing modifier '%s' from object '%s'." % (self.shrink_wrap.name, self.active.name))
            self.active.modifiers.remove(self.shrink_wrap)
            print(" » Removing vertex group: %s" % (self.vgroup.name))
            self.active.vertex_groups.remove(self.vgroup)

            m3.set_mode("EDIT")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.active = m3.get_active()

        self.vgroup, self.shrink_wrap = self.main(self.active)
        self.stash = self.active.MM.stashes[self.active.MM.active_stash_idx]

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        args = (self, context)
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        active = m3.get_active()

        vgroup, shrink_wrap = self.main(active)

        print(" » Applying modifier '%s' to object '%s'." % (shrink_wrap.name, active.name))
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=shrink_wrap.name)

        print(" » Removing vertex group: %s" % (vgroup.name))
        active.vertex_groups.remove(vgroup)

        m3.set_mode("EDIT")
        return {'FINISHED'}

    def main(self, active):
        vert_ids = m3.get_selection("VERT")

        m3.set_mode("OBJECT")
        active.show_wire = True
        active.show_all_edges = True

        vgroup = self.add_vgroup(active, vert_ids, "conform")
        stash = active.MM.stashes[active.MM.active_stash_idx]
        stashobj = stash.obj

        # check if the active object has moved, because shrinkwrap doesnt work in local space like data transfer, so the locations need to match
        if stashobj.matrix_world != active.matrix_world:
            stashobj.matrix_world = active.matrix_world

        shrink_wrap = self.add_shrink_wrap_mod(active, stashobj, "conform", vgroup, self.shrink_wrap_offset, methodict[self.method])
        return vgroup, shrink_wrap

    def add_shrink_wrap_mod(self, obj, target, name, vgroup, offset, method):
        # add shrinkwrap mod
        shrink_wrap = obj.modifiers.new(name, "SHRINKWRAP")
        shrink_wrap.target = target
        shrink_wrap.vertex_group = vgroup.name
        shrink_wrap.offset = offset
        shrink_wrap.wrap_method = method

        shrink_wrap.show_expanded = False

        print(" » Added modifier '%s' to object '%s'." % (name, obj.name))

        return shrink_wrap

    def add_vgroup(self, obj, vert_ids, name):
        vgroup = obj.vertex_groups.new(name=name)
        print(" » Created new vertex group: %s" % (name))

        vgroup.add(vert_ids, 1, "ADD")
        return vgroup
