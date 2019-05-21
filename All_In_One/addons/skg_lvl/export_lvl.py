import bpy
import bmesh
import os
import struct


def save(operator, context, filename=""):
    models = {}

    for o in bpy.data.objects:
        if o.type != 'MESH':
            print("Skipped object:", o.name, "of type:", o.type)
            continue  # Skip if it's not a mesh
        print("Exporting object: " + o.name)
        models[o.name] = {}  # Each model is a dict
        # Python note: http://stackoverflow.com/questions/2465921/how-to-copy-a-dictionary-and-only-edit-the-copy
        # Since we want to mutate it anyway no need to copy it back
        model = models[o.name]
        mesh = o.data
        # Get texture name
        # blender.stackexchange.com/questions/5121/find-the-name-of-textures-linked-to-an-object-in-python
        print("Reading material slots to find the texture")
        # TODO not very robust, probably takes the last possible texture in the last material, beautify if needed
        for mat_slot in o.material_slots:
            for mtex_slot in mat_slot.material.texture_slots:
                if mtex_slot:
                    if hasattr(mtex_slot.texture, 'image'):
                        model['texture_name'] = os.path.splitext(mtex_slot.texture.image.name)[0]
                        print("Found an image for material slot: " + mtex_slot.texture.image.name)

        # If not a single texture was found in any of the materials assigned raise exception
        # Oh, you are still here? Learn something about exceptions:
        # http://www.ianbicking.org/blog/2007/09/re-raising-exceptions.html
        if model['texture_name'] is None:
            raise ValueError("No texture for assigned material found. ADD ONE! Object: " + o.name)

        # Debug output
        print("Texture name: " + model['texture_name'])

        # Recalculate normals, TODO is this good or needed?
        mesh.calc_normals_split()  # Calculate split vertex normals, which preserve sharp edges
        # Since we changed the mesh, we have to validate it
        mesh.update()
        mesh.validate()
        # Get bmesh for detailed data
        bmesh_mesh = bmesh.new()
        bmesh_mesh.from_mesh(mesh)
        # Set name
        model['element_name'] = o.name
        model['shape_name'] = mesh.name
        # Set world matrix
        model['world_matrix'] = get_mat4(o.matrix_world)
        # TODO the world matrix does not handle very small values (changes from import to export?)
        # Check if model is visible TODO might be something else entirely
        model['is_visible'] = 0 if o.hide else 1
        # Iterate through each of their actions and make animations out of it TODO animation export
        model['animations'] = []
        # Iterate through each of their vertices and grab all the data ==> Be aware that IB magic has to be applied
        model['vertex_data'] = {}
        model['vertex_data']['position'] = []
        model['vertex_data']['uv'] = []
        model['vertex_data']['normals'] = []
        model['vertex_data']['vertex_color'] = []
        model['index_buffer'] = []

        # TODO it's the job of the artist to triangulate the models, should throw an exception
        uv_layer = bmesh_mesh.loops.layers.uv.active
        # Check if vertex_color / _alpha exists
        has_vertex_color = True
        has_vertex_alpha = True
        try:
            vertex_color = bmesh_mesh.loops.layers.color['rgb']
        except KeyError:
            has_vertex_color = False
        try:
            vertex_alpha = bmesh_mesh.loops.layers.color['a']
        except KeyError:
            has_vertex_alpha = False

        print("Object has " + str(len(bmesh_mesh.faces)) + " faces")
        # Go through each face
        n_of_shared_vertices = 0
        for i, face in enumerate(bmesh_mesh.faces):
            triangle_indices = []
            triangle = face.loops  # Loops ==> Triangles
            # Check if loop is a triangle
            if len(triangle) != 3:
                raise ValueError("Loop != 3 vertices, triangulate / check for stray vertices; Meshname: " + model['shape_name'])
            # Go through each vertex in the face (l_i ==> loop_index)
            for l_i in range(3):
                triangle_vertex = triangle[l_i]
                x, y, z = triangle[l_i].vert.co[0:3]
                uv_data = triangle_vertex[uv_layer].uv
                u, v = uv_data[0:2]
                nx, ny, nz = triangle[l_i].vert.normal[0:3]
                # Optional data: If it doesn't exist will use default value 1.0
                # TODO try except when we check for stuff (vertex_color / _alpha) to not check for EVERY SINGLE vertex
                if has_vertex_color:
                    rgb_data = triangle_vertex[vertex_color]
                    r, g, b = rgb_data[0:3]
                else:
                    r = g = b = 1.0

                if has_vertex_alpha:
                    a_data = triangle_vertex[vertex_alpha]
                    a = a_data[0]
                else:
                    a = 1.0
                # -1 ==> no vertex found at the if below
                found_vertex = -1
                # Compare if its exact data is already used in vertex_data

                for vertex_index in range(len(model['vertex_data']['position'])):
                    # Get data for one of the existing vertices
                    pos = model['vertex_data']['position'][vertex_index]
                    uvs = model['vertex_data']['uv'][vertex_index]
                    normals = model['vertex_data']['normals'][vertex_index]

                    vertex_colors = model['vertex_data']['vertex_color'][vertex_index]
                    # Check if any of the vertex attributes is different
                    if pos[0] != x or pos[1] != y or pos[2] != z or uvs[0] != u or uvs[1] != v:
                        continue
                    if normals[0] != nx or normals[1] != ny or normals[2] != nz:
                        continue
                    if vertex_colors[0] != r or vertex_colors[1] != g or vertex_colors[2] != b or vertex_colors[3] != a:
                        continue
                    # If we got this far we found a matching vertex we can reuse
                    found_vertex = vertex_index
                    n_of_shared_vertices += 1  # Used for debug output
                    break  # End for-loop because we already found one

                if found_vertex == -1:  # We have to create a new vertex in the list
                    model['vertex_data']['position'].append([x, y, z])
                    model['vertex_data']['uv'].append([u, v])
                    model['vertex_data']['normals'].append([nx, ny, nz])
                    model['vertex_data']['vertex_color'].append([r, g, b, a])
                    found_vertex = len(model['vertex_data']['position']) - 1

                # Add index to triangle_indices (the current triangle)
                triangle_indices.append(found_vertex)

            # Add triangle to index_buffer
            model['index_buffer'].append(triangle_indices)

        # Just for logs
        print("The current model contains " + str(n_of_shared_vertices) + " shared vertices")

        # Write bounding box data
        # Get minimal/maximal x/y/z positions
        x_min = y_min = z_min = 0
        x_max = y_max = z_max = 0
        for position in model['vertex_data']['position']:
            x_min = min(x_min, position[0])
            x_max = max(x_max, position[0])
            y_min = min(y_min, position[1])
            y_max = max(y_max, position[1])
            z_min = min(z_min, position[2])
            z_max = max(z_max, position[2])

        model['bounding_box'] = [x_min, y_min, z_min, x_max, y_max, z_max]

        # Done with current model
        print("=====================================")

    # Setup path
    working_directory = os.path.dirname(filename)

    # Write sgi
    # TODO currently no animations, add them to sgi and sgm
    with open(filename, 'wb') as f:
        write_pascal_string(f, "2.0")
        f.write(struct.pack('>Q', len(models)))
        for k, current_model in models.items():
            write_pascal_string(f, current_model['element_name'])
            write_pascal_string(f, current_model['shape_name'])
            # World matrix
            for entry in current_model['world_matrix']:
                f.write(struct.pack('>f', entry))
            # Write if object is visible TODO again, this might be something else
            f.write(struct.pack('B', current_model['is_visible']))
            # unknown TODO unknown, fix it, default value 0
            f.write(struct.pack('B', 0))
            # Number of animations, 0 for now (see todo above with statement)
            n_of_animations = 0
            f.write(struct.pack('>Q', n_of_animations))
    # Write sgm
    # Currently no data for sgs in the vertex data (the joints)
    for key, model in models.items():
        with open(os.path.join(working_directory, model['shape_name'] + '.sgm.msb'), 'wb') as f:
            # Write header data
            write_pascal_string(f, "2.0")
            write_pascal_string(f, model['texture_name'])
            # 13 unknown floats, seems to be the same in every file
            f.write(struct.pack('>fffffffffffff', 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 90))
            # Write rest of header
            write_pascal_string(f, "float p[3],n[3],uv[2]; uchar4 c;")  # TODO Doesn't work for files with sgs
            f.write(struct.pack('>Q', 36))  # TODO doesn't work for files with sgs
            f.write(struct.pack('>Q', len(model['vertex_data']['position'])))  # Write number of vertices
            f.write(struct.pack('>Q', len(model['index_buffer'])))  # Write number of triangles (loops)
            f.write(struct.pack('>Q', 0))  # TODO doesn't work for sgs files, so, what is it?
            for vertex_index in range(len(model['vertex_data']['position'])):
                # Write vertex data
                f.write(struct.pack('>f', model['vertex_data']['position'][vertex_index][0]))
                f.write(struct.pack('>f', model['vertex_data']['position'][vertex_index][1]))
                f.write(struct.pack('>f', model['vertex_data']['position'][vertex_index][2]))

                f.write(struct.pack('>f', model['vertex_data']['normals'][vertex_index][0]))
                f.write(struct.pack('>f', model['vertex_data']['normals'][vertex_index][1]))
                f.write(struct.pack('>f', model['vertex_data']['normals'][vertex_index][2]))

                f.write(struct.pack('>f', model['vertex_data']['uv'][vertex_index][0]))
                f.write(struct.pack('>f', model['vertex_data']['uv'][vertex_index][1]))
                # Range in Blender: 0.0 to 1.0, Range in sgm: 0 to 255
                f.write(struct.pack('>B', round(model['vertex_data']['vertex_color'][vertex_index][0] * 255.0)))
                f.write(struct.pack('>B', round(model['vertex_data']['vertex_color'][vertex_index][1] * 255.0)))
                f.write(struct.pack('>B', round(model['vertex_data']['vertex_color'][vertex_index][2] * 255.0)))
                f.write(struct.pack('>B', round(model['vertex_data']['vertex_color'][vertex_index][3] * 255.0)))
            for triangle in model['index_buffer']:
                # Write index buffer
                for i in range(3):
                    f.write(struct.pack('>H', triangle[i]))
            # Write the bounding box data TODO check if anything changes with files with a sgs
            for i in range(6):
                f.write(struct.pack('>f', model['bounding_box'][i]))
            # TODO no sgs is currently written
            # Write bone names
            # Write bone data

    # Write sga
    # Write sgs

    return {'FINISHED'}


def write_pascal_string(f, string):
    ascii_string = string.encode('ascii')
    f.write(struct.pack('>Q', len(ascii_string)))
    f.write(ascii_string)


def get_mat4(mat):
        return [mat[0][0], mat[1][0], mat[2][0], mat[3][0],
                mat[0][1], mat[1][1], mat[2][1], mat[3][1],
                mat[0][2], mat[1][2], mat[2][2], mat[3][2],
                mat[0][3], mat[1][3], mat[2][3], mat[3][3]]