######################################################################################################
# A simple add-on that enhance the override material tool (from renderlayer panel)                   #
# Actualy partly uncommented - if you do not understand some parts of the code,                      #
# please see further version or contact me                                                           #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################


############# Add-on description (used by Blender)

bl_info = {
    "name": "Material Advanced Override",
    "description": 'Material Override Tools - with advanced exclude options',
    "author": "Lapineige",
    "version": (1, 6),
    "blender": (2, 72, 0),
    "location": "Properties > Render Layers",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=26&t=810",
    "category": "Learnbgame"
}

import bpy
import blf
from bpy.app.handlers import persistent

############
# Properties

bpy.types.Scene.OW_only_selected = bpy.props.BoolProperty(name='Affect Only Selected', default=False, description='Override material only for selected objects')
bpy.types.Scene.OW_exclude_type = bpy.props.EnumProperty(items=[('index','Material Index','Exclude by Material Index',0),('group','Group','Exclude by Object Group',1),('layer','Layer','Exclude by Layer',2),('emit','Emit','Exclude materials using emission shader',3)], description='Set exclusion criterion')
bpy.types.Scene.OW_pass_index = bpy.props.IntProperty(name='Pass Index', default=1, description='(Material) pass index exclude')
bpy.types.Scene.OW_material = bpy.props.StringProperty(name='Material', maxlen=63, description='Material to exclude')
bpy.types.Scene.OW_group = bpy.props.StringProperty(name='Group', maxlen=63, description='Group of objects to exclude')
bpy.types.Scene.OW_display_override = bpy.props.BoolProperty(name="Show 'Override ON' Reminder", default=True, description="Show 'Override On' in the 3D view")
bpy.types.Scene.OW_start_on_render = bpy.props.BoolProperty(name="Override Render", default=False, description='Override material during render')
bpy.types.Scene.OW_vis_hide_camera = bpy.props.BoolProperty(name="Hide From Camera", default=False, description='Hide excluded objects from camera rays')


############

def draw_callback_px(self, context):
    if context.scene.OW_display_override:
        font_id = 0  # XXX, need to find out how best to get this
        blf.position(font_id, 28, bpy.context.area.height-85, 0)
        blf.draw(font_id, "Override ON")
        
############
# Layout

class AdvancedMaterialOverride(bpy.types.Panel):
    """  """
    bl_label = "Advanced Material Override"
    bl_idname = "advanced_material_override"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render_layer"  
    
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        if bpy.types.RENDER_OT_override_setup.l_mat:
            row.operator('render.override_restore')
            row.prop(context.scene, 'OW_start_on_render', toggle=True, icon='RENDER_STILL')
            layout.prop(context.scene, 'OW_display_override')
        else:
            row.operator('render.override_setup')
            row.prop(context.scene, 'OW_start_on_render', toggle=True, icon='RENDER_STILL')

        layout.prop_search(context.scene, "OW_material", bpy.data, "materials", icon='MATERIAL_DATA')
        layout.prop(context.scene, 'OW_only_selected', toggle=True, icon='BORDER_RECT')
        
        box = layout.box()
        box.label('Exclude from effect:')
        box.prop(context.scene, 'OW_vis_hide_camera', toggle=True, icon='RESTRICT_VIEW_ON')
        row = box.row()
        row.prop(context.scene, 'OW_exclude_type', expand=True)
        if context.scene.OW_exclude_type == 'index':
            box.prop(context.scene, 'OW_pass_index')
        elif context.scene.OW_exclude_type == 'group':
            box.prop_search(context.scene, "OW_group", bpy.data, "groups", icon='GROUP')
        elif context.scene.OW_exclude_type == 'layer':
            box.prop(context.scene, 'override_layer', text='')

############
# Viewport

class OverrideDraw(bpy.types.Operator):
    """  """
    bl_idname = "view3d.display_override"
    bl_label = "Display Override"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        #context.area.tag_redraw()
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
        return {'FINISHED'}

############
# Operators

class OverrideSetup(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "render.override_setup"
    bl_label = "Override Setup"
    
    l_mat = list()
    l_mesh = list()
    l_hidden = list()
    
    bpy.types.Scene.override_layer = bpy.props.BoolVectorProperty(subtype='LAYER', size=20, default=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    
    @classmethod
    def poll(cls, context):
        if not bpy.context.scene.render.engine == 'CYCLES':
            return False
        if context.scene.OW_exclude_type == 'group' and not context.scene.OW_group:
            return False
        if context.scene.OW_exclude_type == 'layer' and not True in [i for i in context.scene.override_layer]:
            return False
        return context.scene.OW_material
    
    def execute(self, context):

        for obj in bpy.data.objects:
            if (obj.select == True)*context.scene.OW_only_selected or not context.scene.OW_only_selected:
                if not hasattr(obj.data,'name'): # for empty, camera, lamp
                    continue
                if not obj.data.name in self.l_mesh: # test mesh insteed of object -> in case of instancing, avoid duplicate 
                    self.l_mesh.append(obj.data.name)
                else:
                    continue

                if not len(obj.material_slots) and hasattr(obj.data,'materials'):
                    new_mat = bpy.data.materials.new('Default')
                    obj.data.materials.append(new_mat)
                elif len(obj.material_slots):
                    if context.scene.OW_exclude_type == 'index':
                        if not obj.material_slots[0].material.pass_index == context.scene.OW_pass_index:
                            self._save_mat(obj)
                            self._change_mat(context,obj)
                            obj.material_slots[0].material = bpy.data.materials[context.scene.OW_material]
                        else:
                            if context.scene.OW_vis_hide_camera:
                                self.l_hidden.append( (obj,obj.cycles_visibility.camera) )
                                obj.cycles_visibility.camera = False

                    elif context.scene.OW_exclude_type == 'group' and context.scene.OW_group:
                        if obj.name in [g_obj.name for g_obj in bpy.data.groups[context.scene.OW_group].objects]:
                            self._save_mat(obj)
                            self._change_mat(context, obj)
                            obj.material_slots[0].material = bpy.data.materials[context.scene.OW_material]
                        else:
                            if context.scene.OW_vis_hide_camera:
                                self.l_hidden.append( (obj,obj.cycles_visibility.camera) )
                                obj.cycles_visibility.camera = False

                    elif context.scene.OW_exclude_type == 'layer':
                        if not (True in [(context.scene.override_layer[index])*(context.scene.override_layer[index]==obj.layers[index]) for index in range(len(obj.layers))]):
                            self._save_mat(obj)
                            self._change_mat(context, obj)
                            obj.material_slots[0].material = bpy.data.materials[context.scene.OW_material]
                        else:
                            if context.scene.OW_vis_hide_camera:
                                self.l_hidden.append( (obj,obj.cycles_visibility.camera) )
                                obj.cycles_visibility.camera = False
                    elif context.scene.OW_exclude_type == 'emit':
                        if not self._check_if_emit(context, obj):
                            self._save_mat(obj)
                            self._change_mat(context, obj)
                            obj.material_slots[0].material = bpy.data.materials[context.scene.OW_material]
                        else:
                            if context.scene.OW_vis_hide_camera:
                                self.l_hidden.append( (obj,obj.cycles_visibility.camera) )
                                obj.cycles_visibility.camera = False

        
        context.scene.OW_display_override = True
        bpy.ops.view3d.display_override()
        return {'FINISHED'}

    def _save_mat(self, obj):
        self.l_mat.append( (obj,[]) )
        for slot in obj.material_slots:
            self.l_mat[-1][1].append( (slot,slot.material) )

    def _change_mat(self, context, obj):
        for slot in obj.material_slots:
            slot.material = bpy.data.materials[context.scene.OW_material]

    def _check_if_emit(self, context, obj):
        for slot in obj.material_slots:
            if not hasattr(slot.material,'node_tree.nodes'):
                continue
            for node in slot.material.node_tree.nodes:
                if node.type == 'EMISSION':
                    return True
        return False

class OverrideRestore(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "render.override_restore"
    bl_label = "Override Restore"
    
    def execute(self, context):
        context.scene.OW_display_override = False

        for data in bpy.types.RENDER_OT_override_setup.l_mat:
            obj, mat_data= data
            if bpy.data.objects.find(obj.name) != -1: # to be sure obj exist => avoid crash
                for slot, material in mat_data:
                    slot.material = material
            else:
                self.report({'WARNING'}, 'Failed to restore material for object: ' + obj.name)

        for data in bpy.types.RENDER_OT_override_setup.l_hidden:
            obj,cam_visibility = data
            obj.cycles_visibility.camera = cam_visibility

        bpy.types.RENDER_OT_override_setup.l_mat = list()
        bpy.types.RENDER_OT_override_setup.l_mesh = list()
        bpy.types.RENDER_OT_override_setup.l_hidden = list()
        return {'FINISHED'}

############
# Handlers

@persistent
def stop_on_save(dummy):
    if bpy.types.RENDER_OT_override_setup.l_mat:
        bpy.ops.render.override_restore()

@persistent
def mat_override_pre_render(dummy):
    if not bpy.types.RENDER_OT_override_setup.l_mat:
        if bpy.context.scene.OW_start_on_render and bpy.ops.render.override_setup.poll():
            bpy.ops.render.override_setup()
@persistent
def mat_override_post_render(dummy):
    if bpy.context.scene.OW_start_on_render:
        bpy.ops.render.override_restore()

@persistent
def mat_override_stop_on_load(dummy):
    if hasattr(bpy.types, 'RENDER_OT_override_setup'): # as it is persistent, need to be sure the add-on is active
        if bpy.types.RENDER_OT_override_setup.l_mesh: 
            bpy.ops.render.override_restore()     

##############

def register():
    bpy.utils.register_class(OverrideSetup)
    bpy.utils.register_class(OverrideRestore)
    bpy.utils.register_class(AdvancedMaterialOverride)
    bpy.utils.register_class(OverrideDraw)    
    bpy.app.handlers.save_pre.append(stop_on_save)
    bpy.app.handlers.render_init.append(mat_override_pre_render)
    bpy.app.handlers.render_post.append(mat_override_post_render)
    bpy.app.handlers.load_pre.append(mat_override_stop_on_load)

def unregister():
    if bpy.types.RENDER_OT_override_setup.l_mat:
            bpy.ops.render.override_restore() # To make sure materials will be restored
    bpy.utils.unregister_class(OverrideSetup)
    bpy.utils.unregister_class(OverrideRestore)
    bpy.utils.unregister_class(AdvancedMaterialOverride)
    bpy.utils.unregister_class(OverrideDraw)
    bpy.app.handlers.save_pre.remove(stop_on_save)
    bpy.app.handlers.render_init.remove(mat_override_pre_render)
    bpy.app.handlers.render_post.remove(mat_override_post_render)
    bpy.app.handlers.load_pre.remove(mat_override_stop_on_load)


if __name__ == "__main__":
    register()
