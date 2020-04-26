import bpy
import bmesh
import bgl
import mathutils
from bpy.props import BoolProperty, EnumProperty, FloatProperty
from .. utils.core import get_sides
from .. utils.graph import build_edge_graph
from .. utils.support import get_distance_between_verts
from .. utils.developer import output_traceback
from .. utils.ui import wrap_mouse, draw_init, draw_end, draw_title, draw_prop, step_enum, popup_message
from .. utils import MACHIN3 as m3



# TODO: add secondary way to mark fixed on the other side, perhas by using the freeestyle edges?
# maybe via a method mode SIDE vs MARKEDLOOPS

# TODO: do a proximity merge as well, verts that a renot on the edge loop, but are close(extra threshould?) to a fixed vert,
# TODO: what you really want here is closeness to an edge, hmm

# TODO: center merge instead of target merge?


sideselctionitems = [("A", "A", ""),
                     ("B", "B", "")]


class BooleanCleanup(bpy.types.Operator):
    bl_idname = "machin3.boolean_cleanup"
    bl_label = "MACHIN3: Boolean Cleanup"
    bl_options = {'REGISTER', 'UNDO'}

    sideselection = EnumProperty(name="Side", items=sideselctionitems, default="A")

    threshold = FloatProperty(name="Threshold", default=0, min=0, step=0.1)

    triangulate = BoolProperty(name="Triangulate", default=False)

    # modal
    allowmodalthreashold = BoolProperty(default=True)

    # hidden
    sharp = BoolProperty(default=False)
    debuginit = BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        mode = tuple(context.tool_settings.mesh_select_mode)

        if mode == (True, False, False) or mode == (False, True, False):
            return len([v for v in bm.verts if v.select]) >= 1


    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.prop(self, "sideselection", expand=True)

        column.prop(self, "threshold")

        column.prop(self, "triangulate")

    def draw_VIEW3D(self, args):
        fixedcolor = (0.25, 1, 0.25)
        unmovedcolor = (1, 0.25, 0.25)
        alpha = 1

        mx = self.active.matrix_world

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glDisable(bgl.GL_DEPTH_TEST)


        # draw fixed verts

        pointcolor = (*fixedcolor, alpha)
        bgl.glColor4f(*pointcolor)
        bgl.glPointSize(8)
        bgl.glBegin(bgl.GL_POINTS)

        for coords in self.fixed_verts:
            vco = mx * coords

            bgl.glVertex3f(*vco)

        bgl.glEnd()

        # draw moveable verts

        pointcolor = (*unmovedcolor, alpha)
        bgl.glColor4f(*pointcolor)
        bgl.glPointSize(6)
        bgl.glBegin(bgl.GL_POINTS)

        for coords in self.unmoved_verts:
            vco = mx * coords

            bgl.glVertex3f(*vco)

        draw_end()

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Boolean Cleanup")

        draw_prop(self, "Side", self.sideselection, key="scroll UP/DOWN")
        self.offset += 10

        draw_prop(self, "Threshold", self.threshold, offset=18, decimal=4, active=self.allowmodalthreashold, key="move LEFT/RIGHT, toggle W, reset ALT + W")
        self.offset += 10

        draw_prop(self, "Triangulate", self.triangulate, offset=18, key="toggle T")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['WHEELUPMOUSE', 'ONE', 'WHEELDOWNMOUSE', 'TWO', 'W', 'T']

        # only consider MOUSEMOVE as a trigger, when modalthreshod is actually active
        if self.allowmodalthreashold:
            events.append('MOUSEMOVE')

        if event.type in events:

            # CONTROL threshold

            if event.type == 'MOUSEMOVE':
                wrap_mouse(self, context, event, x=True)
                delta = self.mouse_x - self.init_mouse_x  # bigger if going to the right

                if self.allowmodalthreashold:
                    if event.shift:
                        self.threshold = delta * 0.0001
                    elif event.ctrl:
                        self.threshold = delta * 0.01
                    else:
                        self.threshold = delta * 0.001


            # TOGGLE triangulate

            elif event.type == 'W' and event.value == "PRESS":
                if event.alt:
                    self.allowmodalthreashold = False
                    self.threshold = 0
                else:
                    self.allowmodalthreashold = not self.allowmodalthreashold

            elif event.type == 'T' and event.value == "PRESS":
                self.triangulate = not self.triangulate


            # SELECT side/fixed

            elif event.type in ['WHEELUPMOUSE', 'ONE'] and event.value == "PRESS":
                self.sideselection = step_enum(self.sideselection, sideselctionitems, 1)

            elif event.type in ['WHEELDOWNMOUSE', 'TWO'] and event.value == "PRESS":
                self.sideselection = step_enum(self.sideselection, sideselctionitems, -1)


            # modal BooleanCleanup
            try:
                ret = self.main(self.active, modal=True)

                # caught and error
                if ret is False:
                    bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                    bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
                    return {'FINISHED'}
            # unexpected error
            except:
                output_traceback(self)
                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
                return {'FINISHED'}

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel_modal(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
        bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')

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

        args = (self, context)
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')
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
        debug = False
        # debug = True

        if debug:
            m3.clear()
            if self.debuginit:
                m3.debug_idx()
                self.debuginit = False

        mesh = active.data

        m3.set_mode("OBJECT")

        # reset the mesh the initial state
        if modal:
            self.initbm.to_mesh(active.data)

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]
        edges = [e for e in bm.edges if e.select]

        if any([not e.smooth for e in edges]):
            self.sharp = True

        # create the side lists of dictionaries
        sideA, sideB, cyclic, err = get_sides(bm, verts, edges, debug=debug)

        if sideA and sideB:
            # tag the fixed verts, based on the side selection
            self.tag_fixed_verts(sideA, sideB)

            # fix the end verts for non-cyclic selections
            if not cyclic:
                sideA[0]["vert"].tag = True
                sideA[-1]["vert"].tag = True

            # create mesh_graph (for the selected verts)
            mg = build_edge_graph(verts, edges, debug=debug)

            # move the verts that aren't fixed and get the coordinates of the fixed and unmoved ones for bgl drawing
            self.fixed_verts, self.unmoved_verts = self.move_merts(bm, mg, cyclic, debug=debug)

            # triangulate
            if self.triangulate:
                self.triangulate_side(bm, sideA, sideB)

            # merge
            bmesh.ops.remove_doubles(bm, verts=verts, dist=0.00001)

            # triangulization may result in some edges no longer being sharp, if they were before!
            if self.triangulate and self.sharp:
                for e in bm.edges:
                    if e.select:
                        e.smooth = False

            bm.to_mesh(mesh)
            m3.set_mode("EDIT")

            return True

        else:
            popup_message(err[0], title=err[1])
            m3.set_mode("EDIT")

            return False

    def triangulate_side(self, bm, sideA, sideB):
        faces = []
        # note, this is intentionally reversed! you want to triangulize the opposite side
        if self.sideselection == "A":
            for sB in sideB:
                for f in sB["faces"]:
                    if f not in faces:
                        faces.append(f)
        else:
            for sA in sideA:
                for f in sA["faces"]:
                    if f not in faces:
                        faces.append(f)

        bmesh.ops.triangulate(bm, faces=faces)

    def move_merts(self, bm, mg, cyclic, debug=False):
        fixed_vert_coords = []
        unmoved_vert_coords = []

        if debug:
            print("cylclic selection:", cyclic)

        for eidx, vidx in enumerate(mg):
            if debug:
                print("vert:", vidx)

            # A and B does not refer to the previous sides of the edge selection here,  but to the verts on either side of the current vert
            fixed = mg[vidx]["fixed"]
            if debug:
                print(" » fixed:", fixed)

            # fixed vert
            if fixed:
                fixed_vert_coords.append(mathutils.Vector((bm.verts[vidx].co)))
                continue

            # moveable vert
            else:
                A = mg[vidx]["connected"][0]
                B = mg[vidx]["connected"][1]

                Aidx, Afixed, Adist = A
                Bidx, Bfixed, Bdist = B

                lsort = [A, B]
                lsort = sorted(lsort, key=lambda l: l[2])
                closest = lsort[0]
                furthest = lsort[1]

                # move the verts to the closest neighbouring vert
                if closest[2] <= self.threshold:
                    closestidx = closest[0]
                    closestdist = closest[2]

                    furthestidx = furthest[0]

                    # move vert and any potentil children
                    bm.verts[vidx].co = bm.verts[closestidx].co
                    if debug:
                        print(" » moved to vert %d - distance: %f" % (closestidx, closestdist))

                    for childidx in mg[vidx]["children"]:
                        bm.verts[childidx].co = bm.verts[closestidx].co
                        if debug:
                            print("  » moved the child vert %d as well" % (childidx))


                    # update closest verts 'children' entry
                    mg[closestidx]["children"].append(vidx)
                    if debug:
                        print(" » updated %d's mg 'children' entry with vert %d" % (closestidx, vidx))


                    for childidx in mg[vidx]["children"]:
                        mg[closestidx]["children"].append(childidx)

                        if debug:
                            print("  » updated %d's mg 'children' entry with vert %d" % (closestidx, childidx))


                    # update the "connected" mg entries of the clostest and furthest verts, essentially making the movable vert invisible, as its now only a child of the closests
                    closest_conected = mg[closestidx]["connected"]
                    furthest_connected = mg[furthestidx]["connected"]


                    # you can't just get the new distance by adding the distance to the closest to the distance to the furthest.
                    # you need to calculate it from  the closest and furthest vert positions, as with the current vert moved, there's now a straight line between closest and furthest
                    newdist = get_distance_between_verts(bm.verts[closestidx], bm.verts[furthestidx])

                    # in the closest and furthest vert of the one we have moved, find which of the 2 connected verts is the one we have moved
                    # and replace it with the furthest/clostest, effectively, stepping over the moved one, as if it were merged already
                    for i, con in enumerate(closest_conected):
                        if con[0] == vidx:
                            mg[closestidx]["connected"][i] = (furthestidx, furthest[1], newdist)

                    if debug:
                        print(" » updated %d's mg 'connected' entry with vert %d replacing vert %d" % (closestidx, furthestidx, vidx))

                    for i, con in enumerate(furthest_connected):
                        if con[0] == vidx:
                            mg[furthestidx]["connected"][i] = (closestidx, closest[1], newdist)

                    if debug:
                        print(" » updated %d's mg 'connected' entry with vert %d replacing vert %d" % (furthestidx, closestidx, vidx))

                # not moving this vert as its below the distance threashold
                else:
                    unmoved_vert_coords.append(mathutils.Vector((bm.verts[vidx].co)))

        return fixed_vert_coords, unmoved_vert_coords

    def tag_fixed_verts(self, sideA, sideB):
        if self.sideselection == "A":
            for sA in sideA:
                if sA["edges"]:
                    # edge = sA["edges"][0]
                    # edge.select = True

                    # tag the vert to mark it is fixed
                    sA["vert"].tag = True
        else:
            for sB in sideB:
                if sB["edges"]:
                    # edge = sB["edges"][0]
                    # edge.select = True

                    # tag the vert to mark it is fixed
                    sB["vert"].tag = True
