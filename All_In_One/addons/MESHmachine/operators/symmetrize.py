import bpy
from bpy.props import BoolProperty, FloatProperty, EnumProperty
import mathutils
import bmesh
from .. utils.normal import normal_clear, normal_transfer_from_obj
from .. utils.support import loop_index_update, add_vgroup
from .. utils.ui import negate_string
from .. utils.developer import output_traceback
from .. utils import MACHIN3 as m3


# TODO: make it work it optionally work on selections only?


cnmirrormethoditems = [("INDEX", "Index", ""),
                       ("LOCATION", "Location", "")]

fixcentermethoditems = [("CLEAR", "Clear Normals", ""),
                        ("TRANSFER", "Transfer Normals", "")]

axisitems = [("X", "X", ""),
             ("Y", "Y", ""),
             ("Z", "Z", "")]

directionitems = [("POSITIVE", "+ to -", ""),
                  ("NEGATIVE", "- to +", "")]


vertids = []


class Symmetrize(bpy.types.Operator):
    bl_idname = "machin3.symmetrize"
    bl_label = "MACHIN3: Symmetrize"
    bl_options = {'REGISTER', 'UNDO'}

    # onlyselected = BoolProperty(name="Selected Only", default=False)

    axis = EnumProperty(name="Axis", items=axisitems, default="X")
    direction = EnumProperty(name="Direction", items=directionitems, default="POSITIVE")

    cnmirror = BoolProperty(name="Mirror Custom Normals", default=True)

    cnmirrormethod = EnumProperty(name="CN Mirror Method", items=cnmirrormethoditems, default="INDEX")

    fixcenter = BoolProperty(name="Fix Center Seam", default=False)
    fixcentermethod = EnumProperty(name="Fix Center Method", items=fixcentermethoditems, default="CLEAR")
    clearsharps = BoolProperty(name="Clear Center Sharps", default=True)

    # hidden
    hascustomnormals = BoolProperty(default=False)

    # debug
    debug = BoolProperty(default=False)
    alpha = FloatProperty(name="Alpha", default=0.3, min=0.1, max=1)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.prop(self, "axis", expand=True)
        row.prop(self, "direction", expand=True)

        if self.hascustomnormals:
            column.separator()
            column.prop(self, "cnmirror")

            if self.cnmirror:
                box = column.box()
                box.label("Custom Normal Pairing Method")
                row = box.row()
                row.prop(self, "cnmirrormethod", expand=True)

                column.separator()
                column.prop(self, "fixcenter")

                if self.fixcenter:
                    box = column.box()

                    row = box.row()
                    row.label("Fix Center Method")
                    row.prop(self, "clearsharps")

                    row = box.row()
                    row.prop(self, "fixcentermethod", expand=True)

    def execute(self, context):
        # if self.debug:
            # try:
                # bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            # except:
                # pass

        self.active = m3.get_active()

        try:
            custom_normals, ret = self.main(self.active)

            if custom_normals:
                original, mirror, center, mirror_verts, mirror_faces, mirror_loops = ret
            else:
                original, mirror, center = ret

            # if we want to draw the symmetrize while maintaining the ability to REDO the symmetrize op,
            # we need to do the drawing with a seperate op that doesn't have REDO in the bl_options otherwise there will be crashes

            # set the verts for the drawing op
            global vertids
            vertids = mirror + center

            bpy.ops.machin3.draw_symmetrize()

        except:
            output_traceback(self)

        # if self.debug:
            # original, mirror, center, mirror_verts, mirror_faces, mirror_loops = ret

            # # debug mirror verts
            # self.mvs = mirror_verts
            # args = (self, context)
            # self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D_debug_pairing, (args, ), 'WINDOW', 'POST_VIEW')

        return {'FINISHED'}

    def main(self, active):
        # self.debug = True

        if self.debug:
            m3.clear()
            m3.debug_idx()

        print("\nSymmetrizing %s" % (active.name))

        mesh = active.data
        self.hascustomnormals = mesh.has_custom_normals

        nrmsrc = False
        if self.hascustomnormals:
            print(" » Custom Normals detected!")

            if self.cnmirror and self.fixcenter and self.fixcentermethod == "TRANSFER":
                print(" » Creating normal source!")

                active.update_from_editmode()

                nrmsrc = active.copy()
                nrmsrc.data = active.data.copy()


        # unhide and select all, as the symmetrize op works on selections
        m3.unhide_all("MESH")
        m3.select_all("MESH")

        direction = "%s_%s" % (self.direction, self.axis)
        bpy.ops.mesh.symmetrize(direction=direction, threshold=0.0001)

        m3.unselect_all("MESH")

        # custom normals
        if self.hascustomnormals and self.cnmirror:
            # its possible the mesh has custom normas, but has auto smooth turned off
            # force it on so as to not losse them, because you cant mirror them with it turned off and expect to turn it on afterwards with normals intact
            if not mesh.use_auto_smooth:
                mesh.use_auto_smooth = True

            m3.set_mode("OBJECT")

            # get existing loop normals
            mesh = active.data
            mesh.calc_normals_split()

            loop_normals = []
            for idx, loop in enumerate(mesh.loops):
                loop_normals.append(loop.normal.normalized())  # normalized them, or you will run into weird issues at the end!
                if self.debug:
                    print(idx, loop.normal)

            # create new bmesh
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            # some of the loop indices are invalid, interesting, as all that was done is call a bpy.ops and create a fresh bm
            loop_index_update(bm)

            # get vertex lists for each side + center line
            sides = self.sort_verts_into_sides(bm, self.axis, self.direction, debug=self.debug)

            # get vertex pairs in form of a dict {v_original: v_mirror, ...}
            # LOCATION is 1.5-2x slower as it's matching individual vertex locations
            if self.cnmirrormethod == "INDEX":
                mirror_verts = self.get_mirror_verts_via_index(bm, *sides, debug=self.debug)
            elif self.cnmirrormethod == "LOCATION":
                mirror_verts = self.get_mirror_verts_via_location(bm, *sides, self.axis, debug=self.debug)

            # we are then matching faces with their mirrored faces
            mirror_faces, loops = self.get_mirror_faces(bm, mirror_verts)

            # finally we set up a loop dict, that we can can then use to  associate each loop of a face with it's mirrored part
            mirror_loops = self.get_mirror_loops(bm, mirror_verts, mirror_faces, loops)

            # edit the original loop_normals list and replace the normals of the mirrord verts, with reflections of the original normals
            if self.axis == "X":
                mirror = mathutils.Vector((1, 0, 0))
            elif self.axis == "Y":
                mirror = mathutils.Vector((0, 1, 0))
            elif self.axis == "Z":
                mirror = mathutils.Vector((0, 0, 1))

            for ml in mirror_loops:
                loop_normals[mirror_loops[ml]] = loop_normals[ml].reflect(mirror)

            # set the new normals on the active obj's mesh
            mesh.normals_split_custom_set(loop_normals)

            # fix the center / go back into edit mode
            if sides[2]:  # only attempt to do it, if there actually are center verts!
                self.fix_center_seam(active, sides[2], nrmsrc)

            if nrmsrc:
                print(" » Removing normal source!")
                bpy.data.objects.remove(nrmsrc, do_unlink=True)

            return True, (sides[0], sides[1], sides[2], mirror_verts, mirror_faces, mirror_loops)

        else:
            m3.set_mode("OBJECT")

            mesh = active.data

            # create new bmesh
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            # some of the loop indices are invalid, interesting, as all that was done is call a bpy.ops and create a fresh bm
            loop_index_update(bm)

            # get vertex lists for each side + center line
            sides = self.sort_verts_into_sides(bm, self.axis, self.direction, debug=self.debug)

            m3.set_mode("EDIT")

        return False, (sides[0], sides[1], sides[2])

    def fix_center_seam(self, active, center, nrmsrc):
        if self.fixcenter:
            if self.fixcentermethod == "CLEAR":
                print(" » Fixing Center Seam by clearing normals.")
            elif self.fixcentermethod == "TRANFER":
                print(" » Fixing Center Seam by transfering normals")

            # select center line
            for v in active.data.vertices:
                if v.index in center:
                    v.select = True

        m3.set_mode("EDIT")

        if self.fixcenter:
            mode = m3.get_mode()
            if mode != "VERT":
                m3.set_mode("VERT")

            # sometimes not all center verts are marked for some reason, so loop select
            bpy.ops.mesh.loop_multi_select(ring=False)

            # clear sharps
            if self.clearsharps:
                print(" » Removing Center Seam Sharps.")
                bpy.ops.mesh.mark_sharp(clear=True)

            # clear or transfer
            if self.fixcentermethod == "CLEAR":
                normal_clear(self.active, limit=False)
            elif self.fixcentermethod == "TRANSFER":
                normal_transfer_from_obj(active, nrmsrc, vertids=center, remove_vgroup=True)

            m3.unselect_all("MESH")

            if mode != "VERT":
                m3.set_mode(mode)


    def get_mirror_loops(self, bm, mirror_verts, mirror_faces, loops):
        # set up a dict to select loops via (face.index, vert.index) tuples
        mirror_loops = {}
        for fidx in mirror_faces:
            for loop in bm.faces[fidx].loops:
                mirror_loops[loop.index] = loops[(mirror_faces[fidx], mirror_verts[loop.vert.index])]

        if self.debug:
            print("loops")
            for ml in mirror_loops:
                print(ml, mirror_loops[ml])

            for face in bm.faces:
                print("face:", face.index)
                for loop in face.loops:
                    print(" » ", "loop: %d, vert: %d" % (loop.index, loop.vert.index))

        return mirror_loops

    def get_mirror_faces(self, bm, mirror_verts):
        # we are using frozensets of the per face vert indices as keys
        # for frozensets - as with sets -  the order doesnt matter, which is important as the order of face.verts is probably not the same on both sides
        # sets are not hashable, so cant be used as keys for dicts, but frozensets are and can!
        faces = {}
        loops = {}
        for face in bm.faces:
            vertlist = [v.index for v in face.verts]
            faces[frozenset(vertlist)] = face.index

            # we are also creating a loops dict, with (face.index, vert.index) tuples as keys. the face, vert combination uniquely identifies every loop
            for loop in face.loops:
                loops[(face.index, loop.vert.index)] = loop.index

        if self.debug:
            print(faces)
            print()
            print(loops)
            print()

        mirror_faces = {}
        for vertlist in faces:
            # you can only find mirror verts with original verts, not the other way around
            # we also only want to find the mirror faces using the original ones
            try:
                mirrored_vertlist = frozenset([mirror_verts[idx] for idx in vertlist])
                mirror_faces[faces[vertlist]] = faces[mirrored_vertlist]
            except:
                pass

        if self.debug:
            print("faces")
            for mf in mirror_faces:
                print(mf, mirror_faces[mf])
            print()

        return mirror_faces, loops

    def sort_verts_into_sides(self, bm, axis, direction, debug=False):
        original = []
        mirror = []
        center = []

        # threshold to correct vertices that should be at zero but aren't (due to float precision issues? due to the symmetrize threshold?)
        # this can prevent cases where the original and mirror lists are of different lengths
        # if that happens, you'll get a keyerror in the LOCATION based pairing
        # it looks like this also fixes the INDEX issues that led to the creation of the LOCATION method in the first place

        threshold = 0.0001  # expose this?

        for v in bm.verts:

            # X axis
            if axis == "X":
                if -threshold < v.co[0] < threshold:
                    v.co[0] = 0
                    if debug:
                        print("centered vertex %d" % (v.index))

                if direction == "POSITIVE":
                    if v.co[0] == 0:
                        center.append(v.index)
                    elif v.co[0] > 0:
                        original.append(v.index)
                    else:
                        mirror.append(v.index)
                elif direction == "NEGATIVE":
                    if v.co[0] == 0:
                        center.append(v.index)
                    elif v.co[0] < 0:
                        original.append(v.index)
                    else:
                        mirror.append(v.index)

            # Y axis
            if axis == "Y":
                if -threshold < v.co[1] < threshold:
                    v.co[1] = 0
                    if debug:
                        print("centered vertex %d" % (v.index))

                if direction == "POSITIVE":
                    if v.co[1] == 0:
                        center.append(v.index)
                    elif v.co[1] > 0:
                        original.append(v.index)
                    else:
                        mirror.append(v.index)
                elif direction == "NEGATIVE":
                    if v.co[1] == 0:
                        center.append(v.index)
                    elif v.co[1] < 0:
                        original.append(v.index)
                    else:
                        mirror.append(v.index)

            # Z axis
            if axis == "Z":
                if -threshold < v.co[2] < threshold:
                    v.co[2] = 0
                    if debug:
                        print("centered vertex %d" % (v.index))

                if direction == "POSITIVE":
                    if v.co[2] == 0:
                        center.append(v.index)
                    elif v.co[2] > 0:
                        original.append(v.index)
                    else:
                        mirror.append(v.index)
                elif direction == "NEGATIVE":
                    if v.co[2] == 0:
                        center.append(v.index)
                    elif v.co[2] < 0:
                        original.append(v.index)
                    else:
                        mirror.append(v.index)

            v.select = False
        bm.select_flush(False)

        # warn if list sizes are still uneven
        if len(original) != len(mirror):
            print(" ! WARNING, uneven vertex list sizes!")

        return original, mirror, center

    def get_mirror_verts_via_index(self, bm, original, mirror, center, debug=False):
        # match vetices on both sides
        # it turns out, they are often in perfect order already and can be matched simply by their positions in the original/mirror lists
        # so we can set up the mirror vert pairs in a dict by iterating over both sides in parallel
        # this allows us to pick a vert on the original side and retrieve it's mirror vert

        mirror_verts = {}
        for vm, vp in zip(mirror, original):
            mirror_verts[vp] = vm

        # now add the center verts as double pairs
        for vz in center:
            mirror_verts[vz] = vz

        if debug:
            print("verts")
            for mv in mirror_verts:
                print(mv, mirror_verts[mv])
            print()

        return mirror_verts

    def get_mirror_verts_via_location(self, bm, original, mirror, center, axis, debug=False):
        precision = 10

        if debug:
            print("original:", original)
            print("mirror:", mirror)

        # create a dictionary of dictionaries to select verts by their secondary location axis set as keys first
        # (y, z) for X mirror, (x, z) for Y mirror and (x, y) for Z mirrorm
        # then add dicts as values, using the mirror axis as a key and the vertex index as the value

        if axis == "X":
            yz = {}
        elif axis == "Y":
            xz = {}
        elif axis == "Z":
            xy = {}

        for v in bm.verts:
            x = "%.*f" % (precision, v.co[0])
            y = "%.*f" % (precision, v.co[1])
            z = "%.*f" % (precision, v.co[2])

            if debug:
                print(v.index, "»", x, y, z)

            if axis == "X":
                if (y, z) not in yz:
                    yz[(y, z)] = {}

                yz[(y, z)][x] = v.index
            elif axis == "Y":
                if (x, z) not in xz:
                    xz[(x, z)] = {}

                xz[(x, z)][y] = v.index
            elif axis == "Z":
                if (x, y) not in xy:
                    xy[(x, y)] = {}

                xy[(x, y)][z] = v.index

        if debug:
            print()
            if axis == "X":
                print("yz keys")
                for vert in yz:
                    print(vert)
                    print(" »", yz[vert])
            elif axis == "Y":
                print("xz keys")
                for vert in xz:
                    print(vert)
                    print(" »", xz[vert])
            elif axis == "Z":
                print("xy keys")
                for vert in xy:
                    print(vert)
                    print(" »", xy[vert])

        # create the mirror pairs
        mirror_verts = {}


        for idx in original:
            vo = bm.verts[idx]

            x = "%.*f" % (precision, vo.co[0])
            y = "%.*f" % (precision, vo.co[1])
            z = "%.*f" % (precision, vo.co[2])

            if axis == "X":
                mirror_verts[idx] = yz[(y, z)][negate_string(x)]
            elif axis == "Y":
                mirror_verts[idx] = xz[(x, z)][negate_string(y)]
            elif axis == "Z":
                mirror_verts[idx] = xy[(x, y)][negate_string(z)]

        # now add the center verts as double pairs
        for vc in center:
            mirror_verts[vc] = vc

        if debug:
            for mv in mirror_verts:
                print(mv, mirror_verts[mv])

        return mirror_verts
