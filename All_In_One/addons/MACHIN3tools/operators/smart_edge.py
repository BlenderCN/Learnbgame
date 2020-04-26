import bpy
import bmesh
from bpy.props import EnumProperty
from .. utils import MACHIN3 as m3



class SmartEdge(bpy.types.Operator):
    bl_idname = "machin3.smart_edge"
    bl_label = "MACHIN3: Smart Edge"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return m3.get_mode() in ["VERT", "EDGE", "FACE"]

    def execute(self, context):
        mode = m3.get_mode()


        if mode == "VERT":
            selverts = m3.get_selection("VERT")

            # KNIFE

            if len(selverts) <= 1:
                bpy.ops.mesh.knife_tool('INVOKE_DEFAULT')


            # PATH / STAR CONNECT

            else:
                active = m3.get_active()

                # star connects when appropriate, and if it doesn't returns false, because there doesn't seem to be a good way to do a path connect in bmesh
                connect = self.connect(active)

                if not connect:
                    bpy.ops.mesh.vert_connect_path()


        elif mode == "EDGE":
            seledges = m3.get_selection("EDGE")

            # LOOPCUT

            if len(seledges) == 0:
                bpy.ops.mesh.loopcut_slide('INVOKE_DEFAULT')


            # TURN EDGE

            elif 1 <= len(seledges) < 4:
                bpy.ops.mesh.edge_rotate(use_ccw=False)

            # LOOP TO REGION

            elif len(seledges) >= 4:
                bpy.ops.mesh.loop_to_region()
                m3.set_mode("FACE")


        elif mode == "FACE":
            selfaces = m3.get_selection("FACE")

            # LOOPCUT

            if len(selfaces) == 0:
                bpy.ops.mesh.loopcut_slide('INVOKE_DEFAULT')

            # REGION TO LOOP

            elif len(selfaces) >= 1:

                # NOTE, there seems to be an issue, where blender doesn't update the mode properly
                # futhermore, I can't manually update if after region to loop either
                # doing it before works however
                m3.set_mode("EDGE")

                bpy.ops.mesh.region_to_loop()

        return {'FINISHED'}

    def connect(self, active):
        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]
        history = list(bm.select_history)
        last = history[-1] if history else None

        # check if there's a common face shared by all the verts, a good indicator for star connect
        faces = [f for v in verts for f in v.link_faces]

        common = None
        for f in faces:
            if all([v in f.verts for v in verts]):
                common = f


        # with only two verts, only a path connect makes sence, unless the verts are connected already, then nothing should be done, it works even without a history in the case of just 2
        if len(verts) == 2 and not bm.edges.get([verts[0], verts[1]]):
            return False

        # with 3 verts the base assumption is, you want to make a path connect, common face or not
        elif len(verts) == 3:
            # nothing goes without an active vert
            if last:

                # for path connect you need to have a complete history
                if len(verts) == len(history):
                    return False

                # without a complete history the only option is star connect, but that works only with a common face
                elif common:
                    self.star_connect(bm, last, verts)


        # with more than 3 verts, the base assumption is, you want to make a star connect, complete history or not
        elif len(verts) > 3:
            # nothing goes without an active vert
            if last:

                # for star connect, you need to have a common face
                if common:
                    self.star_connect(bm, last, verts)


                # without a common face, the only option is path connect but that needs a complete history
                elif len(verts) == len(history):
                    return False

        bmesh.update_edit_mesh(active.data)
        return True

    def star_connect(self, bm, last, verts):
        verts.remove(last)

        for v in verts:
            bmesh.ops.connect_verts(bm, verts=[last, v])
