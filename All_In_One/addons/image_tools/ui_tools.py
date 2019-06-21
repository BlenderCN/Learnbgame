# common ui features

## drawExpand(layout, 'section title', 'path to any boolean expand prop')
# a generic expand : returns True if visible
# from a draw() section, you can :
'''
if drawExpand(layout,'Sub section title','scene.myclass.expand_otl') :
    box = layout.box()
    row = box.row()
    row.label( 
    [...]
'''
from bpy import context
# 2.6
try :
    from bpy.types import Operator
    from bpy.props import StringProperty
except :
    import bpy
    Operator = bpy.types.Operator
    StringProperty = bpy.props.StringProperty

def seekAreas(area_name='IMAGE_EDITOR',verbose=False):
    screen = bpy.context.window.screen
    for id, area in enumerate(screen.areas) :
        dprint('    %s : %s'%(id,area.type),5)
        if area.type == area_name :
            return area
    return False

def drawExpand(layout,section_name,section_tag,box=False) :
        expand = eval('context.%s'%section_tag)
        if box :
            box = layout.box()
            row = box.row()
        else :
            box = True
            row = layout.row()
        row.alignment = 'LEFT'
        row.operator("wm.panel_expand", text=section_name, icon='TRIA_DOWN' if expand else 'TRIA_RIGHT', emboss=False).panel = section_tag
        return box if expand else False

class WM_OT_Panel_expand(Operator):
    ''''''
    bl_idname = "wm.panel_expand"
    bl_label = ""

    panel = StringProperty(name="toggle_panel", description="name of the panel to show/hide")

    def execute(self, context):
        exec('context.%s = not context.%s'%(self.panel,self.panel))
        return {'FINISHED'}