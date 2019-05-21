import array
import os
import time
import re
import bpy
import bmesh
import mathutils
import math
from random import *
from bpy_extras.io_utils import unpack_list
from progress_report import ProgressReport, ProgressReportSubstep

def create_cylinder(axis_1, axis_2, radius):
    x1,y1,z1 = axis_1
    x2,y2,z2 = axis_2
    r = radius
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    dist = math.sqrt(dx**2 + dy**2 + dz**2)

    bpy.ops.mesh.primitive_cylinder_add(
      radius = r, 
      depth = dist,
      location = (dx/2 + x1, dy/2 + y1, dz/2 + z1)
    )

    bpy.context.object.rotation_euler[1] = math.acos(dz/dist) # theta
    bpy.context.object.rotation_euler[2] = math.atan2(dy, dx) # phi

def create_circle(circum_1,circum_2,center,radius):
    x1,y1,z1 = circum_1
    x2,y2,z2 = center
    x3,y3,z3 = circum_2
    r = radius

    dx1 = x1 - x2
    dy1 = y1 - y2
    dz1 = z1 - z2
    dx2 = x3 - x2
    dy2 = y3 - y2
    dz2 = z3 - z2

    normal = mathutils.Vector.cross(mathutils.Vector((dx1,dy1,dz1)), mathutils.Vector((dx2,dy2,dz2)))

    bpy.ops.mesh.primitive_circle_add(
        radius = r, 
        location = center
    )

    # From  parametric equation of a circle: 
    # P(t) = r.cos(t).u + r.sin(t).n x u + C, where u = [-sin(phi),cos(phi),0].

    theta = -math.atan( dy1 / dz1 )
    phi = math.acos( dz1 / r )
    # angle_z = math.atan( - math.cos( angle_x ) * math.sin( angle_y ) / math.sin( angle_x) ) - math.atan( dx / dy )

    bpy.context.object.rotation_euler[1] = theta #TODO: fix rotation
    bpy.context.object.rotation_euler[2] = phi

def create_mesh(global_matrix,
                verts_loc,
                lines,
                face_lines,
                face_points,
                cylinders,
                circles,
                TEMPLATE_FLAG,
                dataname
                ):

    scene = bpy.context.scene

    if TEMPLATE_FLAG in ["3D_F_PTS","3D_F_LNS"]:
        mesh_data = bpy.data.meshes.new(dataname)
        if face_points:
            mesh_data.from_pydata(verts_loc, [], face_points)
        else:
            bm = bmesh.new()
            # Import only lines
            for key in lines:
                if hasattr(bm.verts, "ensure_lookup_table"):
                    bm.verts.ensure_lookup_table()
                    v1 = bm.verts.new(verts_loc[key[0]])
                    v2 = bm.verts.new(verts_loc[key[1]])
                    bm.edges.new((v1, v2))
            bm.to_mesh(mesh_data)
            bm.free()

        mesh_data.update()
        obj = bpy.data.objects.new(dataname, mesh_data)
        scene.objects.link(obj)
        scene.objects.active = obj
        obj.select = True
        obj.matrix_world = global_matrix

    elif TEMPLATE_FLAG == "3D_CYL":
        create_cylinder( *cylinders)

    elif TEMPLATE_FLAG == "3D_CIR":
        create_circle( *circles)

    # new_objects.append(obj)

def load(operator, context, filepath,
         global_clamp_size=0.0,
         relpath=None,
         global_matrix=None,
         ):

    TEMPLATE_FLAG = ""

    def regex_search(text,line):
        return bool(re.search(text,line,re.IGNORECASE))

    nFacelines = 0

    seed = ["b","l","e","n","d","r","v","t","i","s","p","a","z","y"]
    verts_loc = []
    lines = []
    face_points = []
    face_lines = []
    cylinders = []
    circles = []

    t_defined = ["3D_PTS", 
                "3D_LNS",
                "3D_F_LNS",
                "3D_F_PTS",
                "3D_CYL",
                "3D_CIR"]

    with ProgressReport(context.window_manager) as progress:
        progress.enter_substeps(1, "Importing CAO %r..." % filepath)

        if global_matrix is None:
            global_matrix = mathutils.Matrix()

        time_main = time.time()

        # deselect all
        if bpy.ops.object.select_all.poll():
            # bpy.ops.object.mode_set(mode='OBJECT') # TODO: check if object is mesh
            bpy.ops.object.select_all(action='DESELECT')

        scene = context.scene
        new_objects = []  # put new objects here
        index = 0

        progress.enter_substeps(3, "Parsing CAO file...")
        with open(filepath, 'rb') as f:
            for line in f:
                line_split = line.split()

                if not line_split:
                    continue

                line_void = line.replace(b'\t', b'').replace(b' ', b'')

                if not line_void.split(b'#')[0]:
                    continue

                data = line.split(b'#')[0].split()
                data_size = len(data)

                if data_size == 1:
                    if data[0].isdigit():
                        TEMPLATE_FLAG = t_defined[index]
                        index += 1

                if TEMPLATE_FLAG == "3D_PTS":
                    if len(data) == 3:
                        verts_loc.append(list(map(float,[x for x in data])))

                elif TEMPLATE_FLAG == "3D_LNS":
                    if len(data) >= 2:
                        lines.append(list(map(int,[x for x in data[:2]])))

                elif TEMPLATE_FLAG == "3D_F_LNS":
                    if len(data) == 1:
                        nFacelines =int(data[0])
                        if nFacelines == 0 and len(lines) > 0:
                            # import only lines
                            shuffle(seed)
                            create_mesh(global_matrix,verts_loc,lines,[],[],[],[],TEMPLATE_FLAG,"3D Lines" + "_" + "".join(seed))                                                

                    elif len(data) >= 4:
                        face_lines.append(list(map(int,[data[i] for i in range(1,int(data[0])+1)])))
                        shuffle(seed)
                        verts = [verts_loc[i] for i in [lines[i][0] for i in face_lines[-1]]]
                        create_mesh(global_matrix,verts,[],[],[list(range(len(verts)))],[],[],TEMPLATE_FLAG,"3D Lines" + "_" + "".join(seed))                    

                elif TEMPLATE_FLAG == "3D_F_PTS":
                    if len(data) >= 4:
                        face_points.append(list(map(int,[data[i] for i in range(1,int(data[0])+1)])))
                        shuffle(seed)
                        verts = [verts_loc[i] for i in face_points[-1]]
                        create_mesh(global_matrix,verts,[],[],[list(range(len(verts)))],[],[],TEMPLATE_FLAG,"3D Faces" + "_" + "".join(seed))

                elif TEMPLATE_FLAG == "3D_CYL":
                    if len(data) >= 3:
                        cylinders = [verts_loc[int(data[0])],verts_loc[int(data[1])],float(data[2])]
                        shuffle(seed)
                        create_mesh(global_matrix,verts_loc,[],[],[],cylinders,[],TEMPLATE_FLAG,"3D Cylinder" + "_" + "".join(seed))                        

                elif TEMPLATE_FLAG == "3D_CIR":
                    if len(data) >= 4:
                        circles = [verts_loc[int(data[2])],verts_loc[int(data[3])],verts_loc[int(data[1])],float(data[0])]
                        shuffle(seed)
                        create_mesh(global_matrix,verts_loc,[],[],[],[],circles,TEMPLATE_FLAG,"3D Cylinder" + "_" + "".join(seed))                        

        progress.step("Done")

        scene.update()

        progress.leave_substeps("Done.")
        progress.leave_substeps("Finished importing: %r" % filepath)

    return {'FINISHED'}
