#BEGIN GPL LICENSE BLOCK

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software Foundation,
#Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

#END GPL LICENCE BLOCK

bl_info = {
    'name': "bTrace",
    'author': "liero, crazycourier, Atom, Meta-Androcto, MacKracken",
    'version': (1, 0, ),
    'blender': (2, 6, 4),
    'location': "View3D > Tools",
    'description': "Tools for converting/animating objects/particles into curves",
    'warning': "Still under development, bug reports appreciated",
    'wiki_url': "",
    'tracker_url': "",
    "category": "Learnbgame",
    }

#### TO DO LIST ####
### [   ]  Make grow animation happen to all selected, not just current
### [   ]  Adjust bevel radius for grow curve
### [   ]  Add Smooth option to curves
### [   ] Fix F-Curve Time Scale
### [   ] Grease Pencil doesn't show if nothing selected
    
    
import bpy
from bpy.props import *

# Class to define properties
class TracerProperties(bpy.types.PropertyGroup):
    p = bpy.props
    enabled = p.IntProperty(default=0)
    # Object Curve Settings
    TRcurve_spline = p.EnumProperty(name="Spline", items=(("POLY", "Poly", "Use Poly spline type"),  ("NURBS", "Nurbs", "Use Nurbs spline type"), ("BEZIER", "Bezier", "Use Bezier spline type")), description="Choose which type of spline to use when curve is created", default="BEZIER")
    TRcurve_handle = p.EnumProperty(name="Handle", items=(("ALIGNED", "Aligned", "Use Aligned Handle Type"), ("AUTOMATIC", "Automatic", "Use Auto Handle Type"), ("FREE_ALIGN", "Free Align", "Use Free Handle Type"), ("VECTOR", "Vector", "Use Vector Handle Type")), description="Choose which type of handle to use when curve is created",  default="VECTOR")
    TRcurve_resolution = p.IntProperty(name="Bevel Resolution" , min=1, max=32, default=4, description="Adjust the Bevel resolution")
    TRcurve_depth = p.FloatProperty(name="Bevel Depth", min=0.0, max=100.0, default=0.125, description="Adjust the Bevel depth")
    TRcurve_u = p.IntProperty(name="Resolution U", min=0, max=64, default=12, description="Adjust the Surface resolution")
    TRcurve_join = p.BoolProperty(name="Join Curves", default=False, description="Join all the curves after they have been created")
    # Option to Duplicate Mesh
    TRobject_duplicate = p.BoolProperty(name="Apply to Copy", default=False, description="Apply curve to a copy of object")
    # Distort Mesh options
    TRdistort_modscale = p.IntProperty(name="Modulation Scale", default=2, description="Add a scale to modulate the curve at random points, set to 0 to disable")
    TRdistort_noise = p.FloatProperty(name="Mesh Noise", min=0.0, max=50.0, default=0.00, description="Adjust noise added to mesh before adding curve")
    # Particle Options    
    TRparticle_step = p.IntProperty(name="Step Size", min=1, max=50, default=5, description="Sample one every this number of frames")
    TRparticle_auto = p.BoolProperty(name='Auto Frame Range', default=True, description='Calculate Frame Range from particles life')
    TRparticle_f_start = p.IntProperty( name='Start Frame', min=1, max=5000, default=1, description='Start frame')
    TRparticle_f_end = p.IntProperty( name='End Frame', min=1, max=5000, default=250, description='End frame')
    # F-Curve Modifier Properties
    TRfcnoise_rot = p.BoolProperty(name="Rotation", default=False, description="Affect Rotation")
    TRfcnoise_loc = p.BoolProperty(name="Location", default=True, description="Affect Location")
    TRfcnoise_scale = p.BoolProperty(name="Scale", default=False, description="Affect Scale")
    TRfcnoise_amp = p.IntProperty(name="Amp", min=1, max=500, default=5, description="Adjust the amplitude")
    TRfcnoise_timescale = p.FloatProperty(name="Time Scale", min=1, max=500, default=50, description="Adjust the time scale")
    TRfcnoise_key = p.BoolProperty(name="Add Keyframe", default=True, description="Keyframe is needed for tool, this adds a LocRotScale keyframe")
    # Toolbar Settings/Options Booleans
    TRcurve_settings = p.BoolProperty(name="Curve Settings", default=False, description="Change the settings for the created curve")
    TRparticle_settings = p.BoolProperty(name="Particle Settings", default=False, description="Show the settings for the created curve")
    TRanimation_settings = p.BoolProperty(name="Animation Settings", default=False, description="Show the settings for the Animations")
    TRdistort_curve = p.BoolProperty(name="Add Distortion", default=False, description="Set options to distort the final curve")
    TRconnect_noise = p.BoolProperty(name="F-Curve Noise", default=False, description="Adds F-Curve Noise Modifier to selected objects")
    TRsettings_objectTrace = p.BoolProperty(name="Object Trace Settings", default=False, description="Trace selected mesh object with a curve")
    TRsettings_objectsConnect = p.BoolProperty(name="Objects Connect Settings", default=False, description="Connect objects with a curve controlled by hooks")
    TRsettings_particleTrace = p.BoolProperty(name="Particle Trace Settings", default=False, description="Trace particle path with a  curve")
    TRsettings_particleConnect = p.BoolProperty(name="Particle Connect Settings", default=False, description="Connect particles with a curves and animated over particle lifetime")
    TRsettings_growCurve = p.BoolProperty(name="Grow Curve Settings", default=False, description="Animate curve bevel over time by keyframing points radius")
    TRsettings_fcurve = p.BoolProperty(name="F-Curve Settings", default=False, description="F-Curve Settings")
    # Toolbar Tool show/hide booleans
    TRtool_objectTrace = p.BoolProperty(name="Object Trace", default=False, description="Trace selected mesh object with a curve")
    TRtool_objectsConnect = p.BoolProperty(name="Objects Connect", default=False, description="Connect objects with a curve controlled by hooks")
    TRtool_particleTrace = p.BoolProperty(name="Particle Trace", default=False, description="Trace particle path with a  curve")
    TRtool_particleConnect = p.BoolProperty(name="Particle Connect", default=False, description="Connect particles with a curves and animated over particle lifetime")
    TRtool_growCurve = p.BoolProperty(name="Grow Curve", default=False, description="Animate curve bevel over time by keyframing points radius")
    TRtool_handwrite = p.BoolProperty(name="Handwriting", default=False, description="Create and Animate curve using the grease pencil")
    TRtool_fcurve = p.BoolProperty(name="F-Curve Noise", default=False, description="Add F-Curve noise to selected objects")
    # Animation Options
    TRanim_auto = p.BoolProperty(name='Auto Frame Range', default=True, description='Automatically calculate Frame Range')
    TRanim_f_start = p.IntProperty(name='Start', min=1, max=2500, default=1, description='Start frame / Hidden object')
    TRanim_length = p.IntProperty(name='Duration', min=1, soft_max=1000, max=2500, default=100, description='Animation Length')
    TRanim_f_fade = p.IntProperty(name='Fade After', min=0, soft_max=250, max=2500, default=10, description='Fade after this frames / Zero means no fade')
    TRanim_delay = p.IntProperty(name='Grow', min=0, max=50, default=5, description='Frames it takes a point to grow')
    TRanim_tails = p.BoolProperty(name='Tails', default=True, description='Set radius to zero for open splines endpoints')
    TRanim_keepr = p.BoolProperty(name='Radius', default=True, description='Try to keep radius data from original curve')
    TRanimate = p.BoolProperty(name="Animate Result", default=False, description='Animate the final curve objects')
    # Convert to Curve options
    TRconvert_conti = p.BoolProperty(name='Continuous', default=True, description='Create a continuous curve using verts from mesh')
    TRconvert_everyedge = p.BoolProperty(name='Every Edge', default=False, description='Create a curve from all verts in a mesh')
    TRconvert_edgetype = p.EnumProperty(name="Edge Type for Curves", 
        items=(("CONTI", "Continuous", "Create a continuous curve using verts from mesh"),  ("EDGEALL", "All Edges", "Create a curve from every edge in a mesh")), 
        description="Choose which type of spline to use when curve is created", default="CONTI")
    TRconvert_joinbefore = p.BoolProperty(name="Join objects before convert", default=False, description='Join all selected mesh to one object before converting to mesh')


############################    
## Draw Brush panel in Toolbar
############################
class addTracerObjectPanel(bpy.types.Panel):
    bl_label = "bTrace: Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'bTrace'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        bTrace=bpy.context.window_manager.curve_tracer
        obj = bpy.context.object
            
        ######################
        ## Start  Object Tools ###
        ######################
        row = self.layout.row()
        row.label(text="Object Tools")
        TRdistort_curve = bTrace.TRdistort_curve
        TRtool_objectTrace, TRsettings_objectTrace, TRconvert_joinbefore, TRconvert_edgetype = bTrace.TRtool_objectTrace, bTrace.TRsettings_objectTrace, bTrace.TRconvert_joinbefore, bTrace.TRconvert_edgetype
        TRanimate = bTrace.TRanimate
        TRanim_auto, TRcurve_join = bTrace.TRanim_auto, bTrace.TRcurve_join
        TRsettings_particleTrace, TRsettings_particleConnect = bTrace.TRsettings_particleTrace, bTrace.TRsettings_particleConnect
        sel = bpy.context.selected_objects
        ############################
        ### Object Trace
        ############################
        box = self.layout.box()
        row  = box.row ()
        ObjectText="Show: Objects Trace"
        if TRtool_objectTrace:
            ObjectText="Hide: Objects Trace"
        else:
            ObjectText="Show: Objects Trace"
        row.prop(bTrace, "TRtool_objectTrace", text=ObjectText, icon="FORCE_MAGNETIC")
        if TRtool_objectTrace:
            row  = box.row ()
            row.label(text="Object Trace", icon="FORCE_MAGNETIC")
            row.operator("object.btobjecttrace", text="Run!", icon="PLAY")  
            row  = box.row ()
            row.prop(bTrace, "TRsettings_objectTrace", icon='MODIFIER', text='Settings')
            row.label(text="")
            if TRsettings_objectTrace:
                row = box.row()
                row.label(text='Edge Draw Method')
                row = box.row(align=True)
                row.prop(bTrace, 'TRconvert_edgetype')
                box.prop(bTrace, "TRobject_duplicate")
                if len(sel) > 1 :
                    box.prop(bTrace, 'TRconvert_joinbefore')
                row = box.row()
                row.prop(bTrace, "TRdistort_curve")
                if TRdistort_curve:
                    col = box.column(align=True)
                    col.prop(bTrace, "TRdistort_modscale")
                    col.prop(bTrace, "TRdistort_noise")
                row = box.row()
                row.prop(bTrace, "TRanimate", text="Add Grow Curve Animation")
                if TRanimate:
                    # animation settings here
                    box.label(text='Frame Animation Settings:')
                    col = box.column(align=True)
                    col.prop(bTrace, 'TRanim_auto')
                    if not TRanim_auto:
                        row = col.row(align=True)
                        row.prop(bTrace,'TRanim_f_start')
                        row.prop(bTrace,'TRanim_length')
                    row = col.row(align=True)
                    row.prop(bTrace,'TRanim_delay')
                    row.prop(bTrace,'TRanim_f_fade')

                    box.label(text='Additional Settings')
                    row = box.row()
                    row.prop(bTrace,'TRanim_tails')
                    row.prop(bTrace,'TRanim_keepr')

        ############################
        ### Objects Connect
        ############################
        TRconnect_noise = bTrace.TRconnect_noise 
        TRtool_objectsConnect, TRsettings_objectsConnect = bTrace.TRtool_objectsConnect, bTrace.TRsettings_objectsConnect
        box = self.layout.box()
        row  = box.row ()
        ObjectConnText="Show: Objects Connect"
        if TRtool_objectsConnect:
            ObjectConnText="Hide: Objects Connect"
        else:
            ObjectConnText="Show: Objects Connect"
        row.prop(bTrace, "TRtool_objectsConnect", text=ObjectConnText, icon="OUTLINER_OB_EMPTY")
        if TRtool_objectsConnect:
            row  = box.row ()
            row.label(text="Objects Connect", icon="OUTLINER_OB_EMPTY")
            row.operator("object.btobjectsconnect", text="Run!", icon="PLAY")
            row = box.row()
            row.prop(bTrace, "TRsettings_objectsConnect", icon='MODIFIER', text='Settings')
            row.label(text='')
            if TRsettings_objectsConnect:
                box.prop(bTrace, "TRconnect_noise")
                if TRconnect_noise:
                    row = box.row()
                    row.label(text="F-Curve Noise")
                    row = box.row(align=True)
                    row.prop(bTrace, "TRfcnoise_rot")
                    row.prop(bTrace, "TRfcnoise_loc")
                    row.prop(bTrace, "TRfcnoise_scale")
                    col = box.column(align=True)
                    col.prop(bTrace, "TRfcnoise_amp")
                    col.prop(bTrace, "TRfcnoise_timescale")
                    box.prop(bTrace, "TRfcnoise_key")
                # Grow settings here
                row = box.row()
                row.prop(bTrace, "TRanimate", text="Add Grow Curve Animation")
                if TRanimate:
                    box.label(text='Frame Animation Settings:')
                    col = box.column(align=True)
                    col.prop(bTrace, 'TRanim_auto')
                    if not TRanim_auto:
                        row = col.row(align=True)
                        row.prop(bTrace,'TRanim_f_start')
                        row.prop(bTrace,'TRanim_length')
                    row = col.row(align=True)
                    row.prop(bTrace,'TRanim_delay')
                    row.prop(bTrace,'TRanim_f_fade')

                    box.label(text='Additional Settings')
                    row = box.row()
                    row.prop(bTrace,'TRanim_tails')
                    row.prop(bTrace,'TRanim_keepr')
    
        ############################
        ### Handwriting Tools
        ############################
        TRtool_handwrite = bTrace.TRtool_handwrite
        box = self.layout.box()
        row = box.row()
        handText="Show: Handwriting Tool"
        if TRtool_handwrite:
            handText="Hide: Handwriting Tool"
        else:
            handText="Show: Handwriting Tool"
        row.prop(bTrace, 'TRtool_handwrite', text=handText, icon='BRUSH_DATA')
        if TRtool_handwrite:
            row = box.row()
            row.label(text='Handwriting', icon='BRUSH_DATA')
            row.operator("curve.btwriting", text="Run!", icon='PLAY')
            box.prop(bTrace, "TRanimate", text="Grow Curve Animation Settings")
            if TRanimate:
                # animation settings here
                box.label(text='Frame Animation Settings:')
                col = box.column(align=True)
                col.prop(bTrace, 'TRanim_auto')
                if not TRanim_auto:
                    row = col.row(align=True)
                    row.prop(bTrace,'TRanim_f_start')
                    row.prop(bTrace,'TRanim_length')
                row = col.row(align=True)
                row.prop(bTrace,'TRanim_delay')
                row.prop(bTrace,'TRanim_f_fade')

                box.label(text='Additional Settings')
                row = box.row()
                row.prop(bTrace,'TRanim_tails')
                row.prop(bTrace,'TRanim_keepr')
            box.label(text='Grease Pencil Writing Tools')
            col = box.column(align=True)
            row = col.row()
            row.operator("gpencil.draw", text="Draw", icon='BRUSH_DATA').mode = 'DRAW'
            row.operator("gpencil.draw", text="Poly", icon='VPAINT_HLT').mode = 'DRAW_POLY'
            row = col.row(align=True)
            row.operator("gpencil.draw", text="Line", icon='ZOOMOUT').mode = 'DRAW_STRAIGHT'
            row.operator("gpencil.draw", text="Erase", icon='TPAINT_HLT').mode = 'ERASER'
            row = box.row()
            row.operator("gpencil.data_unlink", text="Delete Grease Pencil Layer", icon="CANCEL")
            row = box.row()
            
        
        ############################
        ### Particle Trace
        ############################
        TRtool_particleTrace = bTrace.TRtool_particleTrace
        box = self.layout.box()
        row = box.row()
        ParticleText="Show: Particle Trace"
        if TRtool_particleTrace:
            ParticleText="Hide: Particle Trace"
        else:
            ParticleText="Show: Particle Trace"
        row.prop(bTrace, "TRtool_particleTrace", icon="PARTICLES", text=ParticleText)
        if TRtool_particleTrace:
            row = box.row()
            row.label(text="Particle Trace", icon="PARTICLES")
            row.operator("particles.particletrace", text="Run!", icon="PLAY")
            row = box.row()
            row.prop(bTrace, 'TRsettings_particleTrace', icon='MODIFIER', text='Settings')
            row.label(text='')
            if TRsettings_particleTrace:
                box.prop(bTrace, "TRparticle_step")
                row = box.row()
                row.prop(bTrace, "TRcurve_join")
                row.prop(bTrace, "TRanimate", text="Add Grow Curve Animation")
                if TRanimate:
                    # animation settings here
                    box.label(text='Frame Animation Settings:')
                    col = box.column(align=True)
                    col.prop(bTrace, 'TRanim_auto')
                    if not TRanim_auto:
                        row = col.row(align=True)
                        row.prop(bTrace,'TRanim_f_start')
                        row.prop(bTrace,'TRanim_length')
                    row = col.row(align=True)
                    row.prop(bTrace,'TRanim_delay')
                    row.prop(bTrace,'TRanim_f_fade')

                    box.label(text='Additional Settings')
                    row = box.row()
                    row.prop(bTrace,'TRanim_tails')
                    row.prop(bTrace,'TRanim_keepr')
        
        ############################
        ### Connect Particles
        ############################
        TRparticle_auto = bTrace.TRparticle_auto
        TRtool_particleConnect = bTrace.TRtool_particleConnect
        box = self.layout.box()
        row = box.row()
        ParticleConnText="Show: Particle Connect"
        if TRtool_particleConnect:
            ParticleConnText="Hide: Particle Connect"
        else:
            ParticleConnText="Show: Particle Connect"
        row.prop(bTrace, "TRtool_particleConnect", icon="MOD_PARTICLES", text=ParticleConnText)
        if TRtool_particleConnect:
            row = box.row()
            row.label(text='Particle Connect', icon='MOD_PARTICLES')
            row.operator("particles.connect", icon="PLAY", text='Run!')
            row = box.row()
            row.prop(bTrace, 'TRsettings_particleConnect', icon='MODIFIER', text='Settings')
            row.label(text='')
            if TRsettings_particleConnect:
                box.prop(bTrace, "TRparticle_step")
                row= box.row()
                row.prop(bTrace, 'TRparticle_auto')
                row.prop(bTrace, 'TRanimate', text='Add Grow Curve Animation')
                col = box.column(align=True)
                if not TRparticle_auto:
                    row = box.row(align=True)
                    row.prop(bTrace, 'TRparticle_f_start')
                    row.prop(bTrace, 'TRparticle_f_end')
                if TRanimate:
                    # animation settings here
                    box.label(text='Frame Animation Settings:')
                    col = box.column(align=True)
                    col.prop(bTrace, 'TRanim_auto')
                    if not TRanim_auto:
                        row = col.row(align=True)
                        row.prop(bTrace,'TRanim_f_start')
                        row.prop(bTrace,'TRanim_length')
                    row = col.row(align=True)
                    row.prop(bTrace,'TRanim_delay')
                    row.prop(bTrace,'TRanim_f_fade')

                    box.label(text='Additional Settings')
                    row = box.row()
                    row.prop(bTrace,'TRanim_tails')
                    row.prop(bTrace,'TRanim_keepr')

        ############################
        ## Curve options
        ############################
        TRcurve_settings = bTrace.TRcurve_settings
        row = self.layout.row()
        row.label(text="Universal Curve Settings")
        box = self.layout.box()
        row = box.row()
        CurveSettingText="Show: Curve Settings"
        if TRcurve_settings:
            CurveSettingText="Hide: Curve Settings"
        else:
            CurveSettingText="Show: Curve Settings"
        row.prop(bTrace, 'TRcurve_settings', icon='CURVE_BEZCURVE', text=CurveSettingText)
        if TRcurve_settings:
            box.label(text="Curve Settings", icon="CURVE_BEZCURVE")
            if obj.type == 'CURVE':
                col = box.column(align=True)
                col.label(text="Edit Curves for")
                col.label(text="Selected Curve")
                col.prop(obj.data, 'bevel_depth')
                col.prop(obj.data, 'bevel_resolution')
                col.prop(obj.data, 'resolution_u')
            else:
                ############################
                ## Object Curve Settings 
                ############################
                TRcurve_spline, TRcurve_handle, TRcurve_depth, TRcurve_resolution, TRcurve_u = bTrace.TRcurve_spline, bTrace.TRcurve_handle, bTrace.TRcurve_depth, bTrace.TRcurve_resolution, bTrace.TRcurve_u
                box.label(text="New Curve Settings")
                box.prop(bTrace, "TRcurve_spline")
                box.prop(bTrace, "TRcurve_handle")
                col = box.column(align=True)
                col.prop(bTrace, "TRcurve_depth")
                col.prop(bTrace, "TRcurve_resolution")
                col.prop(bTrace, "TRcurve_u")

                
        #######################
        #### Animate Curve ####
        #######################
        row = self.layout.row()
        row.label(text="Curve Animation Tools")
        
        TRanimation_settings = bTrace.TRanimation_settings
        TRsettings_growCurve = bTrace.TRsettings_growCurve
        box = self.layout.box()
        row = box.row()
        GrowText="Show: Grow Curve Animation"
        if TRanimation_settings:
            GrowText="Hide: Grow Curve Animation"
        else:
            GrowText="Show: Grow Curve Animation"
        row.prop(bTrace, 'TRanimation_settings', icon="META_BALL", text=GrowText)
        if TRanimation_settings:
            row = box.row()
            row.label(text="Grow Curve", icon="META_BALL")
            row.operator('curve.btgrow', text='Run!', icon='PLAY')
            row = box.row()
            row.prop(bTrace, "TRsettings_growCurve", icon='MODIFIER', text='Settings')
            row.operator('object.btreset',  icon='KEY_DEHLT')
            if TRsettings_growCurve:
                box.label(text='Frame Animation Settings:')
                col = box.column(align=True)
                row = col.row(align=True)
                row.prop(bTrace,'TRanim_f_start')
                row.prop(bTrace,'TRanim_length')
                row = col.row(align=True)
                row.prop(bTrace,'TRanim_delay')
                row.prop(bTrace,'TRanim_f_fade')

                box.label(text='Additional Settings')
                row = box.row()
                row.prop(bTrace,'TRanim_tails')
                row.prop(bTrace,'TRanim_keepr')
                
        #######################
        #### F-Curve Noise Curve ####
        #######################
        TRtool_fcurve = bTrace.TRtool_fcurve
        TRsettings_fcurve = bTrace.TRsettings_fcurve
        box = self.layout.box()
        row = box.row()
        fcurveText="Show: F-Curve Noise"
        if TRtool_fcurve:
            fcurveText="Hide: F-Curve Noise"
        else:
            fcurveText="Show: F-Curve Noise"
        row.prop(bTrace, "TRtool_fcurve", text=fcurveText, icon='RNDCURVE')
        if TRtool_fcurve:
            row = box.row()
            row.label(text="F-Curve Noise", icon='RNDCURVE')
            row.operator("object.btfcnoise", icon='PLAY', text="Run!")
            row = box.row()
            row.prop(bTrace, "TRsettings_fcurve", icon='MODIFIER', text='Settings')
            row.operator('object.btreset',  icon='KEY_DEHLT')
            if TRsettings_fcurve:
                row = box.row(align=True)
                row.prop(bTrace, "TRfcnoise_rot")
                row.prop(bTrace, "TRfcnoise_loc")
                row.prop(bTrace, "TRfcnoise_scale")
                col = box.column(align=True)
                col.prop(bTrace, "TRfcnoise_amp")
                col.prop(bTrace, "TRfcnoise_timescale")
                box.prop(bTrace, "TRfcnoise_key")
###### END PANEL ##############
###############################            


################## ################## ################## ############
## Object Trace
## creates a curve with a modulated radius connecting points of a mesh
################## ################## ################## ############

class OBJECT_OT_objecttrace(bpy.types.Operator):
    bl_idname = "object.btobjecttrace"
    bl_label = "bTrace: Object Trace"
    bl_description = "Trace selected mesh object with a curve with the option to animate"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type in ['MESH'])
    
    def invoke(self, context, event):
        import bpy
        
        # Run through each selected object and convert to to a curved object
        brushObj = bpy.context.selected_objects
        TRobjectDupli = bpy.context.window_manager.curve_tracer.TRobject_duplicate # Get duplicate check setting
        TRconvert_joinbefore = bpy.context.window_manager.curve_tracer.TRconvert_joinbefore
        TRanimate = bpy.context.window_manager.curve_tracer.TRanimate
        # Duplicate Mesh
        if TRobjectDupli:
            bpy.ops.object.duplicate_move()
            brushObj = bpy.context.selected_objects
        # Join Mesh
        if TRconvert_joinbefore:
            bpy.ops.object.join()
            brushObj = bpy.context.selected_objects
        
        for i in brushObj:
            bpy.context.scene.objects.active = i
            if i and i.type == 'MESH':
                bpy.ops.object.btconvertcurve()
                addtracemat(bpy.context.object.data)
            if TRanimate:
                bpy.ops.curve.btgrow()
        return{"FINISHED"}


################## ################## ################## ############
## Objects Connect
## connect selected objects with a curve + hooks to each node
## possible handle types: 'FREE' 'AUTO' 'VECTOR' 'ALIGNED'
################## ################## ################## ############


class OBJECT_OT_objectconnect(bpy.types.Operator):
    bl_idname = "object.btobjectsconnect"
    bl_label = "bTrace: Objects Connect"
    bl_description = "Connect selected objects with a curve and add hooks to each node."
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (len(bpy.context.selected_objects) > 1)
    
    def invoke(self, context, event):
        import bpy
        list = []
        bTrace = bpy.context.window_manager.curve_tracer
        TRobjectHandle = bTrace.TRcurve_handle # Get Handle selection
        TRobjectrez = bTrace.TRcurve_resolution # Get Bevel resolution 
        TRobjectdepth = bTrace.TRcurve_depth # Get Bevel Depth
        TRanimate = bTrace.TRanimate # add Grow Curve
        
        # list objects
        for a in bpy.selection:  
            list.append(a)
            a.select = False

        # trace the origins
        tracer = bpy.data.curves.new('tracer','CURVE')
        tracer.dimensions = '3D'
        spline = tracer.splines.new('BEZIER')
        spline.bezier_points.add(len(list)-1)
        curve = bpy.data.objects.new('curve',tracer)
        bpy.context.scene.objects.link(curve)

        # render ready curve
        tracer.resolution_u = 64
        tracer.bevel_resolution = TRobjectrez # Set bevel resolution from Panel options
        tracer.fill_mode = 'FULL'
        tracer.bevel_depth = TRobjectdepth # Set bevel depth from Panel options

        # move nodes to objects
        for i in range(len(list)):
            p = spline.bezier_points[i]
            p.co = list[i].location
            p.handle_right_type=TRobjectHandle
            p.handle_left_type=TRobjectHandle

        bpy.context.scene.objects.active = curve
        bpy.ops.object.mode_set()

        # place hooks
        for i in range(len(list)):
            list[i].select = True
            curve.data.splines[0].bezier_points[i].select_control_point = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.hook_add_selob()
            bpy.ops.object.editmode_toggle()
            curve.data.splines[0].bezier_points[i].select_control_point = False
            list[i].select = False
        addtracemat(bpy.context.object.data) # Add material
        if TRanimate: # Add Curve Grow it?
            bpy.ops.curve.btgrow()
        for a in list : a.select = True
        ### add F-curve if statement here
        bTrace=bpy.context.window_manager.curve_tracer
        TRconnect_noise = bTrace.TRconnect_noise 
        if TRconnect_noise:
            bpy.ops.object.btfcnoise()
        return{"FINISHED"}


################## ################## ################## ############
## Particle Trace
## creates a curve from each particle of a system
################## ################## ################## ############
def  curvetracer(curvename, splinename):
    bTrace = bpy.context.window_manager.curve_tracer
    tracer = bpy.data.curves.new(splinename,'CURVE') 
    tracer.dimensions = '3D'
    curve = bpy.data.objects.new(curvename, tracer)
    bpy.context.scene.objects.link(curve)
    addtracemat(tracer) #Add material
    # tracer.materials.append(bpy.data.materials.get('TraceMat'))
    try: tracer.fill_mode = 'FULL'
    except: tracer.use_fill_front = tracer.use_fill_back = False
    tracer.bevel_resolution = bTrace.TRcurve_resolution
    tracer.bevel_depth = bTrace.TRcurve_depth
    tracer.resolution_u = bTrace.TRcurve_u
    return tracer
    

class OBJECT_OT_particletrace(bpy.types.Operator):
    bl_idname = "particles.particletrace"
    bl_label = "bTrace: Particle Trace"
    bl_description = "Creates a curve from each particle of a system. Keeping particle amount under 250 will make this run faster."
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (bpy.context.object and bpy.context.object.particle_systems)
    
    def execute(self, context):
        bTrace = bpy.context.window_manager.curve_tracer
        TRstepSize = bTrace.TRparticle_step    # step size in frames
        TRcurve_join = bTrace.TRcurve_join # join curves after created
        obj = bpy.context.object
        ps = obj.particle_systems.active
        
        if bTrace.TRcurve_join:
            tracer = curvetracer('Tracer', 'Splines')
        
        for x in ps.particles:
            if not bTrace.TRcurve_join:
                tracer = curvetracer('Tracer.000', 'Spline.000')
            spline = tracer.splines.new('BEZIER')
            spline.bezier_points.add((x.lifetime-1)//TRstepSize) #add point to spline based on 
            for t in list(range(int(x.lifetime))):
                bpy.context.scene.frame_set(t+x.birth_time)
                if not t%TRstepSize:            
                    p = spline.bezier_points[t//TRstepSize]
                    p.co = x.location
                    p.handle_right_type='AUTO'
                    p.handle_left_type='AUTO'     
                particlesObj = bpy.context.selected_objects
                for i in particlesObj:
                    bpy.context.scene.objects.active = i
                    if bTrace.TRanimate:
                        bpy.ops.curve.btgrow()
        return{"FINISHED"}


###########################################################################
## Particle Connect
## connect all particles in active system with a continuous animated curve
###########################################################################

class OBJECT_OT_traceallparticles(bpy.types.Operator):
    bl_idname = 'particles.connect'
    bl_label = 'Connect Particles'
    bl_description = 'Create a continuous animated curve from particles in active system.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (bpy.context.object and bpy.context.object.particle_systems)

    def execute(self, context):
        
        obj = bpy.context.object
        ps = obj.particle_systems.active
        set = ps.settings

        # Grids distribution not supported
        if set.distribution == 'GRID':
            self.report('INFO',"Grid distribution mode for particles not supported.")
            return{'FINISHED'}
        
        bTrace = bpy.context.window_manager.curve_tracer
        TRparticleHandle = bTrace.TRcurve_handle # Get Handle selection
        TRparticleSpline = bTrace.TRcurve_spline # Get Spline selection  
        TRstepSize = bTrace.TRparticle_step    # step size in frames
        TRparticlerez = bTrace.TRcurve_resolution # Get Bevel resolution 
        TRparticledepth = bTrace.TRcurve_depth # Get Bevel Depth
        TRparticleauto = bTrace.TRparticle_auto # Get Auto Time Range
        TRparticle_f_start = bTrace.TRparticle_f_start # Get frame start
        TRparticle_f_end = bTrace.TRparticle_f_end # Get frame end
        
        tracer = bpy.data.curves.new('Splines','CURVE') # define what kind of object to create
        curve = bpy.data.objects.new('Tracer',tracer) # Create new object with settings listed above
        bpy.context.scene.objects.link(curve) # Link newly created object to the scene
        spline = tracer.splines.new('BEZIER')  # add a new Bezier point in the new curve
        spline.bezier_points.add(set.count-1)
		
        tracer.dimensions = '3D'
        tracer.resolution_u = 32
        tracer.bevel_resolution = 1
        tracer.fill_mode = 'FULL'
        tracer.bevel_depth = 0.025

        addtracemat(tracer) #Add material

        if TRparticleauto:
            f_start = int(set.frame_start)
            f_end = int(set.frame_end + set.lifetime)
        else:
            if TRparticle_f_end <= TRparticle_f_start:
                 TRparticle_f_end = TRparticle_f_start + 1
            f_start = TRparticle_f_start
            f_end = TRparticle_f_end
        print ('range: ', f_start, '/', f_end)

        for bFrames in range(f_start, f_end):
            bpy.context.scene.frame_set(bFrames)
            if not (bFrames-f_start) % TRstepSize:
                print ('done frame: ',bFrames)
                for bFrames in range(set.count):
                    if ps.particles[bFrames].alive_state != 'UNBORN': 
                        e = bFrames
                    spline.bezier_points[bFrames].co = ps.particles[e].location
                    spline.bezier_points[bFrames].handle_left = ps.particles[e].location
                    spline.bezier_points[bFrames].handle_right = ps.particles[e].location
                    spline.bezier_points[bFrames].handle_right_type=TRparticleHandle
                    spline.bezier_points[bFrames].handle_left_type=TRparticleHandle
                    spline.bezier_points[bFrames].keyframe_insert('co')
                    spline.bezier_points[bFrames].keyframe_insert('handle_left')
                    spline.bezier_points[bFrames].keyframe_insert('handle_right')
        particlesObj = bpy.context.selected_objects
        for i in particlesObj:
            bpy.context.scene.objects.active = i
            if bTrace.TRanimate:
                bpy.ops.curve.btgrow()
        return{'FINISHED'}

################## ################## ################## ############
## Writing Tool
## Writes a curve by animating its point's radii
## 
################## ################## ################## ############
class OBJECT_OT_writing(bpy.types.Operator):
    bl_idname = 'curve.btwriting'
    bl_label = 'Write'
    bl_description = 'Use Grease Pencil to write and convert to curves'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type in ['MESH','FONT','CURVE'])

    def execute(self, context):
        bTrace, obj = bpy.context.window_manager.curve_tracer, bpy.context.object
        TRanimate = bTrace.TRanimate
        gactive = bpy.context.active_object # set selected object before convert
        bpy.ops.gpencil.convert(type='CURVE')
        gactiveCurve = bpy.context.active_object # get curve after convert
        writeObj = bpy.context.selected_objects
        for i in writeObj:
            bpy.context.scene.objects.active = i
            bpy.ops.curve.btgrow()
            addtracemat(bpy.context.object.data) #Add material
        # Delete grease pencil strokes
        bpy.context.scene.objects.active = gactive
        bpy.ops.gpencil.data_unlink()
        bpy.context.scene.objects.active = gactiveCurve
        # Return to first frame
        bpy.context.scene.frame_set(bTrace.TRanim_f_start)
        
        return{'FINISHED'}

################## ################## ################## ############
## Create Curve
## Convert mesh to curve using either Continuous, All Edges, or Sharp Edges
## Option to create noise
################## ################## ################## ############

class OBJECT_OT_convertcurve(bpy.types.Operator):
    bl_idname = "object.btconvertcurve"
    bl_label = "bTrace: Create Curve"
    bl_description = "Convert mesh to curve using either Continuous, All Edges, or Sharp Edges"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        import bpy, random, mathutils
        from mathutils import Vector

        bTrace = bpy.context.window_manager.curve_tracer
        TRdistort_modscale = bTrace.TRdistort_modscale # add a scale to the modular random 
        TRdistort_curve = bTrace.TRdistort_curve    # modulate the resulting curve
        TRobjectHandle = bTrace.TRcurve_handle # Get Handle selection
        TRobjectSpline = bTrace.TRcurve_spline # Get Spline selection
        TRobjectDupli = bTrace.TRobject_duplicate # Get duplicate check setting
        TRobjectrez = bTrace.TRcurve_resolution # Get Bevel resolution 
        TRobjectdepth = bTrace.TRcurve_depth # Get Bevel Depth
        TRobjectU = bTrace.TRcurve_u # Get Bevel Depth
        TRobjectnoise = bTrace.TRdistort_noise # Get Bevel Depth
        TRconvert_joinbefore = bTrace.TRconvert_joinbefore 
        TRconvert_edgetype = bTrace.TRconvert_edgetype
        TRtraceobjects = bpy.context.selected_objects # create a list with all the selected objects

        obj = bpy.context.object
        
        ### Convert Font... But not working right now ???
        if obj.type == 'FONT':
            bpy.ops.object.mode_set()
            bpy.ops.object.convert(target='CURVE') # Convert edges to curve
            bpy.context.object.data.dimensions = '3D'
            
        # make a continuous edge through all vertices
        if obj.type == 'MESH':
            # Add noise to mesh
            if TRdistort_curve:
                for v in obj.data.vertices:
                    for u in range(3):
                        v.co[u] += TRobjectnoise*(random.random()*2-1)

            if TRconvert_edgetype == 'CONTI':
                ## Start Continuous edge
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.delete(type='EDGE_FACE')
                bpy.ops.mesh.select_all(action='DESELECT')
                verts = bpy.context.object.data.vertices
                bpy.ops.object.mode_set()
                li = []
                p1 = int(random.random()*(1+len(verts))) 
                if p1 >= len(verts):
                    p1 = int(random.random()*(1+len(verts)))
                
                for v in verts: li.append(v.index)
                li.remove(p1)
                for z in range(len(li)):
                    x = 999
                    for px in li:
                        d = verts[p1].co - verts[px].co
                        if d.length < x:
                            x = d.length
                            p2 = px
                    verts[p1].select = verts[p2].select = True
                    bpy.ops.object.editmode_toggle()
                    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
                    bpy.ops.mesh.edge_face_add()
                    bpy.ops.object.editmode_toggle()
                    verts[p1].select = verts[p2].select = False
                    li.remove(p2)
                    p1 = p2
                # Convert edges to curve
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.convert(target='CURVE') 
            
            if TRconvert_edgetype == 'EDGEALL':
                ## Start All edges
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.delete(type='ONLY_FACE')
                bpy.ops.object.mode_set()
                bpy.ops.object.convert(target='CURVE')
                for sp in obj.data.splines:
                    sp.type = 'BEZIER'

        obj = bpy.context.object
        # Set spline type to custom property in panel
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.spline_type_set(type=TRobjectSpline) 
        # Set handle type to custom property in panel
        bpy.ops.curve.handle_type_set(type=TRobjectHandle) 
        bpy.ops.object.editmode_toggle()
        obj.data.fill_mode = 'FULL'
        # Set resolution to custom property in panel
        obj.data.bevel_resolution = TRobjectrez 
        obj.data.resolution_u = TRobjectU 
        # Set depth to custom property in panel
        obj.data.bevel_depth = TRobjectdepth 
        
        # Modulate curve radius and add distortion
        if TRdistort_curve: 
            scale = TRdistort_modscale
            if scale == 0:
                return{"FINISHED"}
            for u in obj.data.splines:
                for v in u.bezier_points:
                    v.radius = scale*round(random.random(),3) 
        
        return{"FINISHED"}


###################################################################
#### Add Tracer Material
###################################################################        

def addtracemat(matobj):
    if 'TraceMat' not in bpy.data.materials:
        TraceMat = bpy.data.materials.new('TraceMat')
        TraceMat.diffuse_color = [0,.5,1]
        TraceMat.specular_intensity = 0.5
    matobj.materials.append(bpy.data.materials.get('TraceMat'))
    return {'FINISHED'}
        
################## ################## ################## ############
## F-Curve Noise
## will add noise modifiers to each selected object f-curves
## change type to: 'rotation' | 'location' | 'scale' | '' to effect all
## first record a keyframe for this to work (to generate the f-curves)
################## ################## ################## ############

class OBJECT_OT_fcnoise(bpy.types.Operator):
    bl_idname = "object.btfcnoise"
    bl_label = "bTrace: F-curve Noise"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        import bpy, random
        
        bTrace = bpy.context.window_manager.curve_tracer
        TR_amp = bTrace.TRfcnoise_amp
        TR_timescale = bTrace.TRfcnoise_timescale
        TR_addkeyframe = bTrace.TRfcnoise_key
        
        # This sets properties for Loc, Rot and Scale if they're checked in the Tools window
        noise_rot = 'rotation'
        noise_loc = 'location'
        noise_scale = 'scale'
        if not bTrace.TRfcnoise_rot:
            noise_rot = 'none'
        if not bTrace.TRfcnoise_loc:
            noise_loc = 'none'
        if not bTrace.TRfcnoise_scale:
            noise_scale = 'none'
            
        type = noise_loc, noise_rot, noise_scale # Add settings from panel for type of keyframes
        amplitude = TR_amp
        time_scale = TR_timescale
        
        # Add keyframes, this is messy and should only add keyframes for what is checked
        if TR_addkeyframe == True:
            bpy.ops.anim.keyframe_insert(type="LocRotScale") 
        
        for obj in bpy.context.selected_objects:
            if obj.animation_data:
                for c in obj.animation_data.action.fcurves:
                    if c.data_path.startswith(type):
                        # clean modifiers
                        for m in c.modifiers : c.modifiers.remove(m)
                        # add noide modifiers
                        n = c.modifiers.new('NOISE')
                        n.strength = amplitude
                        n.scale = time_scale
                        n.phase = int(random.random() * 999)
        return{"FINISHED"}

################## ################## ################## ############
## Curve Grow Animation
## Animate curve radius over length of time
################## ################## ################## ############     
class OBJECT_OT_curvegrow(bpy.types.Operator):
    bl_idname = 'curve.btgrow'
    bl_label = 'Run Script'
    bl_description = 'Keyframe points radius'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type in ['FONT','CURVE'])
    
    def execute(self, context):
        bTrace, obj = bpy.context.window_manager.curve_tracer, bpy.context.object
        TRanim_f_start, TRanim_length, TRanim_auto = bTrace.TRanim_f_start, bTrace.TRanim_length, bTrace.TRanim_auto
        # make the curve visible
        try: obj.data.fill_mode = 'FULL'
        except: obj.data.use_fill_front = obj.data.use_fill_back = False
        if not obj.data.bevel_resolution:
            obj.data.bevel_resolution = 5
        if not obj.data.bevel_depth:
            obj.data.bevel_depth = 0.1
        if TRanim_auto:
            TRanim_f_start = bpy.context.scene.frame_start
            TRanim_length = bpy.context.scene.frame_end
        # get points data and beautify
        actual, total = TRanim_f_start, 0
        for sp in obj.data.splines:
            total += len(sp.points) + len(sp.bezier_points)
        step = TRanim_length / total
        for sp in obj.data.splines:
            sp.radius_interpolation = 'BSPLINE'
            po = [p for p in sp.points] + [p for p in sp.bezier_points]
            if not bTrace.TRanim_keepr:
                for p in po: p.radius = 1
            if bTrace.TRanim_tails and not sp.use_cyclic_u:
                po[0].radius = po[-1].radius = 0
                po[1].radius = po[-2].radius = .65
            ra = [p.radius for p in po]

            # record the keyframes
            for i in range(len(po)):
                bpy.context.scene.frame_set(actual)
                po[i].radius = 0
                po[i].keyframe_insert('radius')
                actual += step
                bpy.context.scene.frame_set(actual + bTrace.TRanim_delay)
                po[i].radius = ra[i]
                po[i].keyframe_insert('radius')

                if bTrace.TRanim_f_fade:
                    bpy.context.scene.frame_set(actual + bTrace.TRanim_f_fade - step)
                    po[i].radius = ra[i]
                    po[i].keyframe_insert('radius')
                    bpy.context.scene.frame_set(actual + bTrace.TRanim_delay + bTrace.TRanim_f_fade)
                    po[i].radius = 0
                    po[i].keyframe_insert('radius')

        bpy.context.scene.frame_set(bTrace.TRanim_f_start)
        return{'FINISHED'}

################## ################## ################## ############
## Remove animation and curve radius data
################## ################## ################## ############
class OBJECT_OT_reset(bpy.types.Operator):
    bl_idname = 'object.btreset'
    bl_label = 'Clear animation'
    bl_description = 'Remove animation / curve radius data'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object
        multi = bpy.context.selected_objects
        ### Need to make this work on a entire group, only works on one object so far
        obj.animation_data_clear()
        if obj.type == 'CURVE':
            print('Its curvalicious')
            for sp in obj.data.splines:
                po = [p for p in sp.points] + [p for p in sp.bezier_points]
                for p in po:
                    p.radius = 1
        return{'FINISHED'}


#############################################################
###  Select order tool - thanks to MacKracken
#### writes bpy.selection when a new object is selected or deselected
#### it compares bpy.selection with bpy.context.selected_objects
#############################################################

def select():
	if bpy.context.mode=="OBJECT":
		obj = bpy.context.object
		sel = len(bpy.context.selected_objects)
		
		if sel==0:
			bpy.selection=[]
		else:
			if sel==1:
				bpy.selection=[]
				bpy.selection.append(obj)
			elif sel>len(bpy.selection):
				for sobj in bpy.context.selected_objects:
					if (sobj in bpy.selection)==False:
						bpy.selection.append(sobj)
			
			elif sel<len(bpy.selection):
				for it in bpy.selection:
					if (it in bpy.context.selected_objects)==False:
						bpy.selection.remove(it)		

	#on edit mode doesnt work well

#executes selection by order at 3d view
class Selection(bpy.types.Header):
	bl_label = "Selection"
	bl_space_type = "VIEW_3D"
	
	def __init__(self):
		#print("hey")
		select()

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.label("Sel: "+str(len(bpy.selection)))      

### Define Classes to register
classes = [TracerProperties,
    addTracerObjectPanel,
    OBJECT_OT_convertcurve,
    OBJECT_OT_objecttrace,
    OBJECT_OT_objectconnect,
    OBJECT_OT_writing,
    OBJECT_OT_particletrace,
    OBJECT_OT_traceallparticles,
    OBJECT_OT_curvegrow,
    OBJECT_OT_reset,
    OBJECT_OT_fcnoise,
    Selection]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.curve_tracer = bpy.props.PointerProperty(type=TracerProperties)
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.WindowManager.curve_tracer
if __name__ == "__main__":
    register()