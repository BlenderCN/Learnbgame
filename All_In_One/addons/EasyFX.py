bl_info = {
    "name": "EasyFX",
    "description": "Do post-production in the Image Editor",
    "author": "Nils Soderman (rymdnisse)",
    "version": (1, 0, 0),
    "blender": (2, 75, 0),
    "location": "UV/Image Editor > Tool Shelf",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render"
}

import bpy, math

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
# ------------------------------------------------------------------------
#    variables
# ------------------------------------------------------------------------

s_sky = False
s_cell = True
first = True
imgs =""
skyimg = ""



        
def Auto_Update(self, context):
    if bpy.context.scene.easyfx.use_auto_update == True:
        bpy.ops.object.update_operator()


# ------------------------------------------------------------------------
#    store properties
# ------------------------------------------------------------------------

class MySettings(PropertyGroup):

    # Nodes
    use_auto_update = BoolProperty(
        name="Auto Update",
        description="Automatically update when a value is altered",
        default = True, update=Auto_Update)
    # Filters
    use_vignette = BoolProperty(
        name="Vignette",
        description="Gradual decrease in light intensity towards the image borders",
        default = False, update=Auto_Update)
    vignette_v = FloatProperty(name="Viggnette Amount",description="Amount", default=70, min=0, max=100, subtype="PERCENTAGE", update=Auto_Update)
    use_glow = BoolProperty(
        name="Glow",
        description="Glow",
        default = False, update=Auto_Update)
    glow_em = BoolProperty(
        name="Only Emission",
        description="Only materials with an emission value will glow",
        default = False, update=Auto_Update)
    glow_v = FloatProperty(name="Viggnette Amount",description="Amount", default=1, min=0, update=Auto_Update)
    use_streaks = BoolProperty(
        name="Streaks",
        description="Streaks",
        default = False, update=Auto_Update)
    streaks_em = BoolProperty(
        name="Only Emission",
        description="Only materials with an emission value will generate streaks",
        default = False, update=Auto_Update)
    streaks_v = FloatProperty(name="Viggnette Amount",description="Amount", default=1, min=0, update=Auto_Update)
    streaks_n = IntProperty(name="Number of streaks",description="Number of streaks", default=4,min=2,max=16, update=Auto_Update)
    streaks_d = FloatProperty(name="Angle Offset",description="Streak angle offset", default=0,min=0, max=math.pi, unit='ROTATION', update=Auto_Update)
    sharpen_v = FloatProperty(name="Sharpen",description="Sharpen image", default=0,min=0, update=Auto_Update)
    soften_v = FloatProperty(name="Soften",description="Soften image", default=0,min=0, update=Auto_Update)
    
    # Blurs
    use_speedb = BoolProperty(
        name="Motion Blur",
        description="Blurs out fast motions",
        default = False, update=Auto_Update)
    motionb_v = FloatProperty(name="Motion blur amount",description="Amount of motion blur", default=1.0, min=0, update=Auto_Update)
    use_dof = BoolProperty(
        name="Depth of field",
        description="Range of distance that appears acceptably sharp",
        default = False, update=Auto_Update)
    dof_v = FloatProperty(name="Defocus amount",description="Amount of blur", default=50.0, min=0, max=128, update=Auto_Update)
    
    
    # Color
    bw_v = FloatProperty(name="Saturation",description="Saturation", default=1, min=0, max=4, subtype="FACTOR", update=Auto_Update)
    contrast_v = FloatProperty(name="Contrast",description="The difference in color and light between parts of an image", default=0, update=Auto_Update)
    brightness_v = FloatProperty(name="Brightness",description="Brightness", default=0, update=Auto_Update)
    shadows_v = bpy.props.FloatVectorProperty(name="Shadows",description="Shadows", subtype="COLOR_GAMMA",default=(1,1,1),min=0, max=2, update=Auto_Update)
    midtones_v = bpy.props.FloatVectorProperty(name="Midtones",description="Midtones", subtype="COLOR_GAMMA",default=(1,1,1),min=0, max=2, update=Auto_Update)
    highlights_v = bpy.props.FloatVectorProperty(name="Highlights",description="Highlights", subtype="COLOR_GAMMA",default=(1,1,1),min=0, max=2, update=Auto_Update)
    check_v = bpy.props.FloatVectorProperty(default=(1,1,1),subtype="COLOR_GAMMA", update=Auto_Update)
    
    # Distort / Lens
    use_flip = BoolProperty(
        name="Flip image",
        description="Flip image on the X axis",
        default = False, update=Auto_Update)
    lens_distort_v = FloatProperty(name="Distort",description="Distort the lens", default=0, min=-0.999, max=1, update=Auto_Update)
    dispersion_v = FloatProperty(name="Dispersion",description="A type of distortion in which there is a failure of a lens to focus all colors to the same convergence point", default=0, min=0, max=1, update=Auto_Update)
    use_flare = BoolProperty(
        name="Lens Flare",
        description="Lens Flare",
        default = False, update=Auto_Update)
    flare_type = EnumProperty(items=[('Fixed', 'Fixed', 'Fixed position'), ('Tracked', 'Tracked', 'Select if you want object to place in the viewport to act like the flare')], update=Auto_Update)
    flare_c = bpy.props.FloatVectorProperty(name="Highlights",description="Flare Color", subtype="COLOR_GAMMA",size=4, default=(1,0.3,0.084, 1),min=0, max=1, update=Auto_Update)    
    flare_x = FloatProperty(name="Flare X Pos",description="Flare X offset", default=0, update=Auto_Update)
    flare_y = FloatProperty(name="Flare Y Pos",description="Flare Y offset", default=0, update=Auto_Update)
    #flare_size = FloatProperty(name="Size",description="Flare Y offset", default=0, update=Auto_Update)
    flare_streak_intensity = FloatProperty(name="Size",description="Streak Intensity", default=0.002, min=0,max=1, subtype='FACTOR', update=Auto_Update)
    flare_streak_lenght = FloatProperty(name="Size",description="Streak Lenght", default=1, max=3,min=0.001, subtype='FACTOR', update=Auto_Update)
    flare_streak_angle = FloatProperty(name="Size",description="Streak Rotatiom", default=0, max=math.pi,min=0, subtype='ANGLE', update=Auto_Update)
    flare_streak_streaks = IntProperty(name="Size",description="Streak Streaks", default=12, max=16,min=2, update=Auto_Update)
    flare_glow = FloatProperty(name="Size",description="Glow Intensity", default=0.03, min=0,max=1, subtype='FACTOR', update=Auto_Update)
    flare_ghost = FloatProperty(name="Size",description="Ghost Intensity", default=1, min=0, update=Auto_Update)
    flare_layer = bpy.props.BoolVectorProperty(name="test", subtype="LAYER", size=20,update=Auto_Update,default=(False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,False,False,False))
    #Tracked
    flaret_streak_intensity = FloatProperty(name="Size",description="Streak Intensity", default=0.03, min=0,max=1, subtype='FACTOR', update=Auto_Update)
    flaret_streak_lenght = FloatProperty(name="Size",description="Streak Lenght", default=1.5, max=3,min=0.001, subtype='FACTOR', update=Auto_Update)
    flaret_streak_angle = FloatProperty(name="Size",description="Streak Rotatiom", default=0, max=math.pi,min=0, subtype='ANGLE', update=Auto_Update)
    flaret_streak_streaks = IntProperty(name="Size",description="Streak Streaks", default=12, max=16,min=2, update=Auto_Update)
    flaret_glow = FloatProperty(name="Size",description="Glow Intensity", default=0.1, min=0,max=1, subtype='FACTOR', update=Auto_Update)
    flaret_ghost = FloatProperty(name="Size",description="Ghost Intensity", default=1.5, min=0, update=Auto_Update)
    flare_center_size = FloatProperty(name="Size",description="Size of the flare source", default=20, min=1, update=Auto_Update)
    
    # World
    use_mist = BoolProperty(
        name="Use Mist",
        description="Mist",
        default = False, update=Auto_Update)
    mist_sky = BoolProperty(
        name="Use Mist",
        description="The mist will affect the sky",
        default = True, update=Auto_Update)
    mist_offset = FloatProperty(name="Size",description="Offset", default=0, update=Auto_Update)
    mist_size = FloatProperty(name="Size",description="Amount", default=0.01, update=Auto_Update)
    mist_min = FloatProperty(name="Size",description="Minimum", default=0, min=0,max=1, update=Auto_Update, subtype="FACTOR")
    mist_max = FloatProperty(name="Size",description="Maximum", default=1, min=0,max=1, update=Auto_Update, subtype="FACTOR")
    mist_color = bpy.props.FloatVectorProperty(name="Mist Color",description="Mist Color", subtype="COLOR_GAMMA",size=4, default=(1,1,1,1),min=0, max=1, update=Auto_Update)
        
    
    
      
    # Settings
    use_cinematic_border = BoolProperty(
        name="Cinematic Border",
        description="Add black borders at top and bottom",
        default = False, update=Auto_Update)
    cinematic_border_v = FloatProperty(name="Cinematic Border",description="border height", default=0.4, min=0, max=1, update=Auto_Update)
    use_transparent_sky = BoolProperty(
        name="Transparent Sky",
        description="Render the sky as transparent",
        default = False, update=Auto_Update)
    use_cel_shading = BoolProperty(
        name="Cell Shading",
        description="Adds a black outline, mimic the style of a comic book or cartoon",
        default = False, update=Auto_Update)
    cel_thickness = FloatProperty(name="Cel shading thickness",description="Line thickness", default=1, min=0, subtype='PIXEL', update=Auto_Update)
    split_image = BoolProperty(
        name="Split Original",
        description="Split the image with the original render",
        default = False, update=Auto_Update)
    split_v = IntProperty(name="Split Value",description="Where to split the image", default=50, min=0, max=100,subtype='PERCENTAGE', update=Auto_Update)
    use_image_sky = BoolProperty(
        name="Image Sky",
        description="Use external image as sky",
        default = False, update=Auto_Update)
    image_sky_img = StringProperty(name="Sky Image",description="Image", default="",subtype='FILE_PATH', update=Auto_Update)
    image_sky_x = FloatProperty(name="Image Sky X",description="Image offset on the X axis", default=0, update=Auto_Update)
    image_sky_y = FloatProperty(name="Image Sky Y",description="Image offset on the Y axis", default=0, update=Auto_Update)
    image_sky_angle = FloatProperty(name="Image Sky Angle",description="Image Rotation", default=0, update=Auto_Update)
    image_sky_scale = FloatProperty(name="Image sky Scale",description="Image Scale", default=1, update=Auto_Update)
    layer_index = IntProperty(name="Layer Index",description="Render Layer to use as main", default=0,min=0, update=Auto_Update)

# ------------------------------------------------------------------------
#    Pannels
# ------------------------------------------------------------------------
class UpdatePanel(bpy.types.Panel):
    bl_category = "EasyFX"
    bl_label = "Update"
    bl_idname = "Update"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align = True)
        row.operator('object.update_render_operator', text = "Update & re-Render", icon="RENDER_STILL")
        row = col.row(align = True)
        row.operator('object.update_operator', text = "Update", icon="SEQ_CHROMA_SCOPE")
#COLOR IMAGE_COL PARTICLES RENDERLAYERS CAMERA_STEREO MOD_PARTICLES SEQ_CHROMA_SCOPE
        scn = context.scene
        mytool = scn.easyfx
        col = layout.column(align=True)
        row = col.row(align = True)
        row.prop(mytool, "use_auto_update", text="Auto Update")
        row.prop(mytool, "use_flip", text="Flip image")
        layout.prop(mytool, "split_image", text="Split with original")
        if mytool.split_image == True:
            layout.prop(mytool, "split_v", text="Split at")
        
class FilterPanel(Panel):
    bl_category = "EasyFX"
    bl_label = "Filter"
    bl_idname = "Filter"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        # get the scene
        scn = context.scene
        mytool = scn.easyfx
        
        # display the property
        layout = self.layout
        
        col = layout.column(align=True)
        row = col.row(align = True)
        row.prop(mytool, "use_glow", text="Glow")
        if mytool.use_glow == True:
            row = col.row(align = True)
            row.prop(mytool, "glow_em", text="Emission only")
            row = col.row(align = True)
            row.prop(mytool, "glow_v", text="Threshold")
        col = layout.column(align=True)
        row = col.row(align = True)
        row.prop(mytool, "use_streaks", text="Streaks")
        if mytool.use_streaks == True:
            row = col.row(align = True)
            row.prop(mytool, "streaks_em", text="Emission only")
            row = col.row(align = True)
            row.prop(mytool, "streaks_v", text="Threshold")
            row = col.row(align = True)
            row.prop(mytool, "streaks_n", text="Streaks")
            row = col.row(align = True)
            row.prop(mytool, "streaks_d", text="Angle offset")
        layout.prop(mytool, "use_vignette", text="Vignette")
        if mytool.use_vignette == True:
            layout.prop(mytool, "vignette_v", text="Amount")
        col = layout.column(align=True)
        row = col.row(align = True)
        row.prop(mytool, "sharpen_v", text="Sharpen")
        row = col.row(align = True)
        row.prop(mytool, "soften_v", text="Soften")
        

class BlurPanel(Panel):
    bl_category = "EasyFX"
    bl_label = "Blur"
    bl_idname = "Blur"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scn = context.scene
        mytool = scn.easyfx
        layout = self.layout
        layout.prop(mytool, "use_dof", text="Depth of field")
        if mytool.use_dof == True:
            layout.prop(mytool, "dof_v", text="F-stop")
            layout.label("Focal point can be set in Camera Properties")
        layout.prop(mytool, "use_speedb", text="Motion blur")
        if mytool.use_speedb == True:
            layout.prop(mytool, "motionb_v", text="Amount")
            
            
class ColorPanel(Panel):
    bl_category = "EasyFX"
    bl_label = "Color"
    bl_idname = "Color"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scn = context.scene
        mytool = scn.easyfx
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align = True)
        row.prop(mytool, "brightness_v", text="Brightness")
        row = col.row(align = True)
        row.prop(mytool, "contrast_v", text="Contrast")
        row = col.row(align = True)
        row.prop(mytool, "bw_v", text="Saturation")
        layout.prop(mytool, "shadows_v", text="Shadows")
        layout.prop(mytool, "midtones_v", text="Midtones")
        layout.prop(mytool, "highlights_v", text="Hightlights")
        
class LensPanel(Panel):
    bl_category = "EasyFX"
    bl_label = "Lens"
    bl_idname = "Lens"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scn = context.scene
        mytool = scn.easyfx
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align = True)
        row.prop(mytool, "lens_distort_v", text="Lens distortion")
        row = col.row(align = True)
        row.prop(mytool, "dispersion_v", text="Chromatic aberration")
        layout.prop(mytool, "use_flare", text="Lens Flare")
        if mytool.use_flare==True:
            layout.prop(mytool, "flare_type", text="Position")
            if mytool.flare_type == 'Fixed':
                col = layout.column(align=True)
                row = col.row(align = True)
                row.prop(mytool, "flare_x", text="X")
                row.prop(mytool, "flare_y", text="Y")
                row = col.row(align = True)
                row.prop(mytool, "flare_center_size", text="Source Size")
                row = col.row(align = True)
                row.prop(mytool, "flare_c", text="")
                col = layout.column(align=True)
                row = col.row(align = True)
                row.prop(mytool, "flare_streak_intensity", text='Streak Intensity')
                row = col.row(align = True)
                row.prop(mytool, "flare_streak_lenght", text="Streak Lenght")
                row = col.row(align = True)
                row.prop(mytool, "flare_streak_angle", text="Rotation")
                row.prop(mytool, "flare_streak_streaks", text="Streaks")
                row = col.row(align = True)
                row.prop(mytool, "flare_glow", text="Glow")
                row = col.row(align = True)
                row.prop(mytool, "flare_ghost", text="Ghost")
            else:
                layout.prop(mytool, "flare_layer", text="")
                col = layout.column(align=True)
                row = col.row(align = True)
                row.prop(mytool, "flaret_streak_intensity", text='Streak Intensity')
                row = col.row(align = True)
                row.prop(mytool, "flaret_streak_lenght", text="Streak Lenght")
                row = col.row(align = True)
                row.prop(mytool, "flaret_streak_angle", text="Rotation")
                row.prop(mytool, "flaret_streak_streaks", text="Streaks")
                row = col.row(align = True)
                row.prop(mytool, "flaret_glow", text="Glow")
                row = col.row(align = True)
                row.prop(mytool, "flaret_ghost", text="Ghost")
            #if mytool.flare_type == 'Tracked':
            #    layout.prop(mytool, "flare_layer", text="")
            
        
        
        
class WorldPanel(Panel):
    bl_category = "EasyFX"
    bl_label = "World"
    bl_idname = "World"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scn = context.scene
        mytool = scn.easyfx
        layout = self.layout
        layout.prop(mytool, "use_mist", text="Mist")
        if mytool.use_mist == True:
            col = layout.column(align=True)
            if bpy.context.scene.render.engine != 'CYCLES':
                row = col.row(align = True)
                row.prop(mytool, "mist_sky", text="Affect sky")
            row = col.row(align = True)
            row.prop(mytool, "mist_offset", text="Offset")
            row = col.row(align = True)
            row.prop(mytool, "mist_size", text="Size")
            row = col.row(align = True)
            row.prop(mytool, "mist_min", text="Min")
            #row = col.row(align = True)
            row.prop(mytool, "mist_max", text="Max")
            row = col.row(align = True)
            row.prop(mytool, "mist_color", text="")
        layout.prop(mytool, "use_transparent_sky", text="Transparent sky")
        layout.prop(mytool, "use_image_sky", text="Image sky")
        if mytool.use_image_sky == True:
            layout.prop(mytool, "image_sky_img", text="")
            col = layout.column(align=True)
            row = col.row(align = True)
            row.prop(mytool, "image_sky_x", text="X")
            row.prop(mytool, "image_sky_y", text="Y")
            row = col.row(align = True)
            row.prop(mytool, "image_sky_angle", text="Rotation")
            row = col.row(align = True)
            row.prop(mytool, "image_sky_scale", text="Scale")
            
class StylePanel(Panel):
    bl_category = "EasyFX"
    bl_label = "Style"
    bl_idname = "Style"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scn = context.scene
        mytool = scn.easyfx
        layout = self.layout
        layout.prop(mytool, "use_cel_shading", text="Cel shading")
        if mytool.use_cel_shading == True:
            layout.prop(mytool, "cel_thickness", text="Line thickness")
        layout.prop(mytool, "use_cinematic_border", text="Cinematic borders")
        if mytool.use_cinematic_border == True:
            layout.prop(mytool, "cinematic_border_v", text="Border height")
        
class SettingPanel(Panel):
    bl_category = "EasyFX"
    bl_label = "Settings"
    bl_idname = "Settings"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scn = context.scene
        mytool = scn.easyfx
        layout = self.layout
        layout.prop(mytool, "layer_index", text="Layer index")
        layout.operator('object.reset_settings_operator', text = "Reset all values", icon="RECOVER_AUTO")
        #ERROR RECOVER_LAST FILE_REFRESH RECOVER_AUTO



# ------------------------------------------------------------------------
#   Update
# ------------------------------------------------------------------------

class UpdateOperator(bpy.types.Operator):
    '''Update'''
    bl_idname = "object.update_operator"
    bl_label = "Update Nodes Operator"
    def execute(self, context):
        editorcheck = False
        ef_use_sky = True
        efFullscreen = False
        for area in bpy.context.screen.areas :
            if area.type == 'NODE_EDITOR' :
                if area.spaces.active.tree_type != 'CompositorNodeTree':
                    area.spaces.active.tree_type = 'CompositorNodeTree'
                editorcheck = True                     
        if editorcheck == False:
            try:
                bpy.context.area.type='NODE_EDITOR'
                bpy.ops.screen.area_split(factor=1)
                bpy.context.area.type='VIEW_3D'
                bpy.context.area.type='IMAGE_EDITOR'
            except:
                bpy.context.area.type='IMAGE_EDITOR'
                bpy.ops.screen.back_to_previous()  
                self.report({'WARNING'}, "Fullscreen is not supported")
                efFullscreen = True
                
        scene = bpy.context.scene
        scene.use_nodes = True
        nodes = scene.node_tree.nodes
        links = scene.node_tree.links
        
        pos_x = 200
        ef = bpy.context.scene.easyfx
        # Layer Index
        layeri = ef.layer_index
        layern = bpy.data.scenes['Scene'].render.layers[layeri].name
        try:
            nodes.remove(nodes['Render Layers'])
            nodes.remove(nodes['Composite'])
        except:
            pass            
        # Default Setup
        # Clear Nodes
        #nodes.clear()
        
        # Input n Output
        try:
            CIn = nodes["Input"]
        except:
            CIn = nodes.new(type='CompositorNodeRLayers')
            CIn.name = "Input"
            CIn.label = "Input"
        try:
            COut = nodes["Output"]
        except:
            COut = nodes.new(type='CompositorNodeComposite')
            COut.name = "Output"
            COut.label = "Output"
        CIn.layer = layern
        latest_node = CIn
        
        
    #--------------------------------------------
    #   Other Settings
    #--------------------------------------------
        global s_sky, s_cell
        
        # Transparent Sky
        if ef.use_transparent_sky == True:
            ef_use_sky = False
        
        # Cell Shading
        if ef.use_cel_shading == True:
            scene.render.line_thickness = ef.cel_thickness
            if s_cell == True:
                scene.render.use_freestyle = True
                self.report({'INFO'}, "Re-render Required")
                s_cell = False
        elif ef.use_cel_shading == False and s_cell == False:
            scene.render.use_freestyle = False
            self.report({'INFO'}, "Re-render Required")
            s_cell = True
        
        
            
        
    #--------------------------------------------
    #   Nodes
    #--------------------------------------------
        # Sharpen
        if ef.sharpen_v != 0:
            try:
                node_sharpen = nodes['Sharpen']
            except:
                node_sharpen = nodes.new(type='CompositorNodeFilter')
                node_sharpen.filter_type = 'SHARPEN'
                node_sharpen.name = 'Sharpen'
            node_sharpen.inputs[0].default_value = ef.sharpen_v
            node_sharpen.location = (pos_x,0)
            pos_x=pos_x+200
            links.new(latest_node.outputs[0], node_sharpen.inputs[1])
            latest_node = node_sharpen
        else:
            try:
                nodes.remove(nodes['Sharpen'])
            except:
                pass
        # Soften
        if ef.soften_v != 0:
            try:
                node_soften = nodes['Soften']
            except:
                node_soften = nodes.new(type='CompositorNodeFilter')
                node_soften.name = 'Soften'
            node_soften.location = (pos_x,0)
            node_soften.inputs[0].default_value = ef.soften_v
            pos_x=pos_x+200
            links.new(latest_node.outputs[0], node_soften.inputs[1])
            latest_node = node_soften
        else:
            try:
                nodes.remove(nodes['Soften'])
            except:
                pass
               
        # Speed Blur
        if ef.use_speedb == True and ef.motionb_v != 0:
            try:
                node_VecBlur = nodes['VecBlur']
            except:
                node_VecBlur = nodes.new(type='CompositorNodeVecBlur')
                links.new(CIn.outputs[0], node_VecBlur.inputs[0])
                node_VecBlur.name = 'VecBlur'
                node_VecBlur.label = 'Motion blur'
                links.new(CIn.outputs[2], node_VecBlur.inputs[1])
                links.new(CIn.outputs[5], node_VecBlur.inputs[2])
            node_VecBlur.location = (pos_x,0)
            node_VecBlur.factor = ef.motionb_v
            pos_x=pos_x+200
            links.new(latest_node.outputs[0], node_VecBlur.inputs[0])
            latest_node = node_VecBlur
            if scene.render.layers[layeri].use_pass_z == True and scene.render.layers[layeri].use_pass_vector == True:
                pass
            else:
                scene.render.layers[layeri].use_pass_z = True
                scene.render.layers[layeri].use_pass_vector = True
                self.report({'INFO'}, "Re-render Required")
        else:
            try:
                nodes.remove(nodes['VecBlur'])
            except:
                pass
            
        # Defocus
        if ef.use_dof == True:
            try:
                node_dof = nodes['DOF']
            except:
                node_dof = nodes.new(type='CompositorNodeDefocus')
                node_dof.use_zbuffer = True
                node_dof.name = 'DOF'
                node_dof.label = 'Depth of field'
                node_dof.use_preview = False
                links.new(CIn.outputs[2], node_dof.inputs[1])
            node_dof.f_stop = ef.dof_v
            node_dof.location = (pos_x,0)
            pos_x=pos_x+200
            bpy.data.cameras[0].show_limits = True
            links.new(latest_node.outputs[0], node_dof.inputs[0])
            latest_node = node_dof
            if scene.render.layers[layeri].use_pass_z == True:
                pass
            else:
                scene.render.layers[layeri].use_pass_z = True
                self.report({'INFO'}, "Re-render Required")
        else:
            try:
                nodes.remove(nodes['DOF'])
            except:
                pass
            
        # Color Correction
        if ef.shadows_v != ef.check_v or ef.midtones_v != ef.check_v or ef.highlights_v != ef.check_v:
            try:
                node_color = nodes['CC']
            except:
                node_color = nodes.new(type='CompositorNodeColorBalance')
                node_color.name = 'CC'
            node_color.lift = ef.shadows_v
            node_color.gamma = ef.midtones_v
            node_color.gain = ef.highlights_v
            node_color.location = (pos_x,0)
            pos_x=pos_x+450
            links.new(latest_node.outputs[0], node_color.inputs[1])
            latest_node = node_color
        else:
            try:
                nodes.remove(nodes['CC'])
            except:
                pass
            
        # Brightness/Contrast
        if ef.contrast_v != 0 or ef.brightness_v != 0:
            try:
                node_brightcont = nodes['BC']
            except:
                node_brightcont = nodes.new(type='CompositorNodeBrightContrast')
                node_brightcont.name= 'BC'
            node_brightcont.location = (pos_x,0)
            pos_x=pos_x+200
            node_brightcont.inputs[1].default_value = ef.brightness_v
            node_brightcont.inputs[2].default_value = ef.contrast_v
            links.new(latest_node.outputs[0], node_brightcont.inputs[0])
            latest_node = node_brightcont
        else:
            try:
                nodes.remove(nodes['BC'])
            except:
                pass
            
        # Mist
        if ef.use_mist == True:
            try:
                node_mist_mapv = nodes['Mist MapV']
                node_mist_mix = nodes['Mist Mix']
                node_mist_cramp = nodes['Mist CRamp']
            except:
                node_mist_mapv = nodes.new(type='CompositorNodeMapValue')
                node_mist_mapv.name = 'Mist MapV'
                node_mist_mapv.label = 'Mist'
                node_mist_cramp = nodes.new(type='CompositorNodeValToRGB')
                node_mist_cramp.name = 'Mist CRamp'
                node_mist_mix = nodes.new(type='CompositorNodeMixRGB')
                node_mist_mix.name = "Mist Mix"
                links.new(CIn.outputs[2], node_mist_mapv.inputs[0])
                links.new(node_mist_mapv.outputs[0], node_mist_cramp.inputs[0])
                links.new(node_mist_cramp.outputs[0], node_mist_mix.inputs[0])
            node_mist_mapv.offset[0] = -1*ef.mist_offset
            node_mist_mapv.size[0] = ef.mist_size
            if ef.mist_min != 0:
                node_mist_mapv.use_min = True
                node_mist_mapv.min[0] = ef.mist_min
            if ef.mist_max != 1:
                node_mist_mapv.use_max = True
                node_mist_mapv.max[0] = ef.mist_max
            node_mist_mix.inputs[2].default_value = ef.mist_color
            node_mist_mapv.location = (pos_x,250)
            pos_x=pos_x+200
            node_mist_cramp.location = (pos_x,250)
            pos_x=pos_x+300
            node_mist_mix.location = (pos_x,0)
            pos_x=pos_x+200
            links.new(latest_node.outputs[0], node_mist_mix.inputs[1])
            latest_node = node_mist_mix
            #Affect Sky
            if ef.mist_sky == False:
                ef_use_sky = False
                try:
                    sky_layer = scene.render.layers['EasyFX - Sky']
                except:
                    sky_layer = bpy.ops.scene.render_layer_add()
                    try:
                        layx = 0
                        while True:
                            sky_layer = bpy.context.scene.render.layers[layx]
                            layx = layx+1
                    except:
                        sky_layer.name = 'EasyFX - Sky'
                        sky_layer.use_solid = False
                        sky_layer.use_halo = False
                        sky_layer.use_ztransp = False
                        sky_layer.use_edge_enhance = False
                        sky_layer.use_strand = False
                        sky_layer.use_freestyle = False
                    layer_active = 0
                    while layer_active < 20:
                        sky_layer.layers[layer_active] = False
                        sky_layer.layers_zmask[layer_active] = True
                        layer_active = layer_active+1
                
                try:
                    node_mist_sky = nodes['Mist_sky']
                    node_mist_alphov = nodes['Mist_alphov']
                except:
                    node_mist_sky = nodes.new(type='CompositorNodeRLayers')
                    node_mist_sky.name = 'Mist_sky'
                    node_mist_sky.label = 'Sky'
                    node_mist_sky.layer = 'EasyFX - Sky'
                    node_mist_alphov = nodes.new(type='CompositorNodeAlphaOver')
                    node_mist_alphov.name = 'Mist_alphov'
                    links.new(CIn.outputs[1], node_mist_alphov.inputs[0])
                    links.new(node_mist_sky.outputs[0], node_mist_alphov.inputs[1])
                    links.new(node_mist_mix.outputs[0], node_mist_alphov.inputs[2])
                node_mist_sky.location = (pos_x-200,-220)
                node_mist_alphov.location = (pos_x,0)
                pos_x=pos_x+200    
                latest_node = node_mist_alphov
            else:
                try:
                    nodes.remove(nodes['Mist_sky'])
                    nodes.remove(nodes['Mist_alphov'])
                except:
                    pass        
        else:
            try:
                nodes.remove(nodes['Mist MapV'])
                nodes.remove(nodes['Mist CRamp'])
                nodes.remove(nodes['Mist Mix'])
                nodes.remove(nodes['Mist_sky'])
                nodes.remove(nodes['Mist_alphov'])
            except:
                pass
        
        # Streaks
        if ef.use_streaks == True:
            try:
                node_streaks = nodes['Streaks']
            except:
                node_streaks = nodes.new(type='CompositorNodeGlare')
                node_streaks.name = 'Streaks'
                node_streaks.label = 'Streaks'
            node_streaks.threshold = ef.streaks_v
            node_streaks.streaks = ef.streaks_n
            node_streaks.angle_offset = ef.streaks_d

            if ef.streaks_em == True:
                if scene.render.layers[layeri].use_pass_emit == False:
                    scene.render.layers[layeri].use_pass_emit = True
                    self.report({'INFO'}, "Re-render Required")
                links.new(CIn.outputs[17], node_streaks.inputs[0])
                try:
                    node_streaks_mix = nodes['Streaks Mix']
                except:
                    node_streaks_mix = nodes.new(type='CompositorNodeMixRGB')
                    node_streaks_mix.blend_type = 'ADD'
                    node_streaks_mix.name = 'Streaks Mix'
                links.new(latest_node.outputs[0], node_streaks_mix.inputs[1])
                links.new(node_streaks.outputs[0], node_streaks_mix.inputs[2])
                latest_node = node_streaks_mix
                node_streaks.location = (pos_x,-170)
                pos_x=pos_x+200
                node_streaks_mix.location = (pos_x,0)
                pos_x=pos_x+200
            else:
                links.new(latest_node.outputs[0], node_streaks.inputs[0])
                latest_node = node_streaks
                node_streaks.location = (pos_x,0)
                pos_x=pos_x+200
                try:
                    nodes.remove(nodes['Streaks Mix'])
                except:
                    pass
        else:
            try:
                nodes.remove(nodes['Streaks'])
                nodes.remove(nodes['Streaks Mix'])
            except:
                pass
                
        # Glow
        if ef.use_glow == True:
            try:
                node_glow = nodes['Glow']
            except:
                node_glow = nodes.new(type='CompositorNodeGlare')
                node_glow.glare_type = 'FOG_GLOW'
                node_glow.name = 'Glow'
                node_glow.label = 'Glow'
            node_glow.threshold = ef.glow_v
            if ef.glow_em == True:
                if scene.render.layers[layeri].use_pass_emit == False:
                    scene.render.layers[layeri].use_pass_emit = True
                    self.report({'INFO'}, "Re-render Required")
                links.new(CIn.outputs[17], node_glow.inputs[0])
                try:
                    node_glow_mix = nodes['Glow Mix']
                except:
                    node_glow_mix = nodes.new(type='CompositorNodeMixRGB')
                    node_glow_mix.blend_type = 'ADD'
                    node_glow_mix.name = 'Glow Mix'
                    links.new(node_glow.outputs[0], node_glow_mix.inputs[2])
                links.new(latest_node.outputs[0], node_glow_mix.inputs[1])
                latest_node = node_glow_mix
                node_glow.location = (pos_x,-170)
                pos_x=pos_x+200
                node_glow_mix.location = (pos_x,0)
                pos_x=pos_x+200
            else:
                links.new(latest_node.outputs[0], node_glow.inputs[0])
                latest_node = node_glow
                node_glow.location = (pos_x,0)
                pos_x=pos_x+200
                try:
                    nodes.remove(nodes['Glow Mix'])
                except:
                    pass
        else:
            try:
                nodes.remove(nodes['Glow'])
                nodes.remove(nodes['Glow Mix'])
            except:
                pass
            
        
        # Image Sky
        if ef.use_image_sky == True:
            try:
                node_imgsky_img = nodes['Image input']
                node_imgsky_alphov = nodes['Image mix']
                node_imgsky_trans = nodes['Image transform']
            except:
                node_imgsky_img = nodes.new(type='CompositorNodeImage')
                node_imgsky_img.name = 'Image input'
                node_imgsky_alphov = nodes.new(type='CompositorNodeAlphaOver')
                node_imgsky_alphov.name = 'Image mix'
                node_imgsky_trans = nodes.new(type='CompositorNodeTransform')
                node_imgsky_trans.name = 'Image transform'
                links.new(node_imgsky_img.outputs[0], node_imgsky_trans.inputs[0])
                links.new(node_imgsky_trans.outputs[0], node_imgsky_alphov.inputs[1])
                pass
            # Update Values
            node_imgsky_trans.inputs[1].default_value = ef.image_sky_x
            node_imgsky_trans.inputs[2].default_value = ef.image_sky_y
            node_imgsky_trans.inputs[3].default_value = ef.image_sky_angle
            node_imgsky_trans.inputs[4].default_value = ef.image_sky_scale*scene.render.resolution_percentage/100
            links.new(latest_node.outputs[0], node_imgsky_alphov.inputs[2])
            latest_node = node_imgsky_alphov
            node_imgsky_img.location = (pos_x-400,250)
            node_imgsky_trans.location = (pos_x-200,250)
            node_imgsky_alphov.location = (pos_x,0)
            pos_x=pos_x+200
            ef_global_sky = True
            global imgs, skyimg
            if imgs != ef.image_sky_img:
                try:
                    path = r"" + bpy.path.abspath(ef.image_sky_img)
                    skyimg = bpy.data.images.load(path)
                    node_imgsky_img.image = skyimg
                except:
                    self.report({'WARNING'}, "Could not load image")
            else:  
                try:
                    node_imgsky_img.image = skyimg
                except:
                    pass
            imgs = ef.image_sky_img
            ef_use_sky = False
        else:
            try:
                nodes.remove(nodes['Image input'])
                nodes.remove(nodes['Image mix'])
                nodes.remove(nodes['Image transform'])
            except:
                pass
        
        
        
        # Lens Flare
        if ef.use_flare == True:
            # Tracked Flare
            if ef.flare_type == 'Tracked':
                # Create Tracker
                try:
                    bpy.data.objects['EasyFX - Flare']
                except:
                    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=16)
                    flare_sphere = bpy.context.object
                    flare_sphere.name = 'EasyFX - Flare'
                    mat = bpy.data.materials.new("EasyFX - Flare")
                    mat.specular_intensity = 0
                    mat.emit = 5
                    bpy.context.object.data.materials.append(mat)
                try:
                    flare_layer = bpy.data.scenes['Scene'].render.layers['EasyFX - Flare']
                except:
                    flare_layer = bpy.ops.scene.render_layer_add()
                    try:
                        layx = 0
                        while True:
                            flare_layer = bpy.context.scene.render.layers[layx]
                            layx = layx+1
                    except:
                        flare_layer.name = 'EasyFX - Flare'
                        flare_layer.use_sky = False
                    layer_active = 0
                    while layer_active < 20:
                        flare_layer.layers[layer_active] = False
                        flare_layer.layers_zmask[layer_active] = True
                        layer_active = layer_active+1
                    #flare_layer.layers[15] = True
                    #flare_layer.layers[19] = False
                flare_layer.layers = ef.flare_layer
                bpy.ops.object.move_to_layer(layers=ef.flare_layer)
            if ef.flare_type == 'Fixed':
                pos_x=pos_x-600
                try:
                    nodes.remove(nodes['flare_rlayer'])
                except:
                    pass    
                try:
                    node_flare_mask1 = nodes['flare_mask1']
                    node_flare_rgb = nodes['flare_rgb']
                    node_flare_dist1 = nodes['flare_dist1']
                    node_flare_dist2 = nodes['flare_dist2']
                    node_flare_mask2 = nodes['flare_mask2']
                    node_flare_mixc = nodes['flare_mixc']
                    node_flare_trans = nodes['flare_translate']
                    node_flare_alphov = nodes['flare_alphaover']
                    node_flare_ckey = nodes['flare_ckey']
                except:
                    node_flare_mask1 = nodes.new(type='CompositorNodeMask')
                    node_flare_mask1.size_source = 'FIXED'
                    node_flare_mask1.name = 'flare_mask1'
                    node_flare_rgb = nodes.new(type='CompositorNodeRGB')
                    node_flare_rgb.name = 'flare_rgb'
                    node_flare_rgb.label = 'Flare Color'
                    node_flare_dist1 = nodes.new(type='CompositorNodeLensdist')
                    node_flare_dist1.inputs[1].default_value = 1
                    node_flare_dist1.name = 'flare_dist1'
                    node_flare_dist2 = nodes.new(type='CompositorNodeLensdist')
                    node_flare_dist2.inputs[1].default_value = 1
                    node_flare_dist2.name = 'flare_dist2'
                    node_flare_mixc = nodes.new(type='CompositorNodeMixRGB')
                    node_flare_mixc.blend_type = 'ADD'
                    node_flare_mixc.name = 'flare_mixc'
                    node_flare_trans = nodes.new(type='CompositorNodeTranslate')
                    node_flare_trans.name = 'flare_translate'
                    node_flare_mask2 = nodes.new(type='CompositorNodeMask')
                    node_flare_mask2.name = 'flare_mask2'
                    node_flare_alphov = nodes.new(type='CompositorNodeAlphaOver')
                    node_flare_alphov.name = 'flare_alphaover'
                    node_flare_ckey = nodes.new(type='CompositorNodeChromaMatte')
                    node_flare_ckey.name = 'flare_ckey'
                    node_flare_ckey.tolerance = 1
                    node_flare_ckey.threshold = 1
                    node_flare_ckey.gain = 0
                    node_flare_ckey.inputs[1].default_value = (0,0,0,1)
                
                    links.new(node_flare_mask1.outputs[0], node_flare_dist1.inputs[0])
                    links.new(node_flare_dist1.outputs[0], node_flare_mixc.inputs[1])
                    links.new(node_flare_rgb.outputs[0], node_flare_dist2.inputs[0])
                    links.new(node_flare_dist2.outputs[0], node_flare_mixc.inputs[2])
                    links.new(node_flare_mixc.outputs[0], node_flare_trans.inputs[0])
                    links.new(node_flare_trans.outputs[0], node_flare_alphov.inputs[2])
                    links.new(node_flare_mask2.outputs[0], node_flare_alphov.inputs[1])
                    links.new(node_flare_alphov.outputs[0], node_flare_ckey.inputs[0])
                node_flare_rgb.outputs[0].default_value = ef.flare_c
                node_flare_trans.inputs[1].default_value = ef.flare_x
                node_flare_trans.inputs[2].default_value = ef.flare_y
                node_flare_layer = node_flare_ckey
                
                
                
                node_flare_mask1.size_x = ef.flare_center_size
                node_flare_mask1.size_y = ef.flare_center_size
                node_flare_mask1.location = (pos_x,-450)
                node_flare_rgb.location = (pos_x,-700)
                pos_x=pos_x+200
                node_flare_dist1.location = (pos_x,-450)
                node_flare_dist2.location = (pos_x,-700)
                pos_x=pos_x+200
                node_flare_mixc.location = (pos_x,-450)
                pos_x=pos_x+200
                node_flare_trans.location = (pos_x,-450)
                node_flare_mask2.location = (pos_x,-200)
                pos_x=pos_x+200
                node_flare_alphov.location = (pos_x,-200)
                pos_x=pos_x+200
                node_flare_ckey.location = (pos_x,-200)
                pos_x=pos_x+200
                
                # If Tracked
            else:
                try:
                    nodes.remove(nodes['flare_mask1'])
                    nodes.remove(nodes['flare_rgb'])
                    nodes.remove(nodes['flare_dist1'])
                    nodes.remove(nodes['flare_dist2'])
                    nodes.remove(nodes['flare_mask2'])
                    nodes.remove(nodes['flare_mixc'])
                    nodes.remove(nodes['flare_translate'])
                    nodes.remove(nodes['flare_alphaover'])
                    nodes.remove(nodes['flare_ckey'])
                except:
                    pass        
                try:
                    node_flare_layer = nodes['flare_rlayer']
                except:
                    node_flare_layer = nodes.new(type='CompositorNodeRLayers')
                    node_flare_layer.name = 'flare_rlayer'
                    node_flare_layer.layer = 'EasyFX - Flare'
                node_flare_layer.location = (pos_x-200,-600)
            try:
                node_flare_ghost = nodes['flare_ghost']
                node_flare_glow = nodes['flare_glow']
                node_flare_streaks = nodes['flare_streaks']
                node_flare_tonemap = nodes['flare_tonemap']
                node_flare_mix1 = nodes['flare_mix1']
                node_flare_mix2 = nodes['flare_mix2']
                node_flare_mix3 = nodes['flare_mix3']
                node_flare_tonemap2 = nodes['flare_tonemap2']
            except:        
                node_flare_ghost = nodes.new(type='CompositorNodeGlare')
                node_flare_ghost.glare_type = 'GHOSTS'
                node_flare_ghost.threshold = 0
                node_flare_ghost.name = 'flare_ghost'
                node_flare_glow = nodes.new(type='CompositorNodeGlare')
                node_flare_glow.glare_type = 'FOG_GLOW'
                node_flare_glow.threshold = 0
                node_flare_glow.quality = 'LOW'
                node_flare_glow.name = 'flare_glow'
                node_flare_streaks = nodes.new(type='CompositorNodeGlare')
                node_flare_streaks.glare_type = 'STREAKS'
                node_flare_streaks.threshold = 0
                node_flare_streaks.streaks = 12
                node_flare_streaks.quality = 'LOW'
                node_flare_streaks.name = 'flare_streaks'
                node_flare_streaks.angle_offset = 10*math.pi/180
                node_flare_tonemap = nodes.new(type='CompositorNodeTonemap')
                node_flare_tonemap.tonemap_type = 'RH_SIMPLE'
                node_flare_tonemap.key = 0.007
                node_flare_tonemap.name = 'flare_tonemap'
                node_flare_mix1 = nodes.new(type='CompositorNodeMixRGB')
                node_flare_mix1.blend_type = 'SCREEN'
                node_flare_mix1.name = 'flare_mix1'
                node_flare_mix2 = nodes.new(type='CompositorNodeMixRGB')
                node_flare_mix2.blend_type = 'SCREEN'
                node_flare_mix2.name = 'flare_mix2'
                node_flare_mix3 = nodes.new(type='CompositorNodeMixRGB')
                node_flare_mix3.blend_type = 'SCREEN'
                node_flare_mix3.name = 'flare_mix3'
                node_flare_tonemap2 = nodes.new(type='CompositorNodeTonemap')
                node_flare_tonemap2.tonemap_type = 'RH_SIMPLE'
                node_flare_tonemap2.name = 'flare_tonemap2'
                links.new(node_flare_mix2.outputs[0], node_flare_mix3.inputs[2])
                links.new(node_flare_mix1.outputs[0], node_flare_mix2.inputs[1])
                links.new(node_flare_streaks.outputs[0], node_flare_mix2.inputs[2])
                links.new(node_flare_tonemap.outputs[0], node_flare_mix1.inputs[1])
                links.new(node_flare_ghost.outputs[0], node_flare_mix1.inputs[2])
                links.new(node_flare_glow.outputs[0], node_flare_tonemap.inputs[0])
                
                links.new(node_flare_streaks.outputs[0], node_flare_tonemap2.inputs[0])
                links.new(node_flare_tonemap2.outputs[0], node_flare_mix2.inputs[2])
                
            links.new(node_flare_layer.outputs[0], node_flare_ghost.inputs[0])   
            links.new(node_flare_layer.outputs[0], node_flare_glow.inputs[0])
            links.new(node_flare_layer.outputs[0], node_flare_streaks.inputs[0]) 
            links.new(latest_node.outputs[0], node_flare_mix3.inputs[1])
            latest_node = node_flare_mix3
            node_flare_ghost.location = (pos_x,-200)
            node_flare_glow.location = (pos_x,-450)
            node_flare_streaks.location = (pos_x,-680)
            pos_x = pos_x+200
            node_flare_tonemap.location = (pos_x,-350)
            pos_x=pos_x+200
            node_flare_tonemap2.location = (pos_x,-400)
            node_flare_mix1.location = (pos_x,-200)
            pos_x=pos_x+200
            node_flare_mix2.location = (pos_x,-200)
            pos_x=pos_x+200
            node_flare_mix3.location = (pos_x,0)
            pos_x=pos_x+200
            
            if ef.flare_type == 'Fixed':
                node_flare_tonemap.key = 0.03
                node_flare_tonemap2.location = (pos_x-600,-550)
                node_flare_tonemap2.offset = 10
                node_flare_streaks.iterations = 5
                node_flare_streaks.quality = 'MEDIUM'
                node_flare_streaks.fade = 0.92
                node_flare_ghost.iterations = 4
                node_flare_tonemap2.key = ef.flare_streak_intensity
                node_flare_tonemap2.gamma = ef.flare_streak_lenght
                node_flare_streaks.angle_offset = ef.flare_streak_angle
                node_flare_streaks.streaks = ef.flare_streak_streaks
                node_flare_tonemap.key = ef.flare_glow
                node_flare_mix1.inputs[0].default_value = ef.flare_ghost
            else:
                node_flare_tonemap2.key = ef.flaret_streak_intensity
                node_flare_tonemap2.gamma = ef.flaret_streak_lenght
                node_flare_streaks.angle_offset = ef.flaret_streak_angle
                node_flare_streaks.streaks = ef.flaret_streak_streaks
                node_flare_tonemap.key = ef.flaret_glow
                node_flare_mix1.inputs[0].default_value = ef.flaret_ghost    
        else:
            try:
                nodes.remove(nodes['flare_ghost'])
                nodes.remove(nodes['flare_glow'])
                nodes.remove(nodes['flare_streaks'])
                nodes.remove(nodes['flare_tonemap'])
                nodes.remove(nodes['flare_mix1'])
                nodes.remove(nodes['flare_mix2'])
                nodes.remove(nodes['flare_mix3'])
                nodes.remove(nodes['flare_tonemap2'])
                nodes.remove(nodes['flare_rlayer'])
            except:
                pass
            try:
                nodes.remove(nodes['flare_mask1'])
                nodes.remove(nodes['flare_rgb'])
                nodes.remove(nodes['flare_dist1'])
                nodes.remove(nodes['flare_dist2'])
                nodes.remove(nodes['flare_mask2'])
                nodes.remove(nodes['flare_mixc'])
                nodes.remove(nodes['flare_translate'])
                nodes.remove(nodes['flare_alphaover'])
                nodes.remove(nodes['flare_ckey'])
            except:
                pass        
        
        # BW Saturation
        if ef.bw_v != 1:
            try:
                node_bw = nodes['ColorC']
            except:
                node_bw = nodes.new(type='CompositorNodeColorCorrection')
                node_bw.name = 'ColorC'
            links.new(latest_node.outputs[0], node_bw.inputs[0])
            node_bw.master_saturation = ef.bw_v
            node_bw.location = (pos_x,0)
            pos_x=pos_x+450
            latest_node = node_bw
        else:
            try:
                nodes.remove(nodes['ColorC'])
            except:
                pass    
        
        # Lens Distortion
        if ef.lens_distort_v != 0:
            try:
                node_lensdist = nodes['LensDist']
            except:
                node_lensdist = nodes.new(type='CompositorNodeLensdist')
                node_lensdist.name = 'LensDist'
            node_lensdist.inputs[1].default_value = ef.lens_distort_v
            links.new(latest_node.outputs[0], node_lensdist.inputs[0])
            node_lensdist.use_fit = True
            node_lensdist.location = (pos_x,0)
            pos_x=pos_x+200
            latest_node = node_lensdist
        else:
            try:
                nodes.remove(nodes['LensDist'])
            except:
                pass
          
        # Dispersion
        if ef.dispersion_v != 0:
            try:
                node_distortion = nodes['Dispersion']
            except:
                node_distortion = nodes.new(type='CompositorNodeLensdist')
                node_distortion.name = 'Dispersion'
                node_distortion.label = 'Dispersion'
            links.new(latest_node.outputs[0], node_distortion.inputs[0])
            node_distortion.inputs[2].default_value = ef.dispersion_v
            node_distortion.use_projector = True
            node_distortion.location = (pos_x,0)
            pos_x=pos_x+200
            latest_node = node_distortion
        else:
            try:
                nodes.remove(nodes['Dispersion'])
            except:
                pass
        # Vignette
        if ef.use_vignette == True:
            #Dist
            try:
                node_vig_dist = nodes['VigDist']
                node_vig_math = nodes['VigMath']
                node_vig_blr = nodes['VigBlur']
                node_vig_mix = nodes['VigMix']
            except:
                node_vig_dist = nodes.new(type='CompositorNodeLensdist')
                node_vig_dist.name = 'VigDist'
                node_vig_dist.inputs[1].default_value = 1            

                #Math
                node_vig_math = nodes.new(type='CompositorNodeMath')
                node_vig_math.operation = 'GREATER_THAN'
                node_vig_math.inputs[1].default_value = 0
                links.new(node_vig_dist.outputs[0], node_vig_math.inputs[0])
                node_vig_math.name = 'VigMath'            

                #Blur
                node_vig_blr = nodes.new(type='CompositorNodeBlur')
                node_vig_blr.filter_type = 'FAST_GAUSS'
                node_vig_blr.use_relative = True
                node_vig_blr.aspect_correction = 'Y'
                node_vig_blr.factor_x = 20
                node_vig_blr.factor_y = 20            
                links.new(node_vig_math.outputs[0], node_vig_blr.inputs[0])
                node_vig_blr.name = 'VigBlur'

                #Mix
                node_vig_mix = nodes.new(type='CompositorNodeMixRGB')
                node_vig_mix.blend_type = 'MULTIPLY'
                node_vig_mix.name = 'VigMix'
                links.new(node_vig_blr.outputs[0], node_vig_mix.inputs[2])
                
            node_vig_mix.inputs[0].default_value = ef.vignette_v/100
            links.new(latest_node.outputs[0], node_vig_dist.inputs[0])
            links.new(latest_node.outputs[0], node_vig_mix.inputs[1])
            node_vig_dist.location = (pos_x,-200)
            pos_x=pos_x+200
            node_vig_math.location = (pos_x,-200)
            pos_x=pos_x+200
            node_vig_blr.location = (pos_x,-200)
            pos_x=pos_x+200
            node_vig_mix.location = (pos_x,0)
            pos_x=pos_x+200
            latest_node = node_vig_mix
        else:
            try:
                nodes.remove(nodes['VigDist'])
                nodes.remove(nodes['VigMath'])
                nodes.remove(nodes['VigBlur'])
                nodes.remove(nodes['VigMix'])
            except:
                pass
                 
        # Cinematic Borders
        if ef.use_cinematic_border == True:
            img_x = scene.render.resolution_x
            img_y = scene.render.resolution_y
            try:
                img = bpy.data.images['cinematic_border']
            except:
                img = bpy.ops.image.new(name = "cinematic_border", width=img_x,height=img_y)
                img = bpy.data.images['cinematic_border']
                for area in bpy.context.screen.areas :
                    if area.type == 'IMAGE_EDITOR' :
                        rend = bpy.data.images['Render Result']
                        area.spaces.active.image = rend
            res_per = scene.render.resolution_percentage/100
            try:
                node_cb_img = nodes['Img sky']
                node_cb_trans1 = nodes['imgsky trans1']
                node_cb_trans2 = nodes['imgsky trans2']
                node_cb_alpha1 = nodes['imgsky alpha1']
                node_cb_alpha2 = nodes['imgsky alpha2']
            except:
                node_cb_img = nodes.new(type='CompositorNodeImage')
                node_cb_img.name = 'Img sky'
                node_cb_trans1 = nodes.new(type='CompositorNodeTransform')
                links.new(node_cb_img.outputs[0], node_cb_trans1.inputs[0])
                node_cb_trans1.name = 'imgsky trans1'
                node_cb_trans2 = nodes.new(type='CompositorNodeTransform')
                links.new(node_cb_img.outputs[0], node_cb_trans2.inputs[0])
                node_cb_trans2.name = 'imgsky trans2'
                node_cb_alpha1 = nodes.new(type='CompositorNodeAlphaOver')
                links.new(node_cb_trans1.outputs[0], node_cb_alpha1.inputs[2])
                node_cb_alpha1.name = 'imgsky alpha1'
                node_cb_alpha2 = nodes.new(type='CompositorNodeAlphaOver')
                node_cb_alpha2.name = 'imgsky alpha2'
                links.new(node_cb_alpha1.outputs[0], node_cb_alpha2.inputs[1])
                links.new(node_cb_trans2.outputs[0], node_cb_alpha2.inputs[2])
            node_cb_img.image = img
            node_cb_trans1.inputs[4].default_value = res_per
            node_cb_trans2.inputs[4].default_value = res_per
            node_cb_img.location=(pos_x-200,-400)
            node_cb_trans1.location = (pos_x,-200)
            pos_x = pos_x+200
            node_cb_trans2.location = (pos_x,-350)
            node_cb_alpha1.location = (pos_x,0)
            pos_x = pos_x+200
            node_cb_alpha2.location = (pos_x,0)
            pos_x = pos_x+200
            ma=(img_y*res_per)-(img_y*res_per)*ef.cinematic_border_v/2
            node_cb_trans1.inputs[2].default_value = ma
            node_cb_trans2.inputs[2].default_value = -ma
            links.new(latest_node.outputs[0], node_cb_alpha1.inputs[1])
            latest_node = node_cb_alpha2
        else:
            try:
                nodes.remove(nodes['Img sky'])
                nodes.remove(nodes['imgsky trans1'])
                nodes.remove(nodes['imgsky trans2'])
                nodes.remove(nodes['imgsky alpha1'])
                nodes.remove(nodes['imgsky alpha2'])    
            except:
                pass
            
        # Split Image
        if ef.split_image == True:
            try:
                node_split_alpha = nodes['split alpha']
                node_split_mask = nodes['split mask']
            except:
                node_split_alpha = nodes.new(type='CompositorNodeAlphaOver')
                node_split_alpha.name = 'split alpha'
                node_split_mask = nodes.new(type='CompositorNodeBoxMask')
                node_split_mask.name = 'split mask'
                links.new(node_split_mask.outputs[0], node_split_alpha.inputs[0])
                links.new(CIn.outputs[0], node_split_alpha.inputs[1])
            node_split_alpha.location = (pos_x,150)
            node_split_mask.location = (pos_x-200,250)
            pos_x = pos_x+200
            node_split_mask.x = -(1-(ef.split_v/100))
            node_split_mask.width = 2
            node_split_mask.height = 2
            links.new(latest_node.outputs[0], node_split_alpha.inputs[2])
            latest_node = node_split_alpha
        else:
            try:
                nodes.remove(nodes['split alpha'])
                nodes.remove(nodes['split mask'])
            except:
                pass
            
        # Flip image
        if ef.use_flip == True:
            try:
                node_flip = nodes['efFlip']
            except:    
                node_flip = nodes.new(type='CompositorNodeFlip')
                node_flip.name = 'efFlip'
            node_flip.location = (pos_x,0)
            pos_x = pos_x+200
            links.new(latest_node.outputs[0], node_flip.inputs[0])
            latest_node = node_flip
        else:
            try:
                nodes.remove(nodes['efFlip'])   
            except:
                pass  
        # Output
        links.new(latest_node.outputs[0], COut.inputs[0])  
        COut.location = (pos_x,0)
        
        
        # Transoarent Sky
        if ef_use_sky == False and s_sky == False:
            if bpy.context.scene.render.engine == 'BLENDER_RENDER' or bpy.context.scene.render.engine == 'BLENDER_GAME':
                scene.render.layers[layeri].use_sky = False
            else:
                bpy.context.scene.cycles.film_transparent = True
            s_sky = True
            self.report({'INFO'}, "Re-render Required")
        elif ef_use_sky == True and s_sky == True:
            if bpy.context.scene.render.engine == 'BLENDER_RENDER' or bpy.context.scene.render.engine == 'BLENDER_GAME':
                scene.render.layers[layeri].use_sky = True
            else:
                bpy.context.scene.cycles.film_transparent = False
            s_sky = False
            self.report({'INFO'}, "Re-render Required")
        return {'FINISHED'}



class UpdateRenderOperator(bpy.types.Operator):
    '''Update and Re-render'''
    bl_idname = "object.update_render_operator"
    bl_label = "Update and Re-render Operator"
    def execute(self, context):
        bpy.ops.object.update_operator()
        bpy.ops.render.render('INVOKE_DEFAULT')
        return {'FINISHED'}

class ResetSettingsOperator(bpy.types.Operator):
    '''Reset all settings'''
    bl_idname = "object.reset_settings_operator"
    bl_label = "Reset Settings"
    def execute(self, context):
        ef = bpy.context.scene.easyfx
        ef.use_auto_update = True
        # Filters
        ef.use_vignette = False
        ef.vignette_v = 70
        ef.use_glow = False
        ef.glow_em = False
        ef.glow_v =1
        ef.use_streaks = False
        ef.streaks_em = False
        ef.streaks_v = 1
        ef.streaks_n = 4
        ef.streaks_d = 0
        ef.sharpen_v = 0
        ef.soften_v = 0
        
        # Blurs
        ef.use_speedb = False
        ef.motionb_v = 1
        ef.use_dof = False
        ef.dof_v = 50
        
        
        # Color
        ef.bw_v =1
        ef.contrast_v = 0
        ef.brightness_v = 0
        ef.shadows_v = (1,1,1)
        ef.midtones_v = (1,1,1)
        ef.highlights_v = (1,1,1)
        ef.check_v = (1,1,1)
        
        # Distort / Lens
        ef.use_flip = False
        ef.lens_distort_v = 0
        ef.dispersion_v = 0
        ef.use_flare = False
        ef.flare_type = 'Fixed'
        ef.flare_c = (1,0.3,0.084, 1)    
        ef.flare_x = 0
        ef.flare_y = 0
        ef.flare_streak_intensity = 0.002
        ef.flare_streak_lenght = 1
        ef.flare_streak_angle = 0
        ef.flare_streak_streaks = 12
        ef.flare_glow = 0.03
        ef.flare_ghost = 1
        ef.flare_layer = (False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,False,False,False,False)
        ef.flaret_streak_intensity = 0.03
        ef.flaret_streak_lenght = 1.5
        ef.flaret_streak_angle = 0
        ef.flaret_streak_streaks = 12
        ef.flaret_glow = 0.1
        ef.flaret_ghost = 1.5
        ef.flare_center_size = 20
        
        # World
        ef.use_mist = False
        ef.mist_sky = True
        ef.mist_offset = 0
        ef.mist_size = 0.01
        ef.mist_min = 0
        ef.mist_max = 1
        ef.mist_color = (1,1,1,1)
        
        
          
        # Settings
        ef.use_cinematic_border = False
        ef.cinematic_border_v = 0.4
        ef.use_transparent_sky =False
        ef.use_cel_shading = False
        ef.cel_thickness = 1
        ef.split_image = False
        ef.split_v = 50
        ef.use_image_sky =False
        ef.image_sky_img = ""
        ef.image_sky_x = 0
        ef.image_sky_y = 0
        ef.image_sky_angle = 0
        ef.image_sky_scale = 1
        ef.layer_index = 0
        bpy.ops.object.update_operator()
        return {'FINISHED'}


# ------------------------------------------------------------------------
#   register and unregister functions
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.easyfx = PointerProperty(type=MySettings)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.easyfx

if __name__ == "__main__":
    register()