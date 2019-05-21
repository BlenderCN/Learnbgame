import bpy

class MeshProperty(bpy.types.PropertyGroup):
    """Property group for mesh information
    Holds all the properties for the meshes used in the animation.
    Used by the Paths-panel and the Spikes-panel"""
    mesh = bpy.props.StringProperty(name="Mesh")
    neuron_object = bpy.props.StringProperty(name="Neuron Object")
    animPaths = bpy.props.BoolProperty(name="Animate paths", default=True)
    animSpikes = bpy.props.BoolProperty(name="Animate spikes", default = False)

    spikeScale = bpy.props.FloatProperty(name = "Spike scaling", description = "How big the spikes should be at the beginning of the animation", default = 3.0)
    spikeFadeout = bpy.props.IntProperty(name = "Spike fadeout", description = "How fast the spikes should scale down, in frames", default = 15)

    spikeUseLayerColor = bpy.props.BoolProperty(name = "Use layer color", default = False)
    spikeColor = bpy.props.FloatVectorProperty(name = "Spike color", default = (1.0, 0.0, 0.0, 1.0), subtype = 'COLOR', size = 4, min = 0.0, max = 1.0)

    orientationType = bpy.props.EnumProperty(
        name="materialOption",
        items=(
            ('NONE', 'None', 'Neuron orientation is not influenced'),
            ('OBJECT', 'Object', 'The neurons are tracking a specific object, e.g. a camera'),
            ('FOLLOW', 'Follow Curve', 'The neuron orientation is following the curve')
        ),
        default='FOLLOW'
    )
    orientationObject = bpy.props.StringProperty(name="Orientation object")

    path_bevel_resolution = bpy.props.IntProperty(name = "Path resolution", min = 0, default = 8)

def register():
    """Registers the mesh properties"""
    bpy.utils.register_class(MeshProperty)
    bpy.types.Scene.pam_anim_mesh = bpy.props.PointerProperty(type=MeshProperty)


def unregister():
    """Unregisters the mesh properties"""
    del bpy.types.Scene.pam_anim_mesh
    bpy.utils.unregister_class(MeshProperty)
