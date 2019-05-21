import bpy
from bpy.props import IntProperty, BoolProperty
import bmesh
import mathutils
import math
from .. utils.support import loop_index_update
from .. utils.debug import draw_vector
from .. utils import MACHIN3 as m3



axisdict = {"X": mathutils.Vector((1, 0, 0)),
            "Y": mathutils.Vector((0, 1, 0)),
            "Z": mathutils.Vector((0, 0, 1))}


class RealMirror(bpy.types.Operator):
    bl_idname = "machin3.real_mirror"
    bl_label = "MACHIN3: Real Mirror"
    bl_options = {'REGISTER', 'UNDO'}

    uoffset = IntProperty(name="U", default=0)
    voffset = IntProperty(name="V", default=0)

    create_mirror_group = BoolProperty(name="Create Mirror Group", default=True)
    apply_data_transfers = BoolProperty(name="Apply Data Transfers", default=True)

    # @classmethod
    # def poll(cls, context):
        # active = m3.get_active()
        # return [mod for mod in active.modifiers if mod.type == "MIRROR" and mod.show_render and mod.show_render]

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        box = layout.box()

        row = box.row()
        row.prop(self, "create_mirror_group")
        row.prop(self, "apply_data_transfers")

        box = layout.box()
        box.label("UV Offset")

        row = box.row()
        row.prop(self, "uoffset")
        row.prop(self, "voffset")

    def execute(self, context):
        debug = False
        # debug = True

        if debug:
            m3.clear()
            m3.set_mode("EDIT")
            m3.debug_idx()
            m3.set_mode("OBJECT")

        sel = m3.selected_objects()

        mirror_objs = []

        while sel:
            active = m3.make_active(sel[0])

            mirrors = [mod for mod in active.modifiers if mod.type == "MIRROR" and mod.show_render and mod.show_render and any([mod.use_x, mod.use_y, mod.use_z])]

            if not mirrors:
                sel.remove(active)
            else:
                self.custom_normals = active.data.has_custom_normals

                # get the loop normals of the original mesh if it has custom normals and create a dictionary to pair loops on the original with the mirror via face and vert indices
                loop_data = self.get_loop_data(active) if self.custom_normals else None

                for mod in mirrors:
                    # get the object to mirror across
                    target = mod.mirror_object if mod.mirror_object else active

                    # toggle the mirror mod off, but keep it around
                    mod.show_viewport = False
                    mod.show_render = False

                    # get the mirror axes
                    axes = (mod.use_x, mod.use_y, mod.use_z)

                    # get uv mirror and offset
                    uvs = (mod.use_mirror_u, mod.use_mirror_v)
                    uvoffsets = (self.uoffset, self.voffset)

                    # if you have one axes selected, one mirror is to be done
                    # if you have two axes selected, three mirrors are to be done, 2 of the original, 1 of a mirror
                    # if you have three axes selected, seven mirrros ara to be done, 3 of the original, 3 of previous mirrors, and 1 of a mirror of a mirror

                    if axes[0]:
                        # print("mirror X, 1.gen")
                        mirror_obj1 = self.real_mirror(active, target, loop_data, mod.name, "X", uvs, uvoffsets, debug=debug)
                        loop_data1 = self.get_loop_data(mirror_obj1) if self.custom_normals else (None, None)

                        # add the mirrored object, to be re-evaluated for mirror mods at the biggining
                        sel.append(mirror_obj1)
                        mirror_objs.append(mirror_obj1)

                        if axes[1]:
                            # print(" » mirror Y, 2.gen")
                            mirror_obj2 = self.real_mirror(mirror_obj1, target, loop_data1, mod.name, "Y", uvs, uvoffsets, debug=debug)
                            loop_data2 = self.get_loop_data(mirror_obj2) if self.custom_normals else (None, None)

                            sel.append(mirror_obj2)
                            mirror_objs.append(mirror_obj2)

                            if axes[2]:
                                # print("  » mirror Z, 3.gen")
                                mirror_obj3 = self.real_mirror(mirror_obj2, target, loop_data2, mod.name, "Z", uvs, uvoffsets, debug=debug)

                                sel.append(mirror_obj3)
                                mirror_objs.append(mirror_obj3)

                        if axes[2]:
                            # print(" » mirror Z, 2.gen")
                            mirror_obj2 = self.real_mirror(mirror_obj1, target, loop_data1, mod.name, "Z", uvs, uvoffsets, debug=debug)
                            loop_data2 = self.get_loop_data(mirror_obj2) if self.custom_normals else (None, None)

                            sel.append(mirror_obj2)
                            mirror_objs.append(mirror_obj2)

                    if axes[1]:
                        # print("mirror Y, 1.gen")
                        mirror_obj1 = self.real_mirror(active, target, loop_data, mod.name, "Y", uvs, uvoffsets, debug=debug)
                        loop_data1 = self.get_loop_data(mirror_obj1) if self.custom_normals else (None, None)

                        sel.append(mirror_obj1)
                        mirror_objs.append(mirror_obj1)

                        if axes[2]:
                            # print(" » mirror Z, 2.gen")
                            mirror_obj2 = self.real_mirror(mirror_obj1, target, loop_data1, mod.name, "Z", uvs, uvoffsets, debug=debug)

                            sel.append(mirror_obj2)
                            mirror_objs.append(mirror_obj2)

                    if axes[2]:
                        # print("mirror Z, 1.gen")
                        mirror_obj1 = self.real_mirror(active, target, loop_data, mod.name, "Z", uvs, uvoffsets, debug=debug)
                        sel.append(mirror_obj1)
                        mirror_objs.append(mirror_obj1)

        # create a group for the mirros to be able to go back to mirrored versions easily
        if self.create_mirror_group and mirror_objs:
            dupsgroup = bpy.data.groups.get("realmirror")
            if not dupsgroup:
                dupsgroup = bpy.data.groups.new("realmirror")

            for obj in mirror_objs:
                dupsgroup.objects.link(obj)

        return {'FINISHED'}

    def real_mirror(self, active, target, loop_data, modname, axis, uvs, uvoffsets, debug=False):
        # create a duplicate object and mirror it
        mirror_obj, loop_data = self.mirror_object(active, target, loop_data, axis, modname, debug=debug)

        # apply the scale, rotate 180° and flip the normals
        bm = self.apply_transformation(mirror_obj, axis)

        # mirror the uvs
        if any(uvs):
            bm = self.mirror_uvs(bm, *uvs, *uvoffsets)

        # mirror the normals
        if self.custom_normals:
            self.mirror_normals(bm, mirror_obj, loop_data, axis, debug=debug)
        else:
            bm.to_mesh(mirror_obj.data)
            bm.clear()

        return mirror_obj

    def mirror_uvs(self, bm, umirror, vmirror, uoffset=0, voffset=0):
        # uvs = bm.loops.layers.uv.verify()
        uvs = bm.loops.layers.uv.active

        if uvs:

            # mirror uvs across origin and collect us and vs and mirrored us and vs

            us = []
            vs = []
            mir_us = []
            mir_vs = []

            for face in bm.faces:
                for loop in face.loops:
                    # original uvs
                    uv = loop[uvs].uv

                    us.append(uv[0])
                    vs.append(uv[1])

                    if umirror:
                        loop[uvs].uv = uv.reflect(mathutils.Vector((1, 0)))
                    if vmirror:
                        loop[uvs].uv = uv.reflect(mathutils.Vector((0, 1)))

                    # mirrord uvs
                    uv = loop[uvs].uv

                    mir_us.append(uv[0])
                    mir_vs.append(uv[1])

            # do a base offset, to put the mirrored uvs into the same location as the original uvs
            # optionally do an additional offset
            for face in bm.faces:
                for loop in face.loops:
                    # base offset
                    loop[uvs].uv += mathutils.Vector((min(us) - min(mir_us), min(vs) - min(mir_vs)))

                    # offset uvs
                    if any([uoffset, voffset]):
                        loop[uvs].uv += mathutils.Vector((uoffset, voffset))

        return bm

    def mirror_normals(self, bm, mirror_obj, loop_data, axis, debug=False):
        # pair the loops
        mirror_loops = self.pair_loops(bm, mirror_obj, loop_data["indices"], debug=debug)

        # create the new normals by reflecting the original ones and the paired loops
        new_loop_normals = self.create_loop_normals(loop_data["normals"], mirror_loops, axis)

        # finally set the new normals
        mirror_obj.data.calc_normals_split()
        mirror_obj.data.normals_split_custom_set(new_loop_normals)

    def create_loop_normals(self, orig_loop_normals, mirror_loops, axis):
        new_loop_normals = []

        for idx in range(len(orig_loop_normals)):
            nrm = orig_loop_normals[mirror_loops[idx]]

            # if you don't do the 180 degree rotation fix in self.apply.transformation you get the new normals by reflecting the old ones across themselves
            # new_loop_normals.append(nrm.reflect(nrm))

            # if you do the rotation fix, you need to properly flect them across the mirror axis
            new_loop_normals.append(nrm.reflect(axisdict[axis]))

        return new_loop_normals

    def pair_loops(self, bm, obj, orig_loop_indices, debug=False):
        loop_index_update(bm)

        mirror_loops = {}

        # associate loops ids on the mirrored obj with the loop ids on the original
        for face in bm.faces:
            if debug:
                print("face:", face.index)

            for loop in face.loops:
                if debug:
                    print(" » vert:", loop.vert.index, "loop:", loop.index)
                    print("  » original loop:", orig_loop_indices[(face.index, loop.vert.index)])
                mirror_loops[loop.index] = orig_loop_indices[(face.index, loop.vert.index)]

        bm.to_mesh(obj.data)
        bm.clear()

        return mirror_loops

    def apply_transformation(self, obj, axis):
        # at this point the scale is negative, so we need to "apply" it
        # we do this by inverting the scale of the object, first on an object level, then on a vert level
        mx_world = obj.matrix_world.copy()
        mx_scale = mathutils.Matrix.Scale(-1, 4)

        # it also looks like the rotation is 180, so compensate for that as well, it's fine without as well, but z is up where it shold be down etc
        mx_rotation = mathutils.Matrix.Rotation(math.radians(180), 4, axis)

        # mx_world.inverted() * mx_world puts it in local space (literally puts it in the scene origin)
        # mx scale scales it, and mx_world puts it back into the original location
        # you may also be able to decompose, negate the scale vector and recompose
        obj.matrix_world = mx_world * mx_rotation * mx_scale * mx_world.inverted() * mx_world

        # inverting the scale on a vert level, also flips the normals
        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        for v in bm.verts:
            v.co = mx_rotation * mx_scale * v.co

        # flip normals
        for f in bm.faces:
            f.normal_flip()

        return bm

    def mirror_object(self, obj, target, loop_data, axis, mirrormodname, debug=False):
        targetmx = target.matrix_world

        # create the mirror object by duplicating the obj
        mir = obj.copy()
        mir.data = obj.data.copy()
        bpy.context.scene.objects.link(mir)
        m3.make_active(mir)

        # remove the mirror modifier
        if mir.modifiers.get(mirrormodname):
            bpy.ops.object.modifier_remove(modifier=mirrormodname)

        # apply data transfer mods, which will produce desired results once the object is mirrored and no longer matches the data transfers source obj
        if self.apply_data_transfers:
            data_transfers = [mod for mod in mir.modifiers if mod.type == "DATA_TRANSFER"]
            for d in data_transfers:
                bpy.ops.object.modifier_apply(modifier=d.name)

            # if a data transfer was applied, you need to check if the object now has custom normals and if so, set the loop_data
            self.custom_normals = mir.data.has_custom_normals

            if self.custom_normals:
                loop_data = self.get_loop_data(mir, debug=debug)


        # mirror the object by scaling across the target's localg axis vector
        mir_mx = mathutils.Matrix.Scale(-1, 4, axisdict[axis])

        # bring into target's local space, scale, bring back into world space
        mir.matrix_world = targetmx * mir_mx * targetmx.inverted() * mir.matrix_world

        return mir, loop_data

    def get_loop_data(self, obj, debug=False):
        obj.data.calc_normals_split()

        # loop normals are not available in bmesh it seems
        loop_normals = []
        for idx, loop in enumerate(obj.data.loops):
            loop_normals.append(loop.normal.normalized())  # normalize them, or you will run into weird issues at the end!
            if debug:
                print(idx, loop.normal)

        # create a dict to select loops by face and vert index, both together uniquely identify a loop
        # face and vert ids will stay the same on the mirrored mesh, but loops are different

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        loop_indices = {}
        for face in bm.faces:
            if debug:
                print("face:", face.index)
            for loop in face.loops:
                if debug:
                    print(" » vert:", loop.vert.index, "loop:", loop)

                loop_indices[(face.index, loop.vert.index)] = loop.index

        bm.clear()

        # create asingle dict carrying both, normals list and indices dict

        loop_data = {}
        loop_data["normals"] = loop_normals
        loop_data["indices"] = loop_indices

        return loop_data
