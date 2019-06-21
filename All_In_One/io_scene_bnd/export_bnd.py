# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####

import os, time, struct, math, sys
import os.path as path

import bpy, bmesh, mathutils

# globals
global apply_modifiers_G
apply_modifiers_G = True

######################################################
# EXPORT HELPERS
######################################################
def bounds(obj):

    local_coords = obj.bound_box[:]
    om = obj.matrix_world
    coords = [p[:] for p in local_coords]

    rotated = zip(*coords[::-1])

    push_axis = []
    for (axis, _list) in zip('xyz', rotated):
        info = lambda: None
        info.max = max(_list)
        info.min = min(_list)
        info.distance = info.max - info.min
        push_axis.append(info)

    import collections

    originals = dict(zip(['x', 'y', 'z'], push_axis))

    o_details = collections.namedtuple('object_details', 'x y z')
    return o_details(**originals)

def get_undupe_name(name):
    nidx = name.find('.')
    return name[:nidx] if nidx != -1 else name


def find_object_ci(name):
    for obj in bpy.data.objects:
        if obj.name.lower() == name.lower() and obj.type == 'MESH':
            return obj
    return None

def write_char_array(file, w_str, length):
    file.write(bytes(w_str, 'utf-8'))
    file.write(bytes('\x00' * (length - len(w_str )), 'utf-8'))

def lerp(fr,to,t):
   return fr + (to - fr) * t

def vec_distance(v1, v2):
  nx = v2[0] - v1[0]
  ny = v2[1] - v1[1]
  return math.sqrt(nx * nx + ny * ny )
   
def poly_overlap_test(pl1, otl, ttc):
  #calculate center of otl
  otl_centerx = 0
  otl_centery = 0
  for p in otl:
    otl_centerx += p[0]
    otl_centery += p[1]
  otl_centerx /= len(otl)
  otl_centery /= len(otl)
  
  pl1.append(pl1[len(pl1) - 1])  
  for p1 in range(len(pl1) - 1):
    edge = (pl1[p1], pl1[p1+1])
    for et in range(11):
      et_prcnt = et/10
      lx = lerp(edge[0][0], edge[1][0], et_prcnt)
      ly = lerp(edge[0][1], edge[1][1], et_prcnt)
      if vec_distance((lx,ly), (otl_centerx, otl_centery)) < ttc:
        return True
  return False
  
def point_in_box(point, box):
  if box[0][0] <= point[0] and point[0] <= box[2][0] and box[0][1] <= point[1] and point[1] <= box[2][1]:
    return True
  return False
  
  
def point_in_polygon(p, vertices):
    # If the point is a vertex, it's in the polygon
    if tuple(p) in (tuple(i) for i in vertices):
        return True

    xs = [i[0] for i in vertices]
    ys = [i[1] for i in vertices]
    # if the point is outside of the polygon's bounding
    # box, it's not in the polygon
    if (p[0] > max(*xs) or p[0] < min(*xs)) or (p[1] > max(*ys) or p[1] < min(*ys)):
        return False

    p1 = vertices[-1] # Start with first and last vertices
    count = 0
    for p2 in vertices:
        # Check if point is between lines y=p1[1] and y=p2[1]
        if p[1] <= max(p1[1], p2[1]) and p[1] >= min(p1[1], p2[1]):
            # Get the intersection with the line that passes
            # through p1 and p2
            xdiv1 = float(p2[0]-p1[0])*float(p[1]-p1[1])
            xdiv2 = float(p2[1]-p1[1])+p1[0]
            
            if xdiv2 > 0:
              x_inters = xdiv1/xdiv2

              # If p[0] is less than or equal to x_inters,
              # we have an intersection
              if p[0] <= x_inters:
                  count += 1
        p1 = p2

    # If the intersections are even, the point is outside of
    # the polygon.
    return count % 2 != 0
    
 
def poly_debug(poly1, color=(0,0,0)):
  # sample data
  coords = []
  for c in poly1:
    coords.append((c[0], c[1], 0))

  # create the Curve Datablock
  curveData = bpy.data.curves.new('poly_debug', type='CURVE')
  curveData.dimensions = '3D'

  # map coords to spline
  polyline = curveData.splines.new('POLY')
  polyline.points.add(len(coords) - 1)
  for i in range(len(coords)):
      x,y,z = coords[i]
      polyline.points[i].co = (x, y, z, 1)
  
  polyline.use_cyclic_u = True 
  
  # create Object
  curveOB = bpy.data.objects.new('poly_debug', curveData)
  curveData.bevel_depth = 0.05
  
  # apply material
  mat = bpy.data.materials.new(name="polydebug")
  mat.diffuse_color = color
  mat.use_shadeless = True
  mat.use_object_color = True
  curveOB.data.materials.append(mat)
  
  # attach to scene and validate context
  scn = bpy.context.scene
  scn.objects.link(curveOB)
  return curveOB

######################################################
# EXPORT MAIN FILES
######################################################
def export_terrain_bound(file, ob):
    # create temp mesh
    temp_mesh = ob.to_mesh(bpy.context.scene, apply_modifiers_G, 'PREVIEW')
    
    # get bmesh
    bm = bmesh.new()
    bm.from_mesh(temp_mesh)
    bm.verts.ensure_lookup_table()
    bm.faces.index_update()
    
    # header
    file.write(struct.pack('f', 1.1))
    file.write(struct.pack('LLB', len(bm.faces), 0, 0))
    
    # boundbox
    bnds = bounds(ob)
    bnd_width = math.fabs(bnds.x.max - bnds.x.min)
    bnd_height = math.fabs(bnds.z.max - bnds.z.min)
    bnd_depth = math.fabs(bnds.y.max - bnds.y.min)
    
    file.write(struct.pack('fff', bnd_width, bnd_height, bnd_depth))
    
    # section data  
    width_sections = max(1, math.ceil(bnd_width / 10))
    depth_sections = max(1, math.ceil(bnd_depth / 10))
    height_sections = 1
    
    total_sections = width_sections * depth_sections
    individual_section_width = (1/(width_sections/bnd_width))/2
    individual_section_depth = (1/(depth_sections/bnd_depth))/2
    
    file.write(struct.pack('LLLL', width_sections, height_sections, depth_sections, total_sections))
    
    #calculate intersecting polygons + poly indices
    poly_indices = 0
    section_groups = []
    
    for d in range(depth_sections):
      for w in range(width_sections):
        section_group = []
        section_center = [lerp(bnds.x.min, bnds.x.max, (w)/width_sections) +  (individual_section_width /2), lerp(bnds.y.max, bnds.y.min, (d)/depth_sections) - (individual_section_depth/2)]
        section_center[0] += individual_section_width/2
        section_center[1] -= individual_section_depth/2
        section_tl = (section_center[0] - (individual_section_width * 1.5), section_center[1] - (individual_section_depth * 1.5))
        section_br = (section_center[0] + (individual_section_width * 1.5), section_center[1] + (individual_section_depth * 1.5))
        section_poly = [(section_tl[0], section_tl[1]), (section_br[0], section_tl[1]), (section_br[0], section_br[1]), (section_tl[0], section_br[1])]
          
        for f in bm.faces:
          # construct face poly 2d
          face_poly = []
          for l in f.loops:
            face_poly.append((bm.verts[l.vert.index].co[0],bm.verts[l.vert.index].co[1]))
          
          # test with edge intersection
          ovr_rslt = poly_overlap_test(face_poly, section_poly, max(individual_section_width, individual_section_depth) * (f.calc_area() / 40))
          
          # vertices within poly test
          if not ovr_rslt:
            for v in face_poly:
              if point_in_box(v, section_poly):
                ovr_rslt = True
          
          # polygon contains sector?
          if not ovr_rslt:
            for p in section_poly:
              if not ovr_rslt:
                ovr_rslt = point_in_polygon(p, face_poly)
          
          # contains center?
          if not ovr_rslt:
            p_ctr = f.calc_center_median()
            p_ctr_2d = (p_ctr[0], p_ctr[1])
            if point_in_polygon(p_ctr_2d, section_poly):
              ovr_result = True
            
          if ovr_rslt == True:
            section_group.append(f.index)
            poly_indices += 1
        
        section_groups.append(section_group)
        
    # continue writing more binary information about boxes and stuff
    file.write(struct.pack('L', poly_indices))
    
    if bnd_width == 0:
      file.write(struct.pack('f', float('Inf')))
    else:
      file.write(struct.pack('f', width_sections / bnd_width))
      
    file.write(struct.pack('f', 1))
      
    if bnd_depth == 0:
      file.write(struct.pack('f', float('Inf')))
    else:
      file.write(struct.pack('f', depth_sections / bnd_depth))
      
    file.write(struct.pack('ffffff',  bnds.x.min, bnds.z.min, bnds.y.min, bnds.x.max, bnds.z.max ,bnds.y.max))
    
    # write index info
    tot_ind = 0
    for i in range(total_sections):
      file.write(struct.pack('H', tot_ind))
      tot_ind += len(section_groups[i])

    for i in range(total_sections):
      file.write(struct.pack('H', len(section_groups[i])))
      
    for i in range(total_sections):
      for j in range(len(section_groups[i])):
          file.write(struct.pack('H', section_groups[i][j]))
      
        
    # finish off
    bpy.data.meshes.remove(temp_mesh)
    bm.free()
    file.close()
    return


def export_binary_bound(file, ob):
    # create temp mesh
    temp_mesh = ob.to_mesh(bpy.context.scene, apply_modifiers_G, 'PREVIEW')
    
    # get bmesh
    bm = bmesh.new()
    bm.from_mesh(temp_mesh)

    # header
    file.write(struct.pack('B', 1))
    file.write(struct.pack('LLL', len(bm.verts), len(ob.material_slots), len(bm.faces)))
    
    # vertices
    for v in bm.verts:
        file.write(struct.pack('fff', v.co[0], v.co[2], v.co[1] * -1))


    # materials
    for ms in ob.material_slots:
        mat = ms.material
        write_char_array(file, get_undupe_name(mat.name), 32)
        file.write(struct.pack('ff', 0.1, 0.5))
        write_char_array(file, 'none', 32)
        write_char_array(file, 'none', 32)
        

    # faces
    bm.verts.index_update()
    for fcs in bm.faces:
        if len(fcs.loops) == 3:
            file.write(struct.pack('HHHHH', fcs.loops[0].vert.index, fcs.loops[1].vert.index, fcs.loops[2].vert.index, 0, fcs.material_index))
        elif len(fcs.loops) == 4:
            file.write(struct.pack('HHHHH', fcs.loops[0].vert.index, fcs.loops[1].vert.index, fcs.loops[2].vert.index, fcs.loops[3].vert.index, fcs.material_index))
    
    # finish off
    bpy.data.meshes.remove(temp_mesh)
    bm.free()
    file.close()
    return


def export_bound(file, ob):
    # create temp mesh
    temp_mesh = ob.to_mesh(bpy.context.scene, apply_modifiers_G, 'PREVIEW')
    
    # get bmesh
    bm = bmesh.new()
    bm.from_mesh(temp_mesh)

    # header
    bnd_file = "version: 1.01\nverts: " + str(len(bm.verts)) + "\nmaterials: " + str(len(ob.material_slots)) + "\nedges: 0\npolys: " + str(len(bm.faces)) + "\n\n"

    # vertices
    for v in bm.verts:
        bnd_file += "v " + "{0:.6f}".format(v.co[0]) + " " + "{0:.6f}".format(v.co[2]) + " " + "{0:.6f}".format(v.co[1] * -1) + "\n"

    bnd_file += "\n"

    # materials
    for ms in ob.material_slots:
        mat = ms.material
        bnd_file += "mtl " + get_undupe_name(mat.name) + " {\n\telasticity: 0.100000\n\tfriction: 0.500000\n\teffect: none\n\tsound: none\n}\n"
        
    bnd_file += "\n"

    # faces
    bm.verts.index_update()
    for fcs in bm.faces:
        if len(fcs.loops) == 3:
            bnd_file += "tri " + str(fcs.loops[0].vert.index) + "  " + str(fcs.loops[1].vert.index) + "  " + str(fcs.loops[2].vert.index) + "  " + str(fcs.material_index) + "\n"
        elif len(fcs.loops) == 4:
            bnd_file += "quad " + str(fcs.loops[0].vert.index) + "  " + str(fcs.loops[1].vert.index) + "  " + str(fcs.loops[2].vert.index) + "  " + str(fcs.loops[3].vert.index) + "  " + str(fcs.material_index) + "\n"
            
    # write BOUND
    file.write(bnd_file)

    # finish off
    bpy.data.meshes.remove(temp_mesh)
    bm.free()
    file.close()
    return


######################################################
# EXPORT
######################################################
def save_bnd(filepath,
             export_binary,
             export_terrain,
             context):

    print("exporting BOUND: %r..." % (filepath))

    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    time1 = time.clock()
    

    # find bound object
    bound_obj = find_object_ci("BOUND")
    if bound_obj is None:
      raise Exception('No BOUND object in scene.')
    
    # write bnd
    file = open(filepath, 'w')
    export_bound(file, bound_obj)
    
    if export_binary:
      # write BBND
      binfile = open(filepath[:-3] + "bbnd", 'wb')
      export_binary_bound(binfile, bound_obj)
    
    if export_terrain:
      # write TER
      terfile = open(filepath[:-3] + "ter", 'wb')
      export_terrain_bound(terfile, bound_obj)
      
    # bound export complete
    print(" done in %.4f sec." % (time.clock() - time1))


def save(operator,
         context,
         filepath="",
         export_binary=False,
         export_terrain=False,
         apply_modifiers=False
         ):
    
    # set object modes
    for ob in context.scene.objects:
      if ob.type == 'MESH' and ob.name.lower() == "bound" and not ob.hide:
        context.scene.objects.active = ob
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
      if ob.name.lower() == "bound" and (ob.hide or ob.type != 'MESH'):
        raise Exception("BOUND has invalid object type, or is not visible in the scene")
    
    # set globals
    global apply_modifiers_G
    apply_modifiers_G = apply_modifiers
    
    # save BND
    save_bnd(filepath,
             export_binary,
             export_terrain,
             context,
             )

    return {'FINISHED'}
