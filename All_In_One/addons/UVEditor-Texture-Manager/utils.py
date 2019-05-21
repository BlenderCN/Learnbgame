'''
Copyright (C) 2017
jim159093@gmial.com

Created by Stokes Lee

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy

class Manager():
    def __init__(self):
        self._last_active_object = None
        self._last_material = None
        self._last_first_image = None
        self._support_engine = ['CYCLES', 'BLENDER_RENDER']
    
    #get bpy property 
    @property
    def uv_editor_areas(self):
        areas = bpy.context.screen.areas
        return [area for area in areas if area.type == 'IMAGE_EDITOR']
    
    @property
    def render_engine(self):
        return bpy.context.scene.render.engine
    
    @property
    def active_object(self):
        return bpy.context.scene.objects.active

    @property
    def is_support(self):
        for engine in self._support_engine:
            if engine == self.render_engine:
                return True
        return False
    
    @property
    def is_first_image_update(self):
        return self._last_first_image != self.first_image
    
    @property
    def is_material_update(self):
        return self._last_material != self.material
    
    @property
    def is_active_object_update(self):
        return self._last_active_object != self.active_object

    @property
    def last_active_object(self):
        return self._last_active_object
    
    @property
    def last_material(self):
        return self._last_material
    
    @property
    def last_first_image(self):
        return self._last_first_image

    @property
    def material(self):
        if self.active_object is not None:
            if len(self.active_object.material_slots) > 0 :
                material = self.active_object.active_material
                return material
        return None
    
    @property
    def use_nodes(self):
        return self.material.use_nodes
    
    @property
    def first_image(self):
        if not self.is_support:
            return None
        if self.material is not None:
            if self.use_nodes:
                if self.first_texture_node is not None:
                    if self.render_engine == 'CYCLES':
                        return self.first_texture_node.image
                    elif self.render_engine == 'BLENDER_RENDER':
                        return self.first_texture_node.texture.image
                else:
                    return None
            else:
                if self.first_slot_texture is not None:
                    if self.render_engine == 'CYCLES':
                        return None
                    elif self.render_engine == 'BLENDER_RENDER':
                        return self.first_slot_texture.texture.image
                else:
                    return None
        else:
            return None

    # texture_slot
    @property
    def first_slot_texture(self):
        if not self.is_support:
            return None
        texture_slots = self.material.texture_slots
        for texture in texture_slots:
            if (texture is not None) and (texture.texture.image is not None):
                return texture
        return None
    
    @property
    def slot_textures(self):
        if not self.is_support:
            return []
        texture_slots = self.material.texture_slots
        filter_textures = []
        for texture in texture_slots:
            if (texture is not None) and (texture.texture.image is not None):
                exist = False
                for filter_texture in filter_textures:
                    if filter_texture.texture.image.name == texture.texture.image.name:
                        exist = True
                        break
                if not exist:
                    filter_textures.append(texture)
        return filter_textures
        # return [texture for texture in texture_slots if (texture is not None) if (texture.texture.image is not None) ]
    
    @property
    def slot_textures_item(self):
        if not self.is_support:
            return None
        textures = self.slot_textures
        return [(str(index), 
                textures[index].texture.image.name, 
                textures[index].texture.image.name) 
                for index in range(0, len(textures))]

    # node_texture
    @property
    def first_texture_node(self):
        if not self.is_support:
            return None
        nodes = self.texture_nodes
        if self.render_engine == 'CYCLES':
            for node in nodes:
                if (node.type == 'TEX_IMAGE') and (node.image is not None):
                    return node
            return None
        elif self.render_engine == 'BLENDER_RENDER':
            for node in nodes:
                if (node.type == 'TEXTURE') and (node.texture.image is not None):
                    return node
            return None
    
    @property
    def texture_nodes(self):
        if not self.is_support:
            return []
        nodes = self.material.node_tree.nodes
        filter_nodes = []
        if self.render_engine == 'CYCLES':
            for node in nodes:
                if (node.type == 'TEX_IMAGE') and (node.image is not None):
                    exist = False
                    for filter_node in filter_nodes:
                        if node.image.name == filter_node.image.name:
                            exist = True
                            break
                    if not exist:
                        filter_nodes.append(node)
            return filter_nodes
            # return [node for node in nodes if (node.type == 'TEX_IMAGE') if (node.image is not None) ]
        elif self.render_engine == 'BLENDER_RENDER':
            for node in nodes:
                if (node.type == 'TEXTURE') and (node.texture.image is not None):
                    exist = False
                    for filter_node in filter_nodes:
                        if node.texture.image.name == filter_node.texture.image.name:
                            exist = True
                            break
                    if not exist:
                        filter_nodes.append(node)
            return filter_nodes
            # return [node for node in nodes if (node.type == 'TEXTURE') if (node.texture.image is not None)]
    
    @property
    def texture_nodes_item(self):
        if not self.is_support:
            return None
        nodes = self.texture_nodes
        if self.render_engine == 'CYCLES':
            return [(str(index), 
                    nodes[index].image.name, 
                    nodes[index].image.name) 
                    for index in range(0, len(nodes))]
        elif self.render_engine == 'BLENDER_RENDER':
            return [(str(index), 
                    nodes[index].texture.image.name, 
                    nodes[index].texture.image.name) 
                    for index in range(0, len(nodes))]
    
    # callback
    def slot_textures_item_update(self, index):
        textures = self.slot_textures
        areas = self.uv_editor_areas
        if self.render_engine == 'CYCLES':
            for area in areas:
                area.spaces.active.image = None
        elif self.render_engine == 'BLENDER_RENDER':
            if textures is not None:
                if len(textures) > index:
                    for area in areas:
                        area.spaces.active.image = textures[index].texture.image

    def texture_nodes_item_update(self, index):
        texture_nodes = self.texture_nodes
        areas = self.uv_editor_areas
        if texture_nodes is not None:
            if len(texture_nodes) > index:
                if self.render_engine == 'CYCLES':
                    for area in areas:
                        area.spaces.active.image = texture_nodes[index].image
                elif self.render_engine == 'BLENDER_RENDER':
                    for area in areas:
                        area.spaces.active.image = texture_nodes[index].texture.image
        else:
            for area in areas:
                area.spaces.active.image = None
    
    def set_first_texture(self):
        areas = self.uv_editor_areas
        for area in areas:
            area.spaces.active.image = self.first_image
    
