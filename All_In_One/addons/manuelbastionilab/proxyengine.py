#ManuelbastioniLAB - Copyright (C) 2015-2017 Manuel Bastioni
#Official site: www.manuelbastioni.com
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import algorithms
import os, json, time
import mathutils
import logging

lab_logger = logging.getLogger('manuelbastionilab_logger')


class ProxyEngine:

    def __init__(self):
        self.has_data = False
        self.data_path = algorithms.get_data_path()
        self.templates_library = algorithms.get_blendlibrary_path()
        self.corrective_modifier_name = "mbastlab_corrective_modifier"
        self.mask_modifier_name = "mbastlab_mask_modifier"

    def add_corrective_smooth_modifier(self, obj):
        parameters = {"show_viewport":True,"show_in_editmode":True,"show_on_cage":True}
        c_smooth = algorithms.new_modifier(obj, self.corrective_modifier_name, 'CORRECTIVE_SMOOTH', parameters)
        algorithms.move_up_modifier(obj, c_smooth)
        self.apply_corrective_smooth(obj)
        algorithms.remove_modifier(obj, self.corrective_modifier_name)

    def apply_corrective_smooth(self,obj):
        proxy_shape = algorithms.get_shapekey(obj,"mbastlab_proxyfit")
        if proxy_shape:
            algorithms.disable_object_modifiers(obj, ['SUBSURF','MASK'])
            raw_obj_mesh = algorithms.raw_mesh_from_object(obj)
            if len(proxy_shape.data) == len(raw_obj_mesh.vertices):
                for i,sk_vert in enumerate(proxy_shape.data):
                    sk_vert.co = raw_obj_mesh.vertices[i].co
            algorithms.remove_mesh(raw_obj_mesh)


    def add_mask_modifier(self, obj, vertgroup_name):
        parameters = {"vertex_group":vertgroup_name,"invert_vertex_group":True}
        algorithms.new_modifier(obj, self.mask_modifier_name, 'MASK', parameters)

    def calibrate_proxy_object(self,proxy):
        old_version_sk = algorithms.get_shapekey(proxy,"Fitted")
        if old_version_sk:
            old_version_sk.value = 0
        if not algorithms.get_shapekey(proxy,"mbastlab_proxyfit"):
            algorithms.apply_object_transformation(proxy)
        if not algorithms.get_shapekey_reference(proxy):
            algorithms.new_shapekey(proxy, "Basis")
            
    def remove_fitting(self):
        status, proxy, body = self.get_proxy_fitting_ingredients()
        if status == "OK":
            algorithms.remove_shapekeys_all(proxy)


    def get_proxy_fitting_ingredients(self):
        objs_selected = bpy.context.selected_objects
        reference_obj = None
        if len(objs_selected) != 2:
            return ["WRONG_SELECTION", None,None]
        for obj in objs_selected:            
            if algorithms.identify_template(obj) != None:
                reference_obj = obj
        if not reference_obj:
            return ["NO_REFERENCE", None, None]
        for obj in objs_selected:
            if obj != reference_obj:
                proxy_obj = obj
                if proxy_obj.type != 'MESH':
                    return ["NO_MESH_SELECTED", None, None]
                return ["OK", proxy_obj, reference_obj]

    def validate_proxy_fitting(self):
        status, proxy_obj, reference_obj = self.get_proxy_fitting_ingredients()
        return status


    def reset_proxy_shapekey(self,proxy):
        fit_shapekey = algorithms.get_shapekey(proxy, "mbastlab_proxyfit")
        if fit_shapekey:
            algorithms.remove_shapekey(proxy, "mbastlab_proxyfit")


    def fit_near_vertices(self, basis_proxy_mesh,basis_body_mesh,proxy_shapekey,raw_body_mesh, proxy_threshold = 0.025):

        #basis_proxy_mesh = proxy in basis shape, without shapekey applied
        #proxy_shapekey = shapekey to modify as final result
        #basis_body_mesh = body in basis shape, without morphings and armature
        #raw_body_mesh = raw copy of current body shape, with morphing and armature applied

        basis_proxy_vertices = basis_proxy_mesh.vertices #Remember that obj.data = untransformed data
        basis_body_polygons = basis_body_mesh.polygons
        raw_body_polygons = raw_body_mesh.polygons

        if len(basis_body_polygons) == len(raw_body_polygons):
            basis_body_tree = algorithms.kdtree_from_mesh_polygons(basis_body_mesh)

            for i,basis_proxy_vert in enumerate(basis_proxy_vertices):

                nearest_body_polygons_data = basis_body_tree.find_n(basis_proxy_vert.co, 25)
                #basis body vs basis proxy
                for body_polygons_data in nearest_body_polygons_data:
                    body_polygon_index = body_polygons_data[1]
                    body_polygon_dist = body_polygons_data[2] #distance basis_body - basis_proxy
                    body_polygon = basis_body_polygons[body_polygon_index]                    
                    if basis_proxy_vert.normal.dot(body_polygon.normal) > 0:
                        break

                if proxy_threshold > 0:
                    f_factor = 1 - ((body_polygon_dist - proxy_threshold)/proxy_threshold)
                    f_factor = min(f_factor,1)
                    f_factor = max(f_factor,0)
                else:
                    f_factor = 0

                basis_body_verts_coords = algorithms.get_polygon_vertices_coords(basis_body_mesh,body_polygon_index)
                p1 = basis_body_verts_coords[0]
                p2 = basis_body_verts_coords[1]
                p3 = basis_body_verts_coords[2]

                raw_body_verts_coords = algorithms.get_polygon_vertices_coords(raw_body_mesh,body_polygon_index)
                p4 = raw_body_verts_coords[0]
                p5 = raw_body_verts_coords[1]
                p6 = raw_body_verts_coords[2]

                proxy_shapekey_vert = proxy_shapekey.data[i]
                fitted_vert = mathutils.geometry.barycentric_transform(basis_proxy_vert.co,p1,p2,p3,p4,p5,p6)
                proxy_shapekey_vert.co = proxy_shapekey_vert.co + f_factor*(fitted_vert-proxy_shapekey_vert.co)


    def fit_proxy_object(self,proxy_offset=1.0, proxy_threshold = 0.025, create_proxy_mask = True):

        status, proxy, body = self.get_proxy_fitting_ingredients()
        if status == "OK":

            self.calibrate_proxy_object(proxy)
            self.reset_proxy_shapekey(proxy)#Always after calibration!


            proxy.matrix_world = body.matrix_world

            template_name = algorithms.identify_template(body)
            lab_logger.info("Fitting proxy {0}".format(proxy.name))
            selected_objs_names = algorithms.get_objects_selected_names()

            body_modfs_status = algorithms.get_object_modifiers_visibility(body)
            proxy_modfs_status = algorithms.get_object_modifiers_visibility(proxy)

            algorithms.disable_object_modifiers(proxy, ['ARMATURE','SUBSURF','MASK'])
            algorithms.disable_object_modifiers(body, ['SUBSURF','MASK'])

            basis_body_mesh = algorithms.import_mesh_from_lib(self.templates_library, template_name)
            basis_proxy_mesh = proxy.data #This is the basis because shapekeys are not computed here

            proxy_shapekey = algorithms.new_shapekey(proxy,"mbastlab_proxyfit")
            raw_body_mesh = algorithms.raw_mesh_from_object(body)

            self.fit_near_vertices(basis_proxy_mesh,basis_body_mesh,proxy_shapekey,raw_body_mesh,proxy_threshold)
            self.proxy_offset(basis_proxy_mesh,basis_body_mesh,proxy_shapekey,raw_body_mesh,proxy_offset)

            if create_proxy_mask:
                self.calculate_mask_vertgroup(body, proxy_shapekey,raw_body_mesh)
            else:
                self.remove_proxy_mask(body)


            algorithms.remove_mesh(raw_body_mesh)
            algorithms.remove_mesh(basis_body_mesh, True)

            algorithms.set_object_modifiers_visibility(body, body_modfs_status)
            algorithms.set_object_modifiers_visibility(proxy, proxy_modfs_status)
            self.add_corrective_smooth_modifier(proxy)

            for obj_name in selected_objs_names:
                algorithms.select_object_by_name(obj_name)


    def proxy_offset(self, basis_proxy_mesh,basis_body_mesh,proxy_shapekey,raw_body_mesh,offset_factor):

        #basis_proxy_mesh = proxy in basis shape, without shapekey applied
        #proxy_shapekey = shapekey of actual, "real" proxy shape to modify as final result
        #basis_body_mesh = body in basis shape, without morphings and armature
        #raw_body_mesh = raw copy of current body shape, with morphing and armature applied

        basis_proxy_vertices = basis_proxy_mesh.vertices
        basis_body_polygons = basis_body_mesh.polygons
        raw_body_polygons = raw_body_mesh.polygons

        if len(basis_body_polygons) == len(raw_body_polygons):

            raw_body_tree = algorithms.kdtree_from_mesh_polygons(raw_body_mesh)

            for i in range(len(basis_proxy_vertices)):
                proxy_shapekey_vert = proxy_shapekey.data[i]
                nearest_body_polygons_data = raw_body_tree.find_n(proxy_shapekey_vert.co, 10)
                body_normals = []

                #raw body vs proxy shapekey
                for body_polygons_data in nearest_body_polygons_data:
                    body_polygon_index = body_polygons_data[1]
                    body_polygon_dist = body_polygons_data[2] #distance body-proxy
                    body_polygon = raw_body_polygons[body_polygon_index]
                    body_polygon_normal = body_polygon.normal
                    body_polygon_center = body_polygon.center
                    body_normals.append(body_polygon_normal)

                offset_vector = mathutils.Vector((0,0,0))
                for n in body_normals:
                    offset_vector += n

                if len(body_normals) != 0:
                    offset_vector = offset_vector/len(body_normals)
                proxy_shapekey_vert.co = proxy_shapekey_vert.co + offset_vector*offset_factor 


    def ray_polygon_intersect(self, origin, direction, polygon_index, obj_mesh):
        pts = algorithms.get_polygon_vertices_coords(obj_mesh,polygon_index)

        if len(pts) == 4:
            i1 = mathutils.geometry.intersect_ray_tri(pts[0], pts[1], pts[2], direction, origin)
            i2 = mathutils.geometry.intersect_ray_tri(pts[2], pts[3], pts[0], direction, origin)
            if i1 != None:
                return True
            if i2 != None:
                return True

        if len(pts) == 3:
            i1 = mathutils.geometry.intersect_ray_tri(pts[0], pts[1], pts[2], direction, origin)
            if i1 != None:
                return True

        return False


    def calculate_mask_vertgroup(self, body, proxy_shapekey,raw_body_mesh,proxy_threshold = 0.025):

        #basis_proxy_mesh = proxy in basis shape, without shapekey applied
        #proxy_shapekey = shapekey of actual, "real" proxy shape as it is after the fitting
        #basis_body_mesh = body in basis shape, without morphings and armature
        #raw_body_mesh = raw copy of current body shape, with morphing and armature applied
        #body = actual "real" body to modify as final result

        raw_body_vertices = raw_body_mesh.vertices
        raw_body_polygons = raw_body_mesh.polygons
        raw_body_tree = algorithms.kdtree_from_mesh_polygons(raw_body_mesh)

        actual_body_polygons = body.data.polygons
        actual_body_vertices = body.data.vertices
        algorithms.remove_vertgroup(body, "mbastlab_mask")

        masked_verts_idx = set()
        mask_group = algorithms.new_vertgroup(body, "mbastlab_mask")

        for actual_vert in proxy_shapekey.data:

            nearest_body_polygon_data = raw_body_tree.find(actual_vert.co)
            involved_vertices = set()
            dist_proxy_body = nearest_body_polygon_data[2]
            raw_body_polygon_idx = nearest_body_polygon_data[1]
            raw_body_polygon = raw_body_polygons[raw_body_polygon_idx]

            if dist_proxy_body < proxy_threshold:
                raw_body_polygon_vertices = raw_body_polygon.vertices
                for v_idx in raw_body_polygon_vertices:
                    masked_verts_idx.add(v_idx)

        algorithms.less_boundary_verts(body, masked_verts_idx, iterations=2)

        for i,vert in enumerate(actual_body_vertices):
            if i in masked_verts_idx:
                mask_group.add([vert.index], 1.0, 'REPLACE')                

        self.add_mask_modifier(body, "mbastlab_mask")

    def remove_proxy_mask(self, body):
        algorithms.remove_modifier(body, self.mask_modifier_name)


