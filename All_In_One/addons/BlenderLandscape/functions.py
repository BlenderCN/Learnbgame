import bpy
import os
import time
import bmesh
import platform
from random import randint, choice


class OBJECT_OT_savepaintcam(bpy.types.Operator):
    bl_idname = "savepaint.cam"
    bl_label = "Save paint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.image.save_dirty()
        return {'FINISHED'}

class OBJECT_OT_createcyclesmat(bpy.types.Operator):
    """Create cycles materials for selected objects"""
    bl_idname = "bi2cycles.material"
    bl_label = "Create cycles materials for selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.render.engine = 'CYCLES'
        bi2cycles()
        return {'FINISHED'}

##########################################################################################

def grad(rad):
    grad = rad*57.2957795
    return grad

def get_nodegroupname_from_obj(obj):
#    if 'cc_node' in [node.node_tree.name for node in obj.material_slots[0].material.node_tree.nodes]:
    if obj.material_slots[0].material.node_tree.nodes['cc_node']:
        nodegroupname = obj.material_slots[0].material.node_tree.nodes['cc_node'].node_tree.name
    else:
        nodegroupname = None
    return nodegroupname



#if 'Material Output' in [node.name for node in bpy.data.materials['your_material_name'].node_tree.nodes]:
#    print('Yes!')



def get_cc_node_in_obj_mat(nodegroupname,type):
    if type == 'RGB':
        type_name = 'RGB Curves'
    if type == 'BC':
        type_name = 'Bright/Contrast'
    if type == 'HS':
        type_name = 'Hue Saturation Value'
    node = bpy.data.node_groups[nodegroupname].nodes[type_name]
    return node


def set_up_lens(obj,sens_width,sens_lenght,lens):
    obj.select = True
    obj.data.lens = lens
    obj.data.sensor_fit = 'HORIZONTAL'
    obj.data.sensor_width = sens_width
    obj.data.sensor_height = sens_lenght
    
def set_up_scene(x,y,ao):
    bpy.context.scene.render.resolution_x = x
    bpy.context.scene.render.resolution_y = y
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.game_settings.material_mode = 'GLSL'
    bpy.context.scene.game_settings.use_glsl_lights = False
    bpy.context.scene.world.light_settings.use_ambient_occlusion = ao
    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
    bpy.context.scene.tool_settings.image_paint.screen_grab_size[0] = x
    bpy.context.scene.tool_settings.image_paint.screen_grab_size[1] = y

def assignmatslots(ob, matlist):
    #given an object and a list of material names
    #removes all material slots form the object
    #adds new ones for each material in matlist
    #adds the materials to the slots as well.

    scn = bpy.context.scene
    ob_active = bpy.context.active_object
    scn.objects.active = ob

    for s in ob.material_slots:
        bpy.ops.object.material_slot_remove()

    # re-add them and assign material
    i = 0
    for m in matlist:
        mat = bpy.data.materials[m]
        ob.data.materials.append(mat)
        bpy.context.object.active_material.use_transparency = True
        bpy.context.object.active_material.alpha = 0.5
        i += 1

    # restore active object:
    scn.objects.active = ob_active


def check_texture(img, mat):
    #finds a texture from an image
    #makes a texture if needed
    #adds it to the material if it isn't there already

    tex = bpy.data.textures.get(img.name)

    if tex is None:
        tex = bpy.data.textures.new(name=img.name, type='IMAGE')

    tex.image = img

    #see if the material already uses this tex
    #add it if needed
    found = False
    for m in mat.texture_slots:
        if m and m.texture == tex:
            found = True
            break
    if not found and mat:
        mtex = mat.texture_slots.add()
        mtex.texture = tex
        mtex.texture_coords = 'UV'
        mtex.use_map_color_diffuse = True

def tex_to_mat():
    # editmode check here!
    editmode = False
    ob = bpy.context.object
    if ob.mode == 'EDIT':
        editmode = True
        bpy.ops.object.mode_set()

    for ob in bpy.context.selected_editable_objects:

        faceindex = []
        unique_images = []

        # get the texface images and store indices
        if (ob.data.uv_textures):
            for f in ob.data.uv_textures.active.data:
                if f.image:
                    img = f.image
                    #build list of unique images
                    if img not in unique_images:
                        unique_images.append(img)
                    faceindex.append(unique_images.index(img))

                else:
                    img = None
                    faceindex.append(None)

        # check materials for images exist; create if needed
        matlist = []
        for i in unique_images:
            if i:
                try:
                    m = bpy.data.materials[i.name]
                except:
                    m = bpy.data.materials.new(name=i.name)
                    continue

                finally:
                    matlist.append(m.name)
                    # add textures if needed
                    check_texture(i, m)

        # set up the object material slots
        assignmatslots(ob, matlist)

        #set texface indices to material slot indices..
        me = ob.data
#class CAMERA_PH_presets(Menu):
#    bl_label = "cameras presets"
#    preset_subdir = "ph_camera"
#    preset_operator = "script.execute_preset"
#    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}
#    draw = Menu.draw_preset

        i = 0
        for f in faceindex:
            if f is not None:
                me.polygons[i].material_index = f
            i += 1
    if editmode:
        bpy.ops.object.mode_set(mode='EDIT')

#        self.layout.operator("cam.visibility", icon="RENDER_REGION", text='Cam visibility')

def check_children_plane(cam_ob):
    check = False
    for obj in cam_ob.children:
        if obj.name.startswith("objplane_"):
            check = True
            pass
        else:
            check = False
    return check

def correctcameraname(cameraname):
#        extensions = ['.jpg','.JPG']
#        for extension in extensions:
    if cameraname.endswith('.JPG'):
        return cameraname
        pass
    else:
        cameranamecor = cameraname + ".JPG"
#                print(cameranamecor)
        return cameranamecor

def decimate_mesh(context,obj,ratio,lod):
    selected_obs = context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
    D = bpy.data
    obj.select = True
    context.scene.objects.active = obj
    bpy.ops.object.editmode_toggle()
    print('Decimating the original mesh to obtain the '+lod+' mesh...')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.object.vertex_group_add()
    bpy.ops.object.vertex_group_assign()
    bpy.ops.object.editmode_toggle()
#    bpy.data.objects[lod1name].modifiers.new("Decimate", type='DECIMATE')
    D.objects[obj.name].modifiers.new("Decimate", type='DECIMATE')
    D.objects[obj.name].modifiers["Decimate"].ratio = ratio
    D.objects[obj.name].modifiers["Decimate"].vertex_group = "Group"
    D.objects[obj.name].modifiers["Decimate"].invert_vertex_group = True
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
#    print("applied modifier")

def setupclonepaint():
    bpy.ops.object.mode_set(mode = 'TEXTURE_PAINT')
    bpy.ops.paint.brush_select(paint_mode='TEXTURE_PAINT', texture_paint_tool='CLONE')
    bpy.context.scene.tool_settings.image_paint.mode = 'MATERIAL'
    bpy.context.scene.tool_settings.image_paint.use_clone_layer = True
#    bpy.context.scene.tool_settings.image_paint.seam_bleed = 16
    obj = bpy.context.scene.objects.active
    
    for matslot in obj.material_slots:
        mat = matslot.material
        original_image = node_retriever(mat, "original")
        clone_image = node_retriever(mat, "source_paint_node")
        for idx, img in enumerate(mat.texture_paint_images):
            if img.name == original_image.image.name:
                mat.paint_active_slot = idx
                print ("I have just set the " + img.name + " image, as a paint image, that corresponds to the index: "+ str(idx))
            if img.name == clone_image.image.name:
                mat.paint_clone_slot = idx
                print ("I have just set the " + img.name + " image, as a paint image, that corresponds to the index: "+ str(idx))

def is_windows():
    if platform.system == 'Windows':
        is_win =True
    else:
        is_win =False
    return is_win

def cycles2bi():
    for ob in bpy.context.selected_objects:
        bpy.ops.object.select_all(action='DESELECT')
        ob.select = True
        bpy.context.scene.objects.active = ob
        for matslot in ob.material_slots:
            mat = matslot.material
            node_original = node_retriever(mat,"original")
#            print(node_original.image.name)
#            print(mat.texture_slots[0].texture.image.name)
            mat.texture_slots[0].texture.image = node_original.image
            
def select_a_mesh(layout):
    row = layout.row()
    row.label(text="Select a mesh to start")

def select_a_node(mat, type):
    nodes = mat.node_tree.nodes
    for node in nodes:
        if node.name == type:
            node.select = True
            nodes.active = node
            is_node = True
            pass
        else:
            is_node = False
    return is_node

# potenzialmente una migliore scrittura del codice:
# nodes = material_slot.material.node_tree.nodes
# texture_node = nodes.get('Image Texture')
# if texture_node is None:

def bake_tex_set(type):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    tot_time = 0
    ob_counter = 1
    scene.cycles.samples = 1
    scene.cycles.max_bounces = 1
    scene.cycles.bake_type = 'DIFFUSE'
    scene.render.bake.use_pass_color = True
    scene.render.bake.use_pass_direct = False
    scene.render.bake.use_pass_indirect = False
    scene.render.bake.use_selected_to_active = False
    scene.render.bake.use_cage = True
    scene.render.bake.cage_extrusion = 0.1
    scene.render.bake.use_clear = True
    start_time = time.time()
    if type == "source":
        if len(bpy.context.selected_objects) > 1:
            ob = scene.objects.active
            print('checking presence of a destination texture set..')
            for matslot in ob.material_slots:
                mat = matslot.material
                select_a_node(mat,"source_paint_node")
            print('start baking..')
            bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_selected_to_active=True, use_clear=True, save_mode='INTERNAL')
        else:
            raise Exception("Select two meshes in order to transfer a clone layer")
            return
        tot_time += (time.time() - start_time)
    if type == "cc":
        tot_selected_ob = len(bpy.context.selected_objects)
        for ob in bpy.context.selected_objects:
            print('start baking "'+ob.name+'" (object '+str(ob_counter)+'/'+str(tot_selected_ob)+')')
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True
            bpy.context.scene.objects.active = ob
            for matslot in ob.material_slots:
                mat = matslot.material
                select_a_node(mat,"cc_image")
#                is_node = select_a_node(mat,"cc_image")
#                if is_node == False:
#                    print("The material " + mat.name +" lacks a cc_image node. I'm creating it..")
#                    create_new_tex_set(mat, "cc_image")
            bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_selected_to_active=False, use_clear=True, save_mode='INTERNAL')
            tot_time += (time.time() - start_time)
            print("--- %s seconds ---" % (time.time() - start_time))
            ob_counter += 1
    print("--- JOB complete in %s seconds ---" % tot_time)

def remove_ori_image(mat):
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    orimagenode = node_retriever(mat, "original")
    newimagenode = node_retriever(mat, "cc_image")
    nodes.remove(orimagenode)
    if newimagenode is not None:
        newimagenode.name = "original"
        newimagenode.location = (-1100, -50)

def set_texset(mat, type):
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    imagenode = node_retriever(mat, type)
    diffusenode = node_retriever(mat, "diffuse")
    links.new(imagenode.outputs[0], diffusenode.inputs[0])

def substring_after(s, delim):
    return s.partition(delim)[2]

def create_new_tex_set(mat, type):
    #retrieve image specs and position from material
    o_image = mat.texture_slots[0].texture.image
    x_image = mat.texture_slots[0].texture.image.size[0]
    y_image = mat.texture_slots[0].texture.image.size[1]
    o_imagepath = mat.texture_slots[0].texture.image.filepath
    o_imagepath_abs = bpy.path.abspath(o_imagepath)
    o_imagedir, o_filename = os.path.split(o_imagepath_abs)
    o_filename_no_ext = os.path.splitext(o_filename)[0]

    nodes = mat.node_tree.nodes
    node_tree = bpy.data.materials[mat.name].node_tree
    if type == "cc_image":
        if o_filename_no_ext.startswith("cc_"):
            print(substring_after(o_filename, "cc_"))
            t_image_name = "cc_2_"+o_filename_no_ext
        else:
            t_image_name = "cc_"+o_filename_no_ext
            print(substring_after(o_filename, "cc_"))
    if type == "source_paint_node":
        t_image_name = "sp_"+o_filename_no_ext
    
    t_image = bpy.data.images.new(name=t_image_name, width=x_image, height=y_image, alpha=False)
    
    # set path to new image
    fn = os.path.join(o_imagedir, t_image_name)
    t_image.filepath_raw = fn+".png"
    t_image.file_format = 'PNG'

    tteximg = nodes.new('ShaderNodeTexImage')
    tteximg.location = (-1100, -450)
    tteximg.image = t_image
    tteximg.name = type 

    for currnode in nodes:
        currnode.select = False

    # node_tree.nodes.select_all(action='DESELECT')
    tteximg.select = True
    node_tree.nodes.active = tteximg
    mat.texture_slots[0].texture.image = t_image

# provide to thsi function a material and a node type and it will send you back the name of the node. With the option "all" you will get a dictionary of the nodes
def node_retriever(mat, type):
    mat_nodes = mat.node_tree.nodes
    list_all_node_type = {}
    cc_node = "cc_node"
    cc_image = "cc_image"
    original = "original"
    source_paint_node = "source_paint_node"
    diffuse = "diffuse"
    list_all_node_type[cc_node] = None
    list_all_node_type[cc_image] = None
    list_all_node_type[original] = None
    list_all_node_type[source_paint_node] = None
    list_all_node_type[diffuse] = None
    node = None 

    if type == "all":
        for node_type in list_all_node_type:
            for node in mat_nodes:
                if node.name == node_type:
                    list_all_node_type[node_type] = node
        #print(list_all_node_type)
        return dict2list(list_all_node_type)
    else:
        for node in mat_nodes:
            if node.name == type:
                #print('Il nodo tipo trovato è :'+ node.name)
                list_all_node_type[type] = node
                return node
                pass
        print("non ho trovato nulla")
        node = False
        return node 
               
# for cycles material

def dict2list(dict):
    list=[]
    for i,j in dict.items():
        list.append(j)
#    print (list)
    return list

def create_correction_nodegroup(name):

    # create a group
#    active_object_name = bpy.context.scene.objects.active.name
    test_group = bpy.data.node_groups.new(name, 'ShaderNodeTree')
#    test_group.label = label

    # create group inputs
    group_inputs = test_group.nodes.new('NodeGroupInput')
    group_inputs.location = (-750,0)
    test_group.inputs.new('NodeSocketColor','tex')

    # create group outputs
    group_outputs = test_group.nodes.new('NodeGroupOutput')
    group_outputs.location = (300,0)
    test_group.outputs.new('NodeSocketColor','cortex')

    # create three math nodes in a group
    bricon = test_group.nodes.new('ShaderNodeBrightContrast')
    bricon.location = (-220, -100)
    bricon.label = 'bricon'

    sathue = test_group.nodes.new('ShaderNodeHueSaturation')
    sathue.location = (0, -100)
    sathue.label = 'sathue'

    RGBcurve = test_group.nodes.new('ShaderNodeRGBCurve')
    RGBcurve.location = (-500, -100)
    RGBcurve.label = 'RGBcurve'

    # link nodes together
    test_group.links.new(sathue.inputs[4], bricon.outputs[0])
    test_group.links.new(bricon.inputs[0], RGBcurve.outputs[0])

    # link inputs
    test_group.links.new(group_inputs.outputs['tex'], RGBcurve.inputs[1])

    #link output
    test_group.links.new(sathue.outputs[0], group_outputs.inputs['cortex'])

def bi2cycles():
    
    for obj in bpy.context.selected_objects:
        active_object_name = bpy.context.scene.objects.active.name
            
        for matslot in obj.material_slots:
            mat = matslot.material
            image = mat.texture_slots[0].texture.image
            mat.use_nodes = True
            mat.node_tree.nodes.clear()
            links = mat.node_tree.links
            nodes = mat.node_tree.nodes
            output = nodes.new('ShaderNodeOutputMaterial')
            output.location = (0, 0)
            mainNode = nodes.new('ShaderNodeBsdfDiffuse')
            mainNode.location = (-400, -50)
            mainNode.name = "diffuse"
            teximg = nodes.new('ShaderNodeTexImage')
            teximg.location = (-1100, -50)
            teximg.image = image
            teximg.name = "original"
#            colcor = nodes.new(type="ShaderNodeGroup")
#            colcor.node_tree = (bpy.data.node_groups[active_object_name])
#            colcor.location = (-800, -50)
            links.new(teximg.outputs[0], mainNode.inputs[0])
#            links.new(colcor.outputs[0], )
            links.new(mainNode.outputs[0], output.inputs[0])
#            colcor.name = "colcornode"

def create_cc_node():#(ob,context):
    active_object_name = bpy.context.scene.objects.active.name
    create_correction_nodegroup(active_object_name)
    
    for obj in bpy.context.selected_objects:
        for matslot in obj.material_slots:
            mat = matslot.material
#            cc_image_node, cc_node, original_node, diffuse_node, source_paint_node = node_retriever(mat, "all")
            links = mat.node_tree.links
            nodes = mat.node_tree.nodes
            mainNode = node_retriever(mat, "diffuse")
            teximg = node_retriever(mat, "original")
            colcor = nodes.new(type="ShaderNodeGroup")
            colcor.node_tree = (bpy.data.node_groups[active_object_name])
            colcor.location = (-800, -50)
            colcor.name = "cc_node"
            links.new(teximg.outputs[0], colcor.inputs[0])
            links.new(colcor.outputs[0], mainNode.inputs[0])

def remove_node(mat, node_to_remove):
    node = node_retriever(mat, node_to_remove)
    if node is not None:
#        links = mat.node_tree.links
#        previous_node = cc_node.inputs[0].links[0].from_node
#        following_node = cc_node.outputs[0].links[0].to_node
#        links.new(previous_node.outputs[0], following_node.inputs[0])
        mat.node_tree.nodes.remove(node)
#    else:
#        print("There is not a color correction node in this material")

# for quick utils____________________________________________
def make_group(ob,context):
    nomeoggetto = str(ob.name)
    if bpy.data.groups.get(nomeoggetto) is not None:
        currentgroup = bpy.data.groups.get(nomeoggetto)
        bpy.ops.group.objects_remove_all()
#        for object in currentgroup.objects:
#            bpy.ops.group.objects_remove(group=currentgroup)
    else:
        bpy.ops.group.create(name=nomeoggetto)
    ob.select = True
    bpy.ops.object.group_link(group=nomeoggetto)


def getnextobjname(name):
#    print("prendo in carico l'oggetto: "+name)
    #lst = ['this','is','just','a','test']
#    if fnmatch.filter(name, '.0*'):
    if name.endswith(".001") or name.endswith(".002") or name.endswith(".003") or name.endswith(".004") or name.endswith(".005"):
        current_nonumber = name[:-3]
#        print("ho ridotto il nome a :"+current_nonumber)
        current_n_integer = int(name[-3:])
#        print("aggiungo un numero")
        current_n_integer +=1
#        print(current_n_integer)
        if current_n_integer > 9:
            nextname = current_nonumber+'0'+str(current_n_integer)
        else:
            nextname = current_nonumber+'00'+str(current_n_integer)
    else:
        nextname = name+'.001'
#    print(nextname)
    return nextname

def newimage2selpoly(ob, nametex):
#    objectname = ob.name
    print("I'm creating texture: T_"+nametex+".png")
    me = ob.data
    tempimage = bpy.data.images.new(name=nametex, width=4096, height=4096, alpha=False)
    tempimage.filepath_raw = "//T_"+nametex+".png"
    tempimage.file_format = 'PNG'
    for uv_face in me.uv_textures.active.data:
        uv_face.image = tempimage
    return

def clean_name(name):
    if name.endswith(".001") or name.endswith(".002") or name.endswith(".003") or name.endswith(".004") or name.endswith(".005")or name.endswith(".006")or name.endswith(".007")or name.endswith(".008")or name.endswith(".009"):
        cname = name[:-4]
    else:
        cname = name
    return cname

def areamesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    area = sum(f.calc_area() for f in bm.faces)
#    print(area)
    bm.free()
    return area

def desiredmatnumber(ob):
    area = areamesh(ob)
    if area > 21:
        if area <103:
            desmatnumber = 6
            if area < 86:
                desmatnumber = 5
                if area < 68:
                    desmatnumber = 4
                    if area < 52:
                        desmatnumber = 3
                        if area < 37:
                            desmatnumber = 2
        else:
            desmatnumber = 6
            print("Be carefull ! the mesh is "+str(area)+" square meters is too big, consider to reduce it under 100. I will use six 4096 texture to describe it.")

    else:
        desmatnumber = 1

    return desmatnumber