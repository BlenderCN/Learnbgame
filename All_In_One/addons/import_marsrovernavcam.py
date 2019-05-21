import bpy
import os
import subprocess
import sys
import math
import mathutils
from mathutils import Vector, Quaternion
import struct
import bmesh
from urllib import request
import time
import re
from datetime import datetime


bl_info = {
    "name": "Mars Rover NAVCAM Import",
    "author": "Rob Haarsma (rob@captainvideo.nl)",
    "version": (0, 2, 0),
    "blender": (2, 80, 0),
    "location": "File > Import > ...  and/or 3D Window Tools menu > Mars Rover NAVCAM Import",
    "description": "Creates Martian landscapes from Mars Rover Navcam images",
    "warning": "This script produces high poly meshes and saves downloaded data in Temp directory",
    "wiki_url": "https://github.com/phaseIV/Blender-Navcam-Importer",
    "tracker_url": "https://github.com/phaseIV/Blender-Navcam-Importer/issues",
    "category": "Learnbgame",
    }


pdsimg_path = 'https://pdsimg.jpl.nasa.gov/data/'
nasaimg_path = 'https://mars.nasa.gov/'

roverDataDir = []
roverImageDir = []
local_data_dir = []
local_file = []

popup_error = None
curve_minval = None
curve_maxval = None


class NavcamDialogOperator(bpy.types.Operator):
    bl_idname = "io.navcamdialog_operator"
    bl_label = "Enter Rover Navcam image ID"

    navcam_string: bpy.props.StringProperty(name="Image Name", default='')
    fillhole_bool: bpy.props.BoolProperty(name="Fill Gaps (draft)", default = True)
    #filllength_float: bpy.props.FloatProperty(name="Max Fill Length", min=0.001, max=100.0, default=0.6)
    radimage_bool: bpy.props.BoolProperty(name="Use 16bit RAD texture", default = False)
        
    def execute(self, context):
        ReadNavcamString(self.navcam_string, self.fillhole_bool, self.radimage_bool)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=550)


def ReadNavcamString(inString, inFillBool, inRadBool):
    global local_data_dir, roverDataDir, roverImageDir, popup_error, curve_minval, curve_maxval

    if inString=="": return
    
    time_start = time.time()
    
    SetRenderSettings()
    local_data_dir = os.path.join(bpy.context.preferences.filepaths.temporary_directory, 'MarsRoverImages/')

    collString = inString.split(",")
    for i in range(0, len(collString)):
        if(len(collString[i]) == 0): collString.pop(i)
    
    for i in range(0, len(collString)):
        theString = os.path.splitext(collString[i].strip( ' ' ))[0]

        if len(theString) == 27 or len(theString) == 36:
            pass
        else:
            popup_error = 3
            bpy.context.window_manager.popup_menu(draw, title="Name Error", icon='ERROR')
            return

        rover = None
   
        if theString.startswith( 'N' ):
            rover = 3
        if theString.startswith( '2N' ):
            rover = 1
        if theString.startswith( '1N' ):
            rover = 2
        
        if rover == None:
            popup_error = 4
            bpy.context.window_manager.popup_menu(draw, title="Name Error", icon='ERROR')
            return

        sol_ref = tosol(rover, theString)

        if rover == 1:
            roverDataDir = 'mer/mer2no_0xxx/data/'
            roverImageDir = 'mer/gallery/all/2/n/'
        if rover == 2:
            roverDataDir = 'mer/mer1no_0xxx/data/'
            roverImageDir = 'mer/gallery/all/1/n/'
        if rover == 3:
            if sol_ref < 1870:
                roverDataDir = 'msl/MSLNAV_1XXX/DATA_V1/'
                roverImageDir = 'msl/MSLNAV_1XXX/EXTRAS_V1/FULL/'
            else:
                roverDataDir = 'msl/MSLNAV_1XXX/DATA/'
                roverImageDir = 'msl/MSLNAV_1XXX/EXTRAS/FULL/'

        print( '\nConstructing mesh %d/%d, sol %d, name %s' %( i + 1, len(collString), sol_ref, theString) )
        
        curve_minval = 0.0
        curve_maxval = 1.0

        if inRadBool:
            image_16bit_texture_filename = get_16bit_texture_image(rover, sol_ref, theString)
            image_texture_filename = convert_to_png(image_16bit_texture_filename)
        else:
            image_texture_filename = get_texture_image(rover, sol_ref, theString)

        if (image_texture_filename == None):
            popup_error = 1
            bpy.context.window_manager.popup_menu(draw, title="URL Error", icon='ERROR')
            return

        image_depth_filename = get_depth_image(rover, sol_ref, theString)
        if (image_depth_filename == None):
            popup_error = 2
            bpy.context.window_manager.popup_menu(draw, title="URL Error", icon='ERROR')
            return

        create_mesh_from_depthimage(rover, sol_ref, image_depth_filename, image_texture_filename, inFillBool, inRadBool)
    
    elapsed = float(time.time() - time_start)
    print("Script execution time: %s" % time.strftime('%H:%M:%S', time.gmtime(elapsed))) 

        
def SetRenderSettings():
    rnd = bpy.data.scenes[0].render  
    rnd.resolution_x = 1024
    rnd.resolution_y = 1024
    rnd.resolution_percentage = 100
    rnd.tile_x = 512
    rnd.tile_y = 512
    wrld = bpy.context.scene.world
    nt = bpy.data.worlds[wrld.name].node_tree
    backNode = nt.nodes['Background']
    backNode.inputs[0].default_value = (0.02, 0.02, 0.02, 1)


def download_file(url):
    global localfile
    proper_url = url.replace('\\','/')
    
    if sys.platform == 'darwin':
        try:
            out = subprocess.check_output(['curl', '-I', proper_url])

            if out.decode().find('200 OK') > 0:
                subprocess.call(['curl', '-o', localfile, '-L', proper_url])
                return True
            else:
                print('Fail to reach a server.\n\n{}'.format(out.decode()))
                return False

        except subprocess.CalledProcessError as e:
            print('Subprocess failed:\nReturncode: {}\n\nOutput:{}'.format(e.returncode, e.output))
            return False
                  
    else:
        try:
            page = request.urlopen(proper_url)

            if page.getcode() is not 200:
                return False

            request.urlretrieve(proper_url, localfile)
            return True

        except:
            return False


def tosol(rover, nameID):
    # origin: https://github.com/natronics/MSL-Feed/blob/master/nasa.py
    # function hacked to return sol from image filename   
    craft_time = None
    
    if rover == 3:
        craft_time = nameID[4:13]
    if rover == 2 or rover == 1:
        craft_time = nameID[2:11]
    
    s = int(craft_time)
    MSD = (s/88775.244) + 44795.9998

    sol = MSD - 49269.2432411704
    sol = sol + 1  # for sol 0
    sol = int(math.ceil(sol))
    
    deviate = None
    
    if rover == 3:
        deviate = -6
    if rover == 2:
        deviate = 3028
    if rover == 1:
        deviate = 3048
    
    return sol+deviate


def get_texture_image(rover, sol, imgname):
    global roverImageDir, local_data_dir, localfile
    
    if rover == 3:
        if sol > 450:
            texname = '%s.PNG' %( imgname )
        else:
            texname = '%s.JPG' %( imgname )
    else:
        texname = '%s.JPG' %( imgname )
    
    s = list( texname )
    
    if rover == 3:
        s[13] = 'R'
        s[14] = 'A'
        s[15] = 'S'
        s[35] = '1'
    else:
        if s[18] == 'F' or s[18] == 'f':
            #mer downsampled??
            s[11] = 'e'
            s[12] = 'd'
            s[13] = 'n'
            s[25] = 'm'
        else:
            s[11] = 'e'
            s[12] = 'f'
            s[13] = 'f'
            s[25] = 'm'

    imagename = '%s' % "".join(s)
    imgfilename = os.path.join(local_data_dir, roverImageDir, '%05d' %(sol), imagename )

    if os.path.isfile(imgfilename):
        print('tex from cache: ', imgfilename)
        return imgfilename
    
    retrievedir = os.path.join(os.path.dirname(local_data_dir), roverImageDir, '%05d' %( sol ) )
    if not os.path.exists(retrievedir):
        os.makedirs(retrievedir)

    localfile = imgfilename
    
    if rover == 2 or rover == 1:
         remotefile = os.path.join(os.path.dirname(nasaimg_path), roverImageDir, '%03d' %(sol), imagename.upper() )
    if rover == 3:
        remotefile = os.path.join(os.path.dirname(pdsimg_path), roverImageDir, 'SOL%05d' %(sol), imagename )
    
    print('downloading tex: ', remotefile)
    
    result = download_file(remotefile)
    if(result == False):
        return None
        
    if os.path.isfile(localfile):
        return imgfilename


def get_16bit_texture_image(rover, sol, imgname):
    global roverImageDir, local_data_dir, localfile
    
    texname = '%s.IMG' %( imgname )
    s = list( texname )
    
    if rover == 3:
        s[13] = 'R'
        s[14] = 'A'
        s[15] = 'D'
        s[35] = '1'
    else:
        s[11] = 'm'
        s[12] = 'r'
        s[13] = 'd'
        s[25] = 'm'
    
    imagename = '%s' % "".join(s)
    imgfilename = os.path.join(local_data_dir, roverDataDir, 'sol%05d' %(sol), imagename )
    
    if os.path.isfile(imgfilename):
        print('rad from cache: ', imgfilename)
        return imgfilename
    
    retrievedir = os.path.join(os.path.dirname(local_data_dir), roverDataDir, 'sol%05d' %( sol ) )
    if not os.path.exists(retrievedir):
        os.makedirs(retrievedir)
    
    localfile = imgfilename
    
    if rover == 2 or rover == 1:
        remotefile = os.path.join(os.path.dirname(pdsimg_path), roverDataDir, 'sol%04d' %(sol), 'rdr', imagename.lower() )
    if rover == 3:
        remotefile = os.path.join(os.path.dirname(pdsimg_path), roverDataDir, 'SOL%05d' %(sol), imagename )
    
    print('downloading rad: ', remotefile)
    
    result = download_file(remotefile)
    if(result == False):
        return None
    
    if os.path.isfile(localfile):
        return imgfilename


def get_depth_image(rover, sol, imgname):
    global roverDataDir, local_data_dir, localfile

    xyzname = '%s.IMG' %( imgname )
    s = list( xyzname )
    
    if rover == 3:
        s[13] = 'X'
        s[14] = 'Y'
        s[15] = 'Z'
        s[35] = '1'
    else :
        s[11] = 'x'
        s[12] = 'y'
        s[13] = 'l'
        s[25] = 'm'
    
    xyzname = '%s' % "".join(s)
    xyzfilename = os.path.join(local_data_dir, roverDataDir, 'sol%05d' %(sol), xyzname )

    if os.path.isfile(xyzfilename):
        print('xyz from cache: ', xyzfilename)
        return xyzfilename
    
    retrievedir = os.path.join(local_data_dir, roverDataDir, 'sol%05d' %(sol) )
    if not os.path.exists(retrievedir):
        os.makedirs(retrievedir)

    localfile = xyzfilename
    
    if rover == 2 or rover == 1:
        remotefile = os.path.join(os.path.dirname(pdsimg_path), roverDataDir, 'sol%04d' %(sol), 'rdr', xyzname.lower() )
    if rover == 3:
        remotefile = os.path.join(os.path.dirname(pdsimg_path), roverDataDir, 'SOL%05d' %(sol), xyzname )

    print('downloading xyz: ', remotefile)

    result = download_file(remotefile)
    if(result == False):
        return None
    
    if os.path.isfile(localfile):
        return xyzfilename


def convert_to_png(image_16bit_texture_filename):
    global curve_minval, curve_maxval
    
    LINES = LINE_SAMPLES = SAMPLE_BITS = BYTES = 0
    SAMPLE_TYPE = ""
    
    FileAndPath = image_16bit_texture_filename
    FileAndExt = os.path.splitext(FileAndPath)
    
    print('creating png...')
    
    # Open the img file (ascii label part)
    try:
        if FileAndExt[1].isupper():
            f = open(FileAndExt[0] + ".IMG", 'r')
        else:
            f = open(FileAndExt[0] + ".img", 'r')
    except:
        return
    
    block = ""
    OFFSET = 0
    for line in f:
        if line.strip() == "END":
            break
        tmp = line.split("=")
        if tmp[0].strip() == "OBJECT" and tmp[1].strip() == "IMAGE":
            block = "IMAGE"
        elif tmp[0].strip() == "END_OBJECT" and tmp[1].strip() == "IMAGE":
            block = ""
        if tmp[0].strip() == "OBJECT" and tmp[1].strip() == "IMAGE_HEADER":
            block = "IMAGE_HEADER"
        elif tmp[0].strip() == "END_OBJECT" and tmp[1].strip() == "IMAGE_HEADER":
            block = ""
        
        if block == "IMAGE":
            if line.find("LINES") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                LINES = int(tmp[1].strip())
            elif line.find("LINE_SAMPLES") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                LINE_SAMPLES = int(tmp[1].strip())
            elif line.find("SAMPLE_TYPE") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                SAMPLE_TYPE = tmp[1].strip()
            elif line.find("SAMPLE_BITS") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                SAMPLE_BITS = int(tmp[1].strip())
        
        if block == "IMAGE_HEADER":
            if line.find("BYTES") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                BYTES = int(tmp[1].strip())
    
    f.close
    
    # Open the img file (binary data part)
    try:
        if FileAndExt[1].isupper():
            f2 = open(FileAndExt[0] + ".IMG", 'rb')
        else:
            f2 = open(FileAndExt[0] + ".img", 'rb')
    except:
        return
    
    edit = f2.read()
    meh = edit.find(b'LBLSIZE')
    f2.seek( meh + BYTES)
    
    bands = []
    for bandnum in range(0, 1):
        
        bands.append([])
        for linenum in range(0, LINES):
            
            bands[bandnum].append([])
            for pixnum in range(0, LINE_SAMPLES):
                
                dataitem = f2.read(2)
                if (dataitem == ""):
                    print ('ERROR, Ran out of data to read before we should have')
                
                bands[bandnum][linenum].append(struct.unpack(">H", dataitem)[0])
    
    f2.close
    
    pixels = [None] * LINES * LINE_SAMPLES
        
    curve_minval = 1.0
    curve_maxval = 0.0

    for j in range(0, LINES):
        for k in range(0, LINE_SAMPLES):
            
            r = g = b = float(bands[0][LINES-1 - j][k] & 0xffff )  / (32768*2)
            a = 1.0
            pixels[(j * LINES) + k] = [r, g, b, a]
            
            if r > curve_maxval: curve_maxval = r
            if r < curve_minval: curve_minval = r
    
    del bands
    
    pixels = [chan for px in pixels for chan in px]
    pngname = FileAndExt[0] + '.PNG'
    
    # modify scene for png export
    scene = bpy.data.scenes[0]
    settings = scene.render.image_settings
    settings.color_depth = '16'
    settings.color_mode = 'BW'
    settings.file_format = 'PNG'
    
    image = bpy.data.images.new(os.path.basename(FileAndExt[0]), LINES, LINE_SAMPLES, float_buffer=True)
    image.pixels = pixels
    image.file_format = 'PNG'
    image.save_render(pngname)
    
    settings.color_depth = '8'
    settings.color_mode = 'RGBA'
    
    # remove converted image from Blender, it will be reloaded
    bpy.data.images.remove(image)
    del pixels
    
    return pngname


# -----------------------------------------------------------------------------
# Cycles/Eevee routines adapted from: https://github.com/florianfelix/io_import_images_as_planes_rewrite

def get_input_nodes(node, links):
    """Get nodes that are a inputs to the given node"""
    # Get all links going to node.
    input_links = {lnk for lnk in links if lnk.to_node == node}
    # Sort those links, get their input nodes (and avoid doubles!).
    sorted_nodes = []
    done_nodes = set()
    for socket in node.inputs:
        done_links = set()
        for link in input_links:
            nd = link.from_node
            if nd in done_nodes:
                # Node already treated!
                done_links.add(link)
            elif link.to_socket == socket:
                sorted_nodes.append(nd)
                done_links.add(link)
                done_nodes.add(nd)
        input_links -= done_links
    return sorted_nodes


def auto_align_nodes(node_tree):
    """Given a shader node tree, arrange nodes neatly relative to the output node."""
    x_gap = 300
    y_gap = 180
    nodes = node_tree.nodes
    links = node_tree.links
    output_node = None
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL' or node.type == 'GROUP_OUTPUT':
            output_node = node
            break

    else:  # Just in case there is no output
        return

    def align(to_node):
        from_nodes = get_input_nodes(to_node, links)
        for i, node in enumerate(from_nodes):
            node.location.x = min(node.location.x, to_node.location.x - x_gap)
            node.location.y = to_node.location.y
            node.location.y -= i * y_gap
            node.location.y += (len(from_nodes) - 1) * y_gap / (len(from_nodes))
            align(node)

    align(output_node)


def clean_node_tree(node_tree):
    """Clear all nodes in a shader node tree except the output. Returns the output node"""
    nodes = node_tree.nodes
    for node in list(nodes):  # copy to avoid altering the loop's data source
        if not node.type == 'OUTPUT_MATERIAL':
            nodes.remove(node)

    return node_tree.nodes[0]


def get_shadeless_node(dest_node_tree):
    """Return a "shadless" cycles/eevee node, creating a node group if nonexistent"""
    try:
        node_tree = bpy.data.node_groups['NAV_SHADELESS']

    except KeyError:
        # need to build node shadeless node group
        node_tree = bpy.data.node_groups.new('NAV_SHADELESS', 'ShaderNodeTree')
        output_node = node_tree.nodes.new('NodeGroupOutput')
        input_node = node_tree.nodes.new('NodeGroupInput')

        node_tree.outputs.new('NodeSocketShader', 'Shader')
        node_tree.inputs.new('NodeSocketColor', 'Color')

        # This could be faster as a transparent shader, but then no ambient occlusion
        diffuse_shader = node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        node_tree.links.new(diffuse_shader.inputs[0], input_node.outputs[0])

        emission_shader = node_tree.nodes.new('ShaderNodeEmission')
        node_tree.links.new(emission_shader.inputs[0], input_node.outputs[0])

        light_path = node_tree.nodes.new('ShaderNodeLightPath')
        is_glossy_ray = light_path.outputs['Is Glossy Ray']
        is_shadow_ray = light_path.outputs['Is Shadow Ray']
        ray_depth = light_path.outputs['Ray Depth']
        transmission_depth = light_path.outputs['Transmission Depth']

        unrefracted_depth = node_tree.nodes.new('ShaderNodeMath')
        unrefracted_depth.operation = 'SUBTRACT'
        unrefracted_depth.label = 'Bounce Count'
        node_tree.links.new(unrefracted_depth.inputs[0], ray_depth)
        node_tree.links.new(unrefracted_depth.inputs[1], transmission_depth)

        refracted = node_tree.nodes.new('ShaderNodeMath')
        refracted.operation = 'SUBTRACT'
        refracted.label = 'Camera or Refracted'
        refracted.inputs[0].default_value = 1.0
        node_tree.links.new(refracted.inputs[1], unrefracted_depth.outputs[0])

        reflection_limit = node_tree.nodes.new('ShaderNodeMath')
        reflection_limit.operation = 'SUBTRACT'
        reflection_limit.label = 'Limit Reflections'
        reflection_limit.inputs[0].default_value = 2.0
        node_tree.links.new(reflection_limit.inputs[1], ray_depth)

        camera_reflected = node_tree.nodes.new('ShaderNodeMath')
        camera_reflected.operation = 'MULTIPLY'
        camera_reflected.label = 'Camera Ray to Glossy'
        node_tree.links.new(camera_reflected.inputs[0], reflection_limit.outputs[0])
        node_tree.links.new(camera_reflected.inputs[1], is_glossy_ray)

        shadow_or_reflect = node_tree.nodes.new('ShaderNodeMath')
        shadow_or_reflect.operation = 'MAXIMUM'
        shadow_or_reflect.label = 'Shadow or Reflection?'
        node_tree.links.new(shadow_or_reflect.inputs[0], camera_reflected.outputs[0])
        node_tree.links.new(shadow_or_reflect.inputs[1], is_shadow_ray)

        shadow_or_reflect_or_refract = node_tree.nodes.new('ShaderNodeMath')
        shadow_or_reflect_or_refract.operation = 'MAXIMUM'
        shadow_or_reflect_or_refract.label = 'Shadow, Reflect or Refract?'
        node_tree.links.new(shadow_or_reflect_or_refract.inputs[0], shadow_or_reflect.outputs[0])
        node_tree.links.new(shadow_or_reflect_or_refract.inputs[1], refracted.outputs[0])

        mix_shader = node_tree.nodes.new('ShaderNodeMixShader')
        node_tree.links.new(mix_shader.inputs[0], shadow_or_reflect_or_refract.outputs[0])
        node_tree.links.new(mix_shader.inputs[1], diffuse_shader.outputs[0])
        node_tree.links.new(mix_shader.inputs[2], emission_shader.outputs[0])

        node_tree.links.new(output_node.inputs[0], mix_shader.outputs[0])

        auto_align_nodes(node_tree)

    group_node = dest_node_tree.nodes.new("ShaderNodeGroup")
    group_node.node_tree = node_tree

    return group_node


def create_cycles_texnode(context, node_tree, image):
    tex_image = node_tree.nodes.new('ShaderNodeTexImage')
    tex_image.image = image
    tex_image.show_texture = True
    image_user = tex_image.image_user
    tex_image.extension = 'CLIP'  # Default of "Repeat" can cause artifacts
    return tex_image


def create_cycles_material(context, image):
    global curve_minval, curve_maxval

    name_compat = bpy.path.display_name_from_filepath(image.filepath)
    material = None
    if not material:
        material = bpy.data.materials.new(name=name_compat)

    material.use_nodes = True
    node_tree = material.node_tree
    out_node = clean_node_tree(node_tree)

    tex_image = create_cycles_texnode(context, node_tree, image)

    core_shader = get_shadeless_node(node_tree)
     
    curvenode = node_tree.nodes.new('ShaderNodeRGBCurve')
    curvenode.mapping.curves[3].points[0].location.x = curve_minval
    curvenode.mapping.curves[3].points[0].location.y = 0.0
    curvenode.mapping.curves[3].points[1].location.x = curve_maxval
    curvenode.mapping.curves[3].points[1].location.y = 1.0
    curvenode.mapping.update()

    # Connect color from texture to curves
    node_tree.links.new(curvenode.inputs[1], tex_image.outputs[0])
 
    #Connect color from curves to shadeless
    node_tree.links.new(core_shader.inputs[0], curvenode.outputs[0])
    node_tree.links.new(out_node.inputs[0], core_shader.outputs[0])

    auto_align_nodes(node_tree)
    return material


def create_named_material(context, name):
    name_compat = name
    material = None
    if not material:
        material = bpy.data.materials.new(name=name_compat)

    material.use_nodes = True
    node_tree = material.node_tree
    out_node = clean_node_tree(node_tree)

    core_shader = get_shadeless_node(node_tree)
    core_shader.inputs[0].default_value = (1, 1, 1, 1)

    # Connect color from texture
    node_tree.links.new(out_node.inputs[0], core_shader.outputs[0])

    auto_align_nodes(node_tree)
    return material

# -----------------------------------------------------------------------------


def find_collection(context, item):
    collections = item.users_collection
    if len(collections) > 0:
        return collections[0]
    return context.scene.collection


def get_collection(name):
    if bpy.data.collections.get(name) is None:
        new_collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(new_collection)
        return new_collection
    else:
        return bpy.data.collections.get(name)


def create_mesh_from_depthimage(rover, sol, image_depth_filename, image_texture_filename, do_fill, do_rad):
    # snippets used from:
    # https://svn.blender.org/svnroot/bf-extensions/contrib/py/scripts/addons/io_import_LRO_Lola_MGS_Mola_img.py
    # https://arsf-dan.nerc.ac.uk/trac/attachment/wiki/Processing/SyntheticDataset/data_handler.py

    global curve_minval, curve_maxval

    bRoverVec = Vector((0.0, 0.0, 0.0))

    if image_depth_filename == '':
        return
    
    creation_date = None
    LINES = LINE_SAMPLES = SAMPLE_BITS = 0
    SAMPLE_TYPE = ""
    
    FileAndPath = image_depth_filename
    FileAndExt = os.path.splitext(FileAndPath)
    
    print('creating mesh...')

    # Open the img label file (ascii label part)
    try:
        if FileAndExt[1].isupper():
            f = open(FileAndExt[0] + ".IMG", 'r')
        else:
            f = open(FileAndExt[0] + ".img", 'r')
    except:
        return

    block = ""
    OFFSET = 0
    for line in f:
        if line.strip() == "END":
            break
        tmp = line.split("=")
        if tmp[0].strip() == "OBJECT" and tmp[1].strip() == "IMAGE":
            block = "IMAGE"
        elif tmp[0].strip() == "END_OBJECT" and tmp[1].strip() == "IMAGE":
            block = ""
        if tmp[0].strip() == "OBJECT" and tmp[1].strip() == "IMAGE_HEADER":
            block = "IMAGE_HEADER"
        elif tmp[0].strip() == "END_OBJECT" and tmp[1].strip() == "IMAGE_HEADER":
            block = ""
        if tmp[0].strip() == "GROUP" and tmp[1].strip() == "ROVER_COORDINATE_SYSTEM":
            block = "ROVER_COORDINATE_SYSTEM"
        elif tmp[0].strip() == "END_GROUP" and tmp[1].strip() == "ROVER_COORDINATE_SYSTEM":
            block = ""
        
        elif tmp[0].strip() == "START_TIME":
            creation_date = str(tmp[1].strip())
        
        if block == "IMAGE":
            if line.find("LINES") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                LINES = int(tmp[1].strip())
            elif line.find("LINE_SAMPLES") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                LINE_SAMPLES = int(tmp[1].strip())
            elif line.find("SAMPLE_TYPE") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                SAMPLE_TYPE = tmp[1].strip()
            elif line.find("SAMPLE_BITS") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                SAMPLE_BITS = int(tmp[1].strip())

        if block == "IMAGE_HEADER":
            if line.find("BYTES") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                BYTES = int(tmp[1].strip())

        if block == "ROVER_COORDINATE_SYSTEM":
            if line.find("ORIGIN_OFFSET_VECTOR") != -1 and not(line.startswith("/*")):
                tmp = line.split("=")
                ORIGIN_OFFSET_VECTOR = str(tmp[1].strip())
                
                fline = re.sub('[(!@#$)]', '', ORIGIN_OFFSET_VECTOR)
                pf = fline.strip().split(",")
                
                bRoverVec[:] = float(pf[1]), float(pf[0]), -float(pf[2])

    f.close

    # Open the img label file (binary data part)
    try:
        if FileAndExt[1].isupper():
            f2 = open(FileAndExt[0] + ".IMG", 'rb')
        else:
            f2 = open(FileAndExt[0] + ".img", 'rb')
    except:
        return
            
    edit = f2.read()
    meh = edit.find(b'LBLSIZE')
    f2.seek( meh + BYTES)

    # Create a list of bands containing an empty list for each band
    bands = []
    
    # Read data for each band at a time
    for bandnum in range(0, 3):
        bands.append([])
        
        for linenum in range(0, LINES):
            
            bands[bandnum].append([])
            
            for pixnum in range(0, LINE_SAMPLES):
            
                # Read one data item (pixel) from the data file.
                dataitem = f2.read(4)
                
                if (dataitem == ""):
                    print ('ERROR, Ran out of data to read before we should have')
                
                # If everything worked, unpack the binary value and store it in the appropriate pixel value
                bands[bandnum][linenum].append(struct.unpack('>f', dataitem)[0])

    f2.close
    
    Vertex = []
    Faces = []

    nulvec = Vector((0.0,0.0,0.0))

    for j in range(0, LINES):
        for k in range(0, LINE_SAMPLES):
            vec = Vector((float(bands[1][j][k]), float(bands[0][j][k]), float(-bands[2][j][k])))
            vec = vec*0.1
            Vertex.append(vec)
            
    del bands
    
    #simple dehole (bridge)
    #max_fill_length = fill_length
    max_fill_length = 0.6
    if(do_fill):       
        for j in range(0, LINES-1):
            for k in range(0, LINE_SAMPLES-1):
                if Vertex[j * LINE_SAMPLES + k] != nulvec:
                    m = 1
                    while Vertex[(j + m) * LINE_SAMPLES + k] == nulvec and (j + m) < LINES-1:
                        m = m + 1
                    
                    if m != 1 and Vertex[(j + m) * LINE_SAMPLES + k] != nulvec:
                        VertexA = Vertex[j * LINE_SAMPLES + k]
                        VertexB = Vertex[(j + m) * LINE_SAMPLES + k]
                        sparevec = VertexB - VertexA
                        if sparevec.length < max_fill_length:
                            for n in range(0, m):
                                Vertex[(j + n) * LINE_SAMPLES + k] = VertexA + (sparevec / m) * n

    for j in range(0, LINES-1):
        for k in range(0, LINE_SAMPLES-1):
            Faces.append(( (j * LINE_SAMPLES + k), (j * LINE_SAMPLES + k + 1), ((j + 1) * LINE_SAMPLES + k + 1), ((j + 1) * LINE_SAMPLES + k) ))
            
    os.path.basename(FileAndExt[0])
    TARGET_NAME = '%s-%s' %(sol, os.path.basename(FileAndExt[0]))
    mesh = bpy.data.meshes.new(TARGET_NAME)
    TARGET_NAME = mesh.name
    mesh.from_pydata(Vertex, [], Faces)

    del Vertex
    del Faces
    mesh.update()
    
    print('texturing mesh...')

    ob_new = bpy.data.objects.new(TARGET_NAME, mesh)
    ob_new.data = mesh

    theSolCollection = get_collection('Sol%s' %(sol))
    theSolCollection.objects.link(ob_new)
    ob_new.select_set(state=True)
    bpy.context.view_layer.objects.active = ob_new

    obj = bpy.context.object

    try:
        with open(image_texture_filename):
            img = bpy.data.images.load(image_texture_filename)
            img.pack(as_png=False)
            
            engine = bpy.context.scene.render.engine
            if engine in {'CYCLES', 'BLENDER_EEVEE', 'BLENDER_OPENGL'}:
                material = create_cycles_material(bpy.context, img)

            # add material to object
            obj.data.materials.append(material)

            me = obj.data
            me.show_double_sided = True
            bpy.ops.mesh.uv_texture_add()

    except IOError:
        print('Oh dear. Missing %s' %(image_texture_filename))
    
    uvteller = 0

    #per face !
    for j in range(0, LINES -1):
        for k in range(0, LINE_SAMPLES-1):
            tc1 = Vector(((1.0 / LINE_SAMPLES) * k, 1.0 - (1.0 / LINES) * j))
            tc2 = Vector(((1.0 / LINE_SAMPLES) * (k + 1), 1.0 - (1.0 / LINES) * j))
            tc3 = Vector(((1.0 / LINE_SAMPLES) * (k + 1), 1.0 - (1.0 / LINES) * (j + 1)))
            tc4 = Vector(((1.0 / LINE_SAMPLES) * k, 1.0 - (1.0 / LINES) * (j + 1)))
            
            bpy.data.objects[TARGET_NAME].data.uv_layers[0].data[uvteller].uv = tc1
            uvteller = uvteller + 1
            bpy.data.objects[TARGET_NAME].data.uv_layers[0].data[uvteller].uv = tc2
            uvteller = uvteller + 1
            bpy.data.objects[TARGET_NAME].data.uv_layers[0].data[uvteller].uv = tc3
            uvteller = uvteller + 1
            bpy.data.objects[TARGET_NAME].data.uv_layers[0].data[uvteller].uv = tc4
            uvteller = uvteller + 1

    # remove verts lacking xyz data
    bpy.ops.object.mode_set(mode='EDIT')
    mesh_ob = bpy.context.object
    me = mesh_ob.data
    bm = bmesh.from_edit_mesh(me)
    
    verts = [v for v in bm.verts if v.co[0] == 0.0 and v.co[1] == 0.0 and v.co[2] == 0.0]
    bmesh.ops.delete(bm, geom=verts, context="VERTS")
    bmesh.update_edit_mesh(me)

    # remove redundant verts
    bpy.ops.object.mode_set(mode='EDIT')
    mesh_ob = bpy.context.object
    me = mesh_ob.data
    bm = bmesh.from_edit_mesh(me)
    
    verts = [v for v in bm.verts if len(v.link_faces) == 0]
    bmesh.ops.delete(bm, geom=verts, context="VERTS")
    bmesh.update_edit_mesh(me)

    bpy.ops.object.editmode_toggle()
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    #mesh generation is done here, adding camera and text follows

    cam = bpy.data.cameras.new('Camera')
    cam.lens = 40
    cam.clip_start = 0.01
    cam_ob = bpy.data.objects.new('Cam-' + os.path.basename(FileAndExt[0]), cam)
    
    bRoverVec = bRoverVec * 0.1
    
    mat_loc = mathutils.Matrix.Translation(bRoverVec)
    mat_trans = mathutils.Matrix.Translation((0.0, 0.0, 0.15))
    
    cam_ob.matrix_world = mat_loc @ mat_trans    
        
    # Create Credit text
    trover = [ 'Spirit', 'Opportunity', 'Curiosity' ]

    if creation_date.startswith( '\"' ):
        date_object = datetime.strptime(creation_date[1:23], '%Y-%m-%dT%H:%M:%S.%f')
    else:
        date_object = datetime.strptime(creation_date[0:22], '%Y-%m-%dT%H:%M:%S.%f')

    # MSL provides Right Navcam Depth data
    s = list(os.path.basename(image_texture_filename))
    if rover == 2 or rover == 1:
        if s[23] == 'L' or s[23] == 'l':
            whichcam = 'Left'
        else:
            whichcam = 'Right'

    if rover == 3:
        if s[1]  == 'L' or s[1] == 'l':
            whichcam = 'Left'
        else:
            whichcam = 'Right'

    tagtext = trover[rover-1] + ' ' + whichcam +' Navcam Image at Sol ' + str(sol) + '\n' + str(date_object.strftime('%d %b %Y %H:%M:%S')) + ' UTC\nNASA / JPL-CALTECH / phaseIV'
    
    bpy.ops.object.text_add(enter_editmode=True, location = (-0.02, -0.0185, -0.05)) #location = (-0.018, -0.0185, -0.05))
    bpy.ops.font.delete(type='PREVIOUS_WORD')
    bpy.ops.font.text_insert(text=str(tagtext))
    bpy.ops.object.editmode_toggle()
    
    textSize = 0.001
    text_ob = bpy.context.view_layer.objects.active
    text_ob.scale = [textSize, textSize, textSize]

    tempColl = find_collection(bpy.context, text_ob)
    theSolCollection.objects.link(text_ob)
    tempColl.objects.unlink(text_ob)
    
    found = None
    
    for i in range(len(bpy.data.materials)) :
        if bpy.data.materials[i].name == 'White text':
            mat = bpy.data.materials[i]
            found = True
    if not found:
        mat = create_named_material(bpy.context, 'White text')
        
    text_ob.data.materials.append(mat)
    text_ob.parent = cam_ob
    
    objloc = Vector(mesh_ob.location)
    rovloc = Vector(bRoverVec)
    distvec = rovloc - objloc

    expoint = obj.matrix_world.to_translation()+Vector((0.0, 0.0, -0.04-distvec.length*0.1))
    look_at(cam_ob, expoint)
    
    theSolCollection.objects.link(cam_ob)
    bpy.context.scene.camera = cam_ob
    bpy.context.scene.update()

    print ('mesh generation complete.')


def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()

    direction = point - loc_camera

    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj_camera.rotation_euler = rot_quat.to_euler()


def draw(self, context):
    global popup_error
    
    if(popup_error == 1):
        self.layout.label(text="Unable to retrieve NAVCAM texture image.")
        print("Unable to retrieve NAVCAM texture image.")
    
    if(popup_error == 2):
        self.layout.label(text="Unable to retrieve NAVCAM depth image.")
        print("Unable to retrieve NAVCAM depth image.")

    if(popup_error == 3):
        self.layout.label(text="Navcam imagename has incorrect length.")
        print("Navcam imagename has incorrect length.")

    if(popup_error == 4):
        self.layout.label(text="Not a valid Left Navcam imagename.")
        print("Not a valid Left Navcam imagename.")


class NavcamToolsPanel(bpy.types.Panel):
    bl_label = "Mars Rover Import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("io.navcamdialog_operator")


def menu_func_import(self, context):
    self.layout.operator(NavcamDialogOperator.bl_idname, text="Mars Rover NAVCAM Import")


def register():
    bpy.utils.register_class(NavcamDialogOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(NavcamToolsPanel)


def unregister():
    bpy.utils.unregister_class(NavcamDialogOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(NavcamToolsPanel)


if __name__ == "__main__":
    register()
