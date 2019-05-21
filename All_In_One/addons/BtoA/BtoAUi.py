import bpy
from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
                       IntProperty, FloatProperty, FloatVectorProperty,
                       EnumProperty, PointerProperty)

# Use some of the existing buttons.
from bl_ui import properties_render
properties_render.RENDER_PT_render.COMPAT_ENGINES.add('BtoA')
properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add('BtoA')
# properties_render.RENDER_PT_antialiasing.COMPAT_ENGINES.add('POVRAY_RENDER')
#properties_render.RENDER_PT_shading.COMPAT_ENGINES.add('BtoA')
properties_render.RENDER_PT_output.COMPAT_ENGINES.add('BtoA')
del properties_render

class BtoASceneSettings(bpy.types.PropertyGroup):
    name="BtoASceneSettings"
    # Sampling
    AA_samples = IntProperty(name="Global Samples",
                             description="Number of samples per pixel",
                             min=-10, max=32, default=2)
    AA_pattern = EnumProperty(items=(("0","regular",""),
                             ("1","random",""),
                             ("2","jittered",""),
                             ("3","multi_jittered",""),
                             ("4","poisson_bc",""),
                             ("5","dithered",""),
                             ("6","nrooks",""),
                             ("7","schlick","")), 
                             name="Pattern", description="AA pattern", default="3")
    AA_seed = IntProperty(name="Seed", description="Seed for samples",
                          min=-1000, max=1000, default=1)
    AA_motionblur_pattern = EnumProperty(items=(("0","regular",""),
                             ("1","random",""),
                             ("2","jittered",""),
                             ("3","multi_jittered",""),
                             ("4","poisson_bc",""),
                             ("5","dithered",""),
                             ("6","nrooks",""),
                             ("7","schlick","")), 
                             name="MBlur Pattern", description="Motionblur pattern",
                             default="2")
    AA_sample_clamp = FloatProperty(name="Sample Clamp",
                                    description="Clamp distance",default=1e+30)
    AA_clamp_affect_aovs = BoolProperty(name="Clamp AOVs", 
                                        description="Clamp affects AOVs")
    AA_sampling_dither = IntProperty(name="Dither", description="Dither for samples",
                                     min=0, max=100, default=4)
    # GI Settings
    GI_diffuse_samples = IntProperty(name="GI Diffuse",
                                     description="Number of samples for GI diffuse",
                                     min=0, max=32, default=2)
    GI_glossy_samples = IntProperty(name="GI Glossy",
                                    description="Number of samples for GI glossy",
                                    min=0, max=32, default=2)
    GI_diffuse_depth = IntProperty(name="Diffuse Depth",
                                description="Number of bounces for GI diffuse",
                                min=0, max=32, default=2)
    GI_glossy_depth = IntProperty(name="Glossy Depth",
                                description="Number of bounces for glossy",
                                 min=0, max=32, default=2)
    GI_reflection_depth = IntProperty(name="Reflection",
                                    description="Number of bounces for reflection",
                                    min=0, max=32, default=2)
    GI_refraction_depth = IntProperty(name="Refraction",
                                    description="Number of bounces for refraction",
                                    min=0, max=32, default=2)
    # interactive settings
    progressive_min = IntProperty(name="Progressive Min",
                                description="lowest sample for progressive",
                                min=-20, max=0, default=-3)
    enable_progressive = BoolProperty(name="Progressive", 
                                    description="Enable Progressive Rendering",
                                    default=True)
    bucket_size = IntProperty(name="Bucket Size",
                            description="Size of buckets",
                            min=8, max=1024, default=64)
    bucket_scanning = EnumProperty(items=(("-1","Bucket Scan",""),
                                ("0","top",""),
                                ("1","bottom",""),
                                ("2","letf",""),
                                ("3","right",""),
                                ("4","random",""),
                                ("5","woven",""),
                                ("6","spiral",""),
                                ("7","hilbert","")), 
                                name="", description="bucket scanning",
                                default="0")

bpy.utils.register_class(BtoASceneSettings)
bpy.types.Scene.BtoA = PointerProperty(type=BtoASceneSettings,name='BtoA')

class RenderButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return (rd.use_game_engine == False) and (rd.engine in cls.COMPAT_ENGINES)

class BtoA_interactive_settings(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Interactive Settings"
    COMPAT_ENGINES = {'BtoA'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        BtoA = scene.BtoA
        rd = scene.render
        split = layout.split()
        col = split.column()
        col.prop(BtoA, "enable_progressive")
        col.prop(BtoA,"bucket_size")
        col2 = split.column()
        col2.prop(BtoA,"progressive_min")
        col2.label(text="Bucket Scanning")
        col2.prop(BtoA,"bucket_scanning")

class BtoA_render_sample_settings(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Sampler Settings"
    COMPAT_ENGINES = {'BtoA'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        BtoA = scene.BtoA
        rd = scene.render
        split = layout.split()
        col = split.column()
        col.label(text="Anti-Aliasing")
        split = layout.split()
        col = split.column()
        col.prop(BtoA, "AA_samples")
        col2 = split.column()
        col2.prop(BtoA,"AA_pattern")
        col.prop(BtoA,"AA_seed")
        col2.prop(BtoA,"AA_motionblur_pattern")       
        col.prop(BtoA,"AA_sample_clamp")
        col2.prop(BtoA,"AA_clamp_affect_aovs")       
        col.prop(BtoA,"AA_sampling_dither")
 
        split = layout.split()
        col = split.column()
        col.label(text="GI Samples")
        split = layout.split()
        col = split.column()
        col.prop(BtoA,"GI_diffuse_samples")
        col2 = split.column()
        col2.prop(BtoA,"GI_glossy_samples")

class BtoA_render_raydepth_settings(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Ray Depth"
    COMPAT_ENGINES = {'BtoA'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        BtoA = scene.BtoA
        rd = scene.render
        split = layout.split()
        col1 = split.column()
        col2 = split.column()
        col1.prop(BtoA, "GI_diffuse_depth")
        col1.prop(BtoA,"GI_reflection_depth")
        col2.prop(BtoA,"GI_glossy_depth")
        col2.prop(BtoA,"GI_refraction_depth")

