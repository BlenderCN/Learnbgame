import bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty, EnumProperty
import bmesh
import mathutils
from .. utils.core import get_sides
from .. utils.support import average_normals
from .. utils.ui import wrap_mouse, draw_init, draw_end, draw_title, draw_prop, step_enum, popup_message
from .. utils.developer import output_traceback
from .. utils import MACHIN3 as m3


# TODO: auto conform (without using obj dup and surface proximity)

outerfacemethoditems = [("REBUILD", "Rebuild", ""),
                        ("REPLACE", "Replace", "")]

sideselectionitems = [("A", "Side A", ""),
                      ("B", "Side B", "")]


class OffsetSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'allowmodalwidth', 'sideselection', 'reach', 'face_method', 'loop_slide', 'width', 'merge']:
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


class Offset(bpy.types.Operator, OffsetSettings):
    bl_idname = "machin3.offset"
    bl_label = "MACHIN3: Offset"
    bl_options = {'REGISTER', 'UNDO'}

    sideselection = EnumProperty(name="Side Select", items=sideselectionitems, default="A")

    width = FloatProperty("Width", default=0.01, min=0, step=0.1)
    smooth = BoolProperty(name="Smooth", default=True)

    loop_slide = BoolProperty(name="Loop Slide ", default=False)

    face_method = EnumProperty(name="Face Method", items=outerfacemethoditems, default="REBUILD")

    merge = BoolProperty(name="Merge", default=False)
    reach = IntProperty(name="Reach", default=0, min=0)

    create_vgroup = BoolProperty(name="Create Vertex Group", default=True)

    # modal
    allowmodalwidth = BoolProperty(default=True)

    # hidden
    debuginit = BoolProperty(default=True)
    vgroup = None

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        mode = tuple(context.tool_settings.mesh_select_mode)

        if mode == (True, False, False) or mode == (False, True, False):
            return len([e for e in bm.edges if e.select]) >= 1

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.prop(self, "sideselection", expand=True)

        column.separator()
        column.prop(self, "width")

        column.separator()
        row = column.row()
        row.prop(self, "loop_slide", text="Loop Slide")
        row.prop(self, "smooth", text="Smooth")
        column.prop(self, "create_vgroup")

        column.separator()
        row = column.row()
        row.prop(self, "face_method", expand=True)

        if self.face_method == "REBUILD":
            column.prop(self, "merge", text="Merge")
        elif self.face_method == "REPLACE":
            column.prop(self, "reach")

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Offset")

        draw_prop(self, "Width", self.width, decimal=3, active=self.allowmodalwidth, key="move LEFT/RIGHT, toggle W")
        self.offset += 10

        draw_prop(self, "Side", self.sideselection, offset=18, key="scroll UP/DOWN")
        draw_prop(self, "Loop Slide", self.loop_slide, offset=18, key="toggle Q")
        self.offset += 10

        draw_prop(self, "Face Method", self.face_method, offset=18, key="CTRL scroll UP/DOWN")

        if self.face_method == "REBUILD":
            draw_prop(self, "Merge Perimeter", self.merge, offset=18, key="toggle M")

        elif self.face_method == "REPLACE":
            draw_prop(self, "Reach", self.reach, offset=18, key="ALT scroll UP/DOWN")

        self.offset += 10
        draw_prop(self, "Smooth", self.smooth, offset=18, key="toggle S")
        draw_prop(self, "Vertex Group", self.create_vgroup, offset=18, key="toggle V")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['WHEELUPMOUSE', 'ONE', 'WHEELDOWNMOUSE', 'TWO', 'W', 'S', 'Q', 'M', 'V']

        # only consider MOUSEMOVE as a trigger for main(), when modalwidth is actually active
        if self.allowmodalwidth:
            events.append('MOUSEMOVE')


        if event.type in events:

            # CONTROL width

            if event.type == 'MOUSEMOVE':
                wrap_mouse(self, context, event, x=True)

                delta = self.mouse_x - self.init_mouse_x  # bigger if going to the right

                if event.shift:
                    self.width = delta * 0.00001
                else:
                    self.width = delta * 0.0001


            # SELECT side

            elif event.type in ['WHEELUPMOUSE', 'ONE'] and event.value == "PRESS":
                if event.ctrl:
                    self.face_method = step_enum(self.face_method, outerfacemethoditems, 1)
                elif event.alt:
                    if self.face_method == "REPLACE":
                        self.reach += 1
                else:
                    self.sideselection = step_enum(self.sideselection, sideselectionitems, 1)

            elif event.type in ['WHEELDOWNMOUSE', 'TWO'] and event.value == "PRESS":
                if event.ctrl:
                    self.face_method = step_enum(self.face_method, outerfacemethoditems, -1)
                elif event.alt:
                    if self.face_method == "REPLACE":
                        self.reach -= 1
                else:
                    self.sideselection = step_enum(self.sideselection, sideselectionitems, -1)

            # TOGGLE smooth

            elif event.type == 'S' and event.value == "PRESS":
                self.smooth = not self.smooth

            # TOGGLE loop slide

            elif event.type == 'Q' and event.value == "PRESS":
                self.loop_slide = not self.loop_slide

            # TOGGLE modal width
            elif event.type == 'W' and event.value == "PRESS":
                self.allowmodalwidth = not self.allowmodalwidth

            # TOGGLE REBUILD merge
            elif event.type == 'M' and event.value == "PRESS":
                if self.face_method == "REBUILD":
                    self.merge = not self.merge

            # TOGGLE vgroup
            elif event.type == 'V' and event.value == "PRESS":
                    self.create_vgroup = not self.create_vgroup


            # modal offset
            try:
                ret = self.main(self.active, modal=True)

                if ret:
                    self.save_settings()

                # caught an error
                else:
                    self.active.vertex_groups.remove(self.vgroup)
                    bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                    return {'FINISHED'}
            # unexpected error
            except:
                self.active.vertex_groups.remove(self.vgroup)
                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                output_traceback(self)
                return {'FINISHED'}

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            if not self.create_vgroup:
                self.active.vertex_groups.remove(self.vgroup)

            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            self.active.vertex_groups.remove(self.vgroup)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel_modal(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

        m3.set_mode("OBJECT")
        self.initbm.to_mesh(self.active.data)
        m3.set_mode("EDIT")

    def invoke(self, context, event):
        self.load_settings()

        self.active = m3.get_active()

        # create vgroup (always create it, and delete it at the end if create_vgroup is toggled off)
        self.vgroup = self.active.vertex_groups.new(name="offset")

        # make sure the current edit mode state is saved to obj.data
        self.active.update_from_editmode()

        # save this initial mesh state, this will be used when canceling the modal and to reset it for each mousemove event
        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        args = (self, context)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        active = m3.get_active()

        # check if the operator has created a vgroup before
        # we only want to create a new one once and not for each redo
        if self.create_vgroup:
            if not self.vgroup:
                self.vgroup = active.vertex_groups.new(name="offset")

        # remove any vgroup created previously in this operator run, if the create prop is False
        else:
            if self.vgroup:
                active.vertex_groups.remove(self.vgroup)
                self.vgroup = None

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

        groups = bm.verts.layers.deform.verify()

        verts = [v for v in bm.verts if v.select]
        edges = [e for e in bm.edges if e.select]

        # create the side lists of dictionaries
        sideA, sideB, cyclic, err = get_sides(bm, verts, edges, debug=debug)

        if sideA and sideB:
            # get normals for each vert on each side
            self.get_normals(bm, sideA, sideB, debug=debug)

            # create offset verts
            offsetdict = self.create_offset_verts(bm, sideA, sideB, self.width, self.sideselection, self.loop_slide, debug=debug)

            # build outer faces for REBUILD mode
            old_faces, new_faces = self.rebuild_outer_faces(bm, sideA, sideB, offsetdict, self.sideselection)

            # extend both sides, if the selection is cyclic
            if cyclic:
                sideA.append(sideA[0])
                sideB.append(sideB[0])

            # rebuild inner faces
            inner_faces, rail = self.rebuild_inner_faces(bm, sideA, sideB, self.sideselection)

            # flush so the we have nice visual face selection
            bm.select_flush(True)

            if self.face_method == "REBUILD":
                # move perimeter
                if self.merge:
                    mergeverts, dissovleedges = self.move_perimeter(bm, rail, debug=debug)

                # delete the old faces for REBUILD mode, they are needed for and will be replaced by the REPLACE mode as well
                bmesh.ops.delete(bm, geom=old_faces, context=5)

                # merge perimeter
                if self.merge:
                    bmesh.ops.dissolve_edges(bm, edges=dissovleedges)

                    # the edge dissolving may have removed some verts already, so remove these from the list
                    doubles = [v for v in mergeverts if v.is_valid]

                    bmesh.ops.remove_doubles(bm, verts=doubles, dist=0.00001)

            elif self.face_method == "REPLACE":
                side = sideA if self.sideselection == "A" else sideB

                outer_edges = self.replace_outer_faces(bm, verts, edges, side, rail, new_faces, reach=self.reach)

                # build outer faces for REPLACE mode
                repl_faces = []

                # prevent the bridge ops from running when the outer edges list is empty
                # this results in an opening, but its better than an exception
                if outer_edges:
                    ret = bmesh.ops.bridge_loops(bm, edges=rail + outer_edges)
                    repl_faces += ret["faces"]


            # assign new faces/verts ot the vertex group
            if self.create_vgroup:
                for f in inner_faces:
                    for v in f.verts:
                        v[groups][self.vgroup.index] = 1

            bm.to_mesh(mesh)
            m3.set_mode("EDIT")

            return True

        else:
            popup_message(err[0], title=err[1])
            m3.set_mode("EDIT")

            return False

    def move_perimeter(self, bm, rail, debug=False):
        if debug:
            print("Merging perimeter")

        railverts = []
        mergeverts = []
        dissovleedges =[]
        seen = []

        for e in rail:
            for v in e.verts:
                if v not in seen:
                    seen.append(v)
                else:
                    continue

                ves = [e for e in v.link_edges if e not in rail and not e.select]

                # find potential merge verts
                for e in ves:
                    # ignore edges if the remote verts are selected/part of the rail (this happens for flushedges)
                    if e.other_vert(v).select:
                        continue
                    else:
                        mv = e.other_vert(v)

                        # dissove the edge, if its remote vert was seen before
                        if mv in mergeverts:
                            dissovleedges.append(e)

                        # move the vert to the rail to be merged other wise
                        else:
                            if debug:
                                print(" » vert:", mv.index, "merge to:", v.index)

                            mv.co = v.co

                            mergeverts.append(mv)

                            if v not in railverts:
                                railverts.append(v)

                            # also dissolve edges of merge verts connected to other merge verts
                            # this preves sharpness being "overwritten" and avoids weired edges "sliding under" rail edges, see 082_offset.blend for some exampled
                            for e in mv.link_edges:
                                if e.other_vert(mv) in mergeverts:
                                    dissovleedges.append(e)

        # # the edge dissolving may have removed some verts already, so remove these from the list
        # doubles = [v for v in mergeverts + railverts if v.is_valid]

        return mergeverts + railverts, dissovleedges

    def replace_outer_faces(self, bm, verts, edges, side, rail, new_faces, reach=0):
        def get_perimeter(outer_faces, inner_verts):
            outer_edges = []
            outer_verts = []
            for f in outer_faces:
                for e in f.edges:
                    if e in edges + rail:
                        e.select = False
                    elif any([v in inner_verts for v in e.verts]):
                        continue
                    else:
                        outer_edges.append(e)
                        # e.select = True
                        for v in e.verts:
                            if v not in outer_verts:
                                outer_verts.append(v)

            return outer_edges, outer_verts

        # initial run, get the outer faces from the side list of dicts
        outer_faces = []
        for s in side:
            for f in s["faces"]:
                if f not in outer_faces:
                    outer_faces.append(f)
                    # f.select = True


        outer_edges, outer_verts = get_perimeter(outer_faces, verts)

        # additional runs based on previous runs determined by the reach value
        for i in range(reach):
            next_outer_faces = []
            for v in outer_verts:
                for f in v.link_faces:
                    if f not in outer_faces + next_outer_faces + new_faces:
                        next_outer_faces.append(f)
                        # f.select = True

            next_outer_edges, next_outer_verts = get_perimeter(next_outer_faces, outer_verts)

            # collect all outer faces, but only the preremiter edges/verts or the last run
            # outer_faces += [f for f in next_outer_faces if f not in outer_faces]
            outer_faces += next_outer_faces
            outer_edges = next_outer_edges
            outer_verts = next_outer_verts

        # delete the old ones
        bmesh.ops.delete(bm, geom=outer_faces + new_faces, context=5)

        # some edges may have become invalid/deleted, see chamfer_fail.blend for an example
        # nothing to worry about, the remaining edges are still a complete loop, just remove the invalid ones

        outer_edges = [e for e in outer_edges if e.is_valid]

        return outer_edges

    def rebuild_inner_faces(self, bm, sideA, sideB, sideselection):
        rail = []
        inner_faces = []

        # rebuild inser sides
        if sideselection == "A":
            for idx, sA in enumerate(sideA):
                if idx == len(sideA) - 1:
                    break

                vert = sA["vert"]
                offset_vert = sA["offset_vert"]
                vert_next = sideA[idx + 1]["vert"]
                offset_vert_next = sideA[idx + 1]["offset_vert"]

                face = bm.faces.new([vert, vert_next, offset_vert_next, offset_vert])
                face.smooth = self.smooth

                inner_faces.append(face)

                re = bm.edges.get([offset_vert, offset_vert_next])
                rail.append(re)
                re.select = True

            bm.edges.index_update()

            return inner_faces, rail

        elif sideselection == "B":
            for idx, sB in enumerate(sideB):
                if idx == len(sideA) - 1:
                    break

                vert = sB["vert"]
                offset_vert = sB["offset_vert"]
                vert_next = sideB[idx + 1]["vert"]
                offset_vert_next = sideB[idx + 1]["offset_vert"]

                # face = bm.faces.new([vert, vert_next, offset_vert_next, offset_vert])
                face = bm.faces.new([vert, offset_vert, offset_vert_next, vert_next])
                face.smooth = self.smooth

                inner_faces.append(face)

                re = bm.edges.get([offset_vert, offset_vert_next])
                rail.append(re)

                re.select = True

            bm.edges.index_update()

            return inner_faces, rail

    def rebuild_outer_faces(self, bm, sideA, sideB, offsetdict, sideselection):
        # get verts of new faces in proper order by checking the existing faces and replacing the verts, that are part of the initial selection with the offset verts
        new_face_verts = []
        old_faces = []
        for sA, sB in zip(sideA, sideB):
            if sideselection == "A":
                for face in sA["faces"]:
                    if face not in old_faces:
                        old_faces.append(face)

                        face_verts = []
                        for v in face.verts:
                            if v in offsetdict:
                                face_verts.append(offsetdict[v]["offsetA"])
                            else:
                                face_verts.append(v)

                        new_face_verts.append(face_verts)

            elif sideselection == "B":
                for face in sB["faces"]:
                    if face not in old_faces:
                        old_faces.append(face)

                        face_verts = []
                        for v in face.verts:
                            if v in offsetdict:
                                face_verts.append(offsetdict[v]["offsetB"])
                            else:
                                face_verts.append(v)

                        new_face_verts.append(face_verts)

        new_faces = []

        # create the new faces
        for f in new_face_verts:
            face = bm.faces.new(f)
            face.smooth = self.smooth
            new_faces.append(face)

        bm.faces.index_update()

        return old_faces, new_faces

    def create_offset_verts(self, bm, sideA, sideB, width, sideselection, loopslide, debug=False):
        # create cutting plane from face normals and intersect each side with it
        for sA, sB in zip(sideA, sideB):
            vert = sA["vert"]
            cuttingnormal = mathutils.geometry.normal([vert.co, vert.co + sA["normal"], vert.co + sB["normal"]])

            # SIDE A

            if sideselection == "A":
                # slide an existing edge offshooting edge, if it exists and it loop_slide_sideA is on
                if loopslide and sA["edges"]:
                    if debug:
                        print(" » Loop Sliding on Side A")

                    edge = sA["edges"][0]

                    vert_end = edge.other_vert(vert)
                    offset_vectorA = (vert_end.co - vert.co).normalized()

                # intersetct side A
                else:
                    ivsA = mathutils.geometry.intersect_plane_plane(vert.co, sA["normal"], vert.co, cuttingnormal)

                    # flip direction of offset vector, based on seledge angle/depending on convacity/convexity
                    if sA["seledge"].calc_face_angle_signed() >= 0:
                        offset_vectorA = ivsA[1]
                    else:
                        offset_vectorA = ivsA[1].reflect(ivsA[1])

                # create offset vert
                overtA = bm.verts.new()
                overtA.co = vert.co + offset_vectorA * width

                # set the offset vert in the dict
                sA["offset_vert"] = overtA

                if debug:
                    e = bm.edges.new([vert, overtA])
                    e.select = True

            # SIDE B

            elif sideselection == "B":
                # slide an existing edge offshooting edge, if it exists and it loop_slide_sideB is on
                if loopslide and sB["edges"]:
                    if debug:
                        print(" » Loop Sliding on Side B")

                    edge = sB["edges"][0]

                    vert_end = edge.other_vert(vert)
                    offset_vectorB = (vert_end.co - vert.co).normalized()

                # intersetct side B, reversing the order of arguments like this, seems to produce the desired results
                else:
                    # ivsB = mathutils.geometry.intersect_plane_plane(vert.co, sB["normal"], vert.co, cuttingnormal)
                    ivsB = mathutils.geometry.intersect_plane_plane(vert.co, cuttingnormal, vert.co, sB["normal"])

                    # flip direction of offset vector, based on seledge angle/depending on convacity/convexity
                    if sB["seledge"].calc_face_angle_signed() >= 0:
                        offset_vectorB = ivsB[1]
                    else:
                        offset_vectorB = ivsB[1].reflect(ivsB[1])

                overtB = bm.verts.new()
                overtB.co = vert.co + offset_vectorB * width

                # set the offset vert in the dict
                sB["offset_vert"] = overtB

                if debug:
                    e = bm.edges.new([vert, overtB])
                    e.select = True

            bm.verts.index_update()

        # create a dict to allow for easy association/selection fo vert and offset vert on each side
        offsetdict = {}

        for sA, sB in zip(sideA, sideB):
            if sA["vert"] not in offsetdict:
                offsetdict[sA["vert"]] = {}

            if sideselection == "A":
                offsetdict[sA["vert"]]["offsetA"] = sA["offset_vert"]

            elif sideselection == "B":
                offsetdict[sA["vert"]]["offsetB"] = sB["offset_vert"]

        return offsetdict

    def get_normals(self, bm, sideA, sideB, debug=False):
        for sA, sB in zip(sideA, sideB):
            if debug:
                print()
                print("vertA:", sA["vert"].index, "\tvertB:", sB["vert"].index)
                print(" » edgesA:", [e.index for e in sA["edges"]], "\tedgesB:", [e.index for e in sB["edges"]])
                print(" » facesA:", [f.index for f in sA["faces"]], "\tfacesB:", [f.index for f in sB["faces"]])


            sA["normal"] = average_normals([f.normal for f in sA["faces"]])
            sB["normal"] = average_normals([f.normal for f in sB["faces"]])

            if debug:
                endvert = bm.verts.new()
                endvert.co = sA["vert"].co + sA["normal"] * 0.05
                bm.edges.new([sA["vert"], endvert])

                endvert = bm.verts.new()
                endvert.co = sB["vert"].co + sB["normal"] * 0.05
                bm.edges.new([sB["vert"], endvert])
