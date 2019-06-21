"""
This script imports PayDay 2 Model File format files to Blender.

Usage:
Execute this script from the "File->Import" menu and choose a .model file to
open.

"""

import os
import bpy
import bmesh
import ctypes
from mathutils import Matrix
from bmesh.types import BMVert
from struct import unpack

from xml.dom.minidom import parse
from xml.dom.minidom import Node

class Pd2ModelImport:

	# Definition of sections type/tag :
	
    animation_data_tag                = int('5DC011B8', 16)    # Animation data
    author_tag                        = int('7623C465', 16)    # Author tag
    material_group_tag                = int('29276B1D', 16)    # Material Group
    material_tag                      = int('3C54609C', 16)    # Material
    object3D_tag                      = int('0FFCD100', 16)    # Object3D
    model_data_tag                    = int('62212D88', 16)    # Model data
    geometry_tag                      = int('7AB072D3', 16)    # Geometry
    topology_tag                      = int('4C507A13', 16)    # Topology
    passthroughGP_tag                 = int('E3A3B1CA', 16)    # PassthroughGP
    topologyIP_tag                    = int('03B634BD', 16)    # TopologyIP
    quatLinearRotationController_tag  = int('648A206C', 16)    # QuatLinearRotationController
    quatBezRotationController_tag     = int('197345A5', 16)    # QuatBezRotationController
    skinbones_tag                     = int('65CC1825', 16)    # SkinBones
    bones_tag                         = int('2EB43C77', 16)    # Bones
	# section_unknown1			      = int('803BA1FF', 16)    # ?   Ex: in str_vehicle_van_player.model
	# section_unknown2                = int('8C12A526', 16)    # ?   Ex: in str_vehicle_van_player.model
	
    hllDll = None
    hllDllPath = "HashDLLPath"
    try:
        hllDll = ctypes.CDLL(hllDllPath)
    except:
        raise NameError("Could not load Hash64 dll %s" % hllDllPath)
	
    def __init__(self):
        #constructor, do initialisation and stuff
        self.buff=''
        self.dictionary = {} #Hashlist
        self.object_file = ''
        self.materials = {} #Materials by key
        self.assets_path = 'D:\\PD2 Extract\\'
        #c:\\Program Files (x86)\\Steam\\SteamApps\\common\\PAYDAY The Heist\\assets\\extract\\
        #c:\\Program Files (x86)\\Steam\\SteamApps\\common\\PAYDAY 2\\assets\\extract\\
        HashlistPath = "Hashlist Path"
        with open(HashlistPath) as f:
          lines = f.read().splitlines() 
          for line in lines:
              hashcode = int(self.get_hash(str(line)))
              self.dictionary[hashcode] = line
              #print("[" + str(hashcode) + "] = " + self.dictionary[hashcode])

    def read(self, file_path):

        try:
            f = open(file_path, "rb")
        except IOError as e:
            print("({})".format(e))

        print('import file : %s' % file_path)
        self.buff = f.read()
        f.close()
        
        model_path = os.path.splitext(file_path)[0]
        
        objectData = None
        try:
            objectData = parse(model_path + '.object')
        except:
            print("Could not load object, trying .object.xml")
            try:
                objectData = parse(model_path + '.object.xml')
            except:
                raise NameError("Could not load object %s" % model_path)
        
        diesel = objectData.getElementsByTagName("diesel")
        mats_path = diesel[0].getAttribute("materials")
        #Can read enabled/disabled/effects later from object file
        objectData.unlink()
        
        mat_configData = None
        try:
            mat_configData = parse(self.assets_path + mats_path + '.material_config')
        except:
            print("Could not load material config, trying .material_config.xml")
            try:
                mat_configData = parse(self.assets_path + mats_path + '.material_config.xml')
            except:
                raise NameError("Could not load material_config %s" % mats_path)
        
        
			
        mat_config_materials = mat_configData.getElementsByTagName("material")
        for mat in mat_config_materials:
          mat_name = mat.getAttribute("name")
          mat_textures = mat.getElementsByTagName("diffuse_texture")
          for mat_texture in mat_textures:
            realpath = self.assets_path + mat_texture.getAttribute("file")
            try:
                img = bpy.data.images.load(realpath + ".texture")
                self.materials[mat_name] = realpath + ".texture"
            except:
                print("Could not load texture " + realpath + " attempting with .texture.dds extension")
                try:
                    img = bpy.data.images.load(realpath + ".texture.dds")
                    self.materials[mat_name] = realpath + ".texture.dds"
                except:
                    raise NameError("Cannot load image %s" % realpath)

            cTex = bpy.data.textures.new(mat_name, type = 'IMAGE')
            cTex.image = img
            # Create material
            new_mat = bpy.data.materials.new(mat_name)
            # Add texture slot for color texture
            mtex = new_mat.texture_slots.add()
            mtex.texture = cTex
            mtex.texture_coords = 'UV'
            mtex.use_map_color_diffuse = True 
            mtex.use_map_color_emission = True 
            mtex.emission_color_factor = 0.5
            mtex.use_map_density = True 
            mtex.mapping = 'FLAT' 
            
        mat_configData.unlink()
        

        # Unpack 4 bytes to interpret as a "little endian int" at offset 0x0 of buff
        # section_count = unpack("<i", self.buff[0:4])[0]
        # print('section count (1) : %d' % section_count)

        sections = self.parse_file()
        parsed_sections = {}

        for section in sections:

            if section[1] == self.animation_data_tag:
                #print("animation_data_tag")
                parsed_sections[section[2]] = self.parse_animation_data(section[0]+12, section[3], section[2])

            elif section[1] == self.author_tag:
                #print("author_tag")
                parsed_sections[section[2]] = self.parse_author(section[0]+12, section[3], section[2])

            elif section[1] == self.material_group_tag:
                #print("material_group_tag")
                parsed_sections[section[2]] = self.parse_material_group(section[0]+12, section[3], section[2])

            elif section[1] == self.material_tag:
                #print("material_tag")
                parsed_sections[section[2]] = self.parse_material(section[0]+12, section[3], section[2])

            elif section[1] == self.object3D_tag:
                #print("object3D_tag")
                parsed_sections[section[2]] = self.parse_object3d(section[0]+12, section[3], section[2])

            elif section[1] == self.geometry_tag:
                #print("geometry_tag")
                parsed_sections[section[2]] = self.parse_geometry(section[0]+12, section[3], section[2])

            elif section[1] == self.model_data_tag:
                #print("geometry_tag")
                parsed_sections[section[2]] = self.parse_model_data(section[0]+12, section[3], section[2])

            elif section[1] == self.topology_tag:
                #print("topology_tag")
                parsed_sections[section[2]] = self.parse_topology(section[0]+12, section[3], section[2])
 
            elif section[1] == self.passthroughGP_tag:
                #print("passthroughGP_tag")
                parsed_sections[section[2]] = self.parse_passthrough_gp(section[0]+12, section[3], section[2])

            elif section[1] == self.topologyIP_tag:
                #print("topologyIP_tag")
                parsed_sections[section[2]] = self.parse_topology_ip(section[0]+12, section[3], section[2])

            elif section[1] == self.quatLinearRotationController_tag:
                print("quatLinearRotationController_tag    /!\    No parser defined   /!\ ")
                #parsed_sections[section[2]] =

            elif section[1] == self.quatBezRotationController_tag:
                print("quatBezRotationController_tag    /!\    No parser defined   /!\ ")
                #parsed_sections[section[2]] =

            elif section[1] == self.skinbones_tag:
                print("skinbones_tag    /!\    No parser defined   /!\ ")
                #parsed_sections[section[2]] =

            elif section[1] == self.bones_tag:
                print("bones_tag    /!\    No parser defined   /!\ ")
                #parsed_sections[section[2]] =

            else:
                print("Unknown section tag %d" % section[1] )



        for section in sections:

            if section[1] == self.model_data_tag:
                model_data = parsed_sections[section[2]]
                if model_data[3] == 6:
                    continue
                
                model_id = self.dictionary.get(model_data[2][1], str(model_data[2][1]))
                #model_id = "model-%x" % model_data[2][2]
                geometry = parsed_sections[parsed_sections[model_data[4]][2]]
                topology = parsed_sections[parsed_sections[model_data[4]][3]]
                faces = topology[4]
                verts = geometry[6]
                uvs = geometry[7]
                normals = geometry[8]
                colors = geometry[9]
                weights = geometry[10]
                
                
                rotation_matrix = Matrix((
                  (model_data[2][4][0],model_data[2][4][4],model_data[2][4][8],model_data[2][4][12]),
                  (model_data[2][4][1],model_data[2][4][5],model_data[2][4][9],model_data[2][4][13]),
                  (model_data[2][4][2],model_data[2][4][6],model_data[2][4][10],model_data[2][4][14]),
                  (model_data[2][4][3],model_data[2][4][7],model_data[2][4][11],model_data[2][4][15])))
                #loc, rot, scale = rotation_matrix.decompose()
                rot = rotation_matrix.to_quaternion()
                loc = model_data[2][5]
                
                if model_data[2][6] > 0:
                    obj_parent_data = parsed_sections[model_data[2][6]]
                    if obj_parent_data[0] == 'Model':
                      obj_parent_data = obj_parent_data[2]
                    
                    obj_parent = self.dictionary.get(obj_parent_data[2], str(obj_parent_data[2]))
                else:
                    obj_parent = str(0)
                
                material_names = []
                marerial_indecies = None
                if model_data[3] == 3:
                  mat_group_sec_id = model_data[8]
                  mat_group_sec_data = parsed_sections[mat_group_sec_id]
                  for item in mat_group_sec_data[3]:
                    mat_sec_data = parsed_sections[item]
                    if self.dictionary.get(mat_sec_data[2], None) != None:
                      material_names.append(self.dictionary.get(mat_sec_data[2], None))
                    
                  marerial_indecies = model_data[7]
                
                self.build_model(model_id, verts, uvs, normals, faces, colors, weights, obj_parent, loc, rot, material_names, marerial_indecies)
            elif section[1] == self.object3D_tag:
                object3D_data = parsed_sections[section[2]]
                obj_name = self.dictionary.get(object3D_data[2], str(object3D_data[2]))
                obj_position = object3D_data[6]
                
                obj_rotationMat = Matrix((
                  (object3D_data[5][0],object3D_data[5][4],object3D_data[5][8],object3D_data[5][12]),
                  (object3D_data[5][1],object3D_data[5][5],object3D_data[5][9],object3D_data[5][13]),
                  (object3D_data[5][2],object3D_data[5][6],object3D_data[5][10],object3D_data[5][14]),
                  (object3D_data[5][3],object3D_data[5][7],object3D_data[5][11],object3D_data[5][15])))
                
                #loc, rot, scale = obj_rotationMat.decompose()
                rot = obj_rotationMat.to_quaternion()
                
                loc = object3D_data[6]
                
                if object3D_data[7] > 0:
                    obj_parent_data = parsed_sections[object3D_data[7]]
                    if obj_parent_data[0] == 'Model':
                      obj_parent_data = obj_parent_data[2]
                    
                    obj_parent = self.dictionary.get(obj_parent_data[2], str(obj_parent_data[2]))
                else:
                    obj_parent = str(0)
                    
                self.build_emptyObject(obj_name, loc, rot, obj_parent)
            
        print("Import done")
		
		
    def rao(self, offset, size):
        return self.buff[offset:offset+size]

    def read_string(self, offset):
        out = ''
        while self.buff[offset] != 0:
            out += chr(self.buff[offset])
            offset += 1
        return out, offset+1

    #read 3 unsigned int (little endian) at address "offset"
    def parse_section_header(self, offset):
        return unpack("<III", self.rao(offset, 12))

    def parse_file(self):
        out_sections = []
        file_size = 0

        section_count = unpack("<i", self.rao(0, 4))[0]

        current_offset = 4

        if section_count == -1:
            file_size, section_count = unpack("<ii", self.rao(4, 8))
            current_offset += 8
            print("file_size: %d bytes, section count : %d" % (file_size, section_count))

        # Sections headers contains : uint32 section_type  // Uses one of the below tags. Tags are assigned to serializable objects within the Diesel engine.
        #                             uint32 section_id    // Appears to be a random, but unique value assigned to the section. Unknown if these have any requirements or meanings.
        #                             uint32 section size
        for x in range(section_count):
            pieces = self.parse_section_header(current_offset)
            out_sections.append((current_offset, pieces[0], pieces[1], pieces[2]))
            print("current_offset %d, p0: %u, p1: %u, p2: %u" % (current_offset, pieces[0], pieces[1], pieces[2]))
            current_offset += pieces[2] + 12
            print("next_offset %d" % current_offset)


        return out_sections

    def parse_author(self, offset, size, section_id):
        unknown = unpack("<q", self.rao(offset, 8))[0]
        email, next_offset = self.read_string(offset+8)
        source_file, next_offset = self.read_string(next_offset)
        unknown2 = unpack("<i", self.rao(next_offset, 4))[0]
        return ('Author', section_id, unknown, email, source_file, unknown2)

    def parse_material_group(self, offset, size, section_id):
        count = unpack("<i", self.rao(offset, 4))[0]
        items = []
        for x in range(count):
            items.append(unpack("<i", self.rao(offset + 4 + (x*4), 4))[0])
        return ('Material Group', section_id, count, items)

    def parse_animation_data(self, offset, size, section_id):
        unknown1, unknown2, unknown3, count = unpack("<qiii", self.rao(offset, 20))
        items = []
        for x in range(count):
            items.append(unpack("<f", roa(offset + 20 + (x*4), 4))[0])
        return ('Animation Data', section_id, unknown1, unknown2, unknown3, count, items)

    def parse_geometry(self, offset, size, section_id):
        cur_offset = offset
        # 1 is verts, 7 is uvs, 2 is normals, 20 is unkown, 21 is unknown
        size_index = [0,4,8,12,16,4,4,8,12]
        count1, count2 = unpack("<ii", self.rao(offset, 8))
        cur_offset += 8
        headers = []
        calc_size = 0
        for x in range(count2):
            item_size, item_type = unpack("<ii", self.rao(cur_offset, 8))
            calc_size += size_index[item_size]
            headers.append((item_size,item_type))
            cur_offset += 8
        verts = []
        uvs = []
        normals = []
        colors = []
        weights = []
        #print('len(headers) = ' + str(len(headers)))
        for header in headers:
            if header[1] == 1:
                for x in range(count1):
                    verts.append(unpack("<fff", self.rao(cur_offset, 12)))
                    cur_offset += 12
            elif header[1] == 7:
                for x in range(count1):
                    u,v = unpack("<ff", self.rao(cur_offset, 8))
                    cur_offset += 8
                    uvs.append((u, -v))
            elif header[1] == 2:
                for x in range(count1):
                    normals.append(unpack("<fff", self.rao(cur_offset, 12)))
                    cur_offset += 12
            elif header[1] == 5:
                for x in range(count1):
                    colors.append(unpack("<BBBB", self.rao(cur_offset, 4)))
                    cur_offset += 4
            elif header[1] == 17:
                for x in range(count1):
                    weights.append(unpack("<fff", self.rao(cur_offset, 12)))
                    cur_offset += 12
            
            else:
                #print('header[1] = ' + str(header[1]))
                #print('size_index[header[0]] = ' + str(size_index[header[0]]))
                cur_offset += size_index[header[0]] * count1
        
        return ('Geometry', section_id, count1, count2, headers, count1*calc_size, verts, uvs, normals, colors, weights)

    def parse_topology(self, offset, size, section_id):
        cur_offset = offset
        unknown1, count1 = unpack("<ii", self.rao(offset, 8))
        cur_offset += 8
        facelist = []
        for x in range(int(count1/3)):
            facelist.append(unpack("<HHH", self.rao(cur_offset, 6)))
            cur_offset += 6
        count2 = unpack("<i", self.rao(offset+8+count1*2, 4))[0]
        items2 = unpack("<"+count2*"b", self.rao(offset+8+count1*2+4, count2))
        unknown2 = unpack("<q", self.rao(offset+8+4+count2+count1*2, 8))[0]
        return ("Topology", section_id, unknown1, count1, facelist, count2, items2, unknown2)

    def parse_material(self, offset, size, section_id):
        cur_offset = offset
        hashname = unpack("<Q", self.rao(offset, 8))[0]
        cur_offset += 8
        return ('Material', section_id, hashname)

    def parse_object3d(self, offset, size, section_id):
        cur_offset = offset
        hashname, count = unpack("<Qi", self.rao(offset, 12))
        cur_offset += 12
        items = []
        for x in range(count):
            items.append(unpack("<iii", self.rao(cur_offset, 12)))
            cur_offset += 12
        int_count = 64/4
        rotation_matrix = unpack("<"+int(int_count)*"f", self.rao(cur_offset, 64))
        cur_offset += 64
        position = unpack("<fff", self.rao(cur_offset, 12))
        cur_offset += 12
        parentID = unpack("<i", self.rao(cur_offset, 4))[0]
        return ('Object3D', section_id, hashname, count, items, rotation_matrix, position, parentID)

    def parse_topology_ip(self, offset, size, section_id):
        topology_section_id = unpack("<i", self.rao(offset, 4))[0]
        return ('TopologyIP', section_id, topology_section_id)

    def parse_passthrough_gp(self, offset, size, section_id):
        geometry_section, facelist_section = unpack("<ii", self.rao(offset, 8))
        return ('PassthroughGP', section_id, geometry_section, facelist_section)

    def parse_model_data(self, offset, size, section_id):
        cur_offset = offset
        hashname, count = unpack("<Qi", self.rao(offset, 12))
        cur_offset += 12
        items = []
        for x in range(count):
            items.append(unpack("<iii", self.rao(cur_offset, 12)))
            cur_offset += 12
        int_count = 64/4
        rotation_matrix = unpack("<"+int(int_count)*"f", self.rao(cur_offset, 64))
        cur_offset += 64
        position = unpack("<fff", self.rao(cur_offset, 12))
        cur_offset += 12
        parentID = unpack("<i", self.rao(cur_offset, 4))[0]
        cur_offset += 4
        object3d = ('Object3D', hashname, count, items, rotation_matrix, position, parentID)
        version = unpack("<i", self.rao(cur_offset, 4))[0]
        cur_offset += 4
        if version == 6:
            unknown5 = unpack("<fff", self.rao(cur_offset, 12))
            cur_offset += 12
            unknown6 = unpack("<fff", self.rao(cur_offset, 12))
            cur_offset += 12
            unknown7, unknown8 = unpack("<ii", self.rao(cur_offset, 8))
            return ('Model', section_id, object3d, version, unknown5, unknown6, unknown7, unknown8)
        else:
            a, b, count2 = unpack("<iii", self.rao(cur_offset, 12))
            cur_offset += 12
            items2 = []
            for x in range(count2):
                items2.append(unpack("<iiiii", self.rao(cur_offset, 20)))
                cur_offset += 20
            material_group_section_id, unknown10 = unpack("<ii", self.rao(cur_offset, 8))
            cur_offset += 8
            #There's more to this section...
            #public UInt32 unknown10;
            #public Vector3D bounds_min; // Z (max), X (low), Y (low)
            #public Vector3D bounds_max; // Z (low), X (max), Y (max)
            #public UInt32 unknown11;
            #public UInt32 unknown12;
            #public UInt32 unknown13;
            #public UInt32 skinbones_ID;
            
            return ('Model', section_id, object3d, version, a, b, count2, items2, material_group_section_id, unknown10)

    def build_emptyObject(self, name, position, rotation_matrix, parentID):
            
            bpy.ops.object.add(type='EMPTY', view_align=False, enter_editmode=False, location=position)
            
            bpy.context.active_object.name = name
            
            bpy.data.objects[name].rotation_mode = 'QUATERNION'
            bpy.data.objects[name].location = position
            bpy.data.objects[name].rotation_quaternion = rotation_matrix
            #bpy.data.objects[name].show_x_ray = True
            #bpy.data.objects[name].show_name = True
            
            
            if parentID != str(0):
              if bpy.data.objects.get(parentID) is not None:
                bpy.data.objects[name].parent = bpy.data.objects[parentID]
            
            #bpy.data.objects[name]
            
            
    def build_model(self, name, verts, uvs, normals, faces, colors, weights, parentID, loc, rot, material_names, material_indecies):
            mesh = bpy.data.meshes.new(name)
            #mesh.from_pydata(verts, [], faces)
            bm = bmesh.new()
            for vert in verts:
                bm.verts.new(vert)

            if hasattr(bm.verts, "ensure_lookup_table"):
                bm.verts.ensure_lookup_table()
				
            if len(normals) > 0:
                for x in range(len(verts)):
                    bm.verts[x].normal.x = normals[x][0]
                    bm.verts[x].normal.y = normals[x][1]
                    bm.verts[x].normal.z = normals[x][2]
            for face in faces:
                try:
                    bm.faces.new([bm.verts[face[0]], bm.verts[face[1]], bm.verts[face[2]]])
                except:
                    print("Face allready exist")
            
            if len(uvs) > 0:
              #mesh.uv_textures.new("UV Map")
            
              uv_layer = bm.loops.layers.uv.verify()
              bm.faces.layers.tex.verify()
              
              if hasattr(bm.faces, "ensure_lookup_table"):
                bm.faces.ensure_lookup_table()
              
              face = bm.faces[-1]
              for i, loop in enumerate(face.loops):
                  loop[uv_layer].uv[0] = uvs[loop.vert.index][0]
                  loop[uv_layer].uv[1] = uvs[loop.vert.index][1]
                  
              for face in bm.faces:        # Iterate over all of the object's faces
                face.material_index = 0 # Assing random material to face
                 
            #Weights
            if len(weights) > 0:
                dvert_lay = bm.verts.layers.deform.verify()
                
                for x in range(len(verts)):
                    dvert = bm.verts[x][dvert_lay]

                    dvert[0] = weights[x][0]
                    dvert[1] = weights[x][1]
                    dvert[2] = weights[x][2]
                    
                    #if group_index in dvert:
                    #    print("Weight %f" % dvert[group_index])
                    #else:
                    #    print("Setting Weight")
                    #    dvert[0] = weights[x][0]
                
                '''
                ob.vertex_groups.new("Bone 1")
                ob.vertex_groups.new("Bone 2")
                ob.vertex_groups.new("Bone 3")
                
                b1_id = ob.vertex_groups["Bone 1"].index
                b2_id = ob.vertex_groups["Bone 2"].index
                b3_id = ob.vertex_groups["Bone 3"].index
                
                for grp in ob.vertex_groups:
                    grp.add(range(0,len(weights)), 1.0, 'REPLACE')
                
                for x in range(len(verts)):
                    bm.verts[x].groups[b1_id].weight = weights[x][0]
                    bm.verts[x].groups[b2_id].weight = weights[x][1]
                    bm.verts[x].groups[b3_id].weight = weights[x][2]
                    
            '''
            
            
                  
            bm.to_mesh(mesh)
            ob = bpy.data.objects.new(name, mesh)
            ob.rotation_mode = 'QUATERNION'
            ob.location = loc
            ob.rotation_quaternion = rot
            ob_mesh = ob.data
            
            if len(weights) > 0:
                ob.vertex_groups.new("Bone 1")
                ob.vertex_groups.new("Bone 2")
                ob.vertex_groups.new("Bone 3")
                
            
            #print("len(colors)=" + str(len(colors)))
            if len(colors) > 0:
              if not ob_mesh.vertex_colors:
                ob_mesh.vertex_colors.new()
              
              color_map = ob_mesh.vertex_colors["Col"]
              
              for poly in ob_mesh.polygons:
                  for loop_index in poly.loop_indices:
                    loop_vert_index = mesh.loops[loop_index].vertex_index
                    color_map.data[loop_index].color = [ colors[loop_vert_index][2]/255.0, colors[loop_vert_index][1]/255.0, colors[loop_vert_index][0]/255.0 ]
            
            #UVs
            if len(uvs) > 0:
              for poly in ob_mesh.polygons:
                    #print("Polygon", poly.index, "from loop index", poly.loop_start, "and length", poly.loop_total)
                    for i in poly.loop_indices: # <-- python Range object with the proper indices already set
                        l = ob_mesh.loops[i] # The loop entry this polygon point refers to
                        v = ob_mesh.vertices[l.vertex_index] # The vertex data that loop entry refers to
                        #print("\tLoop index", l.index, "points to vertex index", l.vertex_index, "at position", v.co)
                        for j,ul in enumerate(ob_mesh.uv_layers):
                            ul.data[l.index].uv = uvs[l.vertex_index]
                            #print("\t\tUV Map", j, "has coordinates", ul.data[l.index].uv, "for this loop index")
              
            bpy.context.scene.objects.link(ob)
            
            if parentID != str(0):
              if bpy.data.objects.get(parentID) is not None:
                if bpy.data.objects[name] != bpy.data.objects[parentID]:
                  bpy.data.objects[name].parent = bpy.data.objects[parentID]
                  
            loaded_images = []
            
            for mat_name in material_names:
              if bpy.data.materials.get(mat_name) is not None:
                  bpy.data.objects[name].data.materials.append(bpy.data.materials[mat_name])
                  retrieved_material = self.materials.get(mat_name, None)
                  loaded_images.append(bpy.data.images.load(retrieved_material))
              
            if material_indecies != None:
              face_index = 0
              for modelItem in material_indecies:
                if len(uvs) > 0:
                  if bpy.data.objects[name].data.uv_textures.active.data:
                    for indx, uv_tex_face in enumerate(bpy.data.objects[name].data.uv_textures.active.data, start=face_index): 
                      if indx == face_index + modelItem[3]:
                        break
                      print('Name='+name + " modelItem[4]="+str(modelItem[4]))
                      for uv_tex_face in bpy.data.objects[name].data.uv_textures.active.data: 
                          uv_tex_face.image = loaded_images[modelItem[4]]
                      
                    face_index += modelItem[3]
                  
            mesh.update()
            
    def get_hash(self, text):
      str_bytes = bytes(text, 'UTF8')

      self.hllDll.Hash.restype = ctypes.c_ulonglong
      self.hllDll.Hash.argtypes = [(ctypes.c_ubyte * len(str_bytes)), ctypes.c_ulonglong, ctypes.c_ulonglong]

      dll_p1 = (ctypes.c_ubyte * len(str_bytes)).from_buffer_copy(str_bytes)
      dll_p2 = ctypes.c_ulonglong (len(dll_p1))
      dll_p3 = ctypes.c_ulonglong (0)
      
      return (self.hllDll.Hash(dll_p1, dll_p2, dll_p3))