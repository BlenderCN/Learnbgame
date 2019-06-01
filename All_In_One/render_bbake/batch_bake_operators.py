import bpy
from bpy.props import *
from bpy.types import Operator
from .batch_bake_utils import *

import os
from time import time
####################################################################

def bake_aov(context, ob, aov):
    STARTAOV = time()
    render = context.scene.render
    bake_settings = render.bake

    #SET SCENE SETTINGS TO AOV SETTINGS
    set_pass_settings(context, aov)

    #FILEPATH AND IMAGE SETUP
    image = setup_materials(ob, aov)

    #DO THE BAKING
    msg('\nBaking "%s"  - - >  %s' %(ob.name, aov.name))
    context.scene.update()
    bpy.ops.object.bake(type=aov.name.upper(),
                        filepath=image.filepath,
                        save_mode='INTERNAL',
                        width=image.generated_width,
                        height=image.generated_height,
                        margin=bake_settings.margin,
                        cage_extrusion=bake_settings.cage_extrusion,
                        use_cage=bake_settings.use_cage,
                        cage_object=bake_settings.cage_object,
                        normal_space=bake_settings.normal_space,
                        normal_r=bake_settings.normal_r,
                        normal_g=bake_settings.normal_g,
                        normal_b=bake_settings.normal_b,
                        use_split_materials=bake_settings.use_split_materials,
                        use_selected_to_active=bake_settings.use_selected_to_active,
                        use_clear=bake_settings.use_clear,
                        )


    image.save_render(image.filepath, context.scene)
    ENDAOV = time() - STARTAOV
    msg('AOV: %s    Time: %s Seconds\n%s' %(aov.name.ljust(13), str(round(ENDAOV, 2)), image.filepath))
    update_image(image)
    ### AOV FINISHED

def testob(ob):
    '''Make sure this object is bakeable'''
    bbake = ob.bbake
    ob_settings = bbake.ob_settings

    #IS MESH
    if not ob.type == 'MESH':
        return False

    #BBAKE TURNED ON
    if not ob_settings.use:
        return False

    #FILEPATH IS WRITEABLE
    path = bpy.path.abspath(ob_settings.path)
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except:
            msg('FAILED to create bake Folder:%s\n for object "%s"\nSkipping.' %(path, ob.name))
            return False

    #ADD UV_LAYER
    if not ob.data.uv_layers:
        uv_layer = add_smart_projection(ob)
        if not uv_layer:
            msg('"%s": Failed to add UVs. Skipping' %(ob.name))
            return False

    #ADD MATERIAL
    if not has_material(ob):
        material = add_material(ob)
        if not material:
            msg('"%s": Failed to add Material. Skipping' %(ob.name))
            return False

    #IS RENDER RESTRICTED
    if ob.hide_render:
        msg('"%s" is set not renderable. Skipping' %(ob.name))
        return False

    return True

def bbake_bake_selected(self, context):
    render = context.scene.render
    bake_settings = render.bake
    if not self.all:
        objects_to_bake = [ob for ob in context.selected_objects if testob(ob)]
    else:
        objects_to_bake = [ob for ob in context.scene.objects if testob(ob)]
    msg('\n%s\nBatch Baking Objects started:\n%s'%('_'*40, str([ob.name for ob in objects_to_bake])))

    ### BAKE ALL OBJECTS IN SELECTION
    STARTALL = time()
    for ob in objects_to_bake:
        STARTOB = time()
        bbake = ob.bbake
        ob_settings = bbake.ob_settings

        #Set scene bake settings to this obs ob_settings
        set_ob_settings(context, ob)

        #deselect all obs
        for obj in context.scene.objects:
            obj.select = False

        #setup bake object
        ob.select = True
        context.scene.objects.active = ob

        msg('\n%s'%('_'*40))
        #IF SELECTED TO ACTIVE
        if ob_settings.use_selected_to_active:

            #Names of Source objects for selected to active baking
            source_names = [s.strip() for s in ob_settings.sources.split(',')]

            found_sources = []
            for obinscene in context.scene.objects:
                if bake_settings.use_selected_to_active:
                    if obinscene.name in source_names:
                        obinscene.select = True
                        found_sources.append(obinscene)

            msg('\n\n%s\nActive: "%s" --> Selected: %s' %('_'*40, ob.name, str([ob.name for ob in found_sources])))
            #abort object if no sources found
            if not found_sources:
                msg('No Source Objects found for %s' %(ob.name))
                continue

            #store single source if available
            if ob_settings.align:
                if len(source_names) == 1:
                    source_ob = next(iter([ob_sel for ob_sel in context.selected_objects
                                           if not ob_sel == ob]), None)
                else:
                    source_ob = None

            ## Align origins
            if ob_settings.align and source_ob:
                source_start = source_ob.location.copy()
                source_ob.location = ob.location

                if bake_settings.cage_object:
                    cage_ob = context.scene.objects[bake_settings.cage_object]
                    cage_start = cage_ob.location.copy()
                    cage_ob.location = ob.location


        ## BAKE AOVs
        context.scene.update()


        if bbake.aov_combined.use:
            bake_aov(context, ob, bbake.aov_combined)

        if bbake.aov_diffuse.use:
            bake_aov(context, ob, bbake.aov_diffuse)

        if bbake.aov_glossy.use:
            bake_aov(context, ob, bbake.aov_glossy)

        if bbake.aov_transmission.use:
            bake_aov(context, ob, bbake.aov_transmission)

        if bbake.aov_subsurface.use:
            bake_aov(context, ob, bbake.aov_subsurface)

        if bbake.aov_normal.use:
            bake_aov(context, ob, bbake.aov_normal)

        if bbake.aov_ao.use:
            bake_aov(context, ob, bbake.aov_ao)

        if bbake.aov_shadow.use:
            bake_aov(context, ob, bbake.aov_shadow)

        if bbake.aov_emit.use:
            bake_aov(context, ob, bbake.aov_emit)

        if bbake.aov_uv.use:
            bake_aov(context, ob, bbake.aov_uv)

        if bbake.aov_environment.use:
            bake_aov(context, ob, bbake.aov_environment)

        ### CLEANUP
        #IF SELECTED TO ACTIVE
        if ob_settings.use_selected_to_active:
            #reset aligned objects
            if ob_settings.align and source_ob:
                source_ob.location = source_start
                if bake_settings.cage_object:
                    cage_ob.location = cage_start

        OBTIME = time() - STARTOB
        msg('\nOBJECT: %s Time: %s Seconds' %(ob.name.ljust(13), str(round(OBTIME, 2))))

        if context.scene.bbake.turn_off:
            ob.bbake.ob_settings.use = False
        #### OB FINISHED

    ENDALL = time() - STARTALL
    msg('\nALL OBJECTS           Time: %s Seconds' %(str(round(ENDALL, 2))))
    ### ALL FINISHED

class BBake_Bake_Selected(Operator):
    ''''''
    bl_idname = "scene.bbake_bake_selected"
    bl_label = "BBake Bake Selected"
    bl_options = {'REGISTER'}
    bl_description = "BBake objects."

    all = BoolProperty(
        name='All Objects',
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'}
        )

    ##### POLL #####
    @classmethod
    def poll(cls, context):
        return context.selected_objects

    ##### EXECUTE #####
    def execute(self, context):
        setup_log()
        bbake_bake_selected(self, context)
        msg('\nDONE BAKING...\n\n')
        self.report({'INFO'}, 'Report in Text "BBake Baking Report"')
        return {'FINISHED'}

###########################################################################
def bbake_set_sources(self, context):
    active = context.active_object
    ob_settings = active.bbake.ob_settings

    if self.clear:
        ob_settings.sources = ''
        return

    renderable = {'MESH', 'CURVE', 'FONT', 'META', 'SURFACE'}
    sources = [ob for ob in context.selected_objects
               if ob.type in renderable
               and not ob == active]
    source_names = [ob.name for ob in sources]
    if not source_names:
        ob_settings.sources = ''
        return

    source_names = ', '.join(source_names)

    ob_settings.sources = source_names

class BBake_Set_Sources(Operator):
    ''''''
    bl_idname = "object.set_bbake_sources"
    bl_label = "BBake Set Sources"
    bl_options = {'REGISTER', 'UNDO'}

    bl_description = "Set sources for baking selected (sources) to active (this active object)."

    clear = BoolProperty(
        name='Clear Source List',
        default=False,
        )

    ##### POLL #####
    @classmethod
    def poll(cls, context):
        return context.active_object

    ##### EXECUTE #####
    def execute(self, context):
        bbake_set_sources(self, context)
        return {'FINISHED'}

####################################################################
class BBake_Setup_Copy_Settings(Operator):
    ''''''
    bl_idname = "object.bbake_copy_settings"
    bl_label = "BBake Copy Settings to Selected"
    bl_options = {'REGISTER'}
    bl_description = "Copy BBake Settings from this object to selected"

    copy_aov = BoolProperty(
        name='Copy AOVs',
        default=True,
        )
    copy_ob_settings = BoolProperty(
        name='Copy object Settings',
        default=False,
        )

    ##### POLL #####
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 1

    ##### EXECUTE #####
    def execute(self, context):
        bbake_copy_settings(self, context)
        return {'FINISHED'}

####################################################################
def register():
    #print('\nREGISTER:\n', __name__)
    bpy.utils.register_class(BBake_Bake_Selected)
    bpy.utils.register_class(BBake_Set_Sources)
    bpy.utils.register_class(BBake_Setup_Copy_Settings)

def unregister():
    #print('\nUN-REGISTER:\n', __name__)
    bpy.utils.unregister_class(BBake_Bake_Selected)
    bpy.utils.unregister_class(BBake_Set_Sources)
    bpy.utils.unregister_class(BBake_Setup_Copy_Settings)
