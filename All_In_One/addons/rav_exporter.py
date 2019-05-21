bl_info = {
    "name": "RavenEngine (.rav, .rani)",
    "category": "Import-Export",
    "version": (0, 1),
    "blender": (2, 76, 0),
    "location": "File > Export > RavenEngine",
}

import sys, getopt
import bpy
from bpy_extras.io_utils import ExportHelper

def ytuple(v):
    return tuple([v[0], v[1], v[2]])

def yrtuple(v):
    return tuple([v[0], v[1], v[2], v[3]])


class RaniExport(bpy.types.Operator, ExportHelper):
    """Export a single object as a RavenEngine RANI armature, """ \
    """poses, and keyframes?..."""
    bl_idname       = "export_animation.rani"
    bl_label        = "Export RANI"
    bl_options      = {'PRESET'}

    filename_ext    = ".rani"

    def __init__(self):
        pass

    def execute(self, context):
        print("Execute was called.")

        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        print("Exporting Animation")
        self.export_animation(filepath, context)

        print("Finished")
        return {'FINISHED'}

    def export_animation(self, filepath, context):

        # base objects
        scene = context.scene
        obj = context.active_object

        armature = bpy.data.armatures[0]
        armature = bpy.data.objects[armature.name] # why...
        pose = armature.pose

        # write file
        file = open(filepath, "w", encoding="utf8", newline="\n")
        fw = file.write

        for action in bpy.data.actions:
            print("Action: " + action.name)
            fw(action.name + "\n")

            bones = {}
            boneList = []
            frames = []

            # x y z qr qi qj qk sx sy sz
            for fcurve in action.fcurves:

                s = fcurve.data_path.split('.')
                s2 = fcurve.data_path.split('"')
                boneName = s2[1]
                prop = s[-1]

                bone = None

                if boneName in bones:
                    bone = bones[boneName]
                else:
                    bone = {
                        'head': [],
                        'tail': [],
                        'location': [],
                        'rotation': [],
                        'scale': [],
                        'vector': [],
                        'parent': None,
                        'name': boneName
                    }
                    bones[boneName] = bone
                    boneList.append(bone)

                for kf in fcurve.keyframe_points:
                    frameIndex = int(kf.co[0])

                    frames.append(frameIndex)
            print(frames)
            frames = list(set(frames))
            frames.sort()
            print(frames)

            # for name in bones:
            #     bone = bones[name]
            #     posebone = pose.bones[bone['name']]
            #     bone['head'] = posebone.head
            #     bone['tail'] = posebone.tail

            # get tail
            bpy.context.scene.frame_set(0)

            for frame in frames:

                fw(str(frame) + " ")

                bpy.context.scene.frame_set(frame)

                for name in bones:
                    bone = bones[name]
                    posebone = armature.pose.bones[bone['name']]

                    bone['location'].append(posebone.location[:])
                    bone['rotation'].append(posebone.rotation_quaternion[:])
                    bone['scale'].append(posebone.scale[:])
                    bone['vector'].append(posebone.vector[:])
                    bone['head'].append(posebone.head[:])
                    bone['tail'].append(posebone.tail[:])
                    print(frame)
                    print(posebone.rotation_quaternion)
                    print(posebone.head)
                    print(posebone.tail)
                    print()

                    if posebone.parent is not None:
                        bone['parent'] = posebone.parent.name

            fw("\n")

            for bone in boneList:

                fw(str(bone['name']) + "\n")
                fw(str(bone['parent']) + "\n")
                # fw("%.6f %.6f %.6f " % tuple(bone['head']))
                # fw("\n")
                # fw("%.6f %.6f %.6f " % tuple(bone['tail']))
                # fw("\n")

                for location in bone['location']:
                    fw("%.6f %.6f %.6f " % ytuple(location))
                fw("\n")

                for rotation in bone['rotation']:
                    fw("%.6f %.6f %.6f %.6f " % yrtuple(rotation))
                fw("\n")

                for scale in bone['scale']:
                    fw("%.6f %.6f %.6f " % ytuple(scale))
                fw("\n")

                for vector in bone['vector']:
                    fw("%.6f %.6f %.6f " % ytuple(vector))
                fw("\n")

                for head in bone['head']:
                    fw("%.6f %.6f %.6f " % ytuple(head))
                fw("\n")

                for tail in bone['tail']:
                    fw("%.6f %.6f %.6f " % ytuple(tail))
                fw("\n")

            fw("\n")

        file.close()

        print("writing %r done" % filepath)


class RavExport(bpy.types.Operator, ExportHelper):
    """Export a single object as a RavenEngine RAV with normals, """ \
    """colors, texture coordinates, armature weights..."""
    bl_idname       = "export_mesh.rav"
    bl_label        = "Export RAV"
    bl_options      = {'PRESET'}

    filename_ext    = ".rav"

    def __init__(self):
        pass

    def execute(self, context):
        print("Execute was called.")

        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        print("Exporting Object")
        self.export_object(filepath, context)

        print("Finished")
        return {'FINISHED'}


    def export_object(self, filepath, context):

        def rvec3d(v):
            return round(v[0], 6), round(v[1], 6), round(v[2], 6)

        def rvec2d(v):
            return round(v[0], 6), round(v[1], 6)

        # base objects
        mesh = bpy.data.meshes[0]
        obj = bpy.data.objects[mesh.name]
        vertex_groups = obj.vertex_groups

        use_normals = True
        use_uv_coords = True
        use_colors = True

        # Be sure tessface & co are available!
        if not mesh.tessfaces and mesh.polygons:
            mesh.calc_tessface()

        has_uv = bool(mesh.tessface_uv_textures)
        has_vcol = bool(mesh.tessface_vertex_colors)

        if not has_uv:
            use_uv_coords = False
        if not has_vcol:
            use_colors = False

        if not use_uv_coords:
            has_uv = False
        if not use_colors:
            has_vcol = False

        if has_uv:
            active_uv_layer = mesh.tessface_uv_textures.active
            if not active_uv_layer:
                use_uv_coords = False
                has_uv = False
            else:
                active_uv_layer = active_uv_layer.data

        if has_vcol:
            active_col_layer = mesh.tessface_vertex_colors.active
            if not active_col_layer:
                use_colors = False
                has_vcol = False
            else:
                active_col_layer = active_col_layer.data

        # in case
        color = uvcoord = uvcoord_key = normal = normal_key = None

        mesh_verts = mesh.vertices  # save a lookup
        ply_verts = []  # list of dictionaries
        # vdict = {} # (index, normal, uv) -> new index
        vdict = [{} for i in range(len(mesh_verts))]
        ply_faces = [[] for f in range(len(mesh.tessfaces))]
        vert_count = 0
        for i, f in enumerate(mesh.tessfaces):

            smooth = not use_normals or f.use_smooth
            if not smooth:
                normal = f.normal[:]
                normal_key = rvec3d(normal)

            if has_uv:
                uv = active_uv_layer[i]
                uv = uv.uv1, uv.uv2, uv.uv3, uv.uv4
            if has_vcol:
                col = active_col_layer[i]
                col = col.color1[:], col.color2[:], col.color3[:], col.color4[:]


            f_verts = f.vertices

            pf = ply_faces[i]
            for j, vidx in enumerate(f_verts):
                v = mesh_verts[vidx]

                if smooth:
                    normal = v.normal[:]
                    normal_key = rvec3d(normal)

                if has_uv:
                    uvcoord = uv[j][0], uv[j][1]
                    uvcoord_key = rvec2d(uvcoord)

                if has_vcol:
                    color = col[j]
                    color = rvec3d(color)

                #groups
                vgroup = []
                for g in v.groups:
                    vgroup.append([g.group, g.weight])

                key = normal_key, uvcoord_key, color

                vdict_local = vdict[vidx]
                pf_vidx = vdict_local.get(key)  # Will be None initially

                if pf_vidx is None:  # same as vdict_local.has_key(key)
                    pf_vidx = vdict_local[key] = vert_count
                    ply_verts.append((vidx, normal, uvcoord, color, vgroup))
                    vert_count += 1

                pf.append(pf_vidx)

        # collect faces
        final_faces = []
        for pf in ply_faces:

            if len(pf) is 4:
                final_faces.append(tuple([pf[0], pf[2], pf[1]]))
                final_faces.append(tuple([pf[3], pf[2], pf[0]]))
            # else:
            #     final_faces.append(tuple([pf[0], pf[2], pf[1]]))

        # write file
        file = open(filepath, "w", encoding="utf8", newline="\n")
        fw = file.write

        fw("rav\n")

        # write the count of vertices and faces
        fw(str(vert_count) + " " + str(len(final_faces)) + "\n")

        # x y z nx ny nz s t r g b a
        for i, v in enumerate(ply_verts):
            # position
            co = mesh_verts[v[0]].co
            co = tuple([co[0], co[2], co[1]])
            fw("%.6f %.6f %.6f" % co)

            # normal
            n = v[1]
            n = tuple([n[0], n[2], n[1]])
            fw(" %.6f %.6f %.6f" % n)

            # uv
            if use_uv_coords:
                fw(" %.6f %.6f" % v[2])
            else:
                fw(" 0 0")

            # col
            if use_colors:
                fw(" %u %u %u" % v[3])
            else:
                fw(" 1 1 1")

            # animation
            fw(" [")
            for group in v[4]:
                fw(" %s %.6f" % tuple(group))

            # done
            fw(" ]\n")


        # faces
        for f in final_faces:
            fw("%d %d %d\n" % f)

        file.close()

        print("writing %r done" % filepath)


# Define a function to create the menu option for exporting.
def menu_func_export(self, context):
    self.layout.operator(RavExport.bl_idname, text="RavenEngine Mesh (.rav)")
    self.layout.operator(RaniExport.bl_idname, text="RavenEngine Animation (.rani)")

# Define the Blender required registration functions.
def register():
    """
    Handles the registration of the Blender Addon.
    """
    bpy.utils.register_class(RavExport);
    bpy.utils.register_class(RaniExport);
    bpy.types.INFO_MT_file_export.append(menu_func_export);

def unregister():
    """
    Handles the unregistering of this Blender Addon.
    """
    bpy.utils.unregister_class(RavExport);
    bpy.utils.unregister_class(RaniExport);
    bpy.types.INFO_MT_file_export.remove(menu_func_export);


# Handle running the script from Blender's text editor.
if (__name__ == "__main__"):
    print("Registering.");
    register();