import bpy

class SomeAddonPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    # here you define the addons customizable props

    bool_baseColor = bpy.props.StringProperty(name= "Basecolor",  default=True)
    bool_roughnessMetalnessAO = bpy.props.StringProperty(name="RMA (roughnessMetalnessAo)", default=True)
    bool_normal = bpy.props.StringProperty(name="Normal", default=True)
    bool_emissive = bpy.props.StringProperty(name="Emissive", default=False)
    bool_roughness = bpy.props.StringProperty(name="Roughness", default=False)
    bool_metalness = bpy.props.StringProperty(name="Metalness", default=False)
    bool_ambientOcclussion = bpy.props.StringProperty(name="AmbientOcclusion", default=False)

    baseColorSuf = bpy.props.StringProperty(name= "Basecolor Suffix",  default="_B")
    normalSuf = bpy.props.StringProperty(name= "Basecolor Suffix",  default="_N")
    roughnessMetalnessAOSuf = bpy.props.StringProperty(name="RMA (roughnessMetalnessAo)", default="_RMA")
    emissiveSuf = bpy.props.StringProperty(name="Emissive", default="_E")
    roughnessSuf = bpy.props.StringProperty(name="Roughness", default="_R")
    metalnessSuf = bpy.props.StringProperty(name="Metalness", default="_M")
    ambientOcclussionSuf = bpy.props.StringProperty(name="AmbientOcclusion", default="_AO")

    props = [
        "bool_baseColor",
        "bool_roughnessMetalnessAO",
        "bool_normal",
        "bool_emissive",
        "bool_roughness",
        "bool_metalness",
        "bool_ambientOcclussion",

        "baseColorSuf",
        "normalSuf",
        "roughnessMetalnessAOSuf",
        "emissiveSuf",
        "roughnessSuf",
        "metalnessSuf",
        "ambientOcclussionSuf"
    ]


    # here you specify how they are drawn
    def draw(self, context):
        layout = self.layout
        for propName in self.props:
            raw = layout.raw()
            raw.prop(self, propName)
