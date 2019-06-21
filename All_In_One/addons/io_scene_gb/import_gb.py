import bpy
import bmesh
import math
import os
import utility

from mathutils import Matrix, Vector, Quaternion

if 'structs' in locals():
    import importlib

    importlib.reload(structs.gb)
else:
    import structs.gb


def add_armature(self, obj):
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Converts DirectX/OpenGL coordinate system difference, where p2 is without scale, since it's not imported
    p1 = (Matrix.Scale(-1, 4, (0, 1, 0)) * Matrix.Rotation(math.pi / 2, 4, 'X'))
    p2 = (Matrix.Scale( 1, 4, (0, 1, 0)) * Matrix.Rotation(math.pi / 2, 4, 'Z')).inverted()

    for i, bone in enumerate(self.bones):
        edit = obj.data.edit_bones.new('Bone.%03d' % i)

        if bone.parent != 0xFF:
            edit.parent = obj.data.edit_bones['Bone.%03d' % bone.parent]

        # Prevents automatic deletion due to a length of zero
        edit.head = Vector([0, 0, 0])
        edit.tail = Vector([1, 0, 0])

        position,\
        rotation,\
        scale = (Matrix(bone.matrix).inverted() * p2).decompose()

        # The imported scale can trigger an internal assertion in Blender
        edit.matrix = Matrix.Scale(SCALE, 4) * p1 * Matrix.Translation(position) * rotation.to_matrix().to_4x4()

    bpy.ops.object.mode_set(mode='OBJECT')


def add_animation(self, obj, pose_matrices):
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='POSE')

    # Converts DirectX/OpenGL coordinate system difference
    p1 = (Matrix.Scale(-1, 4, (0, 1, 0)) * Matrix.Rotation(math.pi / 2, 4, 'X'))
    p2 = (Matrix.Scale(-1, 4, (1, 0, 0)) * Matrix.Rotation(math.pi / 2, 4, 'Z')).inverted()

    zipped = zip(
        self.keyframes,
        self.keyframe_frames,
        self.keyframe_events
    )

    for keyframe, frame, event in zipped:
        frame = math.ceil(frame * 30 / 1000)

        for i, m in enumerate(keyframe):
            pose = obj.pose.bones['Bone.%03d' % i]

            matrix = pose_matrices[m]

            for parent in pose.parent_recursive:
                matrix = pose_matrices[keyframe[int(parent.name[-3:])]] * matrix

            matrix = Matrix.Scale(1 if SCALE > 0 else -1, 4) * p1 * matrix * p2
            matrix[0][3] *= abs(SCALE)
            matrix[1][3] *= abs(SCALE)
            matrix[2][3] *= abs(SCALE)
            pose.matrix = matrix

            bpy.context.scene.update()

            pose.keyframe_insert('location', frame=frame)
            pose.keyframe_insert('rotation_quaternion', frame=frame)
            pose.keyframe_insert('scale', frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')


def add_mesh(self, obj):
    bm = bmesh.new()

    # Vertices
    for v in self.verts:
        bm.verts.new(v['v'])

    bm.verts.index_update()
    bm.verts.ensure_lookup_table()

    # Faces
    for f in self.faces:
        bm.faces.new(bm.verts[i] for i in f)

    bm.faces.index_update()
    bm.faces.ensure_lookup_table()

    # Texture coordinates, ignoring a possible second channel
    if getattr(self, 'material', False):
        uv_layer = bm.loops.layers.uv.verify()

        for i, f in enumerate(bm.faces):
            for j, l in enumerate(f.loops):
                v_index = self.faces[i][j]

                uv = l[uv_layer].uv
                uv[0] = +self.verts[v_index]['t0'][0]
                uv[1] = -self.verts[v_index]['t0'][1]

    # Converts DirectX/OpenGL coordinate system difference
    bm.transform(
        Matrix.Scale(SCALE, 4) * Matrix.Scale(-1, 4, (0, 1, 0)) * Matrix.Rotation(math.pi / 2, 4, 'X')
    )

    # Flip normals due to negative scaling
    for f in bm.faces:
        f.normal_flip()

    bm.to_mesh(obj.data)
    bm.free()


def add_groups(self, obj):
    groups = []
    for index in self.bones:
        groups.append(obj.vertex_groups.new('Bone.%03d' % index))

    for i, v in enumerate(self.verts):
        if 'weights' in v:
            weights = [w for w in v['weights'] if w != 0]

            if sum(weights) != 1:
                weights.append(1 - sum(weights))

            for index, weight in zip(v['indexes'], weights):
                groups[index].add([i], weight, 'ADD')
        else:
            if 'indexes' in v:
                groups[v['indexes'][0]].add([i], 1.0, 'ADD')
            else:
                for group in groups:
                    group.add([i], 1.0, 'ADD')


def add_materials(self, obj, name, image=None):
    mat = bpy.data.materials.new(name + '_Material.000')
    mat.use_nodes = True

    obj.data.materials.append(mat)

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    nodes.clear()
    links.clear()

    # Create new nodes
    new_nodes = []
    new_nodes.append(nodes.new('ShaderNodeTexCoord'))
    new_nodes.append(nodes.new('ShaderNodeMapping'))
    new_nodes.append(nodes.new('ShaderNodeTexImage'))
    new_nodes.append(nodes.new('ShaderNodeBsdfDiffuse'))

    if 'SPECULAR' in self.material.options:
        new_nodes.append(nodes.new('ShaderNodeBsdfGlossy'))
        new_nodes.append(nodes.new('ShaderNodeMixShader'))
    else:
        new_nodes.append(None)
        new_nodes.append(None)

    new_nodes.append(nodes.new('ShaderNodeBsdfTransparent'))

    if 'ARGB' in self.material.options:
        new_nodes.append(nodes.new('ShaderNodeAddShader'))
    else:
        new_nodes.append(nodes.new('ShaderNodeMixShader'))

    new_nodes.append(nodes.new('ShaderNodeBsdfTransparent'))
    new_nodes.append(nodes.new('ShaderNodeMixShader'))
    new_nodes.append(nodes.new('ShaderNodeOutputMaterial'))

    nodes = new_nodes

    # Node coodinates and names for material animations
    data = [
        ((-980, 0),   None),
        ((-780, 0),   'Mapping'),
        ((-400, 0),   None),
        ((-200, 100), None),
        ((-200, 260), None),
        ((0, 260),    None),
        ((0, -100),   None),
        ((200, 0),    None),
        ((200, 100),  None),
        ((400, 0),    'Opacity'),
        ((600, 0),    None),
    ]

    for ((x, y), name), node in zip(data, nodes):
        if node is not None:
            node.location.x = x
            node.location.y = y

            if name is not None:
                node.name = name

    # Set object (uv coordinates)
    nodes[0].object = obj

    # Set mapping
    nodes[1].vector_type = 'TEXTURE'
    nodes[1].translation[0] = self.material.frame.texture_off[0]
    nodes[1].translation[1] = self.material.frame.texture_off[1]
    nodes[1].rotation = self.material.frame.texture_rot

    # Set image
    nodes[2].image = image

    # Set opacity
    nodes[9].inputs[0].default_value = (
            self.material.frame.opacity
    )

    # Set gloss
    if nodes[5] is not None:
        nodes[5].inputs[0].default_value = 0.8

    # Output and opacity mix shader
    links.new(nodes[10].inputs[0], nodes[9].outputs[0])
    links.new(nodes[9].inputs[1], nodes[8].outputs[0])
    links.new(nodes[9].inputs[2], nodes[7].outputs[0])

    mix_shader = 'ARGB' not in self.material.options

    # Use image alpha
    if mix_shader:
        links.new(nodes[7].inputs[0], nodes[2].outputs[1])

    if 'SPECULAR' in self.material.options:
        # Alpha mix or add shader
        links.new(nodes[7].inputs[mix_shader + 0], nodes[6].outputs[0])
        links.new(nodes[7].inputs[mix_shader + 1], nodes[5].outputs[0])

        # Glossy mix
        links.new(nodes[5].inputs[1], nodes[4].outputs[0])
        links.new(nodes[5].inputs[2], nodes[3].outputs[0])

        # Glossy
        links.new(nodes[4].inputs[0], nodes[2].outputs[0])
    else:
        # Alpha mix or add shader
        links.new(nodes[7].inputs[mix_shader + 0], nodes[6].outputs[0])
        links.new(nodes[7].inputs[mix_shader + 1], nodes[3].outputs[0])

    # Diffuse, mapping, coordinates
    links.new(nodes[3].inputs[0], nodes[2].outputs[0])
    links.new(nodes[2].inputs[0], nodes[1].outputs[0])
    links.new(nodes[1].inputs[0], nodes[0].outputs[2])


def add_material_animation(self, obj, keyframe_frames):
    # Only one material is created during import
    nodes = obj.data.materials[0].node_tree.nodes
    mapping = nodes['Mapping']
    opacity = nodes['Opacity']

    for data, frame in zip(self.material.frames, keyframe_frames):
        frame = (frame / 1000) * 24

        mapping.translation[0] = data.texture_off[0]
        mapping.translation[1] = data.texture_off[1]
        mapping.rotation = data.texture_rot
        opacity.inputs[0].default_value = data.opacity

        mapping.keyframe_insert('translation', frame=frame)
        mapping.keyframe_insert('rotation', frame=frame)
        opacity.inputs[0].keyframe_insert('default_value', frame=frame)


@property
def matrix(self):
    mat_rot = Quaternion(self.rotation).to_matrix().to_4x4()

    mat_sca = Matrix([
        [self.scale[0], 0, 0],
        [0, self.scale[1], 0],
        [0, 0, self.scale[2]],
    ]).to_4x4()

    return Matrix.Translation(self.position) * mat_rot * mat_sca


def read_image(path, name):
    # Search in the object-relative and common texture directory
    for path in [path, utility.get_common_path(path)]:
        try:
            return bpy.data.images.load(
                    os.path.join(path, 'tex', name), True)

        except RuntimeError:
            pass  # Ignore, since Blender will print an error message

    return None


def setup():
    """Adds custom Blender import methods to GB objects"""
    structs.gb.GBAnimation.add_animation = add_animation
    structs.gb.GBArmature.add_armature = add_armature
    structs.gb.GBTransformation.matrix = matrix
    structs.gb.GBCollision.add_mesh = add_mesh
    structs.gb.GBMesh.add_mesh = add_mesh
    structs.gb.GBMesh.add_groups = add_groups
    structs.gb.GBMesh.add_materials = add_materials
    structs.gb.GBMesh.add_material_animation = add_material_animation

SCALE = 1

def auto_import(context, filepath, parent, scale, **args):
    setup()

    if scale == 0:
        return {'CANCELLED'}

    global SCALE

    SCALE = scale

    # The cycles renderer is needed for material nodes
    bpy.context.scene.render.engine = 'CYCLES'

    # Load GB
    with open(filepath, 'rb') as stream:
        gb = structs.gb.GBFile().parse(stream)

    # Get existing or create new parent object
    if parent not in bpy.data.objects:
        parent = bpy.data.objects.new(parent, None)

        context.scene.objects.link(parent)
        context.scene.objects.active = parent
    else:
        parent = bpy.data.objects[parent]

    # Get path and name without extension
    path = os.path.dirname(filepath)
    name = os.path.splitext(
            os.path.basename(filepath))[0]

    # Add armature
    if gb.armature is not None:
        dat = bpy.data.armatures.new(name + '_Armature.000')
        obj = bpy.data.objects.new(name + '_Armature.000', dat)

        context.scene.objects.link(obj)
        context.scene.objects.active = obj
        obj.parent = parent

        gb.armature.add_armature(obj)

        # Link to existing meshes
        for mesh in parent.children:
            if mesh.type == 'MESH':
                mesh.modifiers.new(name + '_Modifier.000', 'ARMATURE').object = obj

    # Get armature object if it exists
    for armature in parent.children:
        if armature.type == 'ARMATURE':
            break
    else:
        armature = None

    # Mapping used to insert materials later
    mesh_mapping = {}

    # Add meshes
    for mesh in gb.meshes:
        dat = bpy.data.meshes.new(name + '_Mesh.000')
        obj = bpy.data.objects.new(name + '_Mesh.000', dat)

        context.scene.objects.link(obj)
        context.scene.objects.active = obj
        obj.parent = parent

        mesh.add_mesh(obj)
        mesh.add_groups(obj)

        if args.get('import_tex', False):
            image = read_image(path, os.path.splitext(
                mesh.material.texture.lower())[0] + '.' + args['texture_ext'])
        else:
            image = None

        mesh.add_materials(obj, name, image)

        # Link to existing armature
        if armature is not None:
            obj.modifiers.new(name + '_Armature.000', 'ARMATURE').object = armature

        mesh_mapping[obj.name] = (mesh, obj)

    # Add animations
    if gb.animations:
        pose_matrices = [t.matrix for t in gb.transformations]

        for animation in gb.animations:
            if armature is None:
                print('Info: Imported animation without existing armature.')
            else:
                armature.animation_data_create()
                armature.animation_data.action = (
                        bpy.data.actions.new(name=name + '.000'))

                animation.add_animation(armature, pose_matrices)

            # Animate materials
            for _, (mesh, obj) in mesh_mapping.items():
                if mesh.material.provides_animation:
                    mesh.add_material_animation(
                            obj, animation.keyframe_frames)

    # Add collision
    if args.get('import_col', False) and gb.collision is not None:
        dat = bpy.data.meshes.new(name + '_Collision.000')
        obj = bpy.data.objects.new(name + '_Collision.000', dat)

        context.scene.objects.link(obj)
        context.scene.objects.active = obj
        obj.parent = parent

        # Hide collision object
        obj.hide_render = True
        obj.hide = True

        gb.collision.add_mesh(obj)

    return {'FINISHED'}
