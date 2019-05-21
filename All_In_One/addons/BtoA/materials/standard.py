import imp
from arnold import *

from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty)
from bl_ui import properties_material
pm = properties_material

from ..GuiUtils import pollMaterial

if "bpy" not in locals():
    import bpy

enumValue = ("STANDARD","Standard","")
class BtoAStandardMaterialSettings(bpy.types.PropertyGroup):
    # Diffuse
    Kd = FloatProperty(name="Kd", description="Diffuse Intensity",
                       max = 100, min = 0,default=0.7)
    Kd_color = FloatVectorProperty(name="Kd_color",description="Diffuse Color",
                                   default=(1,1,1),subtype='COLOR')
    diffuse_roughness = FloatProperty(name="diffuse_roughness", description="Diffuse Roughness",
                                      max = 1, min = 0,default=0)
    direct_diffuse =  FloatProperty(name="Direct Diffuse", description="",
                              min = 0,default=1)
    indirect_diffuse =  FloatProperty(name="Indirect Diffuse", description="",
                              min = 0,default=1)
    # Specular
    Ks = FloatProperty(name="Ks", description="Specular Intensity",
                       max = 100, min = 0,default=0.7)
    Ks_color = FloatVectorProperty(name="Ks_color",description="Specular Color",
                                   default=(1,1,1),subtype='COLOR')
    specular_roughness = FloatProperty(
                name="Specular Roughness", description="Specular Roughness",
                max = 1, min = 0,default=0.25)
    specular_brdf = EnumProperty(items=(("0","Stretched Phong",""),
                                 ("1","Ward Duer",""),
                                 ("2","Cook Torrance","")),
                                 name="BRDF", description="Specular BRDF", 
                                 default="0")
    specular_anisotropy = FloatProperty(
                name="Anisotropy", description="Specular Anisotropy",
                max = 1, min = 0,default=0.5)
    specular_rotation = FloatProperty(
                name="Aniso Rotation", description="Specular Anisotropy Rotation",
                max = 1, min = 0,default=0)
    Phong_exponent = FloatProperty(
                name="Phong Exponent", description="Phong Exponent",
                max = 100, min = 0,default=10)
    direct_specular =  FloatProperty(name="Direct Specular", description="",
                              min = 0,default=1)
    indirect_specular =  FloatProperty(name="Indirect Specular", description="",
                              min = 0,default=1)
    enable_glossy_caustics = BoolProperty(name="Glossy Caustics",default=False)
    # Reflection
    Kr = FloatProperty(name="Kr", description="Reflection Intensity",
                       max = 100, min = 0,default=0)
    Kr_color = FloatVectorProperty(name="Kr_color",description="Reflection Color",
                                   default=(1,1,1),subtype='COLOR')
    reflection_exit_color = FloatVectorProperty(name="Exit Color",description="Reflection Exit Color",
                                   default=(0,0,0),subtype='COLOR')
    reflection_exit_use_environment = BoolProperty(
                                        name="Use Environment",default=False)
    enable_reflective_caustics = BoolProperty(name="Reflective Caustics",default=False)
    enable_internal_reflections = BoolProperty(name="Internal Reflections",default=True)
    # Refraction
    Kt = FloatProperty(name="Kt", description="Refraction Intensity",
                       max = 100, min = 0,default=0)
    Kt_color = FloatVectorProperty(name="Kt_color",description="Refraction Color",
                                   default=(1,1,1),subtype='COLOR')
    transmittance = FloatVectorProperty(name="Transmittance Color",description="Transmittance Color",
                                   default=(1,1,1),subtype='COLOR')
    refraction_exit_color = FloatVectorProperty(name="Exit Color",description="Reraction Exit Color",
                                   default=(0,0,0),subtype='COLOR')
    refraction_exit_use_environment = BoolProperty(
                                        name="Use Environment",default=False,description="")
    IOR = FloatProperty(name="Refraction Index", description="Refraction Index",
                       max = 10, min = 0,default=1.3)
    enable_refractive_caustics = BoolProperty(name="Refractive Caustics",default=False)

    Kb =  FloatProperty(name="Bump Amount", description="",
                       max = 10, min = -10,default=1)

    Fresnel = BoolProperty(name="Fresnel",default=False,description="")
    Krn =  FloatProperty(name="Krn", description="",
                       max = 1, min = 0,default=0.5)
    Ksn =  FloatProperty(name="Ksn", description="",
                       max = 1, min = 0,default=0.5)
    specular_Fresnel = BoolProperty(name="Specular Fresnel",default=False,description="")
    Fresnel_affect_diff = BoolProperty(name="Fresnel Affect Diffuse",default=True,description="")
    # indirect contribution
    emission =  FloatProperty(name="Emission", description="",
                              min = 0,default=0)
    emission_color = FloatVectorProperty(name="Emission Color",
                        description="Emissive Color",
                        default=(1,1,1),subtype='COLOR')
    # SSS
    Ksss =  FloatProperty(name="SSS", description="",
                              min = 0,default=0)
    Ksss_color = FloatVectorProperty(name="SSS Color",
                        default=(1,1,1),subtype='COLOR')
    sss_radius = FloatVectorProperty(name="SSS Radius",
                        default=(0.1,0.1,0.1),subtype='COLOR')

    opacity = FloatVectorProperty(name="Opacity",
                        default=(1,1,1),subtype='COLOR')
    bounce_factor =  FloatProperty(name="Bounce Factor", description="",
                              min = 0,default=1)
#STRING        aov_emission                      emission
#STRING        aov_direct_diffuse                direct_diffuse
#STRING        aov_direct_specular               direct_specular
#STRING        aov_indirect_diffuse              indirect_diffuse
#STRING        aov_indirect_specular             indirect_specular
#STRING        aov_reflection                    reflection
#STRING        aov_refraction                    refraction
#STRING        aov_sss                           sss

class BtoAStandardMaterialOpacityGui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Opacity"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        return pollMaterial(cls,context,enumValue[0] )

    def draw(self, context):
        mat = pm.active_node_mat(context.material)
        if mat:
            st = mat.BtoA.standard
            layout = self.layout
            split = layout.split()
            col1 = split.column()
            col2 = split.column()
            col1.prop(st,"opacity",text="Opacity")

class BtoAStandardMaterialDiffuseGui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Diffuse"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        return pollMaterial(cls,context,enumValue[0] )

    def draw(self, context):
        mat = pm.active_node_mat(context.material)
        if mat:
            layout = self.layout
            split = layout.split()
            col1 = split.column()
            col2 = split.column()
            col1.prop(mat.BtoA.standard, "Kd_color", text="")
            col1.prop(mat.BtoA.standard, "Kd", text="Intensity")
            col2.prop(mat.BtoA.standard, "diffuse_roughness",text="Roughness")
            col2.prop(mat.BtoA.standard, "direct_diffuse",text="Direct Diffuse")
            col2.prop(mat.BtoA.standard, "indirect_diffuse",text="Indirect Diffuse")

class BtoAStandardMaterialSpecularGui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Specular"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        return pollMaterial(cls,context,enumValue[0] )

    def draw(self, context):
        mat = pm.active_node_mat(context.material)
        if mat:
            st = mat.BtoA.standard
            layout = self.layout
            split = layout.split()
            col1 = split.column()
            col2 = split.column()
            col1.prop(st, "Ks_color", text="")
            col1.prop(st, "Ks", text="Intensity")
            col2.prop(st, "specular_brdf", text="")

            col2.prop(st, "specular_roughness", text="Roughness")
            if st.specular_brdf == "1":
                col1.prop(st, "specular_anisotropy", text="Anisotropy")
                col2.prop(st, "specular_rotation", text="Rotation")
            if st.specular_brdf == "0":
                col1.prop(st,"Phong_exponent",text="Phong Exponent")

            col2.prop(st, "direct_specular", text="Direct Specular")
            col2.prop(st, "indirect_specular", text="Indirect Specular")

class BtoAStandardMaterialReflGui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Reflection"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        return pollMaterial(cls,context,enumValue[0] )

    def draw(self, context):
        mat = pm.active_node_mat(context.material)
        if mat:
            st = mat.BtoA.standard
            layout = self.layout
            split = layout.split()
            col1 = split.column()
            col2 = split.column()
            col1.prop(st,"Kr_color",text="")
            col1.prop(st,"Kr",text="Reflection")
            col2.prop(st,"reflection_exit_color",text="Exit Color")
            col2.prop(st,"reflection_exit_use_environment",text="Use Environment")
            col2.prop(st,"enable_reflective_caustics",text="Reflective Caustics")
            col2.prop(st,"enable_internal_reflections",text="Internal Reflection")

class BtoAStandardMaterialRefrGui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Refraction"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        return pollMaterial(cls,context,enumValue[0] )

    def draw(self, context):
        mat = pm.active_node_mat(context.material)
        if mat:
            st = mat.BtoA.standard
            layout = self.layout
            split = layout.split()
            col1 = split.column()
            col2 = split.column()
            col1.prop(st,"Kt_color",text="")
            col1.prop(st,"Kt",text="Refractive")
            col1.prop(st,"transmittance",text="Transmitance Col")
            col2.prop(st,"refraction_exit_color",text="Exit Color")
            col2.prop(st,"refraction_exit_use_environment",text="Use Environment")
            col2.prop(st,"IOR")
            col2.prop(st,"enable_refractive_caustics",text="Refractive Caustics")

class BtoAStandardMaterialFresnelGui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Fresnel"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        return pollMaterial(cls,context,enumValue[0] )

    def draw(self, context):
        mat = pm.active_node_mat(context.material)
        if mat:
            st = mat.BtoA.standard
            layout = self.layout
            split = layout.split()
            col1 = split.column()
            col2 = split.column()
            col1.prop(st,"Fresnel")
            col1.prop(st,"Fresnel_affect_diff",text="Diffuse Fresnel")
            col1.prop(st,"specular_Fresnel",text="Specular Fresnel")
            col2.prop(st,"Krn",text="Reflection Fresnel")
            col2.prop(st,"Ksn",text="Specular Fresnel")

class BtoAStandardMaterialEmissionGui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Emission"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        return pollMaterial(cls,context,enumValue[0] )

    def draw(self, context):
        mat = pm.active_node_mat(context.material)
        if mat:
            st = mat.BtoA.standard
            layout = self.layout
            split = layout.split()
            col1 = split.column()
            col2 = split.column()
            col1.prop(st,"emission_color",text="")
            col2.prop(st,"emission",text="Intensity")

class BtoAStandardMaterialSSSGui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Subsurface Scattering"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        return pollMaterial(cls,context,enumValue[0] )

    def draw(self, context):
        mat = pm.active_node_mat(context.material)
        if mat:
            st = mat.BtoA.standard
            layout = self.layout
            split = layout.split()
            col1 = split.column()
            col2 = split.column()
            col1.prop(st,"Ksss_color",text="")
            col1.prop(st,"Ksss",text="Intensity")
            col2.prop(st,"sss_radius",text="SSS Radius")

def write(mat,textures):
    tslots = {}
    tslots['kd_color'] = None

    if textures:
        for i in textures:
            tname = textures[i]['name']
            if tname in mat.texture_slots:
                map = mat.texture_slots[tname]
            #use_map_alpha
            #use_map_ambient
                if map.use_map_color_diffuse:
                    tslots['kd_color'] =textures[i]['pointer']
            #use_map_color_emission
            #use_map_color_reflection
            #use_map_color_spec
            #use_map_color_transmission
            #use_map_density
            #use_map_diffuse
            #use_map_displacement
            #use_map_emission
            #use_map_emit
            #use_map_hardness
            #use_map_mirror
            #use_map_normal
            #use_map_raymir
            #use_map_reflect
            #use_map_scatter
            #use_map_specular
            #use_map_translucency
            #print tname 

    standard = AiNode(b"standard")
    st = mat.BtoA.standard
    if tslots['kd_color']:
        AiNodeLink(tslots['kd_color'],b"Kd_color",standard)
    else:
        AiNodeSetRGB(standard,b"Kd_color",st.Kd_color.r,
                                          st.Kd_color.g,
                                          st.Kd_color.b)
    
    AiNodeSetFlt(standard,b"Kd",st.Kd)
    AiNodeSetFlt(standard,b"diffuse_roughness",st.diffuse_roughness)
    AiNodeSetFlt(standard,b"direct_diffuse",st.direct_diffuse)
    AiNodeSetFlt(standard,b"indirect_diffuse",st.indirect_diffuse)
    # Specular
    AiNodeSetFlt(standard,b"Ks",st.Ks)
    AiNodeSetRGB(standard,b"Ks_color",st.Ks_color.r,
                                      st.Ks_color.g,
                                      st.Ks_color.b)
    AiNodeSetFlt(standard,b"specular_roughness",st.specular_roughness)
    AiNodeSetInt(standard,b"specular_brdf",int(st.specular_brdf))
    AiNodeSetFlt(standard,b"specular_anisotropy",st.specular_anisotropy)
    AiNodeSetFlt(standard,b"specular_rotation",st.specular_rotation)
    AiNodeSetFlt(standard,b"Phong_exponent",st.Phong_exponent)
    AiNodeSetFlt(standard,b"direct_specular",st.direct_specular)
    AiNodeSetFlt(standard,b"indirect_specular",st.indirect_specular)
    AiNodeSetBool(standard,b"enable_glossy_caustics",
                  st.enable_glossy_caustics) 
    
    # Reflection
    AiNodeSetFlt(standard,b"Kr",st.Kr)
    AiNodeSetRGB(standard,b"Kr_color",st.Kr_color.r,
                                      st.Kr_color.g,
                                      st.Kr_color.b)
    AiNodeSetRGB(standard,b"reflection_exit_color",st.reflection_exit_color.r,
                                                   st.reflection_exit_color.g,
                                                   st.reflection_exit_color.b)
    AiNodeSetBool(standard,b"reflection_exit_use_environment",
                  st.reflection_exit_use_environment) 
    AiNodeSetBool(standard,b"enable_reflective_caustics",
                  st.enable_reflective_caustics) 
    AiNodeSetBool(standard,b"enable_internal_reflections",
                  st.enable_internal_reflections) 
    # Refraction
    AiNodeSetFlt(standard,b"Kt",st.Kt)
    AiNodeSetRGB(standard,b"Kt_color",st.Kt_color.r,
                                      st.Kt_color.g,
                                      st.Kt_color.b)
    AiNodeSetRGB(standard,b"refraction_exit_color",st.refraction_exit_color.r,
                                                   st.refraction_exit_color.g,
                                                   st.refraction_exit_color.b)
    AiNodeSetBool(standard,b"refraction_exit_use_environment",
                  st.refraction_exit_use_environment) 
    AiNodeSetFlt(standard,b"IOR",st.IOR)
    AiNodeSetBool(standard,b"enable_refractive_caustics",
                  st.enable_refractive_caustics)
    # Bump
    AiNodeSetFlt(standard,b"Kb",st.Kb)
    # Fresnel
    AiNodeSetBool(standard,b"Fresnel",st.Fresnel) 
    AiNodeSetBool(standard,b"Fresnel_affect_diff",st.Fresnel_affect_diff) 
    AiNodeSetBool(standard,b"specular_Fresnel",st.specular_Fresnel) 
    AiNodeSetFlt(standard,b"Krn",st.Krn)
    AiNodeSetFlt(standard,b"Ksn",st.Ksn)
    # Indirect contribution
    AiNodeSetFlt(standard,b"emission",st.emission)
    AiNodeSetRGB(standard,b"emission_color",st.emission_color.r,
                                      st.emission_color.g,
                                      st.emission_color.b)
    # SSS
    AiNodeSetFlt(standard,b"Ksss",st.Ksss)
    AiNodeSetRGB(standard,b"Ksss_color",st.Ksss_color.r,
                                        st.Ksss_color.g,
                                        st.Ksss_color.b)
    AiNodeSetRGB(standard,b"sss_radius",st.sss_radius.r,
                                        st.sss_radius.g,
                                        st.sss_radius.b)
    AiNodeSetRGB(standard,b"opacity",st.opacity.r,
                                        st.opacity.g,
                                        st.opacity.b)
    AiNodeSetFlt(standard,b"bounce_factor",st.bounce_factor)
    return standard

className= BtoAStandardMaterialSettings
bpy.utils.register_class(className)
