import bpy

"""
    Convenient class which wraps blender python API and allows multiple basic operations on cycles materials
"""


class MaterialMgr:
    def __init__(self):
        pass

    # Materials
    @staticmethod
    def get_active_material():
        """Returns bpy.data.materials[MAT_NAME] or None"""
        return bpy.context.object.active_material

    @staticmethod
    def get_material_by_name(name):
        """Returns the material associated with name. Returns None if any"""
        try:
            return bpy.data.materials[name]
        except KeyError:
            return None

    @staticmethod
    def create_new_material_for_active_obj(material_name, force=False):
        """Create a new Material and applies it to the active object obj.
                :param material_name: the name of the material as a string
                :param force: Force creation of a new material even if a material with the same name already exist,
                              the material is assigned to the object
                """
        active_obj = bpy.context.active_object
        return MaterialMgr.create_new_material(material_name, active_obj, force)

    @staticmethod
    def create_new_material(material_name, obj=None, force=False, engine='CYCLES'):
        """Create a new Material and applies it to object obj.
        :param material_name: the name of the material as a string
        :param obj: Reference to the object to which the material will be assigned or None
        :param force: Force creation of a new material even if a material with the same name already exist, the material
        :param engine: Engine for the new material to create
                      is assigned to the object
        """
        current_engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = engine
        mat = MaterialMgr.get_material_by_name(material_name)
        if force or not mat:
            mat = bpy.data.materials.new(name=material_name)
            mat.use_nodes = True

        if obj:
            obj.data.materials.append(mat)

        bpy.context.scene.render.engine = current_engine
        return mat

    def remove_material(self, name):
        """
        Remove a material from
        :param name:
        :return:
        """
        mat = MaterialMgr.get_material_by_name(name)
        if not mat:
            return False
        else:
            bpy.data.materials.remove(mat)
            return True

    # Material nodes
    @staticmethod
    def deselect_all_nodes():
        """Deselect all nodes in the view
        :return: Returns {'FINISHED'} if sucessfull and {'CANCELLED'} otherwise
        """
        for area in bpy.context.screen.areas:
            if area.type == "NODE_EDITOR":
                override = {'screen': bpy.context.screen, 'area': area}
                return bpy.ops.node.select_all(override, action='DESELECT')
        return {'CANCELLED'}

    @staticmethod
    def get_material_tree(mat):
        return mat.node_tree;

    def get_material_nodes(self, mat):
        """Returns the nodes in the material
        :param mat:
        :return:
        """
        tree = self.get_material_tree(mat)
        return tree.nodes

    def add_node(self, mat, node_name, node_type="ShaderNodeBsdfPrincipled", location=(0, 0)):
        """
        Adds a node to the tree. Returns the created node.
        :param mat: The material
        :param node_type: node_type: String - Any of the ShaderNode listed here https://docs.blender.org/api/blender_python_api_current/bpy.types.ShaderNode.html
        :param location: Tuple - Position of the node as shown in the node editor
        :return: the new node
        """
        nodes = self.get_material_nodes(mat)
        new_node = nodes.new(node_type)
        new_node.name = node_name
        new_node.location = location
        return new_node

    def add_group_node(self, mat, node_name, location=(0, 0)):
        """
        Adds a group node to the target material
        :param mat:
        :param node_name:
        :param location:
        :return:
        """
        group = self.add_node(mat, node_name, "ShaderNodeGroup", location)
        group.node_tree = bpy.data.node_groups[node_name]
        return group

    def link_nodes(self, mat, nodeA, outputAIndex, nodeB, inputBIndex):
        """
        Links two nodes together
        :param mat: The target material
        :param nodeA: The node with the output socket
        :param outputAIndex: output socket index of the node A
        :param nodeB:  The node with the input socket
        :param inputBIndex: Input socket index of the node B
        :return: the link between the two nodes as NodeLinks object
        """
        tree = self.get_material_tree(mat)
        link = tree.links.new(nodeA.outputs[outputAIndex], nodeB.inputs[inputBIndex])
        return link

    def unlink_all_nodes(self, mat):
        """
        Unlinks all nodes
        :param mat:
        :return: None
        """
        tree = self.get_material_tree(mat)
        tree.links.clear()

    def get_material_links(self, mat):
        """Returns a list of links as NodeLink objects among material nodes"""
        tree = self.get_material_tree(mat)
        return tree.links

    def node_type(self, node):
        """
        Returns the type of the node
        :param node:
        :return: type of the node as string
        """
        return node.bl_rna.identifier

    @staticmethod
    def clear(mat):
        """Removes all nodes for the target material"""
        nodes = mat.node_tree.nodes
        for node in nodes:
            nodes.remove(node)
