import bpy
from . import variables as V
from . import helper as H
from . import preferences as P
from . import naming_convention as N
from os import path
import time
import sys
import re

class BpyAsset(object):
    def __init__(self, context, meshes, textures):
        self.separator = '_'
        self.context = context
        self.scn = context.scene
        self.param = V.GetParam(self.scn).param
        self.asset_name = self.get_asset_name(meshes)
        self.asset_root = self.get_asset_root(meshes)
        self.meshes = meshes
        self.textures = textures
        self.texture_set = {}

        self._asset_naming_convention = None
        self._mesh_naming_convention = None
        self._texture_naming_convention = None

        self.asset = None
        
    # Decorators
    def check_asset_exist(func):
        def func_wrapper(self, *args, **kwargs):
            if self.asset_name in bpy.data.collections:
                return func(self, *args, **kwargs)
            else:
                print('Lineup Maker : Asset doesn\'t exist in current scene')
                return None
        return func_wrapper

    def check_length(func):
        def func_wrapper(self, *args, **kwargs):
            if not len(self.meshes):
                print('Lineup Maker : No file found in the asset folder')
                return None
            else:
                return func(self, *args, **kwargs)
        return func_wrapper
    # Methods
    def import_asset(self):
        self.import_mesh()
        self.import_texture()
    
    def update_asset(self):
        self.update_mesh()
        self.update_texture()

    @check_length
    def import_mesh(self, update=False):
        name,ext = path.splitext(path.basename(self.meshes[0]))

        curr_asset_collection = H.create_asset_collection(self.context, self.asset_name)

        H.set_active_collection(self.context, self.asset_name)

        for i,f in enumerate(self.meshes):
            file = path.basename(f)
            name,ext = path.splitext(path.basename(f))

            # Import asset
            if ext.lower() in V.LM_COMPATIBLE_MESH_FORMAT.keys():
                if update:
                    print('Lineup Maker : Updating file "{}" : {}'.format(file, time.ctime(path.getmtime(f))))
                else:
                    print('Lineup Maker : Importing mesh "{}"'.format(name))
                compatible_format = V.LM_COMPATIBLE_MESH_FORMAT[ext.lower()]
                kwargs = {}
                kwargs.update({'filepath':f})
                kwargs.update(compatible_format[1])
                
                # run Import Command
                compatible_format[0](**kwargs)
            else:
                print('Lineup Maker : Skipping file "{}"\n     Incompatible format'.format(f))
                continue
            
            # register the mesh in scene variable
            if update:
                curr_asset = self.context.scene.lm_asset_list[self.asset_name]
            else:
                curr_asset = self.context.scene.lm_asset_list.add()
                curr_asset.name = self.asset_name
            
            curr_asset.last_update = path.getmtime(f)

            curr_mesh_list = curr_asset.mesh_list.add()
            curr_mesh_list.file_path = f

            for o in curr_asset_collection.objects:
                curr_mesh_list.mesh_name = o.name.lower()
                curr_mesh_list.mesh = o

                for m in o.material_slots:
                    if m.name not in curr_asset.material_list:
                        material_list = curr_asset.material_list.add()
                        material_list.name = m.material.name.lower()
                        material_list.material = m.material

                    curr_mesh_material_list = curr_mesh_list.material_list.add()
                    curr_mesh_material_list.name = m.material.name
                    curr_mesh_material_list.material = m.material
            
        self.asset = self.get_asset()
    
    @check_length
    def update_mesh(self):
        H.create_asset_collection(self.context, self.asset_name)
        H.set_active_collection(self.context, self.asset_name)

        curr_asset = self.context.scene.lm_asset_list[self.asset_name]

        need_update = False

        for f in self.meshes:
            if curr_asset.last_update < path.getmtime(f):
                need_update = True
                break

        if need_update:
            print('Lineup Maker : Updating asset "{}" : {}'.format(self.asset_name, time.ctime(curr_asset.last_update)))

            self.remove_objects()
            self.context.scene.update()
            self.import_mesh(update=True)
            # Dirty fix to avoid bad mesh naming when updating asset
            self.rename_objects()
        else:
            print('Lineup Maker : Asset "{}" is already up to date'.format(self.asset_name))

    def import_texture(self):
        # print(P.get_prefs().textureSet_albedo_keyword)
        # print(P.get_prefs().textureSet_normal_keyword)
        # print(P.get_prefs().textureSet_roughness_keyword)
        # print(P.get_prefs().textureSet_metalic_keyword)
        pass
    
    def update_texture(self):
        pass
        

    def feed_material(self, material, texture_set):
        nodes = material.node_tree.nodes

        shader = nodes.get("Principled BSDF")

        return shader

    def create_exposure_node(world):
        # create a group
        exposure_group = bpy.data.node_groups.new('Exposure', 'ShaderNodeTree')
        
        position = (0, 0)
        incr = 200
        # create group inputs
        group_inputs = exposure_group.nodes.new('NodeGroupInput')
        group_inputs.location = position
        exposure_group.inputs.new('NodeSocketColor', 'Color')
        exposure_group.inputs.new('NodeSocketFloat', 'Exposure')
        exposure_group.inputs[1].default_value = 1
        exposure_group.inputs[1].min_value = 0

        position = (position[0] + incr, position[1])

        # create three math nodes in a group
        node_pow = exposure_group.nodes.new('ShaderNodeMath')
        node_pow.operation = 'POWER'
        node_pow.inputs[1].default_value = 2
        node_pow.location = position

        position = (position[0] + incr, position[1])

        node_separate = exposure_group.nodes.new('ShaderNodeSeparateRGB')
        node_separate.location = position

        position = (position[0] + incr, position[1])

        node_x = exposure_group.nodes.new('ShaderNodeMath')
        node_x.operation = 'MULTIPLY'
        node_x.label = 'X'
        node_x.location = position

        position = (position[0], position[1] + incr)

        node_y = exposure_group.nodes.new('ShaderNodeMath')
        node_y.operation = 'MULTIPLY'
        node_y.label = 'Y'
        node_y.location = position

        position = (position[0], position[1] + incr)

        node_z = exposure_group.nodes.new('ShaderNodeMath')
        node_z.operation = 'MULTIPLY'
        node_z.label = 'Z'
        node_z.location = position

        position = (position[0] + incr, position[1] - incr)

        node_combine = exposure_group.nodes.new('ShaderNodeCombineRGB')
        node_combine.location = position

        position = (position[0] + incr, position[1])

        # create group outputs
        group_outputs = exposure_group.nodes.new('NodeGroupOutput')
        group_outputs.location = position

        exposure_group.outputs.new('NodeSocketColor', 'Output')

        # link nodes together
        exposure_group.links.new(node_x.inputs[1], node_pow.outputs[0])
        exposure_group.links.new(node_y.inputs[1], node_pow.outputs[0])
        exposure_group.links.new(node_z.inputs[1], node_pow.outputs[0])

        exposure_group.links.new(node_x.inputs[0], node_separate.outputs[0])
        exposure_group.links.new(node_y.inputs[0], node_separate.outputs[1])
        exposure_group.links.new(node_z.inputs[0], node_separate.outputs[2])
        
        exposure_group.links.new(node_x.outputs[0], node_combine.inputs[0])
        exposure_group.links.new(node_y.outputs[0], node_combine.inputs[1])
        exposure_group.links.new(node_z.outputs[0], node_combine.inputs[2])

        # link inputs
        exposure_group.links.new(group_inputs.outputs['Color'], node_separate.inputs[0])
        exposure_group.links.new(group_inputs.outputs['Exposure'], node_pow.inputs[0])


        #link output
        exposure_group.links.new(node_combine.outputs[0], group_outputs.inputs['Output'])
        
        return exposure_group
    # Helper

    def store_texture_set():
        pass
    
    def get_asset_naming_convention(self):
        asset_convention = self.param['lm_asset_naming_convention']
        
        asset_naming_convention = N.NamingConvention(self.context, self.asset_name, asset_convention)
        naming_convention = asset_naming_convention.naming_convention

        naming_convention['assetname'] = self.asset_name

        return naming_convention
    
    def get_mesh_naming_convention(self):
        mesh_convention = self.param['lm_mesh_naming_convention']
        naming_convention = []

        mesh_names = [path.basename(path.splitext(t)[0]) for t in self.meshes]
        for i,m in enumerate(mesh_names):
            mesh_naming_convention = N.NamingConvention(self.context, m, mesh_convention, self.meshes[i])
            naming_convention.append(mesh_naming_convention.naming_convention)

        return naming_convention

    def get_texture_naming_convention(self):
        texture_convention = self.param['lm_texture_naming_convention']

        naming_convention = {}

        for mesh_name,textures in self.textures.items():
            texture_names = [path.basename(path.splitext(t)[0]) for t in textures]

            texture_naming_convention = {}

            for i,t in enumerate(texture_names):
                t_naming_convention = N.NamingConvention(self.context, t, texture_convention)
                
                channel = t_naming_convention.naming_convention['channel']
                basename = t_naming_convention.pop_name(t_naming_convention.naming_convention['channel'])['fullname'].lower()

                if basename not in texture_naming_convention.keys():
                    texture_naming_convention[basename] = t_naming_convention.naming_convention

                chan = {'name':t, 'file':self.textures[mesh_name][i]}

                if 'channels' in texture_naming_convention[basename].keys():
                    if len(texture_naming_convention[basename]['channels'].keys()):
                        texture_naming_convention[basename]['channels'][channel] = chan
                    else:
                        texture_naming_convention[basename]['channels'] = {channel:chan}
                else:
                    texture_naming_convention[basename]['channels'] = {channel:chan}

                t = t.replace(channel, '')
                # t_length = len(t_naming)
            
            naming_convention[mesh_name] = texture_naming_convention
        
        return naming_convention

    def get_asset_name(self, meshes):
        return path.basename(path.dirname(meshes[0]))
    
    def get_asset_root(self, meshes):
        return path.dirname(meshes[0])

    @check_asset_exist
    def select_asset(self):
        bpy.data.collections[self.asset_name].select_set(True)

    def create_texture_basename_dict(self, mesh_name, texture_names=None):
        if texture_names is None:
            texture_names = [path.basename(path.splitext(t)[0]) for t in self.textures[mesh_name]]
        
        basename_dict = {}

        for i,t in enumerate(texture_names):
            basename = self.get_texture_basename(t)
            if basename not in basename_dict.keys():
                basename_dict[basename] = {}
        
        return basename_dict

    @check_asset_exist    
    def select_objects(self):
        curr_asset_collection = bpy.data.collections[self.asset_name]
        bpy.ops.object.select_all(action='DESELECT')
        for o in curr_asset_collection.all_objects:
            o.select_set(True)
    
    def remove_objects(self):
        self.select_objects()

        bpy.ops.object.delete()

    @check_asset_exist
    def print_asset_objects_name(self):
        names = self.get_objects_name()
        for n in names:
            print(n)

    @check_asset_exist
    def get_objects_name(self):
        names = []
        curr_asset_collection = bpy.data.collections[self.asset_name]
        for o in curr_asset_collection.all_objects:
            names.append(o.name)
        
        return names
    
    @check_asset_exist
    def rename_objects(self):
        curr_asset_collection = bpy.data.collections[self.asset_name]
        separator = '.'
        for o in curr_asset_collection.all_objects:
            splited_name = o.name.split(separator)[:-1]
            name = ''
            for i,split in enumerate(splited_name):
                name = name + split
                if i < len(splited_name) - 1:
                    name = name + separator
            o.name = name
    
    def compare_naming_conventions(self, n1, n2):
        if n1[1] in n1[0].keys() and n2[1] in n2[0].keys():
            return n1[0][n1[1]] == n2[0][n2[1]]
        else:
            if n1[1] in V.LM_NAMING_CONVENTION_KEYWORDS_COMMON or n2[1] in V.LM_NAMING_CONVENTION_KEYWORDS_COMMON:
                return False
            else:
                return True

    def matching_gender(self, g1, g2):
        for gg1 in g1:
            for gg2 in g2:
                if gg1 == gg2:
                    return True
        else:
            return False

    # Properties
    @property
    def texture_channel_names(self):
        texture_channels = []
        for c in self.param['lm_texture_channels']:
            if c.name.lower() not in texture_channels:
                texture_channels.append(c.name.lower())

        return texture_channels

    @property
    def asset_naming_convention(self):
        if self._asset_naming_convention is None:
            self._asset_naming_convention = self.get_asset_naming_convention()
        
        return self._asset_naming_convention
    
    @property
    def mesh_naming_convention(self):
        if self._mesh_naming_convention is None:
            self._mesh_naming_convention = self.get_mesh_naming_convention()
        
        return self._mesh_naming_convention
    
    @property
    def texture_naming_convention(self):
        if self._texture_naming_convention is None:
            self._texture_naming_convention = self.get_texture_naming_convention()
        
        return self._texture_naming_convention

    def get_asset(self):
        if len(self.asset_naming_convention) and len(self.mesh_naming_convention):
            asset = {}
            texture_set = {}
            for m in self.mesh_naming_convention:
                mesh = m['file']

                texture_naming_convention = self.get_texture_naming_convention()

                for t in texture_naming_convention[m['fullname']].keys():
                    if m['fullname'] not in texture_set.keys():
                        texture_set[t] = {}

                for basename,t in texture_naming_convention[m['fullname']].items():
                    matching_asset = True

                    for channel_name in t['channels'].keys():
                        if channel_name in self.texture_channel_names:
                            texture_set[basename][channel_name] = t['channels'][channel_name]['file']

                asset[m['fullname']] = (mesh, texture_set)
            
            return asset

        else:
            print('Lineup Maker : Asset "{}" is not valid'.format(self.asset_name))
            return None

