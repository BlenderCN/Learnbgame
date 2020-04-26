# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# Script copyright (C) Blender Foundation 2012

import bpy
import bmesh

from mathutils import Vector

def _points_from_object(obj, source):

    _source_all = {
        'VERT_OWN', 'EDGE_OWN', 'FACE_OWN',
        'VERT_CHILD', 'EDGE_CHILD', 'FACE_CHILD',
        'PARTICLE_OWN', 'PARTICLE_CHILD',
        'PENCIL',
        }

    print(source - _source_all)
    print(source)
  #  assert(len(source | _source_all) == len(_source_all))
#    assert(len(source))

    points = []

    def edge_center(mesh, edge):
        v1, v2 = edge.vertices
        return (mesh.vertices[v1].co + mesh.vertices[v2].co) / 2.0

    def poly_center(mesh, poly):
        from mathutils import Vector
        co = Vector()
        tot = 0
        for i in poly.loop_indices:
            co += mesh.vertices[mesh.loops[i].vertex_index].co
            tot += 1
        return co / tot

    def points_from_verts(obj):
        """Takes points from _any_ object with geometry"""
        if obj.type == 'MESH':
            mesh = obj.data
            matrix = obj.matrix_world.copy()
            points.extend([matrix * v.co for v in mesh.vertices])
        else:
            try:
                mesh = ob.to_mesh(scene=bpy.context.scene,
                                  apply_modifiers=True,
                                  settings='PREVIEW')
            except:
                mesh = None

            if mesh is not None:
                matrix = obj.matrix_world.copy()
                points.extend([matrix * v.co for v in mesh.vertices])
                bpy.data.meshes.remove(mesh)

    def points_from_particles(obj):
        points.extend([p.location.copy()
                       for psys in obj.particle_systems
                       for p in psys.particles])

    def points_from_edges(obj):
        if obj.type == 'MESH':
            mesh = obj.data
            matrix = obj.matrix_world.copy()
            points.extend([matrix * edge_center(mesh, e) for e in mesh.edges])

    def points_from_faces(obj):
        if obj.type == 'MESH':
            mesh = obj.data
            matrix = obj.matrix_world.copy()
            points.extend([matrix * poly_center(mesh, p) for p in mesh.polygons])

    # geom own
    if 'VERT_OWN' in source:
        points_from_verts(obj)
    if 'EDGE_OWN' in source:
        points_from_edges(obj)
    if 'FACE_OWN' in source:
        points_from_faces(obj)

    # geom children
    if 'VERT_CHILD' in source:
        for obj_child in obj.children:
            points_from_verts(obj_child)
    if 'EDGE_CHILD' in source:
        for obj_child in obj.children:
            points_from_edges(obj_child)
    if 'FACE_CHILD' in source:
        for obj_child in obj.children:
            points_from_faces(obj_child)

    # geom particles
    if 'PARTICLE_OWN' in source:
        points_from_particles(obj)

    if 'PARTICLE_CHILD' in source:
        for obj_child in obj.children:
            points_from_particles(obj_child)

    # grease pencil
    def get_points(stroke):
        return [point.co.copy() for point in stroke.points]

    def get_splines(gp):
        if gp.layers.active:
            frame = gp.layers.active.active_frame
            return [get_points(stroke) for stroke in frame.strokes]
        else:
            return []

    if 'PENCIL' in source:
        gp = obj.grease_pencil
        if gp:
            points.extend([p for spline in get_splines(gp)
                             for p in spline])

    print("Found %d points" % len(points))

    return points


def cell_fracture_objects(scene, obj, material_index):
    
    from . import fracture_cell_calc
    
    ctx = obj.destruction.cell_fracture
    source = ctx.source
    source_limit = ctx.source_limit
    source_noise = ctx.source_noise
    clean = True
    
    # operator options
    use_smooth_faces = ctx.use_smooth_faces
    use_data_match = ctx.use_data_match
    use_island_split = True
    margin = ctx.margin
    use_debug_points = ctx.use_debug_points
    cell_scale = ctx.cell_scale
    
    re_unwrap = obj.destruction.re_unwrap
    smart_angle = obj.destruction.smart_angle

    # -------------------------------------------------------------------------
    # GET POINTS

    points = _points_from_object(obj, source)

    if not points:
        # print using fallback
        points = _points_from_object(obj, {'VERT_OWN'})

    if not points:
        print("no points found")
        return []

    # apply optional clamp
    if source_limit != 0 and source_limit < len(points):
        import random
        random.shuffle(points)
        points[source_limit:] = []


    # saddly we cant be sure there are no doubles
    from mathutils import Vector
    to_tuple = Vector.to_tuple
    points = list({to_tuple(p, 4): p for p in points}.values())
    del to_tuple
    del Vector

    # end remove doubles
    # ------------------

    if source_noise > 0.0:
        from random import random
        # boundbox approx of overall scale
        from mathutils import Vector
        matrix = obj.matrix_world.copy()
        bb_world = [matrix * Vector(v) for v in obj.bound_box]
        scalar = source_noise * ((bb_world[0] - bb_world[6]).length / 2.0)

        from mathutils.noise import random_unit_vector
        
        points[:] = [p + (random_unit_vector() * (scalar * random())) for p in points]


    if use_debug_points:
        bm = bmesh.new()
        for p in points:
            bm.verts.new(p)
        mesh_tmp = bpy.data.meshes.new(name="DebugPoints")
        bm.to_mesh(mesh_tmp)
        bm.free()
        obj_tmp = bpy.data.objects.new(name=mesh_tmp.name, object_data=mesh_tmp)
        scene.objects.link(obj_tmp)
        del obj_tmp, mesh_tmp

    mesh = obj.data
    matrix = obj.matrix_world.copy()
    verts = [matrix * v.co for v in mesh.vertices]

    cells = fracture_cell_calc.points_as_bmesh_cells(verts,
                                                     points,
                                                     cell_scale,
                                                     margin_cell=margin)

    # some hacks here :S
    cell_name = obj.name #+ "_cell"
    
    objects = []
    
    for center_point, cell_points in cells:

        # ---------------------------------------------------------------------
        # BMESH

        # create the convex hulls
        bm = bmesh.new()
        
        # WORKAROUND FOR CONVEX HULL BUG/LIMIT
        # XXX small noise
        import random
        def R(): return (random.random() - 0.5) * 0.001
        # XXX small noise

        for i, co in enumerate(cell_points):
            
            # XXX small noise
            co.x += R()
            co.y += R()
            co.z += R()
            # XXX small noise
            
            bm_vert = bm.verts.new(co)

        import mathutils
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.005)
        try:
            bmesh.ops.convex_hull(bm, input=bm.verts)
        except RuntimeError:
            import traceback
            traceback.print_exc()

        if clean:
            bm.normal_update()
            try:
                bmesh.ops.dissolve_limit(bm, verts=bm.verts, angle_limit=0.001)
            except RuntimeError:
                import traceback
                traceback.print_exc()

        if use_smooth_faces:
            for bm_face in bm.faces:
                bm_face.smooth = True

        if material_index != 0:
            for bm_face in bm.faces:
                bm_face.material_index = material_index


        # ---------------------------------------------------------------------
        # MESH

        mesh_dst = bpy.data.meshes.new(name=cell_name)

        bm.to_mesh(mesh_dst)
        bm.free()
        del bm

        if use_data_match:
            # match materials and data layers so boolean displays them
            # currently only materials + data layers, could do others...
            mesh_src = obj.data
            for mat in mesh_src.materials:
                mesh_dst.materials.append(mat)
            for lay_attr in ("vertex_colors", "uv_textures"):
                lay_src = getattr(mesh_src, lay_attr)
                lay_dst = getattr(mesh_dst, lay_attr)
                for key in lay_src.keys():
                    lay_dst.new(name=key)

        # ---------------------------------------------------------------------
        # OBJECT

        obj_cell = bpy.data.objects.new(name=cell_name, object_data=mesh_dst)
        scene.objects.link(obj_cell)
        # scene.objects.active = obj_cell
        obj_cell.location = center_point
        
        #needed for parenting system
        obj_cell.parent = bpy.context.scene.objects[cell_name].parent

        objects.append(obj_cell)
        
        if re_unwrap:
           scene.objects.active = obj_cell
           bpy.ops.object.mode_set(mode = 'EDIT')
           bpy.ops.mesh.select_all(action = 'SELECT')
           bpy.ops.mesh.dissolve_limited(angle_limit = 0.001)
           bpy.ops.mesh.mark_seam()
           bpy.ops.uv.smart_project(angle_limit = smart_angle)
           bpy.ops.object.mode_set(mode = 'OBJECT')
        
        if obj.destruction.use_debug_redraw:
            scene.update()
            obj.destruction._redraw_yasiamevil()

    scene.update()


    # move this elsewhere...
   # for obj_cell in objects:
#        game = obj_cell.game
 #       game.physics_type = 'RIGID_BODY'
  #      game.use_collision_bounds = True
   #     game.collision_bounds_type = 'CONVEX_HULL'

    return objects


def cell_fracture_boolean(scene, obj, objects, use_interior_hide, level):
    
    ctx = obj.destruction.cell_fracture
    use_debug_bool = ctx.use_debug_bool
    clean = True
    use_island_split = ctx.use_island_split
    use_interior_vgroup = ctx.use_interior_vgroup
    use_debug_redraw = obj.destruction.use_debug_redraw
    remove_doubles = True
    
    objects_boolean = []

    if use_interior_hide and level == 0:
        # only set for level 0
        obj.data.polygons.foreach_set("hide", [False] * len(obj.data.polygons))
    
    #correct position according to parents
    loc = obj.location.copy()
    object = objects[0].copy()
    while object.parent != None:
        loc += object.parent.location
        object = object.parent
    
    obj.location += loc
    
    oldact = bpy.context.active_object.name
    
    bpy.context.scene.objects.active = obj
    bpy.ops.object.transform_apply(location=True)
    bpy.context.scene.objects.active = bpy.data.objects[oldact]
    
    #print("LOKATION: ", loc, obj.location, objects[0].location)

    for obj_cell in objects:
              
        mod = obj_cell.modifiers.new(name="Boolean", type='BOOLEAN')
        mod.object = obj
        mod.operation = 'INTERSECT'

        if not use_debug_bool:
            
            obj_cell.location -= loc
            
            if use_interior_hide:
                obj_cell.data.polygons.foreach_set("hide", [True] * len(obj_cell.data.polygons))
            
            mesh_new = obj_cell.to_mesh(scene,
                                        apply_modifiers=True,
                                        settings='PREVIEW')
            
            
            mesh_old = obj_cell.data
            obj_cell.data = mesh_new
            obj_cell.modifiers.remove(mod)

            # remove if not valid
            if not mesh_old.users:
                bpy.data.meshes.remove(mesh_old)
            if not mesh_new.vertices:
                scene.objects.unlink(obj_cell)
                if not obj_cell.users:
                    bpy.data.objects.remove(obj_cell)
                    obj_cell = None
                    if not mesh_new.users:
                        bpy.data.meshes.remove(mesh_new)
                        mesh_new = None

            # avoid unneeded bmesh re-conversion
            if mesh_new is not None:
                bm = None
                
                if clean:
                    if bm is None:  # ok this will always be true for now...
                        bm = bmesh.new()
                        bm.from_mesh(mesh_new)
                    bm.normal_update()
                    try:
                        bmesh.ops.dissolve_limit(bm, verts=bm.verts, edges=bm.edges, angle_limit=0.001)
                    except RuntimeError:
                        import traceback
                        traceback.print_exc()
                
                if remove_doubles:
                    if bm is None:
                        bm = bmesh.new()
                        bm.from_mesh(mesh_new)
                    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist = 0.005)
                        
                if bm is not None:
                    bm.to_mesh(mesh_new)
                    bm.free()
    
            del mesh_new
            del mesh_old

        if obj_cell is not None:
            objects_boolean.append(obj_cell)

            if obj_cell.destruction.use_debug_redraw:
                scene.update()
                obj_cell.destruction._redraw_yasiamevil()             

    if (not use_debug_bool) and use_island_split:
        # this is ugly and Im not proud of this - campbell
        base = None
        for base in scene.object_bases:
            base.select = False
        for obj_cell in objects_boolean:
            obj_cell.select = True

        bpy.ops.mesh.separate(type='LOOSE')

        objects_boolean[:] = [obj_cell for obj_cell in scene.objects if obj_cell.select]

    scene.update()

    return objects_boolean


def cell_fracture_interior_handle(objects,
                                  use_interior_vgroup=False,
                                  use_sharp_edges=False,
                                  use_sharp_edges_apply=False,
                                  ):
    """Run after doing _all_ booleans"""

    assert(use_interior_vgroup or use_sharp_edges or use_sharp_edges_apply)

    for obj_cell in objects:
        mesh = obj_cell.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
               
        if use_interior_vgroup:
            for bm_vert in bm.verts:
                bm_vert.tag = True
            for bm_face in bm.faces:
                if not bm_face.hide:
                    for bm_vert in bm_face.verts:
                        bm_vert.tag = False

            # now add all vgroups
            defvert_lay = bm.verts.layers.deform.verify()
            for bm_vert in bm.verts:
                if bm_vert.tag:
                    bm_vert[defvert_lay][0] = 1.0

            # add a vgroup
            obj_cell.vertex_groups.new(name="Interior")

        if use_sharp_edges:
            mesh.show_edge_sharp = True
            for bm_edge in bm.edges:
                if len({bm_face.hide for bm_face in bm_edge.link_faces}) == 2:
                    bm_edge.smooth = False
    
        
            if use_sharp_edges_apply:
                edges = [edge for edge in bm.edges if edge.smooth is False]
                if edges:
                    bm.normal_update()
                    bmesh.ops.split_edges(bm, edges=edges)

        for bm_face in bm.faces:
            bm_face.hide = False
    

        bm.to_mesh(mesh)
        bm.free()