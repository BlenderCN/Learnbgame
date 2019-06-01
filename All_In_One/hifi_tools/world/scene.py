# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Scene Logic for Parsing and Navigating Content Tree
# By Matti 'Menithal' Lahtinen


import bpy
from hashlib import md5
from mathutils import Quaternion, Vector, Euler, Matrix

from hifi_tools.world import primitives as prims
from hifi_tools.utils.helpers import PIVOT_VECTOR, swap_nyz, swap_nzy, parse_dict_quaternion, parse_dict_vector, swap_yz, swap_pivot, quat_swap_nyz


class HifiScene:
    def __init__(self, json,
                 uv_sphere=False,
                 join_children=True,
                 merge_distance=0.01,
                 delete_interior_faces=True,
                 use_boolean_operation="NONE"):
        json_entities = json['Entities']

        self.uv_sphere = uv_sphere
        self.join_children = join_children
        self.merge_distance = merge_distance
        self.delete_interior_faces = delete_interior_faces
        self.use_boolean_operation = use_boolean_operation

        self.entities = []
        self.materials = []
        self.entity_ids = []
        self.material_index = []
        self.materials = []
        self.parent_entities = []

        self.root = []

        # Build Indices for entity ids, and build the Objects
        print(' building indices ')
        for idx, entity in enumerate(json_entities):
            self.entity_ids.append(entity['id'])
            hifi_entity = HifiObject(entity, self)
            self.entities.append(hifi_entity)

        # Build Trees by checking if parents exist in parent tree
        print(' building parents ')
        for entity in self.entities:
            self.append_parent(entity)

        self.build_scene()

    # links Parents and children together. to build a tree
    def append_parent(self, entity):
        # Check if parent id for entity exists
        result = self.search_entity(entity.parent_id)
        if result is not None:
            # add entity as a child of parent
            result.add_child(entity)
            # set parent as a parent of entity
            entity.set_parent(result)

    def search_entity(self, id):
        # TODO: May need to do some more advanced tricks here maybe later.
        found_entity = None
        try:
            # Get index of instance of the id from existing ids
            index = self.entity_ids.index(id)
            # if found, return found entity
            found_entity = self.entities[index]
        except e:
            pass
        finally:
            # Regardless of failure, always return None or the entity
            return found_entity

    def build_scene(self):
        # Store context to set cursor
        current_context = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'
        # set context to 3D View and set Cursor
        bpy.context.space_data.cursor_location[0] = 0.0
        bpy.context.space_data.cursor_location[1] = 0.0
        bpy.context.space_data.cursor_location[2] = 0.0
        # return context back to earlier, and build scene.
        bpy.context.area.type = current_context
        print("Building Scene out of " + str(len(self.entities)) + ' Objects and '
              + str(len(self.material_index)) + ' materials')

        for entity in self.entities:
            if entity.is_root():
                entity.build()

    def append_material(self, color):
        # Just Hash result

        material_hash = md5(
            str(color[0] + color[1] << 2 + color[2] << 4).encode('utf-8')).hexdigest()

        if material_hash not in self.material_index:
            index = len(self.material_index)
            self.material_index.append(material_hash)

            mat = bpy.data.materials.new(str(color))
            # convert from rgb to float
            mat.diffuse_color = tuple(c/255 for c in color)

            # Make sure material at first is not metallic
            mat.specular_color = (0, 0, 0)

            self.materials.append(mat)
            return mat

        return self.materials[self.material_index.index(material_hash)]


class HifiObject:

    def __init__(self, entity, scene):

        self.id = entity['id']
        self.children = []
        self.blender_object = None
        self.scene = scene
        # Make sure the Blender Object has a name: And to make it unique, append id of the entity as well.
        if 'name' in entity and len(entity['name'].strip()) > 0:
            self.name = entity['name'] + '-' + self.id
        elif 'shape' in entity:
            self.name = entity['shape'] + '-' + self.id
        else:
            self.name = entity['type'] + '-' + self.id

        self.position_original = Vector(parse_dict_vector(entity, 'position'))
        self.position = swap_nyz(parse_dict_vector(entity, 'position'))

        self.pivot = swap_pivot(parse_dict_vector(
            entity, 'registrationPoint', PIVOT_VECTOR))
        self.dimensions = swap_yz(parse_dict_vector(entity, 'dimensions'))

        self.rotation_original = Quaternion(
            parse_dict_quaternion(entity, 'rotation'))
        self.rotation = quat_swap_nyz(
            parse_dict_quaternion(entity, 'rotation'))

        self.parent = None
        self.children = []

        if 'parentID' in entity:
            self.parent_id = entity['parentID']
        else:
            self.parent_id = None

        self.type = entity['type']
        self.shape = None
        if 'shape' in entity:
            self.shape = entity['shape']

        if self.type != 'Light' and self.type != 'Zone' and self.type != 'Particle':
            if 'color' in entity:
                color = entity['color']
                self.material = scene.append_material(
                    (color['red'], color['green'], color['blue']))
        else:
            self.material = None

    def is_root(self):
        if self.parent is None:
            return True
        return False

    def select(self):
        self.blender_object.select = True

    def build(self):
        # First places down the children (recursive)
        for child in self.children:
            child.build()

        # Place self by selecting what primitive to add, depending on type and shape.
        # Boxes and Spheres are the only primitive to have a separate type vs others
        if self.type == 'Shape':
            if self.shape == 'Icosahedron':
                prims.add_icosahedron(self)
            elif self.shape == 'Dodecahedron':
                prims.add_docadehedron(self)
            elif self.shape == 'Cylinder':
                prims.add_cylinder(self)
            elif self.shape == 'Octagon':
                prims.add_octagon(self)
            elif self.shape == 'Hexagon':
                prims.add_hexagon(self)
            elif self.shape == 'Tetrahedron':
                prims.add_tetrahedron(self)
            elif self.shape == 'Octahedron':
                prims.add_octahedron(self)
            elif self.shape == 'Cone':
                prims.add_cone(self)
            elif self.shape == 'Triangle':
                prims.add_triangle(self)

            # The following will be deprecated, as they are no longer quads or circles when exported
            elif self.shape == 'Quad':
                prims.add_quad(self)
            elif self.shape == 'Circle':
                prims.add_circle(self)
            else:
                print(' Warning: ', self.shape, ' Not Defined ')
                return
        else:
            if self.type == "Text":
                prims.add_box(self)
            elif self.type == "Light":
                prims.add_light(self)
            elif self.type == "Model":
                prims.add_box(self)
            elif self.type == 'Sphere':
                if self.scene.uv_sphere:
                    prims.add_uv_sphere(self)
                else:
                    prims.add_sphere(self)
            elif self.type == 'Box':
                prims.add_box(self)
            else:
                print(' Warning: ', self.type, self.shape, ' Not Supported ')
                return

        # Now if above is a mesh type to do join / boolean operations on
        if self.blender_object.type == "MESH":
            for child in self.children:
                # Material Combinator to pre-combine materials prior to applying boolean operator or joining objects together
                # This allows the materials to be maintained even if they are joined.
                # for each material the child's blender objects have
                for material in child.blender_object.data.materials.values():
                    # and if the material is set, and is not yet set for the parent, add an instance of the material to the parent
                    if material is not None and material not in bpy.context.object.data.materials.values():
                        bpy.context.object.data.materials.append(material)
                # If the scene wants to use boolean operators, this overrides join children (as it is a method to join children)
                if self.scene.use_boolean_operation != "NONE":
                    bpy.ops.object.modifier_add(type='BOOLEAN')
                    # Set name for modifier to keep track of it.
                    name = child.name + '-Boolean'
                    bpy.context.object.modifiers["Boolean"].name = name
                    bpy.context.object.modifiers[name].operation = 'UNION'
                    bpy.context.object.modifiers[name].solver = self.scene.use_boolean_operation
                    bpy.context.object.modifiers[name].object = child.blender_object
                    bpy.ops.object.modifier_apply(
                        apply_as='DATA', modifier=name)
                    # Clean up the child object from the blender scene.
                    bpy.data.objects.remove(child.blender_object)
                    # TODO: Set Child.blender_object as the blender object of the parent to maintain links
                # If not boolean operator, but join_children is still True
                elif self.scene.join_children:
                    # Select the child
                    child.select()
                    # Select self
                    self.select()
                    # Join
                    bpy.ops.object.join()

            # Safety select
            self.select()

            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            bpy.ops.object.mode_set(mode='EDIT')

            if len(self.children) > 0:
                bpy.ops.mesh.remove_doubles(
                    threshold=self.scene.merge_distance)
        # endif

        # And at the end, make sure object is selected.
        bpy.ops.object.mode_set(mode='OBJECT')

    # Position and rotations of children are always relative to parent in Hifi Tree.

    # Get the absolute position by getting the relative position of the parent, and adding my own to it.
    # note that then position is relative to the parents rotation too, so make sure to eliminate that as well.
    def relative_position(self):
        if self.parent is not None:
            return self.parent.relative_rotation() * self.position + self.parent.relative_position()
        else:
            return self.position

    # Rotation is based on the rotaiton of the parent and self.
    def relative_rotation(self):
        if self.parent is not None:
            rotation = self.parent.relative_rotation()
            return rotation * self.rotation
        else:
            return self.rotation

    def set_parent(self, parent):
        if type(parent) is HifiObject:
            self.parent = parent
        else:
            print('Warning: Type parent was not HifiObject')

    def add_child(self, child):
        self.children.append(child)
