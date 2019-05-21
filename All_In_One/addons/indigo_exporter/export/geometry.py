import os

import bpy

import mathutils        #@UnresolvedImport

import time
import math
import hashlib
import array

from ..extensions_framework import util as efutil

from .. core.util import get_worldscale
from .. export import ( indigo_log,
                            xml_builder,
                            SceneIterator, OBJECT_ANALYSIS,
                            indigo_visible,
                            exportutil
                            )
from .. export.igmesh import igmesh_writer
from . import ExportCache

class model_base(xml_builder):
    element_type = 'model'

    def __init__(self, scene):
        self.scene = scene
        super().__init__()

    def get_additional_elements(self, obj):
        return {}

    def get_format(self, obj, mesh_name, matrix_list):
        if len(matrix_list) > 0:
            matrix = matrix_list[0]
        else:
            matrix = None

        xml_format = {
            'mesh_name': [mesh_name],
            # scale == 1.0 because scale data is included in rot matrix
            'scale': [1.0],
        }

        xml_format.update(exportutil.getTransform(self.scene, obj, matrix))
        xml_format.update(self.get_additional_elements(obj))
        return xml_format

    def build_xml_element(self, obj, mesh_name, matrix_list):
        xml = self.Element(self.element_type)

        xml_format = self.get_format(obj, mesh_name, matrix_list)

        self.build_subelements(obj, xml_format, xml)

        return xml

class model_object(model_base):

    # <model> supports IES illumination data and emission_scale
    def get_additional_elements(self, obj):
        d = {}

        for ms in obj.material_slots:
            mat = ms.material
            if mat == None: continue
            ie = mat.indigo_material.indigo_material_emission
            if ie.emission_enabled and ie.emit_ies:
                d['ies_profile'] = {
                    'material_name': [mat.name],
                    'path': [efutil.filesystem_path(ie.emit_ies_path)]
                }

        for ms in obj.material_slots:
            mat = ms.material
            if mat == None: continue
            ie = mat.indigo_material.indigo_material_emission
            if ie.emission_enabled and ie.emission_scale:
                d['emission_scale'] = {
                    'material_name': [mat.name],
                    'measure': [ie.emission_scale_measure],
                    'value': [ie.emission_scale_value * 10**ie.emission_scale_exp]
                }

        if(obj.data != None and obj.data.indigo_mesh.invisible_to_camera):
            d['invisible_to_camera'] = ["true"]

        return d

    def get_format(self, obj, mesh_name, matrix_list):
        xml_format = {
            'mesh_name': [mesh_name],
            # scale == 1.0 because scale data is included in rot matrix
            'scale': [1.0],
        }

        # Add a base static rotation.
        xml_format.update(exportutil.getTransform(self.scene, obj, matrix_list[0][1], xml_format='matrix'))

        if len(matrix_list) > 1:
            # Remove pos, conflicts with keyframes.
            del(xml_format['pos'])
        
            keyframes = exportutil.matrixListToKeyframes(self.scene, obj, matrix_list)
                
            xml_format['keyframe'] = tuple(keyframes)

        xml_format.update(self.get_additional_elements(obj))
        return xml_format

class exit_portal(model_base):
    element_type = 'exit_portal'


class SectionPlane(xml_builder):
    def __init__(self, pos, normal, cull_geometry):
        self.pos = pos
        self.normal = normal
        self.cull_geometry = cull_geometry
        super().__init__()

    def build_xml_element(self):
        xml = self.Element('section_plane')
        self.build_subelements(
            self,
            {
                'point':  list(self.pos)[0:3],
                'normal':  list(self.normal)[0:3],
                'cull_geometry': [str(self.cull_geometry).lower()]
            },
            xml
        )
        return xml

class SpherePrimitive(xml_builder):
    def __init__(self, matrix_world, obj):
        self.matrix_world = matrix_world
        self.obj = obj
        super().__init__()

    def build_xml_element(self):

        mat = ""
        for ms in self.obj.material_slots:
            mat = ms.material.name


        # Compute radius in object space from bounding box
        bb = self.obj.bound_box # Get object-space bounding box
        bb_min = bb[0]
        bb_max = bb[6]

        #print("min")
        #for i in range(0, 8):
        #    print("bb[" + str(i) + "]:")
        #    for c in range(0, 3):
        #        print(str(bb[i][c]))

        bb_radius = max(bb_max[0] - bb_min[0], bb_max[1] - bb_min[1], bb_max[2] - bb_min[2]) * 0.5

        pos = self.matrix_world.col[3]

        # Compute object->world space scale, use the max of the scalings to scale the sphere radius.
        scale_vec = self.matrix_world.to_scale()
        scale = max(math.fabs(scale_vec[0]), math.fabs(scale_vec[1]), math.fabs(scale_vec[2]))

        radius_ws = bb_radius * scale

        #print("pos: " + str(pos))
        #print("bb_radius: " + str(bb_radius))
        #print("scale: " + str(scale))

        xml = self.Element('sphere')
        self.build_subelements(
            self,
            {
                'center':  list(pos)[0:3],
                'radius':  [radius_ws],
                'material_name': [mat]
            },
            xml
        )
        return xml

class LightingChecker:
    def __init__(self, geometry_exporter):        
        self.valid_lighting = False
        
        self.ObjectsChecked = ExportCache("Objects")
        self.LampsChecked = ExportCache("Lamps")
        self.MaterialsChecked = ExportCache("Materials")
        self.CheckedDuplis = ExportCache("Duplis")
        self.geometry_exporter = geometry_exporter
    
    def handleMesh(self, obj):
        if self.valid_lighting or self.ObjectsChecked.have(obj): return
        emitting_object = False
        
        for ms in obj.material_slots:
            if self.MaterialsChecked.have(ms.material): continue
            self.MaterialsChecked.add(ms.material, ms.material)
            
            if ms.material == None: continue
            if ms.material.indigo_material == None: continue

            iem = ms.material.indigo_material.indigo_material_emission
            mat_test = iem.emission_enabled
            if iem.emission_enabled:
                mat_test &= self.check_spectrum(iem, 'emission')
                if iem.emission_scale:
                    mat_test &= (iem.emission_scale_value > 0.0)
                else:
                    mat_test &= (iem.emit_power > 0.0 and iem.emit_gain_val > 0.0)
                mat_test &= self.geometry_exporter.scene.indigo_lightlayers.is_enabled(iem.emit_layer)
            emitting_object |= mat_test

        self.ObjectsChecked.add(obj, obj)
        self.valid_lighting |= emitting_object
    
    def handleLamp(self, obj):
        if self.valid_lighting or self.LampsChecked.have(obj): return
        
        self.valid_lighting |= obj.data.type in ('SUN', 'HEMI')
        self.LampsChecked.add(obj, obj)
        
    def check_spectrum(self, obj, prefix):
            valid_sp = False
            sp_type = getattr(obj, '%s_SP_type' % prefix)
            if sp_type == 'uniform':
                valid_sp = getattr(obj, '%s_SP_uniform_val' % prefix) > 0.0
            elif sp_type == 'rgb':
                valid_sp = getattr(obj, '%s_SP_rgb' % prefix).v > 0.0
            elif sp_type == 'blackbody':
                valid_sp = getattr(obj, '%s_SP_blackbody_gain' % prefix) > 0.0
            return valid_sp
    
    
class GeometryExporter(SceneIterator):
    # Cache
    ExportedMaterials = None
    ExportedObjects = None
    ExportedDuplis = None
    ExportedLamps = None
    ExportedMeshes = None
    MeshesOnDisk = None
    
    mesh_uses_shading_normals = None
    
    # Options
    normalised_time = 0
    mesh_dir = None
    rel_mesh_dir = None
    skip_existing_meshes = False
    verbose = False
    
    # Stats
    total_mesh_export_time = 0

    # serial counter for instances exported
    object_id = 0

    def __init__(self):        
        self.ExportedMaterials = {}
        self.ExportedObjects = {}
        self.ExportedDuplis = {}
        self.ExportedLamps = {}
        self.ExportedMeshes = {}
        self.MeshesOnDisk = {}
        
        self.mesh_uses_shading_normals = {} # Map from exported_mesh_name to boolean
        
        # Lighting
        self.lc = LightingChecker(self)
    
    def isLightingValid(self):
        return self.lc.valid_lighting

    def handleDuplis(self, obj, particle_system=None):
        try:

            try:
                old_draw_method = None
                if particle_system and particle_system.settings.draw_method != 'RENDER':
                    # Switch viewport draw method to allow creating dupli list (viewport draw method should not affect rendering/exporting)
                    old_draw_method = particle_system.settings.draw_method
                    particle_system.settings.draw_method = 'RENDER'
                    bpy.context.scene.update()
                    
                obj.dupli_list_create(self.scene, 'RENDER')
                
                if old_draw_method:
                    # Reset draw method
                    particle_system.settings.draw_method = old_draw_method
                    
                if not obj.dupli_list:
                    raise Exception('cannot create dupli list for object %s' % obj.name)
            except Exception as err:
                indigo_log('%s'%err)
                return
                
            exported_objects = 0

            # Create our own DupliOb list to work around incorrect layers
            # attribute when inside create_dupli_list()..free_dupli_list()
            for dupli_ob in obj.dupli_list:
                if dupli_ob.object.type not in self.supported_mesh_types:
                    continue
                if not indigo_visible(self.scene, dupli_ob.object, is_dupli=True):
                    continue
                if hasattr(dupli_ob.object.data, 'polygons') and not dupli_ob.object.data.polygons and not dupli_ob.object.data.indigo_mesh.valid_proxy():
                    continue
                
                #Lighting
                self.lc.handleMesh(dupli_ob.object)

                do = dupli_ob.object
                dm = dupli_ob.matrix.copy()
                
                # Check for group layer visibility, if the object is in a group
                gviz = len(do.users_group) == 0
                for grp in do.users_group:
                    gviz |= True in [a&b for a,b in zip(do.layers, grp.layers)]
                if not gviz:
                    continue

                exported_objects += 1
                
                self.exportModelElements(
                    do,
                    self.buildMesh(do),
                    dm,
                    dupli_ob,
                    particle_system
                )


            obj.dupli_list_clear()
            
            self.ExportedDuplis[obj] = True
            
            if self.verbose: indigo_log('... done, exported %s duplis' % exported_objects)

        except SystemError as err:
            indigo_log('Error with handleDuplis and object %s: %s' % (obj, err))

    def handleLamp(self, obj):
        if OBJECT_ANALYSIS: indigo_log(' -> handleLamp: %s' % obj)
        #Lighting
        self.lc.handleLamp(obj)

        if obj.data.type == 'AREA':
            pass
        if obj.data.type == 'HEMI':
            self.ExportedLamps[obj.name] = [obj.data.indigo_lamp_hemi.build_xml_element(obj, self.scene)]
        if obj.data.type == 'SUN':
            self.ExportedLamps[obj.name] = [obj.data.indigo_lamp_sun.build_xml_element(obj, self.scene)]

    def handleMesh(self, obj):
        if OBJECT_ANALYSIS: indigo_log(' -> handleMesh: %s' % obj)
        self.lc.handleMesh(obj)
        self.exportModelElements(
            obj,
            self.buildMesh(obj),
            obj.matrix_world.copy()
        )

    def buildMesh(self, obj):
        """
        Process the mesh into required format.
        """

        return self.exportMeshElement(obj)


    def add_vec2_list_hash(self, hash, vec2_list):
        # Convert the list of vec2s to a list of floats
        component_list = []
        for v in vec2_list:
            component_list.extend([v[0], v[1]])

        a = array.array('f', component_list)
        hash.update(a)
        return hash

    def add_vec3_list_hash(self, hash, vec3_list):
        # Convert the list of vec3s to a list of floats
        component_list = []
        for v in vec3_list:
            component_list.extend([v[0], v[1], v[2]])

        a = array.array('f', component_list)
        hash.update(a)
        return hash


    # Compute a hash of the mesh data.
    # Returns a string of hex characters
    def meshHash(self, obj, mesh):

        hash = hashlib.sha224()

        ### Hash material names ###
        for ms in obj.material_slots:
            if ms.material != None:
                hash.update(ms.material.name.encode(encoding='UTF-8'))

        ### Hash Vertex coords ###
        vertices = []
        if mesh:
            for v in mesh.vertices:
                vertices.append(v.co)
        else:
            hash.update(obj.data.indigo_mesh.mesh_path.encode(encoding='UTF-8'))

        self.add_vec3_list_hash(hash, vertices)

        return hash.hexdigest()

    def exportMeshElement(self, obj):
        if OBJECT_ANALYSIS: indigo_log('exportMeshElement: %s' % obj)

        if obj.type in self.supported_mesh_types:
        
            start_time = time.time()
            
            # If this object has already been exported, then don't export it again. 
            exported_mesh = self.ExportedMeshes.get(obj)
            if exported_mesh != None:
                self.total_mesh_export_time += time.time() - start_time
                return exported_mesh
        
            mesh = None
            if not obj.data.indigo_mesh.valid_proxy():
                # Create mesh with applied modifiers
                mesh = obj.to_mesh(self.scene, True, 'RENDER')

            # Compute a hash over the mesh data (vertex positions, material names etc..)
            mesh_hash = self.meshHash(obj, mesh)

            # Form a mesh name like "4618cbf0bc13316135d676fffe0a74fc9b0577909246477354da9254"
            # The name cannot contain the objects name, as the name itself is always unique.
            exported_mesh_name = bpy.path.clean_name(mesh_hash)

            # If this mesh has already been exported, then don't export it again
            exported_mesh = self.MeshesOnDisk.get(exported_mesh_name)
            if exported_mesh != None:
                # Important! If an object is matched to a mesh on disk, add to ExportedMeshes.
                # Otherwise the mesh checksum will be computed over and over again.
                self.ExportedMeshes[obj] = exported_mesh
                if mesh: bpy.data.meshes.remove(mesh)
                self.total_mesh_export_time += time.time() - start_time
                return exported_mesh

            # Make full mesh path.
            mesh_filename = exported_mesh_name + '.igmesh'
            full_mesh_path = efutil.filesystem_path( '/'.join([self.mesh_dir, mesh_filename]) )
            
            #indigo_log('full_mesh_path: %s'%full_mesh_path)

            # pass the full mesh path to write to filesystem if the object is not a proxy
            if hasattr(obj.data, 'indigo_mesh') and not obj.data.indigo_mesh.valid_proxy():
                if os.path.exists(full_mesh_path) and self.skip_existing_meshes:
                    # if skipping mesh write, parse faces to gather used mats
                    used_mat_indices = set()
                    num_smooth = 0
                    for face in mesh.tessfaces:
                        used_mat_indices.add(face.material_index)
                        if face.use_smooth:
                            num_smooth += 1

                    use_shading_normals = num_smooth > 0
                else:
                    # else let the igmesh_writer do its thing
                    (used_mat_indices, use_shading_normals) = igmesh_writer.factory(self.scene, obj, full_mesh_path, mesh, debug=OBJECT_ANALYSIS)
                    self.mesh_uses_shading_normals[full_mesh_path] = use_shading_normals
            else:
                # Assume igmesh has same number of mats as the proxy object
                used_mat_indices = range(len(obj.material_slots))

            # Remove mesh.
            if mesh: bpy.data.meshes.remove(mesh)
            
            # Export materials used by this mesh
            if len(obj.material_slots) > 0:
                for mi in used_mat_indices:
                    mat = obj.material_slots[mi].material
                    if mat == None or mat.name in self.ExportedMaterials: continue
                    mat_xmls = mat.indigo_material.factory(obj, mat, self.scene)
                    self.ExportedMaterials[mat.name] = mat_xmls

            # .. put the relative path in the mesh element
            filename = '/'.join([self.rel_mesh_dir, mesh_filename])

            #print('MESH FILENAME %s' % filename)

            shading_normals = True
            if full_mesh_path in self.mesh_uses_shading_normals:
                shading_normals = self.mesh_uses_shading_normals[full_mesh_path]

            xml = obj.data.indigo_mesh.build_xml_element(obj, filename, shading_normals, exported_name=exported_mesh_name)

            mesh_definition = (exported_mesh_name, xml)
            
            self.MeshesOnDisk[exported_mesh_name] = mesh_definition
            self.ExportedMeshes[obj] = mesh_definition
            
            total = time.time() - start_time
            self.total_mesh_export_time += total
            if self.verbose: indigo_log('Mesh Export took: %f s' % total)

            return mesh_definition

    def exportModelElements(self, obj, mesh_definition, matrix, dupli_ob=None, particle_system=None):
        if OBJECT_ANALYSIS: indigo_log('exportModelElements: %s, %s, %s' % (obj, mesh_definition))
        # If this object was instanced by a DupliObject, hash the DupliObject's persistent_id
        if dupli_ob != None:
            key = hash((obj, particle_system, dupli_ob.persistent_id[0], dupli_ob.id_data))
        else:
            key = hash(obj)
        
        # If the model (object) was already exported, only update the keyframe list.
        emodel = self.ExportedObjects.get(key)
        if emodel != None:
            if emodel[0] == 'OBJECT':
                # Append to list of (time, matrix) tuples.
                emodel[3].append((self.normalised_time, matrix))
            return

        # Special handling for section planes:  If object has the section_plane attribute set, then export it as a section plane.
        if(obj.data != None and obj.data.indigo_mesh.section_plane):
            xml = SectionPlane(matrix.col[3], matrix.col[2], obj.data.indigo_mesh.cull_geometry).build_xml_element()

            model_definition = ('SECTION', xml)

            self.ExportedObjects[key] = model_definition
            self.object_id += 1
            return

        # Special handling for sphere primitives
        if(obj.data != None and obj.data.indigo_mesh.sphere_primitive):
            xml = SpherePrimitive(matrix, obj).build_xml_element()

            model_definition = ('SPHERE', xml)

            self.ExportedObjects[key] = model_definition
            self.object_id += 1
            return

        mesh_name = mesh_definition[0]
        
        # Special handling for exit portals
        if obj.type == 'MESH' and obj.data.indigo_mesh.exit_portal:
            xml = exit_portal(self.scene).build_xml_element(obj, mesh_name, [matrix])
            
            model_definition = ('PORTAL', xml)

            self.ExportedObjects[key] = model_definition
            self.object_id += 1
            return
            
        # Create list of (time, matrix) tuples.
        obj_matrices = [(self.normalised_time, matrix)]

        model_definition = ('OBJECT', obj, mesh_name, obj_matrices, self.scene)

        self.ExportedObjects[key] = model_definition
        self.object_id += 1