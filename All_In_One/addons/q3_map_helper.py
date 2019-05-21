bl_info = {
    "name": "Q3 map helper",
    "description": "This plugin is able to automaticly import fbx files made with Noesis from Q3 based bsp files. It also tries to join meshes based on their lightmap id, if Noesis exported an .meshlmid file too. Then there is a q3 shader interpreter for the cycles rendering engine. After you are satisfied with the scene lighting, you can tell the plugin to prepair lightmap baking. You can simply start baking lightmaps from the cycles baking tab. It will try baking lightmaps for every selected object in the scene",
    "author": "SomaZ",
    "version": (0, 7, 8),
    "blender": (2, 79, 0),
    "location": "3D View > Q3 Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import bpy
import bmesh
import os.path
from math import radians
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       AddonPreferences,
                       )


# ------------------------------------------------------------------------
#    functions
# ------------------------------------------------------------------------
def update_preview_cube(self, context):
    addon_name = __name__.split('.')[0]
    prefs = context.user_preferences.addons[addon_name].preferences
    scene = context.scene
    q3_map_import_tool = scene.q3_map_import_tool
    base_path = prefs.base_path
    shader_path = prefs.shader_dir

    try:
        shader_cube = bpy.data.objects["ShaderPreviewCube"]
        mesh = shader_cube.data
    except:
        # Create an empty mesh and the object.
        mesh = bpy.data.meshes.new('ShaderPreviewCube')
        shader_cube = bpy.data.objects.new("ShaderPreviewCube", mesh)

        # Add the object into the scene.
        scene.objects.link(shader_cube)
        scene.objects.active = shader_cube
        shader_cube.select = True

        # Construct the bmesh cube and assign it to the blender mesh.
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=10.0)
        bm.to_mesh(mesh)
        bm.free()

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.uv.reset()
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = scene.objects["ShaderPreviewCube"].data
        mesh.uv_textures[0].name = "UVMap"

    for (index, mat) in enumerate(mesh.materials):
        if mat.name.lower().strip(" \t\r\n") == scene.q3_map_import_tool.shader.lower().strip(" \t\r\n"):
            mesh.polygons[0].material_index = index
            mesh.polygons[1].material_index = index
            mesh.polygons[2].material_index = index
            mesh.polygons[3].material_index = index
            mesh.polygons[4].material_index = index
            mesh.polygons[5].material_index = index
            break


def preview_shader(self, context):
    addon_name = __name__.split('.')[0]
    prefs = context.user_preferences.addons[addon_name].preferences
    scene = context.scene
    q3_map_import_tool = scene.q3_map_import_tool

    base_path = prefs.base_path
    shader_path = prefs.shader_dir

    try:
        shader_cube = bpy.data.objects["ShaderPreviewCube"]
        mesh = scene.objects["ShaderPreviewCube"].data
        mesh.materials.clear()
        mesh.uv_textures[0].name = "UVMap"
    except:
        # Create an empty mesh and the object.
        mesh = bpy.data.meshes.new('ShaderPreviewCube')
        shader_cube = bpy.data.objects.new("ShaderPreviewCube", mesh)

        # Add the object into the scene.
        scene.objects.link(shader_cube)
        scene.objects.active = shader_cube
        shader_cube.select = True

        # Construct the bmesh cube and assign it to the blender mesh.
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=10.0)
        bm.to_mesh(mesh)
        bm.free()

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.uv.reset()
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = scene.objects["ShaderPreviewCube"].data
        mesh.uv_textures[0].name = "UVMap"

    shader_list = []
    shader_list.append(base_path + shader_path + scene.q3_map_import_tool.shaderF + ".shader")

    for shader_file in shader_list:
        try:
            is_open = 0
            with open(shader_file) as lines:
                for line in lines:
                    line = line.strip(" \t\r\n")

                    #skip empty lines or comments
                    if not line or line.startswith('/'):
                        continue

                    #content
                    if not line.startswith('{') and not line.startswith('}'):
                        if is_open == 0:
                            current_shader = line
                    #marker open
                    elif line.startswith('{'):
                        is_open = is_open + 1
                    #marker close
                    elif line.startswith('}'):
                        #close material
                        if is_open == 1:
                            try:
                                print("Add {} to materials".format(current_shader))
                                mesh.materials.append(bpy.data.materials[current_shader])
                            except:
                                mat = bpy.data.materials.new(name=current_shader)
                                mesh.materials.append(mat)
                                mat.use_nodes = True

                        is_open -= 1
        except:
            print (('error in shaderfile ') + shader_file)

    q3_map_import_tool.only_preview_cube = True
    bpy.ops.q3map.interpret_shaders()
    q3_map_import_tool.only_preview_cube = False


# ------------------------------------------------------------------------
#    store properties in the user preferences
# ------------------------------------------------------------------------
class Q3MapHelperAddonPreferences(AddonPreferences):

    bl_idname = __name__

    base_path = StringProperty(
        name="basepath",
        description="Path to base folder",
        default="",
        maxlen=2048,
        )

    shader_dir = StringProperty(
        name="shader dir",
        description="Shader directory name",
        default="shaders\\",
        maxlen=2048,
        )

    use_gpu = BoolProperty(
        name="Enable GPU computing",
        description="This will automaticly make your GPU the cycles rendering device and adjusts tile size accordingly.",
        default = True
        )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "base_path")
        row.operator("q3map.get_basepath", icon="FILE_FOLDER", text="")
        layout.prop(self, "shader_dir")
        layout.prop(self, "use_gpu")


# ------------------------------------------------------------------------
#    store properties in the active scene
# ------------------------------------------------------------------------
class ImporterSettings(PropertyGroup):

    def shaderF_list_cb(self, context):
        addon_name = __name__.split('.')[0]
        prefs = context.user_preferences.addons[addon_name].preferences

        base_path = prefs.base_path
        shader_dir = os.path.join(base_path, prefs.shader_dir)
        current_shader = ''

        shader_names = []
        try:
            shader_files = sorted(f for f in os.listdir(shader_dir)
                                  if f.endswith(".shader"))
            for shader_file in shader_files:
                current_shader = os.path.join(shader_dir, shader_file)
                current_file = shader_file.split('.')[0]
                shader_names.append(current_file)
        except Exception as e:
            print('Could not open shader ' + current_shader + ", error: " + str(e))

        shader_list = [(shader_file, shader_file, "")
                       for shader_file in sorted(shader_names)]
        return shader_list

    def shader_list_cb(self, context):
        addon_name = __name__.split('.')[0]
        prefs = context.user_preferences.addons[addon_name].preferences

        base_path = prefs.base_path
        shader_path = prefs.shader_dir
        current_shader = ''

        shader_file = base_path + shader_path + bpy.context.scene.q3_map_import_tool.shaderF + ".shader"
        try:
            is_open = 0
            shaders = []
            with open(shader_file) as lines:
                for line in lines:
                    #skip empty lines or comments
                    if line.strip(" \t\r\n").startswith('/') and line.strip("\t\r\n") != ' ':
                        continue

                    #content
                    if not line.strip(" \t\r\n").startswith('{') and not line.strip(" \t\r\n").startswith('}'):
                        if is_open == 0:
                            current_shader = line.strip(" \t\r\n")
                    #marker open
                    elif line.strip(" \t\r\n").startswith('{'):
                        is_open = is_open + 1
                    #marker close
                    elif line.strip(" \t\r\n").startswith('}'):
                        #close material
                        if is_open == 1:
                            shaders.append(current_shader)

                        is_open -= 1
        except Exception as e:
            print("error in shaderfile '{}', error: {}".format(shader_file, str(e)))

        items = [(shader, shader, "") for shader in sorted(shaders)]
        return items

    shaderF = bpy.props.EnumProperty(
        items=shaderF_list_cb,
        name="ShaderFile",
        update=preview_shader)

    shader = bpy.props.EnumProperty(
        items=shader_list_cb,
        name="Material",
        update=update_preview_cube)

    deluxeMapped = BoolProperty(
        name="is the map deluxe mapped?",
        description="If the map is deluxemapped you will only see Lightmap names that are odd or even",
        default=False)

    gl2 = BoolProperty(
        name="gl2 Materials",
        description="are there gl2 compatible materials?",
        default = False)

    sky_number = IntProperty(
        name="Sky Number",
        description="",
        default=0,
        min=0,
        max=100)

    lmSize = IntProperty(
        name="Lightmap Size",
        description="Texture size for the new lightmaps",
        default=128,
        min=128,
        max=1000000)

    default_emissive = FloatProperty(
        name="Default emissive value",
        description="",
        default=1.0,
        min=0.05,
        max=1000.0)

    default_sky_emissive = FloatProperty(
        name="Default sky emissive value",
        description="",
        default=5.0,
        min=0.0,
        max=1000.0)

    default_roughness = FloatProperty(
        name="Default roughness value",
        description="",
        default=0.45,
        min=0.0,
        max=1.0)

    map_name = StringProperty(
        name="map name",
        description="Map name",
        default="",
        maxlen=2048)

    selectedShaderFile = StringProperty(
        name="ShaderFile:",
        default="",
        maxlen=2048)

    #------------------
    # "private" variables
    #------------------
    only_preview_cube = BoolProperty(
        name="only_preview_cube",
        description="skip the sky and sun generation?",
        default=False)


# ------------------------------------------------------------------------
#    import panel in object mode
# ------------------------------------------------------------------------
class ImportPanel(Panel):

    bl_idname = "import_panel"
    bl_label = "Lightmapping helper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Q3 Tools"
    bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return True

    def draw(self, context):
        addon_name = __name__.split('.')[0]
        self.prefs = context.user_preferences.addons[addon_name].preferences

        layout = self.layout
        scene = context.scene
        q3_map_import_tool = scene.q3_map_import_tool

        box = layout.box()
        box.prop(q3_map_import_tool, "map_name")
        box.operator("q3map.import_map")

        box = layout.box()
        box.prop(q3_map_import_tool, "gl2")
        box.prop(q3_map_import_tool, "default_emissive")
        box.prop(q3_map_import_tool, "default_roughness")
        box.prop(q3_map_import_tool, "default_sky_emissive")
        box.prop(q3_map_import_tool, "sky_number")
        box.row().separator()
        box.label('This will recreate')
        box.label('all existing textures and shader nodes!')
        box.operator("q3map.interpret_shaders")

        box = layout.box()
        box.prop(q3_map_import_tool, "deluxeMapped")
        box.prop(q3_map_import_tool, "lmSize")
        box.operator("q3map.prepare_baking")
        box.operator("q3map.save_baked_lms")


# ------------------------------------------------------------------------
#    import panel in object mode
# ------------------------------------------------------------------------
class ShaderPanel(Panel):
    bl_idname = "shader_panel"
    bl_label = "Shader helper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Q3 Tools"
    bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return True

    def draw(self, context):
        addon_name = __name__.split('.')[0]
        self.prefs = context.user_preferences.addons[addon_name].preferences

        layout = self.layout
        scene = context.scene
        q3_map_import_tool = scene.q3_map_import_tool

        box = layout.box()
        box.row().separator()
        box.prop(q3_map_import_tool, "shaderF")
        box.prop(q3_map_import_tool, "shader")
        box.operator("q3map.add_material")
        box.row().separator()


# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------
class WMFileSelector(bpy.types.Operator):

    bl_idname = "q3map.get_basepath"
    bl_label = "base Path"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        addon_name = __name__.split('.')[0]
        self.prefs = context.user_preferences.addons[addon_name].preferences

        fdir = self.filepath
        self.prefs.base_path = fdir
        #context.scene.q3_map_import_tool.base_path = fdir
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ImportMap(bpy.types.Operator):

    bl_idname = "q3map.import_map"
    bl_label = "Import Map"

    def execute(self, context):
        addon_name = __name__.split('.')[0]
        self.prefs = context.user_preferences.addons[addon_name].preferences

        scene = bpy.context.scene
        q3_map_import_tool = scene.q3_map_import_tool
        base_path = self.prefs.base_path
        mapName = q3_map_import_tool.map_name

        names = []
        values = []
        textures = []
        numEnts = 0
        numLms = 0
        file = base_path + 'maps/' + mapName

        #clear meshes
        #for mesh in bpy.data.meshes:
            #if mesh.users > 0:
                #mesh.user_clear()
            #bpy.data.meshes.remove(mesh)

        #clear meshes
        #for object in bpy.data.objects:
            #if object.users > 0:
                #object.user_clear()
            #bpy.data.objects.remove(object)

        # import map .fbx
        try:
            imported_object = bpy.ops.import_scene.fbx(filepath=(file + 'out.fbx'))
        except:
            print ('could not load map: ' + file)

        #get Lightmap ID's
        try:
            with open(file + 'out.meshlmid') as lines:
                for line in lines:
                    first, rest = line.strip(" \t\r\n[]").split(' ', 1)
                    names.append(first)
                    values.append(int(rest))
                    numEnts += 1
                    numLms = max(numLms, int(rest))
        except:
            print ('File ' + file + ' not found')

        #lightmaps
        for i in range(-3, (numLms + 1)):
            bpy.ops.object.select_all(action='DESELECT')
            obs = []
            objects = []
            name = 'Lightmap_' + str(i).zfill(4)
            found = False

            #find all matching objects per lm id
            for j in range(0,numEnts):
                if values[j] == i:
                    objects.append(names[j])

            #select objects by lm id
            for p in objects:
                scene.objects[p].select = True
                obs = scene.objects[p]
                mesh = obs.data
                mesh.uv_textures['DiffuseUV'].name = "UVMap"
                scene.objects.active = scene.objects[p]
                found = True

            #join selected objects
            if found == True:
                obs.name = name
                bpy.ops.object.join()
                bpy.context.scene.objects.active = obs
            print ('Objects with Lightmap number ' + str(i) + ' of ' + str(numLms) + ' joined.')

        misc_models = []
        misc_models_origins = []
        misc_models_scales = []
        misc_models_angles = []
        num_misc_models = 0
        
        lights_origins = []
        lights_light = []
        lights_colors = []
        num_lights = 0

        #get misc_model_static's informations
        try:
            blockOpen = 0
            is_misc_model_static = False
            is_light = False
            has_origin = False
            model = ''
            angle = 0.0
            origin = '0 0 0'
            color = '1.0 1.0 1.0'
            light = '0'
            modelscale = 1.0
            with open(file + '_converted.map') as lines:
                for line in lines:
                    try:
                        if (line.strip(" \t\r\n") == '{'):
                            blockOpen += 1
                            continue
                        if (line.strip(" \t\r\n") == '}'):
                            if is_misc_model_static and has_origin:
                                misc_models.append(model)
                                misc_models_origins.append(origin)
                                misc_models_scales.append(modelscale)
                                misc_models_angles.append(angle)
                                num_misc_models += 1
                            if is_light and has_origin:
                                lights_origins.append(origin)
                                lights_light.append(light)
                                lights_colors.append(color)
                                num_lights += 1
                            model = ''
                            origin = '0 0 0'
                            color = '1.0 1.0 1.0'
                            light = '0'
                            modelscale = 1.0
                            angle = 0.0
                            is_misc_model_static = False
                            is_light = False
                            has_origin = False
                            blockOpen -= 1
                            continue
                        if (blockOpen == 1) and (line.strip("\t\r\n") != '') and (line.strip(" \t\r\n").startswith('"')):
                            first, rest = line.strip("\t\r\n").split(' ', 1)
                            if (first == '"classname"') and (rest == '"misc_model_static"'):
                                is_misc_model_static = True
                            if (first == '"classname"') and (rest == '"light"'):
                                is_light = True
                            if (first == '"model"'):
                                model = rest.strip('"')
                            if (first == '"light"'):
                                light = rest.strip('"')
                            if (first == '"_color"'):
                                color = rest.strip('"')
                            if (first == '"angle"'):
                                angle = rest.strip('"')
                            if (first == '"origin"'):
                                origin = (rest.strip('"'))
                                has_origin = True
                            if (first == '"modelscale"'):
                                modelscale = float(rest.strip('"'))
                    except:
                        print ('line skipped ')
        except:
            print ('could not parse all models from ' + file + '_converted.map')

        #add light entities (SomaZ)
        for misc_light in range(0, num_lights):
            scene.render.engine = 'CYCLES'
            x,y,z = lights_origins[misc_light].strip("\t\r\n").split(' ', 2)
            r,g,b = lights_colors[misc_light].strip("\t\r\n").split(' ', 2)
            light_value = float(lights_light[misc_light])
            
            #add lights
            light = bpy.ops.object.lamp_add(type='POINT', location=(float(x)/100,float(y)/100,float(z)/100))
            light = scene.objects['Point']
            light.name = 'Light_' + str(misc_light)
            light_node = light.data.node_tree.nodes["Emission"]
            light_node.inputs["Color"].default_value = (float(r),float(g),float(b), 1.0)
            light_node.inputs["Strength"].default_value = float(light_value) / 10

        #import fitting models
        addedModels = []
        scene_objects = []
        droppedModels = []
        linkedModels = 0
        for mms in range(0, num_misc_models):
            toAdd = True
            for name in addedModels:
                if name == misc_models[mms]:
                    toAdd = False
            if toAdd:
                addedModels.append(misc_models[mms]);
                try:
                    imported_object = bpy.ops.import_scene.fbx(filepath=(base_path + misc_models[mms][:-4] + 'out.fbx'))

                    scene.objects.active = bpy.context.selected_objects[0]
                    fbx_object = bpy.context.selected_objects[0]
                    bpy.ops.object.join()

                    fbx_object.name = misc_models[mms][:-4]
                    fbx_object.data.name = misc_models[mms][:-4]

                    mesh = fbx_object.data
                    mesh.uv_textures['DiffuseUV'].name = "UVMap"

                    #apply the given scale, should be 0.01 by default, but we make sure it is
                    scale = (.01,.01,.01)
                    fbx_object.scale = scale
                    bpy.ops.object.transform_apply( scale=True )

                    fbx_object.hide = True
                    fbx_object.hide_render = True
                except:
                    droppedModels.append(misc_models[mms][:-4] + 'out.fbx')
                    print ('could not load model: ' + (base_path + misc_models[mms][:-4] + 'out.fbx'))

            # add the misc_model_static linked to the imported model
            try:
                me = bpy.data.objects[misc_models[mms][:-4]].data
                ob = bpy.data.objects.new(misc_models[mms], me)
                bpy.context.scene.objects.link(ob)
                bpy.context.scene.update()

                x,y,z = misc_models_origins[mms].strip("\t\r\n").split(' ', 2)
                ob.location = (float(x)/100,float(y)/100,float(z)/100)
                scale = (misc_models_scales[mms],misc_models_scales[mms],misc_models_scales[mms])
                ob.scale = scale
                ob.rotation_euler = (0.0,0.0,radians(float(misc_models_angles[mms])))
                linkedModels += 1
            except:
                print ('could not link model: ' + (misc_models[mms][:-4] + ' is not imported (Try exporting the model again from Noesis)'))

        if droppedModels:
            print ('Dropped models:')
            print (' ')
        for model in droppedModels:
            print (model)

        return{'FINISHED'}


class Sun(object):

    def __init__(self, r, g, b, yaw, pitch, intensity):
        self.r = r
        self.g = g
        self.b = b
        self.yaw = yaw
        self.pitch = pitch
        self.intensity = intensity


class InterpretShaders(bpy.types.Operator):

    bl_idname = "q3map.interpret_shaders"
    bl_label = "Interpret Shaders"

    def execute(self, context):
        print("=================== InterpretShaders.execute =====================")
        addon_name = __name__.split('.')[0]
        self.prefs = context.user_preferences.addons[addon_name].preferences

        scene = bpy.context.scene
        q3_map_import_tool = scene.q3_map_import_tool
        base_path = self.prefs.base_path
        use_gpu = self.prefs.use_gpu
        gl2 = q3_map_import_tool.gl2
        only_preview_cube = q3_map_import_tool.only_preview_cube
        processing_objects = []

        if only_preview_cube:
            processing_objects.append(bpy.data.objects["ShaderPreviewCube"])
        else:
            for obj in scene.objects:
                processing_objects.append(obj)

        scene.render.engine = 'CYCLES'
        scene.cycles.transparent_min_bounces = 0
        scene.cycles.min_bounces = 0
        scene.cycles.transparent_max_bounces = 6
        scene.cycles.max_bounces = 6
        scene.cycles.transmission_bounces = 6
        scene.cycles.caustics_refractive = False
        scene.cycles.caustics_reflective = False

        #optimize rendering times
        if use_gpu:
            scene.cycles.device = 'GPU'
            scene.render.tile_x = 256
            scene.render.tile_y = 256
        else:
            scene.cycles.device = 'CPU'
            scene.render.tile_x = 16
            scene.render.tile_y = 16

        if gl2:
            node_type = "ShaderNodeBsdfPrincipled"
        else:
            node_type = "ShaderNodeBsdfDiffuse"

        shader_path = self.prefs.shader_dir

        default_roughness = q3_map_import_tool.default_roughness
        default_emissive = q3_map_import_tool.default_emissive
        default_sky_emissive = q3_map_import_tool.default_sky_emissive
        sky_number = q3_map_import_tool.sky_number

        #delete all material nodes and textures
        if not only_preview_cube:
            bpy.ops.object.select_all(action='DESELECT')
            for ob in scene.objects:
                ob.select = False

                if ob.type == 'MESH' and ob.name.startswith("Sky"):
                    ob.select = True
                    bpy.ops.object.delete()

                if ob.name.startswith("Sun"):
                    ob.select = True
                    bpy.ops.object.delete()

            for img in bpy.data.images:
                img.user_clear()

            for img in bpy.data.images:
                if not img.users:
                    bpy.data.images.remove(img)

            for tex in bpy.data.textures:
                tex.user_clear()

            for tex in bpy.data.textures:
                if not tex.users:
                    bpy.data.textures.remove(tex)

            for a in bpy.data.materials:
                a.use_nodes = True
                a.node_tree.nodes.clear()
                node_output = a.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
                node_output.location = 400,100

                node_DiffuseBSDF = a.node_tree.nodes.new(type = node_type)
                node_DiffuseBSDF.location = 200,100
                node_DiffuseBSDF.name = 'Shader'

                node_Mix = a.node_tree.nodes.new(type='ShaderNodeMixShader')
                node_Mix.location = 400,300

                node_Mix.inputs[0].default_value = 1.0

                node_Transparent = a.node_tree.nodes.new(type='ShaderNodeBsdfTransparent')
                node_Transparent.location = 200,300

                links = a.node_tree.links
                links.new(node_DiffuseBSDF.outputs[0], node_Mix.inputs[2])
                links.new(node_Transparent.outputs[0], node_Mix.inputs[1])
                links.new(node_Mix.outputs[0], node_output.inputs[0])
        else:
            print("Prcessing bpy.data.materials")
            for m in bpy.data.materials:
                m.use_nodes = True

                try:
                    nodes = m.node_tree.nodes
                    links = m.node_tree.links

                    nodes.clear()

                    node_output = nodes.new(type='ShaderNodeOutputMaterial')
                    node_output.location = (400,100)

                    node_DiffuseBSDF = nodes.new(type=node_type)
                    node_DiffuseBSDF.location = (200,100)

                    node_Mix = nodes.new(type="ShaderNodeMixShader")
                    node_Mix.location = (400,300)
                    node_Mix.inputs["Fac"].default_value = 1.0

                    node_Transparent = nodes.new(type="ShaderNodeBsdfTransparent")
                    node_Transparent.location = (200,300)

                    links.new(node_DiffuseBSDF.outputs["BSDF"], node_Mix.inputs[2])
                    links.new(node_Transparent.outputs["BSDF"], node_Mix.inputs[1])
                    links.new(node_Mix.outputs["Shader"], node_output.inputs["Surface"])
                except Exception as e:
                    print("..failed adding node links to preview sphere, error: {}"
                          .format(str(e)))

        #build shader_list
        shader_list = []
        try:
            shader_files = os.listdir(os.path.join(base_path, shader_path))
            shader_list = [os.path.join(base_path, shader_path, file_path)
                           for file_path in shader_files
                           if file_path.lower().endswith('.shader')]
        except Exception as e:
            print("Could not build shader list, error {}".format(str(e)))

        #get needed shaders
        needed_shaders = set()
        for ob in processing_objects:
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True

            scene.objects.active = ob
            for m in ob.material_slots:
                m.material.name = os.path.splitext(m.material.name)[0]
                material_name = m.material.name
                needed_shaders.add(m.material.name)

        #find shaders
        shader_names = []
        diffuseTexture = []
        emissiveTexture = []
        is_emissive = []
        is_transparent = []
        current_shader = ''
        buffer_texture = ''
        buffer_diffuse_texture = ''
        buffer_emissive_texture = ''

        sky_shaders = []
        sky_shader_textures = []

        suns = []
        for shader_file in shader_list:
            try:
                found_shader = False
                found_diffuse = False
                found_emissive = False
                diffuse_stage = False
                glow_stage = False
                transparent_stage = False
                is_sky = False
                is_open = 0
                with open(shader_file) as lines:
                    for line in lines:
                        #skip empty lines or comments
                        if line.strip(" \t\r\n").startswith('/') and (line.strip("\t\r\n") != ' '):
                            continue

                        #content
                        if not line.strip(" \t\r\n").startswith('{') and not line.strip(" \t\r\n").startswith('}'):
                            if is_open == 0:
                                for shader in needed_shaders:
                                    if shader == line.strip(" \t\r\n"):
                                        current_shader = line.strip(" \t\r\n")
                                        found_shader = True
                            elif is_open == 1 and found_shader:     #special attributes like material or sky stuff
                                if line.lower().strip(" \t\r\n").startswith('skyparms'):
                                    try:
                                        try:
                                            marker, value = line.strip(" \t\r\n").split('\t', 1)
                                        except:
                                            marker, value = line.strip(" \t\r\n").split(' ', 1)
                                        is_sky = True
                                        buffer_diffuse_texture = value.strip(" \t\r\n")
                                    except:
                                        print ("could not split line: " + line)

                                if line.lower().strip(" \t\r\n").startswith('surfaceparm'):
                                    try:
                                        try:
                                            marker, value = line.strip(" \t\r\n").split('\t', 1)
                                        except:
                                            marker, value = line.strip(" \t\r\n").split(' ', 1)
                                        if value.strip(" \t\r\n") == "sky":
                                            is_sky = True
                                        if value.strip(" \t\r\n") == "trans":
                                            transparent_stage = True
                                    except:
                                        print ("could not split line: " + line)

                                if (line.lower().strip(" \t\r\n").startswith('sun') or
                                    line.strip(" \t\r\n").startswith('q3map_sun') or
                                    line.strip(" \t\r\n").startswith('q3map_sunext')):
                                    try:
                                        try:
                                            marker, r, g, b, i, d, e, deviance, samples = line.strip(" \t\r\n").split('\t', 8)
                                        except:
                                            marker, r, g, b, i, d, e = line.strip(" \t\r\n").split(' ', 6)
                                        suns.append(Sun(float(r), float(g), float(b), float(d), float(e), float(i)))
                                    except:
                                        print ("could not split line: " + line)
                            elif is_open == 2 and found_shader:
                                if line.lower().strip(" \t\r\n") == 'glow':
                                    glow_stage = True
                                elif line.lower().strip(" \t\r\n").startswith('surfacesprites'):
                                    diffuse_stage = False
                                    glow_stage = False
                                    transparent_stage = False
                                elif line.lower().strip(" \t\r\n").startswith('alphafunc'):
                                    marker, value = line.strip(" \t\r\n").split(' ', 1)
                                    if value.strip(" \t\r\n") == "GE192":
                                        transparent_stage = True
                                    if value.strip(" \t\r\n") == "GE128":
                                        transparent_stage = True
                                elif line.lower().strip(" \t\r\n").startswith('blendfunc'):
                                    marker, value = line.strip(" \t\r\n").split(' ', 1)
                                    if value.strip(" \t\r\n") == "GL_ONE GL_ONE":
                                        glow_stage = True
                                elif line.lower().strip(" \t\r\n").startswith('tcgen'):
                                    marker, value = line.strip(" \t\r\n").split(' ', 1)
                                    if value.strip(" \t\r\n") == "environment":
                                        glow_stage = False
                                        diffuse_stage = False
                                elif line.lower().strip(" \t\r\n").startswith('alphagen'):
                                    marker, value = line.strip(" \t\r\n").split(' ', 1)
                                    if value.strip(" \t\r\n") == "lightingSpecular":
                                        glow_stage = False
                                        diffuse_stage = False
                                elif line.lower().strip(" \t\r\n").startswith('clampmap'):
                                    marker, value = line.strip(" \t\r\n").split(' ', 1)
                                    if (value.strip(" \t\r\n") != '$lightmap'):
                                        buffer_texture = value
                                        diffuse_stage = True
                                elif line.lower().strip(" \t\r\n").startswith('map'):
                                    marker, value = line.strip(" \t\r\n").split(' ', 1)
                                    if (value.strip(" \t\r\n") != '$lightmap'):
                                        buffer_texture = value
                                        diffuse_stage = True
                        #marker open
                        elif line.strip(" \t\r\n").startswith('{'):
                            is_open = is_open + 1
                        #marker close
                        elif line.strip(" \t\r\n").startswith('}'):
                            #close stage
                            if is_open == 2:
                                if found_shader and diffuse_stage:
                                    if glow_stage:
                                        buffer_emissive_texture = buffer_texture
                                        found_emissive = True
                                        glow_stage = False
                                    else:
                                        buffer_diffuse_texture = buffer_texture
                            #close material
                            elif is_open == 1 and found_shader:
                                if is_sky:
                                    sky_shaders.append(current_shader)
                                    sky_shader_textures.append(buffer_diffuse_texture.strip(' \t\r\n').split(' ',1)[0])

                                    is_sky = False
                                    found_shader = False
                                    found_emissive = False
                                    buffer_emissive_texture = 'none'
                                    buffer_diffuse_texture = 'none'
                                    buffer_texture = 'none'
                                    diffuse_stage = False
                                    glow_stage = False
                                else:
                                    diffuseTexture.append(buffer_diffuse_texture)
                                    if found_emissive:
                                        emissiveTexture.append(buffer_emissive_texture)
                                        is_emissive.append(True)
                                    else:
                                        emissiveTexture.append('none')
                                        is_emissive.append(False)
                                    is_transparent.append(bool(transparent_stage))
                                    shader_names.append(current_shader)

                                    is_sky = False
                                    found_shader = False
                                    found_emissive = False
                                    buffer_emissive_texture = 'none'
                                    buffer_diffuse_texture = 'none'
                                    buffer_texture = 'none'
                                    diffuse_stage = False
                                    glow_stage = False
                                    transparent_stage = False

                            is_open -= 1
            except:
                print (('error in shaderfile ') + shader_file)

        #sky setup (SomaZ)
        if not only_preview_cube:
            try:
                for (sun_index, sun) in suns:
                    try:
                        bpy.ops.object.lamp_add(type='SUN', radius=0.1)
                        sun_object = scene.objects['Sun']
                        sun_object.name = 'Sun' + str(sun_index)
                        sun_object.rotation_euler = (0.0, radians(90.0 - sun.yaw), sun.pitch)
                        sun_object.data.node_tree.nodes["Emission"].inputs[0].default_value = (sun.r, sun.g, sun.b, 1.0)
                        sun_object.data.node_tree.nodes["Emission"].inputs[1].default_value = sun.intensity / 10.0
                    except:
                        print ('could not parse a sun')

                bpy.ops.mesh.primitive_cube_add(location=(0,0,0))
                for ob in scene.objects:
                    ob.select = False
                    if ob.type == 'MESH' and ob.name.startswith("Cube"):
                        ob.name = "Sky"
                        ob.select = True

                        is_sky = True
                        mesh = ob.data

                        if sky_number >= len(sky_shader_textures):
                            print ('selected Sky Number is invalid. It gets replaced by 0')
                            sky_number = 0

                        texture = sky_shader_textures[sky_number]

                        for side in ["up", "dn", "ft", "bk", "lf", "rt"]:
                            material_name = "{}_{}".format(texture, side)
                            try:
                                mesh.materials.append(bpy.data.materials[material_name])
                            except:
                                mat = bpy.data.materials.new(name=material_name)
                                mesh.materials.append(mat)
                                mat.use_nodes = True

                        for face in mesh.polygons:
                            face.select = True
                            face.flip()

                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.context.tool_settings.mesh_select_mode = [False, False, True]
                        bpy.ops.uv.reset()

                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.shade_smooth()

                        sky_side_mapping = [4, 3, 5, 2, 1, 0]
                        for i in range(6):
                            mesh.polygons[i].material_index = sky_side_mapping[i]

                        bpy.context.scene.update()

                        ob.scale = (500.0, 500.0, 500.0)
                        ob.modifiers.new("subd", type='SUBSURF')
                        ob.modifiers['subd'].levels = 0
                        ob.modifiers['subd'].render_levels = 0
                        ob.cycles_visibility.shadow = False
            except:
                print ('could not setup the sky')

        #textures setup
        use_shader = False
        textures = []
        texture_path = ' '
        emissive_path = ' '
        for m in bpy.data.materials:
            try:
                texture_path = os.path.splitext(m.name)[0]
                texture_path = os.path.splitext(texture_path)[0]
                is_sky = False
                is_sky_texture = False

                for shader in sky_shaders:
                    if shader == m.name:
                        is_sky = True

                for shader in sky_shader_textures:
                    if texture_path.lower().startswith(shader.lower()):
                        is_sky_texture = True

                use_shader = False
                if is_sky:
                    m.use_nodes = True
                    nodes = m.node_tree.nodes

                    material_output = nodes.get("Material Output")
                    node_transparentShader = nodes.new(type='ShaderNodeBsdfTransparent')
                    node_transparentShader.location = 0,400
                    m.node_tree.links.new(
                        node_transparentShader.outputs["BSDF"],
                        material_output.inputs["Surface"])
                else:
                    #check if there is a shader for the material
                    for i in range(len(shader_names)):
                        if shader_names[i] == texture_path:
                            use_shader = True
                            texture_path = '.'.join((diffuseTexture[i]).split('.', 2)[:1])
                            emissive_path = '.'.join((emissiveTexture[i]).split('.', 2)[:1])
                            has_diffuse = True
                            has_glow = bool(is_emissive[i])
                            has_transparency = bool(is_transparent[i])

                    if not use_shader:
                        has_diffuse = True
                        has_transparency = False
                        has_glow = False

                    if is_sky_texture:
                        has_diffuse = False
                        has_glow = True
                        emissive_path = texture_path

                    def load_image(texture_path):
                        for extension in [".jpg", ".tga", ".png"]:
                            try:
                                return bpy.data.images.load(
                                    os.path.join(base_path, texture_path + extension))
                            except:
                                continue

                        return None

                    img = load_image(texture_path)
                    if img is None:
                        has_diffuse = False
                        print ("Can't load image '{}' in shader '{}'".format(texture_path, m.name))

                    if gl2 and has_diffuse:
                        rmo_img = load_image("{}_rmo".format(texture_path))
                        if rmo_img is None:
                            print ("Can't load rmo image '{}' in shader '{}'".format(texture_path, m.name))

                        nh_img = load_image("{}_n".format(texture_path))
                        if nh_img is None:
                            print ("Can't load NH image '{}' in shader '{}'".format(texture_path, m.name))

                    #glow textures
                    if has_glow:
                        img_glow = load_image(emissive_path)
                        if img_glow is None:
                            has_glow = False
                            print ("image %s not found (emissive texture)" % emissive_path)

                    #Node setup
                    m.use_nodes = True
                    nodes = m.node_tree.nodes
                    material_output = nodes.get("Material Output")

                    #is a valid material
                    if has_diffuse or has_glow:
                        node_LightmapUV = nodes.new(type='ShaderNodeUVMap')
                        node_LightmapUV.uv_map = "LightmapUV"
                        node_LightmapUV.location = -500, -200

                        node_DiffuseUV = nodes.new(type='ShaderNodeUVMap')
                        node_DiffuseUV.uv_map = "UVMap"
                        node_DiffuseUV.location = -250, -200

                        node_lmTexture = nodes.new(type='ShaderNodeTexImage')
                        node_lmTexture.location = -500, 300
                        node_lmTexture.name = 'Lightmap'
                        node_lmTexture.label = 'Lightmap'

                        diffuse_node = nodes.get("Shader")

                        mix_node = nodes.get("Mix Shader")

                        links = m.node_tree.links
                        links.new(node_LightmapUV.outputs["UV"], node_lmTexture.inputs["Vector"])

                        if has_diffuse:
                            node_texture = nodes.new(type='ShaderNodeTexImage')
                            node_texture.image = img
                            node_texture.location = 0,100

                            links.new(node_DiffuseUV.outputs["UV"], node_texture.inputs["Vector"])
                            links.new(node_texture.outputs["Color"], diffuse_node.inputs["Color"])

                            if gl2:
                                try:
                                    node_seperate = nodes.new(type='ShaderNodeSeparateRGB')
                                    node_seperate.location = 0, -200

                                    node_rmotexture = nodes.new(type='ShaderNodeTexImage')
                                    node_rmotexture.image = rmo_img
                                    node_rmotexture.location = 0,-400
                                    node_rmotexture.color_space = 'NONE'

                                    node_nhtexture = nodes.new(type='ShaderNodeTexImage')
                                    node_nhtexture.image = nh_img
                                    node_nhtexture.location = 0,-700
                                    node_nhtexture.color_space = 'NONE'

                                    node_normalMap = nodes.new(type='ShaderNodeNormalMap')
                                    node_normalMap.location = 200,-700

                                    links.new(node_rmotexture.outputs[0], node_seperate.inputs[0])
                                    links.new(node_DiffuseUV.outputs[0], node_rmotexture.inputs[0])
                                    links.new(node_seperate.outputs[0], diffuse_node.inputs['Roughness'])
                                    links.new(node_seperate.outputs[1], diffuse_node.inputs['Metallic'])
                                    links.new(node_nhtexture.outputs[0], node_normalMap.inputs[1])
                                    links.new(node_nhtexture.outputs[1], material_output.inputs["Displacement"])
                                    links.new(node_DiffuseUV.outputs[0], node_nhtexture.inputs[0])
                                    links.new(node_normalMap.outputs[0], diffuse_node.inputs['Normal'])
                                except:
                                    print('not gl2 compatible')

                        if has_glow:
                            node_addShader = nodes.new(type='ShaderNodeAddShader')
                            node_addShader.location = 0,400

                            node_glow_texture = nodes.new(type='ShaderNodeTexImage')
                            node_glow_texture.image = img_glow
                            node_glow_texture.location = -250,100

                            node_emissiveShader = nodes.new(type='ShaderNodeEmission')
                            node_emissiveShader.location = -250,300

                            links.new(node_glow_texture.outputs[0], node_emissiveShader.inputs[0])
                            if is_sky_texture:
                                node_emissiveShader.inputs[1].default_value = default_sky_emissive
                                links.new(node_emissiveShader.outputs[0], material_output.inputs["Surface"])
                            else:
                                diffuse_node.inputs['Roughness'].default_value = default_roughness
                                node_emissiveShader.inputs[1].default_value = default_emissive

                                links.new(diffuse_node.outputs["BSDF"], node_addShader.inputs[0])
                                links.new(node_emissiveShader.outputs[0], node_addShader.inputs[1])
                                links.new(node_DiffuseUV.outputs["UV"], node_glow_texture.inputs["Vector"])
                                links.new(node_addShader.outputs["Shader"], material_output.inputs["Shader"])
                        else:
                            if gl2:
                                diffuse_node.inputs['Roughness'].default_value = default_roughness

                            links.new(node_DiffuseUV.outputs["UV"], node_texture.inputs["Vector"])

                        if has_diffuse:
                            links.new(node_texture.outputs["Alpha"], mix_node.inputs["Fac"])
                        elif has_transparency and has_glow:
                            links.new(node_glow_texture.outputs[0], mix_node.inputs["Fac"])
                            links.new(node_addShader.outputs["Shader"], mix_node.inputs[2])
                            links.new(mix_node.outputs["Shader"], material_output.inputs[0])
            except Exception as e:
                print("Could not build cycles shader for '{}', error {}"
                      .format(m.name, str(e)))

        return{'FINISHED'}


class PrepareBaking(bpy.types.Operator):

    bl_idname = "q3map.prepare_baking"
    bl_label = "Prepare Lightmap baking"

    def execute(self, context):
        scene = bpy.context.scene
        q3_map_import_tool = scene.q3_map_import_tool
        deluxeMapping = q3_map_import_tool.deluxeMapped #skip every second lightmap, because of deluxemapping, default should be False
        lmSize = q3_map_import_tool.lmSize
        gl2 = q3_map_import_tool.gl2

        addon_name = __name__.split('.')[0]
        self.prefs = context.user_preferences.addons[addon_name].preferences

        base_path = self.prefs.base_path

        failed = False

        lms = 0

        for ob in scene.objects:
            if ob.name.startswith('Lightmap_'):
                lms += 1

        for i in range(0,lms-1):
            bpy.ops.object.select_all(action='DESELECT')

            if deluxeMapping:
                name = 'Lightmap_' + str(i*2).zfill(4)
            else:
                name = 'Lightmap_' + str(i).zfill(4)
            try:
                obs = scene.objects[name]
                obs.select = True

                scene.objects.active = scene.objects[name]
                obs.data.uv_textures["LightmapUV"].active = True
                obs.data.uv_textures["LightmapUV"].active_render = True

                try:
                    bpy.data.images[name].scale(lmSize,lmSize)
                    image = bpy.data.images[name]
                    if gl2:
                        image.use_generated_float = True
                    image.use_alpha = False
                    image.filepath = base_path + "maps\\" + q3_map_import_tool.map_name + "\\" + name + ".tga"
                    image.file_format = 'TARGA'
                    #image.colorspace_settings.name = 'Linear'
                except:
                    image = bpy.data.images.new(name, lmSize, lmSize)
                    if gl2:
                        image.use_generated_float = True
                    image.use_alpha = False
                    image.filepath = base_path + "maps\\" + q3_map_import_tool.map_name + "\\" + name + ".tga"
                    image.file_format = 'TARGA'
                    #image.colorspace_settings.name = 'Linear'
                try:
                    for ms in obs.material_slots:
                        newname = os.path.splitext(ms.material.name)[0]
                        newname = os.path.splitext(newname)[0] + '.' + name
                        ms.material = ms.material.copy()
                        ms.material.name = newname
                        ms.material.node_tree.nodes['Lightmap'].image = image
                except:
                    print ('error in material slots in ' + name)
            except:
                failed = True
                print ('error in ' + name)

        if not failed:
            found = False

            #select lightmapped objects
            for i in range(lms-1):
                if deluxeMapping:
                    name = 'Lightmap_' + str(i*2).zfill(4)
                else:
                    name = 'Lightmap_' + str(i).zfill(4)

                try:
                    scene.objects[name].select = True
                    obs = scene.objects[name]
                    scene.objects.active = scene.objects[name]
                    found = True
                except:
                    found = False

            #join selected objects
            if found == True:
                obs.name = 'Baking Object'
                bpy.ops.object.join()
                obs.data.use_auto_smooth = False

        return{'FINISHED'}


class SaveBakedLMs(bpy.types.Operator):

    bl_idname = "q3map.save_baked_lms"
    bl_label = "Save baked Lightmaps"

    def execute(self, context):
        scene = bpy.context.scene
        q3_map_import_tool = scene.q3_map_import_tool

        #skip every second lightmap, because of deluxemapping, default should be False
        deluxeMapping = q3_map_import_tool.deluxeMapped
        for img in bpy.data.images:
            if img.name.startswith("Lightmap_"):
                img.save()

        return{'FINISHED'}


class AddSelectedMaterial(bpy.types.Operator):

    bl_idname = "q3map.add_material"
    bl_label = "Add material to current selection"

    def execute(self, context):
        scene = context.scene
        q3_map_import_tool = scene.q3_map_import_tool

        current_shader = scene.q3_map_import_tool.shader

        for obj in bpy.context.selected_objects:
            mesh = obj.data
            try:
                mesh.materials[current_shader]
            except:
                mesh.materials.append(bpy.data.materials[current_shader])

        return{'FINISHED'}


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.q3_map_import_tool = PointerProperty(type=ImporterSettings)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.q3_map_import_tool


if __name__ == "__main__":
    register()
