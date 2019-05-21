import bpy
import bmesh
import mathutils
import os
from . import w3d_struct, w3d_aggregate, w3d_util

def make_mats(materials):
    for mdata in materials:
        pdata = mdata['mpass']
        
        mat = bpy.data.materials.new('Material')
        mdata['BlenderMaterial'] = mat
        
        mat.use_nodes = True
        tree = mat.node_tree
        for n in tree.nodes:
            tree.nodes.remove(n)
        
        w3d = mat.westwood3d
        
        # basic info
        w3d.surface_type = str(mdata['surface'])
        w3d.sort_level = mdata['sort_level']
        
        # add passes
        w3d.mpass_count = len(pdata)
        while len(w3d.mpass) < w3d.mpass_count:
            w3d.mpass.add()
        
        name = ''
        texdone = False
        for p in range(len(pdata)):
            
            w3d.mpass[p].name = pdata[p]['vertex_material']['name']
            name += w3d.mpass[p].name + '-'
            
            vm = pdata[p]['vertex_material']['info']
            w3d.mpass[p].ambient = vm.Ambient
            w3d.mpass[p].diffuse = vm.Diffuse
            w3d.mpass[p].specular = vm.Specular
            w3d.mpass[p].emissive = vm.Emissive
            w3d.mpass[p].shininess = vm.Shininess
            w3d.mpass[p].opacity = vm.Opacity
            w3d.mpass[p].translucency = vm.Translucency
            w3d.mpass[p].mapping0 = str(vm.Mapping0)
            w3d.mpass[p].mapping1 = str(vm.Mapping1)
            
            sh = pdata[p]['shader']
            w3d.mpass[p].srcblend = str(sh['SrcBlend'])
            w3d.mpass[p].destblend = str(sh['DestBlend'])
            w3d.mpass[p].depthmask = sh['DepthMask']
            w3d.mpass[p].alphatest = sh['AlphaTest']
            
            
            textures = []
            s = 0
            for stage in pdata[p]['stages']:
                t = bpy.data.textures.new(stage['name'], 'IMAGE')
                t.image = bpy.data.images[stage['name']] if stage['name'] in bpy.data.images else None
                
                if s == 0:
                    w3d.mpass[p].stage0 = t.name
                else:
                    w3d.mpass[p].stage1 = t.name
                s += 1
                
        # set name
        if name != '':
            mat.name = name
        
        # Create basic node material
        nodegeo = tree.nodes.new('GEOMETRY')
        nodeout = tree.nodes.new('OUTPUT')
        
        if len(w3d.mpass) > 1:
            nodemix = tree.nodes.new('MIX_RGB')
            tree.links.new(nodegeo.outputs[6], nodemix.inputs[0])
            tree.links.new(nodemix.outputs[0], nodeout.inputs[0])
            r = 1
            for mpass in w3d.mpass:
                if mpass.stage0 in bpy.data.textures:
                    nodetex = tree.nodes.new('TEXTURE')
                    nodetex.texture = bpy.data.textures[mpass.stage0]
                    tree.links.new(nodegeo.outputs[4], nodetex.inputs[0])
                    tree.links.new(nodetex.outputs[1], nodemix.inputs[r])
                else:
                    nodeval = tree.nodes.new('VALUE')
                    nodeval.outputs[0].default_value = 1.0
                    tree.links.new(nodeval.outputs[0], nodemix.inputs[r])
                r += 1
                if r > 2:
                    break
        else:
            for mpass in w3d.mpass:
                if mpass.stage0 in bpy.data.textures:
                    nodetex = tree.nodes.new('TEXTURE')
                    nodetex.texture = bpy.data.textures[mpass.stage0]
                    tree.links.new(nodegeo.outputs[4], nodetex.inputs[0])
                    tree.links.new(nodetex.outputs[1], nodeout.inputs[0])
                    break


def deform_mesh(mesh, mdata, pivots):
    inf = mdata.get('vertex_influences')
    if inf is None:
        return
    inf = inf.influences
    
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for v in bm.verts:
        v.co = pivots[inf[v.index]]['blender_object'].matrix_world * v.co
    bm.normal_update()
    bm.to_mesh(mesh)
def make_shapes(root):
    shapes = []
    shapes += root.find('box')
    shapes += root.find('sphere')
    shapes += root.find('ring')
    
    for s in shapes:
        ob = bpy.data.objects.new(s.Name, None)
        ob.location = s.Center
        ob.scale = s.Extent
        
        bpy.context.scene.objects.link(ob)
        
        if s.type() == 'ring':
            ob.empty_draw_type = 'CIRCLE'
        elif s.type() == 'sphere':
            ob.empty_draw_type = 'SPHERE'
        else: # box
            ob.empty_draw_type = 'CUBE'
        
        # for pivot access
        s.blender_object = ob
    
def make_meshes(root):
    meshes = root.find('mesh')
    for m in meshes:
        info = m.get('mesh_header3')
        fullname = info.ContainerName + '.' + info.MeshName
        
        verts = m.get('vertices').vertices
        faces = m.get('triangles').triangles
        
        tex = m.findRec('texture_name')
        mpass = m.findRec('material_pass')
        
        tids = m.getRec('texture_ids')
        if tids != None:
            tids = tids.ids
        
        # create mesh
        me = bpy.data.meshes.new(fullname)
        
        # current bmesh's uv.new() doesn't work properly
        # have to create UVlayers with the old API
        for p in range(len(mpass)):
            uvs = mpass[p].findRec('stage_texcoords')
            for uv in range(len(uvs)):
                me.uv_textures.new('pass' + str(p + 1) + '.' + str(uv))
        bm = bmesh.new()
        bm.from_mesh(me)
        
        for v in verts:
            bm.verts.new(v)
        for f in faces:
            try:
                bm.faces.new([bm.verts[i] for i in f['Vindex']]).material_index = f['Mindex']
            except:
                print("duplicate faces encountered on:" + fullname)
        
        # vertex color information
        for p in range(len(mpass)):
            dcg = mpass[p].get('dcg')
            if dcg is not None:
                alpha = False
                for c in dcg.dcg:
                    if c[3] < 255:
                        alpha = True
                        break
                
                layer = bm.loops.layers.color.new('pass' + str(p + 1))
                for v in range(len(bm.verts)):
                    for loop in bm.verts[v].link_loops:
                        col = dcg.dcg[v]
                        if alpha:
                            loop[layer].r = col[3] / 255
                            loop[layer].g = col[3] / 255
                            loop[layer].b = col[3] / 255
                        else:
                            loop[layer].r = col[0] / 255
                            loop[layer].g = col[1] / 255
                            loop[layer].b = col[2] / 255
        
        # Transfer UVs
        uvs = m.findRec('stage_texcoords')
        for uvi in range(len(uvs)):
            layer = bm.loops.layers.uv[uvi]
            for v in range(len(bm.verts)):
                for loop in bm.verts[v].link_loops:
                    loop[layer].uv = uvs[uvi].texcoords[v]
        
        
        bm.normal_update()
        bm.to_mesh(me)
        
        # attach to object, place in scene
        ob = bpy.data.objects.new(fullname, me)
        bpy.context.scene.objects.link(ob)
        bpy.context.scene.objects.active = ob
            
        # move hidden objects to second layer
        if info.Attributes & 0x00001000:
            # move vis objects way over there
            if info.Attributes & 0x00000040:
                ob.layers[5] = True
                ob.layers[0] = False
            else:
                ob.layers[10] = True
                ob.layers[0] = False
        
        # materials
        for mat in m.Materials:
            bpy.ops.object.material_slot_add()
            ob.material_slots[ob.material_slots.__len__() - 1].material = mat['BlenderMaterial']
        
        # assign textures to uv map
        if tids != None and len(tids) > 0 and len(tex) > 0:
            for uvlay in me.uv_textures:
                i = 0
                for foo in uvlay.data:
                    try:
                        foo.image = bpy.data.images[tex[tids[i]].name]
                    except:
                        pass
                    if i < len(tids) - 1:
                        i += 1
        
        # for pivot access
        m.blender_object = ob
    
def load_images(root, paths):
    # get every image
    filenames = root.findRec('texture_name')
    
    # load images. Blender can figure out duplicates
    for fn in filenames:
        img = None
        for path in paths:
            try:
                img = bpy.data.images.load(os.path.join(path, fn.name))
            except:
                # if it failed, try again with .dds
                try:
                    ddsname = os.path.splitext(fn.name)[0] + '.dds'
                    img = bpy.data.images.load(os.path.join(path, ddsname))
                    fn.name = ddsname
                except:
                    pass
            
            if img != None:
                break
        
        if img == None:
            print('image not loaded: ' + fn.name)
    
def shift_layer(ob, n):
    for i in range(len(ob.layers)):
        if ob.layers[i]:
            ob.layers[i + n] = True
            ob.layers[i] = False
            break
    
def make_pivots(p, parent=None):
    
    subobj = []
    
    # get sub objects
    for data, lod in p['obj']:
        obj = data.blender_object
        subobj.append(obj)
        if lod == -1:
            for i in range(p['lodcount']):
                obj.layers[i] = True
        else:
            shift_layer(obj, lod)
    
    # proxy objects
    for name in p['prx']:
        ob = bpy.data.objects.new(name, None)
        ob.empty_draw_type = 'CUBE'
        ob.show_x_ray = True
        bpy.context.scene.objects.link(ob)
        for i in range(p['lodcount']):
            ob.layers[i] = True
        subobj.append(ob)
    
    # create node
    if len(subobj) == 1:
        ob = subobj[0]
    else:
        ob = bpy.data.objects.new(p['name'], None)
        bpy.context.scene.objects.link(ob)
        for sub in subobj:
            sub.parent = ob
    
    # transformations and stuff
    ob.parent = parent
    ob.location += mathutils.Vector(p['translation'])
    ob.rotation_mode = 'QUATERNION'
    r = p['rotation']
    ob.rotation_quaternion = (r[3], r[0], r[1], r[2])
    ob.rotation_mode = 'XYZ'
    
    # recursive
    for c in p['children']:
        make_pivots(c, ob)
    
    p['blender_object'] = ob
    
    # deform all meshes to match bones
    bpy.context.scene.update()
    for data, lod in p['obj']:
        if data.type() == 'mesh':
            if data.get('vertex_influences') is not None:
                deform_mesh(data.blender_object.data, data, p['index'])
    
def make_bones(ob_tree):
    name = ob_tree.name
    ob_tree.name = 'temp'
    arm = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, arm)
    bpy.context.scene.objects.link(ob)
    bpy.context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    make_b(ob_tree, arm)
    bpy.ops.object.mode_set(mode='OBJECT')

def make_b(ob, arm, parent=None):
    
    bone = arm.edit_bones.new(ob.name)
    
    if ob.location.length > 0:
        # Leaf nodes don't have tails so invent one
        bone.tail = (ob.location.length * 0.5,0,0)
    else:
        # X-Up axis for bones apparently
        bone.tail = (0.1,0,0)
    
    # Seems to work
    bone.transform(ob.matrix_world)
    if bone.vector.y >= 0:
        bone.roll = -bone.roll
    
    # can have connected or loose bones
    if parent:
        if len(ob.parent.children) == 1 and (parent.head - bone.head).length > 0.001:
            parent.tail = bone.head
        else:
            bone.use_connect = False
        bone.parent = parent
    
    for c in ob.children:
        make_b(c, arm, bone)
    
    
def load_scene(root, paths, ignore_lightmap):
    
    load_images(root, paths)
    
    materials = w3d_util.mat_reduce(root, ignore_lightmap)
    
    robj = w3d_util.collect_render_objects(root)
    pivots = w3d_util.make_pivots(root, robj)
    
    make_mats(materials)
    make_meshes(root)
    make_shapes(root)
    
    for p in pivots.values():
        make_pivots(p)
    
    # load aggregates
    for ag in root.find('aggregate'):
        info = ag.get('aggregate_info')
        index = pivots[info.BaseModelName]['index']
        for s in info.Subobjects:
            bone = s['BoneName']
            for i in index:
                if i['agname'] == bone:
                    break
            pivots[s['SubobjectName']]['blender_object'].parent = i['blender_object']
    
# blender stuff
def read_some_data(context, filepath, ignore_lightmap):
    print("running read_some_data...")
    
    # source directories
    current_path = os.path.dirname(filepath)
    paths = [
        current_path,
        os.path.join(current_path, '../textures/'),
    ]
    
    # Load data
    root = w3d_struct.load(filepath)
    w3d_aggregate.aggregate(root, paths)
    
    load_scene(root, paths, ignore_lightmap)
    
    #bpy.context.scene.game_settings.material_mode = 'GLSL'
    for scrn in bpy.data.screens:
        if scrn.name == 'Default':
            bpy.context.window.screen = scrn
            for area in scrn.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.viewport_shade = 'TEXTURED'
    
    print('done')
    return {'FINISHED'}

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportWestwood3D(Operator, ImportHelper):
    '''This appears in the tooltip of the operator and in the generated docs'''
    bl_idname = "import.westwood3d"
    bl_label = "Import Westwood3D"

    # ImportHelper mixin class uses this
    filename_ext = ".w3d"

    filter_glob = StringProperty(
            default="*.w3d",
            options={'HIDDEN'},
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    ignore_lightmap = BoolProperty(
            name="Don't import lightmaps",
            description="Lightmap data increases material count",
            default=True,
            )
    
    def execute(self, context):
        return read_some_data(context, self.filepath, self.ignore_lightmap)
        
# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportWestwood3D.bl_idname, text="Westwood3D (.w3d)")