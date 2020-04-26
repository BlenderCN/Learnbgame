import bpy
import cv2
from ocvl.core.register_utils import ocvl_register, ocvl_unregister


class InitClassForNodeOperator(bpy.types.Operator):
    bl_label = ""

    @staticmethod
    def get_init_kwargs(node):
        """
        Prepare kwargs.
        Suffix _init - suffix used for initialization of class
        Prefix T1_ - prefix used for variables begging on underscore example for cv2.MSER_create()

        :param node:
        :return:
        """
        kwargs_init = {}
        for key in dir(node):
            val = getattr(node, key)
            if isinstance(val, str):
                val = getattr(cv2, val, val)
                try:
                    val = int(val)
                except (ValueError, TypeError):
                    pass

            if key.endswith("_init") and isinstance(val, (int, float, str)):
                kwargs_init[key.replace("_init", "").replace("T1_", "_")] = val
        return kwargs_init

    @staticmethod
    def update_class_instance_dict(node, node_tree, node_name):
        kwargs_init = InitClassForNodeOperator.get_init_kwargs(node)
        instance = node._init_method(**kwargs_init)
        node.loc_class_repr = str(instance)
        globa_instace_dict = node.ABC_GLOBAL_INSTANCE_DICT_NAME
        globa_instace_dict["{}.{}".format(node_tree, node_name)] = instance

    def execute(self, context):
        node_tree, node_name, *props_name = self.origin.split('|><|')
        node = bpy.data.node_groups[node_tree].nodes[node_name]
        self.update_class_instance_dict(node, node_tree, node_name)
        return {'FINISHED'}


class InitFeature2DOperator(InitClassForNodeOperator):
    bl_idname = "node.init_feature_2d"
    bl_label = "Init Feature2D"

    origin = bpy.props.StringProperty("")


class InitDescriptorMatcherOperator(InitClassForNodeOperator):
    bl_idname = "node.init_descriptor_matcher"
    bl_label = "Init DescriptorMatcher"

    origin = bpy.props.StringProperty("")


class Feature2DSaveOperator(bpy.types.Operator):
    bl_idname = "node.feature_2d_save"
    bl_label = "Feature 2D save"

    origin = bpy.props.StringProperty("")

    def execute(self, context):
        node_tree, node_name, *props_name = self.origin.split('|><|')
        node = bpy.data.node_groups[node_tree].nodes[node_name]
        return {'FINISHED'}


def register():
    ocvl_register(InitFeature2DOperator)
    ocvl_register(Feature2DSaveOperator)


def unregister():
    ocvl_unregister(InitFeature2DOperator)
    ocvl_unregister(Feature2DSaveOperator)
