import bpy

import os
from time import time

_LOGTOCONSOLE = True

def setup_log():
    logname = 'BBake Baking Report'
    if not logname in bpy.data.texts:
        bpy.data.texts.new(logname)
    log = bpy.data.texts[logname]
    log.clear()
def msg(body, disp=True):
    if disp and _LOGTOCONSOLE:
        print(body)

    logname = 'BBake Baking Report'
    log = bpy.data.texts[logname]
    lines = body.split('\n')
    for line in lines:
        log.write(line+'\n')


def bbake_copy_settings(self, context):
    source = context.active_object
    targets = [ob for ob in context.selected_objects if ob.type == 'MESH' and not ob ==source]

    aovs = [
            'aov_combined',
            'aov_diffuse',
            'aov_glossy',
            'aov_transmission',
            'aov_subsurface',
            'aov_normal',
            'aov_ao',
            'aov_shadow',
            'aov_emit',
            'aov_uv',
            'aov_environment',
            ]

    bbs = source.bbake
    for target in targets:
        bbt = target.bbake

        if self.copy_aov:
            for aov in aovs:
                for k,v in getattr(bbs, aov).items():
                    getattr(bbt, aov)[k] = v

        if self.copy_ob_settings:
            for k,v in getattr(bbs, 'ob_settings').items():
                getattr(bbt, 'ob_settings')[k] = v

def set_uv_layer(context, ob):
    ob_settings = ob.bbake.ob_settings
    for layer in ob.data.uv_textures:
        if layer.name == ob_settings.uv_layer:
            ob.data.uv_textures.active = layer
            break


def set_ob_settings(context, ob):
    ob_settings = ob.bbake.ob_settings
    bake_settings = context.scene.render.bake
    bake_settings.use_selected_to_active = ob_settings.use_selected_to_active
    bake_settings.cage_extrusion = ob_settings.cage_extrusion
    bake_settings.use_cage = ob_settings.use_cage
    bake_settings.cage_object = ob_settings.cage_object
    bake_settings.margin = ob_settings.margin
    bake_settings.use_clear = ob_settings.use_clear
    set_uv_layer(context, ob)
    context.scene.update()

def set_pass_settings(context, aov):
    render = context.scene.render
    bake_settings = render.bake

    bake_settings.use_pass_direct = aov.use_pass_direct
    bake_settings.use_pass_indirect = aov.use_pass_indirect
    bake_settings.use_pass_color = aov.use_pass_color

    bake_settings.use_pass_ambient_occlusion = aov.use_pass_ambient_occlusion
    bake_settings.use_pass_diffuse = aov.use_pass_diffuse
    bake_settings.use_pass_emit = aov.use_pass_emit
    bake_settings.use_pass_glossy = aov.use_pass_glossy
    bake_settings.use_pass_subsurface = aov.use_pass_subsurface
    bake_settings.use_pass_transmission = aov.use_pass_transmission

    bake_settings.normal_space = aov.normal_space
    bake_settings.normal_r = aov.normal_r
    bake_settings.normal_g = aov.normal_g
    bake_settings.normal_b = aov.normal_b


def getsize(aov):
    '''Return image size of pass for this object'''
    if not aov.dimensions == 'CUSTOM':
        sizex = sizey = int(aov.dimensions)
        return sizex, sizey
        return aov.dimensions_custom.x, aov.dimensions_custom.y


def setup_image(ob, aov):
    render = bpy.context.scene.render
    filename = '%s_%s' %(ob.name, aov.name)
    sizex, sizey = getsize(aov)

    if filename in bpy.data.images:
        img = bpy.data.images[filename]
        if not img.source == 'GENERATED':
            img.source = 'GENERATED'
        img.generated_height = sizey
        img.generated_width = sizex
        img.use_generated_float = True
        image = img
    else:
        image = bpy.data.images.new('bakeimg', sizex, sizey, float_buffer=True)

    image.name = filename

    filepath = os.path.join(ob.bbake.ob_settings.path, image.name + render.file_extension)
    if bpy.context.scene.bbake.create_object_folders:
        filepath = os.path.join(
                                os.path.join(ob.bbake.ob_settings.path, ob.name),
                                image.name + render.file_extension)
    filepath = bpy.path.abspath(filepath)
    image.filepath = filepath

    image.update()
    return image


def setup_bake_node(material, image):
    if not material.use_nodes:
        material.use_nodes = True

    nodes = material.node_tree.nodes
    bake_node = next(iter([n for n in nodes
                           if n.bl_idname == 'ShaderNodeTexImage'
                           and n.image
                           and n.image == image]),
                           None)
    if not bake_node:
        bake_node = nodes.new('ShaderNodeTexImage')
    bake_node.select = True
    nodes.active = bake_node
    bake_node.image = image
    bake_node.label = image.name

    bpy.context.scene.update()

    return bake_node

def setup_materials(ob, aov):

    image = setup_image(ob, aov)
    for slot in ob.material_slots:
        if slot:
            if slot.material:
                setup_bake_node(slot.material, image)
    return image

def add_material(ob):
    msg('%s: Assigning new Material'%ob.name)
    context = bpy.context
    active = context.scene.objects.active
    if not ob == context.scene.objects.active:
        context.scene.objects.active = ob
    material = bpy.data.materials.new(ob.name)
    material.use_nodes = True
    ob.data.materials.append(material)
    context.scene.objects.active = active
    return material

def has_material(ob):
    for slot in ob.material_slots:
        if slot.material:
            return True
    return False

def add_smart_projection(ob):
    msg('%s: Adding UVs'%ob.name)
    context = bpy.context
    active = context.scene.objects.active
    if not ob == context.scene.objects.active:
        context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=0.05)
    bpy.ops.object.mode_set(mode='OBJECT')
    context.scene.objects.active = active
    return ob.data.uv_layers[0]

def update_image(image):
    image.source = 'FILE'
    image.filepath = bpy.path.relpath(image.filepath)
    image.reload()
    image.update()


def register():
    #print('\nREGISTER:\n', __name__)
    pass

def unregister():
    #print('\nUN-REGISTER:\n', __name__)
    pass


