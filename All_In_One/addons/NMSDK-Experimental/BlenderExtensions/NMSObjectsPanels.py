# All the custom panels and properties for all the different object types

import bpy
from bpy.props import (StringProperty, BoolProperty, EnumProperty,  # noqa pylint: disable=import-error, no-name-in-module
                       FloatProperty, IntVectorProperty)
from .MiscFunctions import has_parent

""" Various properties for each of the different node types """


class NMSNodeProperties(bpy.types.PropertyGroup):
    """ Properties for the NMS Nodes """
    node_types = EnumProperty(
        name="Node Types",
        description="Select what type of Node this will be",
        items=[("Mesh", "Mesh", "Standard mesh for visible objects."),
               ("Collision", "Collision", "Shape of collision for object."),
               ("Locator", "Locator",
                "Locator object, used for interaction locations etc."),
               ("Reference", "Reference",
                "Node used to allow other scenes to be placed at this point "
                "in space."),
               # TODO: remove this description if not true?
               ("Joint", "Joint",
                "Node used primarily for animations. All meshes that are to "
                "be animated MUST be a direct child of a joint object."),
               ("Light", "Light",
                "Light that will emit light of a certain colour."),
               ("None", "None",
                "Object that will not be exported.")])
    override_name = StringProperty(
        name="Override name",
        description=("A name to be used to override the name given from "
                     "blender. This should be used with caution and sparingly."
                     " Only use if you require multiple nodes in the scene to "
                     "have the same name. Will not work for Collisions."))


class NMSMeshProperties(bpy.types.PropertyGroup):
    has_entity = BoolProperty(
        name="Requires Entity",
        description="Whether or not the mesh requires an entity file. "
                    "Not all meshes require an entity file. Read the detailed "
                    "guidelines in the readme for more details.",
        default=False)
    material_path = StringProperty(
        name="Material",
        description="(Optional) Path to material mbin file to use instead "
                    "of automatical exporting material attached to this mesh.")


class NMSMaterialProperties(bpy.types.PropertyGroup):
    material_additions = IntVectorProperty(
        name="Force material properties",
        description="List of flags to be added (use int prefix). Ie. "
                    "'_F14_UVSCROLL' == 14",
        min=0, max=64, soft_min=0, soft_max=64, size=5)


class NMSLightProperties(bpy.types.PropertyGroup):
    intensity_value = FloatProperty(name="Intensity",
                                    description="Intensity of the light.")
    FOV_value = FloatProperty(
        name="FOV", description="Field of View of the lightsource.",
        default=360, min=0, max=360)


class NMSAnimationProperties(bpy.types.PropertyGroup):
    anim_name = StringProperty(
        name="Animation Name",
        description="Name of the animation. All animations with the same "
                    "name here will be combined into one.")
    anim_loops_choice = EnumProperty(
        name="Animation Type", description="Type of animation",
        items=[("OneShot", "OneShot", "Animation runs once (per trigger)"),
               ("Loop", "Loop", "Animation loops continuously")])


class NMSLocatorProperties(bpy.types.PropertyGroup):
    has_entity = BoolProperty(
        name="Requires Entity",
        description="Whether or not the mesh requires an entity file. Not "
                    "all meshes require an entity file. Read the detailed "
                    "guidelines in the readme for more details.",
        default=False)


class NMSRotationProperties(bpy.types.PropertyGroup):
    speed = FloatProperty(
        name="Speed",
        description="Speed of the rotation around the specified axis.")


class NMSReferenceProperties(bpy.types.PropertyGroup):
    reference_path = StringProperty(
        name="Reference Path",
        description="Path to scene to be referenced at this location.")


class NMSSceneProperties(bpy.types.PropertyGroup):
    export_directory = StringProperty(
        name="Export Directory",
        description="The base path under which all models will be exported.",
        default="CUSTOMMODELS")
    group_name = StringProperty(
        name="Group Name",
        description="Group name so that models that all belong in the same "
                    "folder are placed there (path becomes group_name/name)")
    batch_mode = BoolProperty(
        name="Batch Mode",
        description="If ticked, each direct child of this node will be "
                    "exported separately",
        default=False)
    create_tangents = BoolProperty(
        name="Create Tangents",
        description="Whether or not to generate tangents along with the mesh",
        default=True)
    # !REMOVE
    dont_compile = BoolProperty(
        name="Don't compile to .mbin",
        description="Whether or not to recompile exml files to mbin.",
        default=False)
    AT_only = BoolProperty(
        name="ActionTriggers Only",
        description="If this box is ticked, all the action trigger data will "
                    "be exported directly to an ENTITY file in the specified "
                    "location with the project name. Anything else in the "
                    "project is ignored",
        default=False)
    is_proc = BoolProperty(
        name="Is a proc-gen scene?",
        description="If checked, then a new panel will appear that can be "
                    "used to describe the proc-gen nature of the scene",
        default=False)


class NMSCollisionProperties(bpy.types.PropertyGroup):
    collision_types = EnumProperty(
        name="Collision Types",
        description="Type of collision to be used",
        items=[  # ("Mesh" , "Mesh" , "Mesh Collision"),
               ("Box", "Box", "Box (rectangular prism collision"),
               ("Sphere", "Sphere", "Spherical collision"),
               ("Cylinder", "Cylinder", "Cylindrical collision")])
    transform_type = EnumProperty(
        name="Scale Transform",
        description="Whether or not to use the transform data, or the "
                    "dimensions of the primitive",
        items=[("Transform", "Transform", "Use Scale transform data"),
               ("Dimensions", "Dimensions", "Use the inherent object "
                                            "dimensions (will also retain the "
                                            "transform data in the scene)")])


class NMSDescriptorProperties(bpy.types.PropertyGroup):
    choice_types = EnumProperty(
        name="Proc type",
        description="Whether or not to have the model always eselected, or "
                    "randomly selected.",
        items=[("Always", "Always", "Node is always rendered (provided "
                                    "parents are rendered)"),
               ("Random", "Random", "Node is randomly selected out of all "
                                    "others in the same hierarchy")])
    proc_prefix = StringProperty(
        name="Proc prefix",
        description="The prefix to put in front of the part name to indicate "
                    "what procedural rule to be grouped with.")


""" Various panels for each of the property types """


class NMSNodePropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Node Properties"
    bl_idname = "OBJECT_PT_node_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if (has_parent(context.object, 'NMS_SCENE') and not
                context.object.name.startswith("NMS_SCENE")):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSNode_props, "node_types", expand=True)
        row = layout.row()
        row.prop(obj.NMSNode_props, "override_name")


class NMSReferencePropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Reference Properties"
    bl_idname = "OBJECT_PT_reference_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if (has_parent(context.object, 'NMS_SCENE') and
                context.object.NMSNode_props.node_types == 'Reference' and not
                context.object.name.startswith("NMS_SCENE")):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSReference_props, "reference_path")


class NMSMaterialPropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Material Properties"
    bl_idname = "MATERIAL_PT_material_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if (has_parent(context.object, 'NMS_SCENE') and
                context.object.NMSNode_props.node_types == 'Mesh' and not
                context.object.name.startswith("NMS_SCENE")):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSMaterial_props, "material_additions")


class NMSMeshPropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Mesh Properties"
    bl_idname = "OBJECT_PT_mesh_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if (has_parent(context.object, 'NMS_SCENE') and
                context.object.NMSNode_props.node_types == 'Mesh' and not
                context.object.name.startswith("NMS_SCENE")):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSMesh_props, "has_entity")
        row = layout.row()
        row.prop(obj.NMSMesh_props, "material_path")


class NMSAnimationPropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Animation Properties"
    bl_idname = "OBJECT_PT_animation_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if (has_parent(context.object, 'NMS_SCENE') and
                context.object.animation_data and not
                context.object.name.startswith("NMS_SCENE")):
            if context.object.animation_data.action:
                return True
            else:
                return False
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSAnimation_props, "anim_name")
        row = layout.row()
        row.prop(obj.NMSAnimation_props, "anim_loops_choice", expand=True)


class NMSLocatorPropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Locator Properties"
    bl_idname = "OBJECT_PT_locator_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if (has_parent(context.object, 'NMS_SCENE') and
                context.object.NMSNode_props.node_types == 'Locator' and not
                context.object.name.startswith("NMS_SCENE")):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSLocator_props, "has_entity")


class NMSRotationPropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Rotation Properties"
    bl_idname = "OBJECT_PT_rotation_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if (has_parent(context.object, 'NMS_SCENE') and
                context.object.name.upper() == 'ROTATION' and not
                context.object.name.startswith("NMS_SCENE")):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSRotation_props, "speed")


class NMSLightPropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Light Properties"
    bl_idname = "OBJECT_PT_light_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if (has_parent(context.object, 'NMS_SCENE') and
                context.object.NMSNode_props.node_types == 'Light' and not
                context.object.name.startswith("NMS_SCENE")):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSLight_props, "intensity_value")
        row = layout.row()
        row.prop(obj.NMSLight_props, "FOV_value")


class NMSCollisionPropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Collision Properties"
    bl_idname = "OBJECT_PT_collision_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if (has_parent(context.object, 'NMS_SCENE') and
                context.object.NMSNode_props.node_types == 'Collision' and not
                context.object.name.startswith("NMS_SCENE")):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSCollision_props, "collision_types", expand=True)
        row = layout.row()
        row.prop(obj.NMSCollision_props, "transform_type", expand=True)


class NMSScenePropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Scene Properties"
    bl_idname = "OBJECT_PT_scene_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        # this should only show for an object that is called NMS_SCENE
        if context.object.name.startswith("NMS_SCENE"):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSScene_props, "export_directory", expand=True)
        row = layout.row()
        row.prop(obj.NMSScene_props, "group_name", expand=True)
        row = layout.row()
        row.prop(obj.NMSScene_props, "batch_mode")
        row = layout.row()
        row.prop(obj.NMSScene_props, "create_tangents")
        row = layout.row()
        row.prop(obj.NMSScene_props, "dont_compile")
        row = layout.row()
        row.prop(obj.NMSScene_props, "AT_only")
        row = layout.row()
        row.prop(obj.NMSScene_props, "is_proc")


class NMSDescriptorPropertyPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "NMS Descriptor Properties"
    bl_idname = "OBJECT_PT_descriptor_properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        try:
            if (has_parent(context.object, 'NMS_SCENE')
                and (context.object.NMSNode_props.node_types == 'Mesh' or
                     context.object.NMSNode_props.node_types == "Locator" or
                     context.object.NMSNode_props.node_types == "Reference")
                and bpy.context.scene.objects['NMS_SCENE'].NMSScene_props.is_proc is True  # noqa
                and not context.object == bpy.context.scene.objects['NMS_SCENE']):  # noqa
                return True
            else:
                return False
        except:     # TODO: what should this be catching??  # noqa
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.prop(obj.NMSDescriptor_props, "choice_types", expand=False)
        row = layout.row()
        row.prop(obj.NMSDescriptor_props, "proc_prefix")


class NMSPanels():
    @staticmethod
    def register():
        # register the properties
        bpy.utils.register_class(NMSNodeProperties)
        bpy.utils.register_class(NMSSceneProperties)
        bpy.utils.register_class(NMSMeshProperties)
        bpy.utils.register_class(NMSMaterialProperties)
        bpy.utils.register_class(NMSReferenceProperties)
        bpy.utils.register_class(NMSLocatorProperties)
        bpy.utils.register_class(NMSLightProperties)
        bpy.utils.register_class(NMSRotationProperties)
        bpy.utils.register_class(NMSAnimationProperties)
        bpy.utils.register_class(NMSCollisionProperties)
        bpy.utils.register_class(NMSDescriptorProperties)
        # link the properties with the objects' internal variables
        bpy.types.Object.NMSNode_props = bpy.props.PointerProperty(
            type=NMSNodeProperties)
        bpy.types.Object.NMSScene_props = bpy.props.PointerProperty(
            type=NMSSceneProperties)
        bpy.types.Object.NMSMesh_props = bpy.props.PointerProperty(
            type=NMSMeshProperties)
        bpy.types.Object.NMSMaterial_props = bpy.props.PointerProperty(
            type=NMSMaterialProperties)
        bpy.types.Object.NMSReference_props = bpy.props.PointerProperty(
            type=NMSReferenceProperties)
        bpy.types.Object.NMSLocator_props = bpy.props.PointerProperty(
            type=NMSLocatorProperties)
        bpy.types.Object.NMSRotation_props = bpy.props.PointerProperty(
            type=NMSRotationProperties)
        bpy.types.Object.NMSLight_props = bpy.props.PointerProperty(
            type=NMSLightProperties)
        bpy.types.Object.NMSAnimation_props = bpy.props.PointerProperty(
            type=NMSAnimationProperties)
        bpy.types.Object.NMSCollision_props = bpy.props.PointerProperty(
            type=NMSCollisionProperties)
        bpy.types.Object.NMSDescriptor_props = bpy.props.PointerProperty(
            type=NMSDescriptorProperties)
        # register the panels
        bpy.utils.register_class(NMSScenePropertyPanel)
        bpy.utils.register_class(NMSNodePropertyPanel)
        bpy.utils.register_class(NMSMeshPropertyPanel)
        bpy.utils.register_class(NMSMaterialPropertyPanel)
        bpy.utils.register_class(NMSReferencePropertyPanel)
        bpy.utils.register_class(NMSLocatorPropertyPanel)
        bpy.utils.register_class(NMSRotationPropertyPanel)
        bpy.utils.register_class(NMSLightPropertyPanel)
        bpy.utils.register_class(NMSAnimationPropertyPanel)
        bpy.utils.register_class(NMSCollisionPropertyPanel)
        bpy.utils.register_class(NMSDescriptorPropertyPanel)

    @staticmethod
    def unregister():
        # unregister the property classes
        bpy.utils.unregister_class(NMSNodeProperties)
        bpy.utils.unregister_class(NMSSceneProperties)
        bpy.utils.unregister_class(NMSMeshProperties)
        bpy.utils.unregister_class(NMSMaterialProperties)
        bpy.utils.unregister_class(NMSRotationProperties)
        bpy.utils.unregister_class(NMSReferenceProperties)
        bpy.utils.unregister_class(NMSLocatorProperties)
        bpy.utils.unregister_class(NMSLightProperties)
        bpy.utils.unregister_class(NMSAnimationProperties)
        bpy.utils.unregister_class(NMSCollisionProperties)
        bpy.utils.unregister_class(NMSDescriptorProperties)
        # delete the properties from the objects
        del bpy.types.Object.NMSNode_props
        del bpy.types.Object.NMSScene_props
        del bpy.types.Object.NMSMesh_props
        del bpy.types.Object.NMSMaterial_props
        del bpy.types.Object.NMSReference_props
        del bpy.types.Object.NMSRotation_props
        del bpy.types.Object.NMSLocator_props
        del bpy.types.Object.NMSLight_props
        del bpy.types.Object.NMSAnimation_props
        del bpy.types.Object.NMSCollision_props
        del bpy.types.Object.NMSDescriptor_props
        # unregister the panels
        bpy.utils.unregister_class(NMSScenePropertyPanel)
        bpy.utils.unregister_class(NMSNodePropertyPanel)
        bpy.utils.unregister_class(NMSMeshPropertyPanel)
        bpy.utils.unregister_class(NMSMaterialPropertyPanel)
        bpy.utils.unregister_class(NMSReferencePropertyPanel)
        bpy.utils.unregister_class(NMSLocatorPropertyPanel)
        bpy.utils.unregister_class(NMSRotationPropertyPanel)
        bpy.utils.unregister_class(NMSLightPropertyPanel)
        bpy.utils.unregister_class(NMSAnimationPropertyPanel)
        bpy.utils.unregister_class(NMSCollisionPropertyPanel)
        bpy.utils.unregister_class(NMSDescriptorPropertyPanel)
