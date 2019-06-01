import bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty, EnumProperty
import bmesh
import mathutils
import bgl
from .. utils.core import get_sides
from .. utils.support import average_normals
from .. utils.ui import wrap_mouse, draw_init, draw_end, draw_title, draw_prop, step_enum, popup_message
from .. utils.developer import output_traceback
from .. utils import MACHIN3 as m3


# TODO: "subdivide" rails?
# TODO: project the plane intersections down to perfectly confirm to a face? but what face depends on how fare out the offsect goes
# #### : a better approach might be to conform it to a stash
# TODO: when loops slide is on, don't just select the first of the available edges, select the one closts to the  offset vector?

# TODO: multi island????

# TODO: limit the reach via freestyle edges?

# TODO: 044_better_chamfer2_fail.blend


outerfacemethoditems = [("REBUILD", "Rebuild", ""),
                        ("REPLACE", "Replace", "")]

modalrailselectitems = [("A", "Side A", ""),
                        ("B", "Side B", "")]


class ChamferSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'allowmodalwidth', 'modal_side_select', 'reachA', 'reachB', 'mergeA', 'mergeB', 'face_method_sideA', 'face_method_sideB', 'loop_slide_sideA', 'loop_slide_sideB', 'width']:
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


class Chamfer(bpy.types.Operator, ChamferSettings):
    bl_idname = "machin3.chamfer"
    bl_label = "MACHIN3: Chamfer"
    bl_options = {'REGISTER', 'UNDO'}

    width = FloatProperty("Width", default=0, min=0, step=0.1)

    smooth = BoolProperty(name="Smooth", default=True)

    loop_slide_sideA = BoolProperty(name="Side A", default=False)
    loop_slide_sideB = BoolProperty(name="Side B", default=False)

    face_method_sideA = EnumProperty(name="Side A", items=outerfacemethoditems, default="REBUILD")
    face_method_sideB = EnumProperty(name="Side B", items=outerfacemethoditems, default="REBUILD")

    mergeA = BoolProperty(name="Merge", default=False)
    mergeB = BoolProperty(name="Merge", default=False)

    reachA = IntProperty(name="Reach", default=0, min=0)
    reachB = IntProperty(name="Reach", default=0, min=0)

    create_vgroup = BoolProperty(name="Create Vertex Groups", default=True)

    # modal
    allowmodalwidth = BoolProperty(default=True)
    modal_side_select = EnumProperty(name="Side Select", items=modalrailselectitems, default="A")

    # hidden
    coA = None
    coB = None
    vgroupA = None
    vgroupB = None


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

        row = column.split(percentage=0.75)
        row.prop(self, "width")
        row.prop(self, "smooth")
        column.prop(self, "create_vgroup")

        column.separator()

        row = column.row()
        row.label("Side A")
        row.label("Side B")

        row = column.row()
        row.prop(self, "loop_slide_sideA", text="Loop Slide", toggle=True)
        row.prop(self, "loop_slide_sideB", text="Loop Slide", toggle=True)

        column.separator()

        row = column.row()
        # r = row.row()
        row.prop(self, "face_method_sideA", expand=True)
        # r = row.row()
        row.prop(self, "face_method_sideB", expand=True)

        row = column.split()
        if self.face_method_sideA == "REBUILD":
            row.prop(self, "mergeA")
        elif self.face_method_sideA == "REPLACE":
            row.prop(self, "reachA")

        if self.face_method_sideB == "REBUILD":
            row.prop(self, "mergeB")
        elif self.face_method_sideB == "REPLACE":
            row.prop(self, "reachB")

    def draw_VIEW3D(self, args):
        if any([self.coA, self.coB]):
            mx = self.active.matrix_world

            rail_cos = getattr(self, "co" + self.modal_side_select)

            color = (1, 1, 1)
            alpha = 1

            edgecolor = (*color, alpha)
            edgewidth = 2

            bgl.glEnable(bgl.GL_BLEND)
            bgl.glDisable(bgl.GL_DEPTH_TEST)

            bgl.glLineWidth(edgewidth)
            bgl.glColor4f(*edgecolor)

            # bgl.glBegin(bgl.GL_LINES)
            bgl.glBegin(bgl.GL_LINE_STRIP)

            for co in rail_cos:
                rco = mx * co
                bgl.glVertex3f(*rco)

            draw_end()

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Chamfer")

        draw_prop(self, "Width", self.width, decimal=3, active=self.allowmodalwidth, key="move LEFT/RIGHT, toggle W")
        self.offset += 10

        draw_prop(self, "Side", self.modal_side_select, offset=18, key="scroll UP/DOWN")
        self.offset += 10

        if self.modal_side_select == "A":
            draw_prop(self, "Loop Slide", self.loop_slide_sideA, offset=18, key="toggle Q")
            draw_prop(self, "Face Method", self.face_method_sideA, offset=18, key="CTRL scroll UP/DOWN")

            if self.face_method_sideA == "REBUILD":
                draw_prop(self, "Merge Perimeter", self.mergeA, offset=18, key="toggle M")
            elif self.face_method_sideA == "REPLACE":
                draw_prop(self, "Reach", self.reachA, offset=18, key="ALT scroll UP/DOWN")
        else:
            draw_prop(self, "Loop Slide", self.loop_slide_sideB, offset=18, key="toggle Q")
            draw_prop(self, "Face Method", self.face_method_sideB, offset=18, key="CTRL scroll UP/DOWN")

            if self.face_method_sideB == "REBUILD":
                draw_prop(self, "Merge Perimeter", self.mergeB, offset=18, key="toggle M")
            elif self.face_method_sideB == "REPLACE":
                draw_prop(self, "Reach", self.reachB, offset=18, key="ALT scroll UP/DOWN")

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

            # TOGGLE smooth

            elif event.type == 'S' and event.value == "PRESS":
                self.smooth = not self.smooth

            # SELECT side

            elif event.type in ['WHEELUPMOUSE', 'ONE'] and event.value == "PRESS":
                if event.ctrl:
                    if self.modal_side_select == "A":
                        self.face_method_sideA = step_enum(self.face_method_sideA, outerfacemethoditems, 1)
                    else:
                        self.face_method_sideB = step_enum(self.face_method_sideB, outerfacemethoditems, 1)
                elif event.alt:
                    if self.modal_side_select == "A" and self.face_method_sideA == "REPLACE":
                        self.reachA += 1

                    elif self.modal_side_select == "B" and self.face_method_sideB == "REPLACE":
                        self.reachB += 1
                else:
                    self.modal_side_select = step_enum(self.modal_side_select, modalrailselectitems, 1)

            elif event.type in ['WHEELDOWNMOUSE', 'TWO'] and event.value == "PRESS":
                if event.ctrl:
                    if self.modal_side_select == "A":
                        self.face_method_sideA = step_enum(self.face_method_sideA, outerfacemethoditems, -1)
                    else:
                        self.face_method_sideB = step_enum(self.face_method_sideB, outerfacemethoditems, -1)
                elif event.alt:
                    if self.modal_side_select == "A" and self.face_method_sideA == "REPLACE":
                        self.reachA -= 1
                    elif self.modal_side_select == "B" and self.face_method_sideB == "REPLACE":
                        self.reachB -= 1
                else:
                    self.modal_side_select = step_enum(self.modal_side_select, modalrailselectitems, -1)

            # TOGGLE loop slide

            elif event.type == 'Q' and event.value == "PRESS":
                if self.modal_side_select == "A":
                    self.loop_slide_sideA = not self.loop_slide_sideA
                else:
                    self.loop_slide_sideB = not self.loop_slide_sideB

            # TOGGLE REBUILD merge

            elif event.type == 'M' and event.value == "PRESS":
                if self.modal_side_select == "A" and self.face_method_sideA == "REBUILD":
                    self.mergeA = not self.mergeA

                elif self.modal_side_select == "B" and self.face_method_sideB == "REBUILD":
                    self.mergeB = not self.mergeB

            # TOGGLE vgroup creation
            elif event.type == 'V' and event.value == "PRESS":
                self.create_vgroup = not self.create_vgroup

            # TOGGLE modal width

            elif event.type == 'W' and event.value == "PRESS":
                self.allowmodalwidth = not self.allowmodalwidth

            # modal chamfer
            try:
                ret = self.main(self.active, modal=True)

                if ret:
                    self.save_settings()

                # caught and error
                else:
                    self.active.vertex_groups.remove(self.vgroupA)
                    self.active.vertex_groups.remove(self.vgroupB)

                    bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                    bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
                    return {'FINISHED'}
            # unexpected error
            except:
                self.active.vertex_groups.remove(self.vgroupA)
                self.active.vertex_groups.remove(self.vgroupB)

                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
                output_traceback(self)
                return {'FINISHED'}

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            if not self.create_vgroup:
                self.active.vertex_groups.remove(self.vgroupA)
                self.active.vertex_groups.remove(self.vgroupB)

            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            self.active.vertex_groups.remove(self.vgroupA)
            self.active.vertex_groups.remove(self.vgroupB)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel_modal(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
        bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')

        m3.set_mode("OBJECT")
        self.initbm.to_mesh(self.active.data)
        m3.set_mode("EDIT")

    def invoke(self, context, event):
        self.load_settings()

        self.active = m3.get_active()

        # create normal transfer vgroup (always create it, and delete it at the end if create_vgroup is toggled off)
        self.vgroupA = self.active.vertex_groups.new(name="chamfer")
        self.vgroupB = self.active.vertex_groups.new(name="chamfer")

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

        # check if the operator has created a chamfer vgroup before
        # we only want to create a new one once and not for each redo
        if self.create_vgroup:
            if not self.vgroupA:
                self.vgroupA = active.vertex_groups.new(name="chamfer")
            if not self.vgroupB:
                self.vgroupB = active.vertex_groups.new(name="chamfer")

        # remove any vgroup created previously in this operator run, if the create prop is False
        else:
            if self.vgroupA:
                active.vertex_groups.remove(self.vgroupA)
                self.vgroupA = None
            if self.vgroupB:
                active.vertex_groups.remove(self.vgroupB)
                self.vgroupB = None

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
            m3.debug_idx()

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
            offsetdict = self.create_offset_verts(bm, sideA, sideB, debug=debug)

            # build outer faces for REBUILD mode
            self.rebuild_outer_faces(bm, sideA, sideB, offsetdict)

            if self.face_method_sideA == "REPLACE":
                outer_edgesA = self.replace_outer_faces(bm, verts, edges, sideA, reach=self.reachA)

            if self.face_method_sideB == "REPLACE":
                outer_edgesB = self.replace_outer_faces(bm, verts, edges, sideB, reach=self.reachB)

            # extend both sides, if the selection is cyclic
            if cyclic:
                sideA.append(sideA[0])
                sideB.append(sideB[0])

            # build chamfer, get rail edges + rail vert coordinates
            chamfer_faces, railA, railB, self.coA, self.coB = self.build_chamfer_faces(bm, sideA, sideB, self.smooth, debug=debug)

            bm.faces.index_update()
            bm.edges.index_update()

            # merge perimeter
            railA_verts = []
            if self.face_method_sideA == "REBUILD" and self.mergeA:
                    railA_verts = self.merge_perimeter(bm, railA, debug=debug)
                    # NOTE: due to the rmoving of doubles these verts may not be a complete rail.
                    # it shouldn't matter howver, the faces we get from these verts should be complete anyway

            railB_verts = []
            if self.face_method_sideB == "REBUILD" and self.mergeB:
                    railB_verts = self.merge_perimeter(bm, railB, debug=debug)

            # build outer faces for REPLACE mode
            railA_faces = []
            if self.face_method_sideA == "REPLACE" and outer_edgesA:
                # prevent the bridge ops from running when the outer edges list is empty
                # this results in an opening, but its better than an exception
                ret = bmesh.ops.bridge_loops(bm, edges=railA + outer_edgesA)
                railA_faces += ret["faces"]

            railB_faces = []
            if self.face_method_sideB == "REPLACE" and outer_edgesB:
                ret = bmesh.ops.bridge_loops(bm, edges=railB + outer_edgesB)
                railB_faces += ret["faces"]

            # assign vgroups
            if self.create_vgroup:
                # side A vgroup
                self.assign_vgroup(groups, chamfer_faces, self.vgroupA, railA, railA_verts, railA_faces)

                # side B v group
                self.assign_vgroup(groups, chamfer_faces, self.vgroupB, railB, railB_verts, railB_faces)

            bm.to_mesh(mesh)
            m3.set_mode("EDIT")

            return True

        else:
            popup_message(err[0], title=err[1])
            m3.set_mode("EDIT")

            return False

    def assign_vgroup(self, deform_layer, chamfer_faces, vgroup, rail, rail_verts, rail_faces):
        # depending on the choices made, different source geo will be available
        if rail_faces:
            for f in rail_faces:
                for v in f.verts:
                    v[deform_layer][vgroup.index] = 1

        elif rail_verts:
            for v in rail_verts:
                for f in [f for f in v.link_faces if f not in chamfer_faces]:
                    for v in f.verts:
                        v[deform_layer][vgroup.index] = 1
        else:
            for e in rail:
                for f in [f for f in e.link_faces if f not in chamfer_faces]:
                    for v in f.verts:
                        v[deform_layer][vgroup.index] = 1

    def merge_perimeter(self, bm, rail, debug=False):
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
                    # ignore edges of the remote verts are selected/part of the rail (this happens for flushedges)
                    if e.other_vert(v).select:
                        continue
                    else:
                        mv = e.other_vert(v)

                        # dissove the edge, if its remote vert was seen before
                        if mv in mergeverts:
                            dissovleedges.append(e)

                        # move the vert to the rail to be merged otherwise
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

        if dissovleedges:
            bmesh.ops.dissolve_edges(bm, edges=dissovleedges)

        # the edge dissolving may have removed some verts already, so remove these from the list
        doubles = [v for v in mergeverts + railverts if v.is_valid]

        bmesh.ops.remove_doubles(bm, verts=doubles, dist=0.00001)

        return [d for d in doubles if d.is_valid]

    def replace_outer_faces(self, bm, verts, edges, side, reach=0):
        def get_perimeter(outer_faces, inner_verts):
            outer_edges = []
            outer_verts = []
            for f in outer_faces:
                for e in f.edges:
                    if e in edges:
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
                    if f not in outer_faces + next_outer_faces:
                        next_outer_faces.append(f)
                        # f.select = True

            next_outer_edges, next_outer_verts = get_perimeter(next_outer_faces, outer_verts)

            # collect all outer faces, but only the preremiter edges/verts or the last run
            # outer_faces += [f for f in next_outer_faces if f not in outer_faces]
            outer_faces += next_outer_faces
            outer_edges = next_outer_edges
            outer_verts = next_outer_verts

        # delete the old ones
        bmesh.ops.delete(bm, geom=outer_faces, context=5)

        # some edges may have become invalid/deleted, see chamfer_fail.blend for an example
        # nothing to worry about, the remaining edges are still a complete loop, just remove the invalid ones

        outer_edges = [e for e in outer_edges if e.is_valid]

        return outer_edges

    def build_chamfer_faces(self, bm, sideA, sideB, smooth, debug=False):
        chamfer_faces = []
        railA = []
        railB = []

        coA = []
        coB = []

        for idx, (sA, sB) in enumerate(zip(sideA, sideB)):
            vA = sA["offset_vert"]
            vB = sB["offset_vert"]

            coA.append(mathutils.Vector(vA.co))
            coB.append(mathutils.Vector(vB.co))

            if idx == len(sideA) - 1:
                break

            vA_next = sideA[idx + 1]["offset_vert"]
            vB_next = sideB[idx + 1]["offset_vert"]


            if debug:
                print(idx)
                print(" » ", vA.index)
                print(" » ", vB.index)
                print(" » ", vB_next.index)
                print(" » ", vA_next.index)

            face = bm.faces.new([vA, vB, vB_next, vA_next])
            face.smooth = smooth
            face.select = True

            chamfer_faces.append(face)

            reA = bm.edges.get([vA, vA_next])
            reB = bm.edges.get([vB, vB_next])

            railA.append(reA)
            railB.append(reB)

            # sharpen the rail edges
            if self.smooth:
                reA.smooth = False
                reB.smooth = False

        return chamfer_faces, railA, railB, coA, coB

    def rebuild_outer_faces(self, bm, sideA, sideB, offsetdict):
        # get verts of new faces in proper order by checking the existing faces and replacing the verts, that are part of the initial selection with the offset verts
        new_face_verts = []
        old_faces = []
        for sA, sB in zip(sideA, sideB):
            if self.face_method_sideA == "REBUILD":
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

            if self.face_method_sideB == "REBUILD":
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


        # create the new faces
        for f in new_face_verts:
            face = bm.faces.new(f)
            face.smooth = self.smooth

        # delete the old ones
        bmesh.ops.delete(bm, geom=old_faces, context=5)

    def create_offset_verts(self, bm, sideA, sideB, debug=False):
        # create cutting plane from face normals and intersect each side with it
        for sA, sB in zip(sideA, sideB):
            vert = sA["vert"]
            cuttingnormal = mathutils.geometry.normal([vert.co, vert.co + sA["normal"], vert.co + sB["normal"]])

            # SIDE A

            # slide an existing edge offshooting edge, if it exists and it loop_slide_sideA is on
            if self.loop_slide_sideA and sA["edges"]:
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
            overtA.co = vert.co + offset_vectorA * self.width

            # set the offset vert in the dict
            sA["offset_vert"] = overtA

            if debug:
                e = bm.edges.new([vert, overtA])
                e.select = True

            # SIDE B

            # slide an existing edge offshooting edge, if it exists and it loop_slide_sideB is on
            if self.loop_slide_sideB and sB["edges"]:
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
            overtB.co = vert.co + offset_vectorB * self.width

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

            offsetdict[sA["vert"]]["offsetA"] = sA["offset_vert"]
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
