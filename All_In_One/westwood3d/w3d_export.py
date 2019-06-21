import bpy
import bmesh
import mathutils
from . import w3d_struct

def make_material(ob, mesh, uvlayers):
    info = mesh.add('material_info')
    info.PassCount = ob.material_slots[0].material.westwood3d.mpass_count
    info.VertexMaterialCount = len(ob.material_slots) * info.PassCount
    info.ShaderCount = info.VertexMaterialCount
    info.TextureCount = info.VertexMaterialCount * 2
    
    vertex_materials = mesh.add('vertex_materials')
    shaders = mesh.add('shaders')
    textures = mesh.add('textures')
    
    for ms in ob.material_slots:
        for p in ms.material.westwood3d.mpass:    
            
            # vertex material
            m = vertex_materials.add('vertex_material')
            
            name = m.add('vertex_material_name')
            name.name = p.name
            
            vinfo = m.add('vertex_material_info')
            
            # shader
            shaders.shaders.append({
                'SrcBlend': 1,
                'DestBlend': 0,
                'DepthMask': 1,
                'AlphaTest': 0,
                
                'PriGradient': 1,
                'SecGradient': 0,
                'DepthCompare': 3,
                'DetailColorFunc': 0,
                'DetailAlphaFunc': 0,
                
                'Texturing': 0,
                'PostDetailColorFunc': 0,
                'PostDetailAlphaFunc': 0
            })
    
            # stages
            for s in (p.stage0, p.stage1):
                if s == '':
                    info.TextureCount -= 1
                    continue
                tex = textures.add('texture')
                name = tex.add('texture_name')
                name.name = s
    
    # passes
    mpass = mesh.add('material_pass')
    for p in range(info.PassCount):
        
        ids = mpass.add('vertex_material_ids')
        ids.ids.append(0)
        
        ids = mpass.add('shader_ids')
        ids.ids.append(0)
        
        stage = mpass.add('texture_stage')
        for s in range(2):
            name = 'pass' + str(p + 1) + '.' + str(s)
            layer = uvlayers[name] if name in uvlayers else None
            if layer is not None:
                
                ids = stage.add('texture_ids')
                ids.ids.append(0)
                
                coords = stage.add('stage_texcoords')
                for uv in layer:
                    coords.texcoords.append(uv)
    
    return info.VertexMaterialCount
    
def make_mesh(ob, root, ctrname):
    mesh = root.add('mesh')
    header = mesh.add('mesh_header3')
    header.MeshName = ob.name.split('.')[-1]
    header.ContainerName = ctrname
    
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    
    header.NumTris = len(bm.faces)
    header.NumVertices = len(bm.faces) * 3
    
    box = ob.bound_box.data.dimensions / 2
    header.Min = (-box[0],-box[1],-box[2])
    header.Max = (box[0],box[1],box[2])
    header.SphRadius = box.length
    header.SphCenter = header.Max
    
    verts = mesh.add('vertices')
    norms = mesh.add('vertex_normals')
    tris = mesh.add('triangles')
    shades = mesh.add('vertex_shade_indices')
    
    vidx = 0
    for f in bm.faces:
        tris.triangles.append({
            'Vindex': (vidx, vidx + 1, vidx + 2),
            'Attributes': 13,
            'Normal': (f.normal[0], f.normal[1], f.normal[2]),
            'Dist': 1
        })
        for v in f.verts:
            verts.vertices.append((v.co[0], v.co[1], v.co[2]))
            norms.normals.append((v.normal[0], v.normal[1], v.normal[2]))
        for v in range(3):
            shades.ids.append(vidx + v)
        vidx += 3
    
    uvlayers = {}
    for i in bm.loops.layers.uv.items():
        uvs = []
        for f in bm.faces:
            for loop in f.loops:
                uvs.append((loop[i].uv[0], loop[i].uv[1]))
        uvlayers[i.name] = uvs
    
    header.NumMaterials = make_material(ob, mesh, uvlayers)
    
def make_pivots(ob, parentid, pivots, subobj):
    id = len(pivots)
    pivots.append((ob.name.split('.')[-1], parentid, ob.location, ob.matrix_local.to_quaternion()))
    
    if ob.type != 'EMPTY' or len(ob.children) == 0:
        subobj.append((id, ob))
    
    for c in ob.children:
        make_pivots(c, id, pivots, subobj)

def write_some_data(context, filepath, use_some_setting):
    print("running write_some_data...")
    
    ctrname = "MYEXPORT"
    
    # find top objects
    top = []
    scene = bpy.context.scene
    for ob in scene.objects:
        if ob.parent is None:
            top.append(ob)
    
    # pivots
    pivots = []
    subobj = []
    if len(top) == 1:
        make_pivots(top[0], 0xffffffff, pivots, subobj)
    else:
        pivots.append(('ROOTTRANSFORM', 0xffffffff, (0,0,0), (1,0,0,0)))
        for ob in top:
            make_pivots(ob, 0, pivots, subobj)
    
    # make the structure
    root = w3d_struct.node()
    
    # hierarchy
    node = root.add('hierarchy')
    
    header = node.add('hierarchy_header')
    header.Name = ctrname
    header.NumPivots = len(pivots)
    
    pnode = node.add('pivots')
    for p in pivots:
        pnode.pivots.append({
            'Name': p[0],
            'ParentIdx': p[1],
            'Translation': p[2],
            'EulerAngles': p[3].to_euler(),
            'Rotation': (p[3][1],p[3][2],p[3][3],p[3][0])
        })
    
    # meshes
    for id, ob in subobj:
        if ob.type == 'MESH':
            make_mesh(ob, root, ctrname)
    
    # hlod
    node = root.add('hlod')
    header = node.add('hlod_header')
    header.Name = ctrname
    header.HierarchyName = ctrname
    
    sub = node.add('hlod_lod_array')
    header = sub.add('hlod_sub_object_array_header')
    header.ModelCount = len(subobj)
    
    for id, ob in subobj:
        s = sub.add('hlod_sub_object')
        s.BoneIndex = id
        s.Name = ctrname[:15] + '.' + ob.name.split('.')[-1][:15]
    
    # save
    w3d_struct.save(root, filepath)
    
    print('done')
    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportWestwood3D(Operator, ExportHelper):
    '''This appears in the tooltip of the operator and in the generated docs'''
    bl_idname = "export.westwood3d"
    bl_label = "Export Westwood3D"

    # ExportHelper mixin class uses this
    filename_ext = ".w3d"

    filter_glob = StringProperty(
            default="*.w3d",
            options={'HIDDEN'},
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )

    type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
            )

    def execute(self, context):
        return write_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportWestwood3D.bl_idname, text="Westwood3D (.w3d)")