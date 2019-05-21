import bpy

class MaterialProperty(bpy.types.PropertyGroup):
    diffuse_color = bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=[1.0,1.0,1.0])
    diffuse_weight = bpy.props.FloatProperty(name="Weight", default=0.7)
    roughness = bpy.props.FloatProperty(name="Roughness", default=0.0)
    backlighting_weight = bpy.props.FloatProperty(name="Backlight", default=0.0)

    specular_color = bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=[1.0,1.0,1.0])
    specular_weight = bpy.props.FloatProperty(name="Weight", default=0.2)
    specular_mode = bpy.props.EnumProperty(name="Mode", items=[('ward', 'Ward', ''), ('ggx', 'GGX', '')], default='ward')
    glossiness = bpy.props.FloatProperty(name="Glossiness", default=90.0)
    anisotropy = bpy.props.FloatProperty(name="Anisotropy", default=0.0)
    rotation = bpy.props.FloatProperty(name="Rotation", default=0.0)
    fresnel_ior_glossy = bpy.props.FloatProperty(name="Fresnel_ior", default=1.5)

    transparency_color = bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=[1.0,1.0,1.0])
    transparency_weight = bpy.props.FloatProperty(name="Weight", default=0.0)

    reflection_color = bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=[1.0,1.0,1.0])
    reflection_weight = bpy.props.FloatProperty(name="Weight", default=0.0)
    fresnel_ior = bpy.props.FloatProperty(name="IOR", default=1.5)

    refraction_color = bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=[1.0,1.0,1.0])
    refraction_weight = bpy.props.FloatProperty(name="Weight", default=0.0)
    refraction_glossiness = bpy.props.FloatProperty(name="Glossiness", default=100.0)
    ior = bpy.props.FloatProperty(name="IOR", default=1.5)

class ElaraDiffusePanel(bpy.types.Panel):
    bl_label = "Diffues"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'elara_renderer'}
    bl_context = "material"

    @classmethod
    def poll(self, context):
        engine = context.scene.render.engine
        return engine in self.COMPAT_ENGINES and context.object.active_material is not None

    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        elara_mat = material.elara_mat

        row = layout.row(align=True)
        row.prop(elara_mat, "diffuse_weight", text="Weight")
        row.prop(elara_mat, "diffuse_color", text="")
        row = layout.row(align=True)
        row.prop(elara_mat, "roughness", text="Roughness")
        row.prop(elara_mat, "backlighting_weight", text="Backlight")

class ElaraSpecularPanel(bpy.types.Panel):
    bl_label = "Specular"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'elara_renderer'}
    bl_context = "material"

    @classmethod
    def poll(self, context):
        engine = context.scene.render.engine
        return engine in self.COMPAT_ENGINES and context.object.active_material is not None

    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        elara_mat = material.elara_mat

        layout.prop(elara_mat, "specular_mode", text="Mode")
        row = layout.row(align=True)
        row.prop(elara_mat, "specular_weight", text="Weight")
        row.prop(elara_mat, "specular_color", text="")
        row = layout.row(align=True)
        row.prop(elara_mat, "glossiness", text="Glossiness")
        row.prop(elara_mat, "fresnel_ior_glossy", text="IOR")
        row = layout.row(align=True)
        row.prop(elara_mat, "anisotropy", text="Anisotropy")
        row.prop(elara_mat, "rotation", text="Rotation")

class ElaraTransparencyPanel(bpy.types.Panel):
    bl_label = "Transparency"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'elara_renderer'}
    bl_context = "material"

    @classmethod
    def poll(self, context):
        engine = context.scene.render.engine
        return engine in self.COMPAT_ENGINES and context.object.active_material is not None

    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        elara_mat = material.elara_mat

        row = layout.row(align=True)
        row.prop(elara_mat, "transparency_weight", text="Weight")
        row.prop(elara_mat, "transparency_color", text="")

class ElaraReflectionPanel(bpy.types.Panel):
    bl_label = "Mirror Reflection"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'elara_renderer'}
    bl_context = "material"

    @classmethod
    def poll(self, context):
        engine = context.scene.render.engine
        return engine in self.COMPAT_ENGINES and context.object.active_material is not None

    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        elara_mat = material.elara_mat

        row = layout.row(align=True)
        row.prop(elara_mat, "reflection_weight", text="Weight")
        row.prop(elara_mat, "reflection_color", text="")
        row = layout.row(align=True)
        row.prop(elara_mat, "fresnel_ior", text="IOR")

class ElaraRefractionPanel(bpy.types.Panel):
    bl_label = "Refraction"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'elara_renderer'}
    bl_context = "material"

    @classmethod
    def poll(self, context):
        engine = context.scene.render.engine
        return engine in self.COMPAT_ENGINES and context.object.active_material is not None


    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        elara_mat = material.elara_mat

        row = layout.row(align=True)
        row.prop(elara_mat, "refraction_weight", text="Weight")
        row.prop(elara_mat, "refraction_color", text="")
        row = layout.row(align=True)
        row.prop(elara_mat, "refraction_glossiness", text="Glossiness")
        row.prop(elara_mat, "ior", text="IOR")

def register():
    bpy.types.MATERIAL_PT_context_material.COMPAT_ENGINES.add('elara_renderer')
    bpy.utils.register_class(MaterialProperty)
    bpy.utils.register_class(ElaraDiffusePanel)
    bpy.utils.register_class(ElaraSpecularPanel)
    bpy.utils.register_class(ElaraTransparencyPanel)
    bpy.utils.register_class(ElaraReflectionPanel)
    bpy.utils.register_class(ElaraRefractionPanel)
    bpy.types.Material.elara_mat = bpy.props.PointerProperty(type=MaterialProperty)

def unregister():
    bpy.utils.unregister_class(MaterialProperty)
    bpy.utils.unregister_class(ElaraDiffusePanel)
    bpy.utils.unregister_class(ElaraSpecularPanel)
    bpy.utils.unregister_class(ElaraTransparencyPanel)
    bpy.utils.unregister_class(ElaraReflectionPanel)
    bpy.utils.unregister_class(ElaraRefractionPanel)
    del bpy.types.Material.elara_mat