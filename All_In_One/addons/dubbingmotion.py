####################################
# Dubbing Motion
#       v.1.0
#  (c)Ishidourou 2013
####################################

#!BPY

bl_info = {
    "name": "Dubbing Motion",
    "author": "ishidourou",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "View3D > Toolbar",
    "description": "Dubbing Motion",
    "warning": "",
    "wiki_url": "http://stonefield.cocolog-nifty.com/higurashi/2013/11/blenderaddondub.html",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
import random
from bpy.props import *

#    Menu in tools region
class DubbingMotionPanel(bpy.types.Panel):
    bl_label = "Dubbing Motion"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        self.layout.operator("dubbing.motion")

def keyframe_IPtype(type):
    bpy.context.area.type = 'GRAPH_EDITOR'
    bpy.ops.graph.interpolation_type(type='LINEAR')
    bpy.context.area.type = 'VIEW_3D'

#------default value------
rectype = 'LocRotScale'
allframe = True
fs = 1
fe = 100
fstep = 10
foffset = 0
order = False
revorder = False
locofs = True
#---------------------

def objselect(objct,selection):
    if (selection == 'ONLY'):
        bpy.ops.object.select_all(action='DESELECT')
#    if (selection != 'POSE'):
#        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = objct
    objct.select = True

def hide(obj,mode):
    bpy.context.area.type = 'VIEW_3D'
    if mode == True:
        objselect(obj,'ONLY')
        bpy.ops.object.hide_view_set(unselected=False)
    else:
        bpy.ops.object.hide_view_clear()
    bpy.context.area.type = 'VIEW_3D'

def set_offset(dobj, sobj, foffset):
    foffset /= 2
    hide(sobj,True)
    objselect(dobj,'ONLY')
    bpy.context.area.type = 'GRAPH_EDITOR'
    bpy.ops.graph.select_all_toggle(invert=False)
    bpy.ops.transform.translate(value=(foffset, 0, 0))
    bpy.ops.graph.select_all_toggle(invert=False)
    bpy.ops.transform.translate(value=(foffset, 0, 0))
    bpy.context.area.type = 'VIEW_3D'
    hide(sobj,False)

def set_euler(sobj, dobj, rtype):
    if rtype != 'Rotation' and rtype != 'BUILTIN_KSI_LocRot' and rtype != 'BUILTIN_KSI_RotScale' and rtype != 'LocRotScale':
        return
    objselect(dobj,'ONLY')
    for i in range(3):
        dobj.rotation_euler[i] = sobj.rotation_euler[i]
    bpy.ops.anim.keyframe_insert_menu(type=rtype)
    keyframe_IPtype('LINEAR')

def set_location(sobj, dobj, offset, rtype):
    if rtype != 'Location' and rtype != 'BUILTIN_KSI_LocRot' and rtype != 'BUILTIN_KSI_LocScale' and rtype != 'LocRotScale':
        return
    for i in range(3):
        dobj.location[i] = sobj.location[i] + offset[i]
    objselect(dobj,'ONLY')
    bpy.ops.anim.keyframe_insert_menu(type=rtype)
    keyframe_IPtype('LINEAR')

def set_scale(sobj, dobj, rtype):
    if rtype != 'Scaling' and rtype != 'BUILTIN_KSI_RotScale' and rtype != 'BUILTIN_KSI_LocScale' and rtype != 'LocRotScale':
        return
    for i in range(3):
        dobj.scale[i] = sobj.scale[i]
    objselect(dobj,'ONLY')
    bpy.ops.anim.keyframe_insert_menu(type=rtype)
    keyframe_IPtype('LINEAR')


def keyclear(sobj,dobj,fs,fe,ktype,allframe):
    if allframe == True:
        hide(sobj,True)
        bpy.context.scene.objects.active = dobj
        dobj.select = True
        bpy.context.area.type = 'GRAPH_EDITOR'
        #bpy.ops.graph.keyframe_insert(type='SEL')
        bpy.ops.anim.keyframe_insert_menu(type=ktype)
        bpy.ops.graph.delete()
        bpy.context.area.type = 'VIEW_3D'
        hide(sobj,False)
        return
    hide(sobj,True)
    bpy.context.scene.objects.active = dobj
    dobj.select = True
    for frm in range(fs,fe+1,1):
        bpy.context.scene.frame_set(frm)
        bpy.ops.anim.keyframe_delete_v3d()
    hide(sobj,False)

#---- main ------
class DubbingMotion(bpy.types.Operator):

    bl_idname = "dubbing.motion"
    bl_label = "Dubbing Motion"
    bl_options = {'REGISTER'}

    my_rectype = EnumProperty(name="Recording Type:",
        items = [('Location','Location','0'),
                 ('Rotation','Rotation','1'),
                 ('Scaling','Scaling','2'),
                 ('BUILTIN_KSI_LocRot','LocRot','3'),
                 ('BUILTIN_KSI_LocScale','LocScale','4'),
                 ('BUILTIN_KSI_RotScale','RotScale','5'),
                 ('LocRotScale','LocRotScale','6'),
                 ('UseOffset','Use Offset Only','7')],
                 default = rectype)
    my_allfrm = BoolProperty(name="All Frame",default=allframe)
    my_fstart = bpy.props.IntProperty(name="Start Frame:",min=0,default = fs)
    my_fend = bpy.props.IntProperty(name="End Frame:",min=1,default = fe)
    my_fstep = bpy.props.IntProperty(name="Frame Step:",min=1,max=100,default = fstep)
    my_foffset = bpy.props.IntProperty(name="Frame offset:",min=-100,max=100,default = foffset)
    my_frandom = bpy.props.IntProperty(name="Random offset:",min=0,max=1000,default = foffset)
    my_order = BoolProperty(name="Order Offset",default=order)
    my_revorder = BoolProperty(name="Order Reverse",default=revorder)
    my_locofs = BoolProperty(name="Location Offset",default=locofs)

    def execute(self, context):

        allframe = self.my_allfrm
        fstep = self.my_fstep
        foffset = self.my_foffset
        frandom = self.my_frandom
        order = self.my_order
        revorder = self.my_revorder
        rectype = self.my_rectype
        offset = [0,0,0]
        locofs = self.my_locofs

        if allframe == True:
            sn = bpy.context.scene
            fs = sn.frame_start
            fe = sn.frame_end
        else:
            fs = self.my_fstart
            fe = self.my_fend

        slist = bpy.context.selected_objects
        #print(slist)
        if revorder == False:
            slist.reverse()
        #print(slist)

        av = bpy.context.active_object
        objselect(av,'ONLY')
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, animation=True)

        dfoffset = foffset

        for i in slist:
             if i.name != av.name:
                bpy.context.scene.frame_set(fs)

                if rectype != 'UseOffset':
                    if locofs == True:
                        for ii in range(3):
                            offset[ii] = i.location[ii] - av.location[ii]
                    keyclear(av,i,fs,fe,rectype,allframe)

                    for frm in range(fs,fe,fstep):
                        bpy.context.scene.frame_set(frm)
                        set_euler(av,i,rectype)
                        set_location(av, i, offset, rectype)
                        set_scale(av, i, rectype)

                    bpy.context.scene.frame_set(fe)
                    set_euler(av, i, rectype)
                    set_location(av, i, offset, rectype)
                    set_scale(av, i, rectype)

                set_offset(i,av,foffset + int(frandom*random.random()))
                if order == True:
                    foffset += dfoffset

        for i in slist:
            i.select = True
        bpy.context.scene.frame_set(1)
        bpy.context.scene.objects.active = av
        av.select = True

        print('Finished')
        return{'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

#   Registration

def register():
    bpy.utils.register_class(DubbingMotionPanel)
    bpy.utils.register_class(DubbingMotion)

def unregister():
    bpy.utils.unregister_class(DubbingMotionPanel)
    bpy.utils.unregister_class(DubbingMotion)

if __name__ == "__main__":
    register()
