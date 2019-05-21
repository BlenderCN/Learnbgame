import bpy
from .. functions import bone_list,find_mirror

class PropertiesPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Properties"

    @classmethod
    def poll(self, context):
        return (context.object and context.object.type =='ARMATURE'
                    and context.object.mode == 'POSE' and context.object.data.SnappingChain)

    def is_selected(self,names):
        # Returns whether any of the named bones are selected.
        if type(names) == list:
            for name in names:
                if name in [b.name for b in bpy.context.selected_pose_bones]:
                    return True
        elif names in [b.name for b in bpy.context.selected_pose_bones]:
            return True
        return False

    def is_active(self,names):
        # Returns whether any of the named bones are selected.
        if bpy.context.active_pose_bone :
            if type(names) == list:
                active_bone_name = bpy.context.active_pose_bone
                for name in names:
                    if name == bpy.context.active_pose_bone.name:
                        return True
            elif names == bpy.context.active_pose_bone.name:
                return True

        return False

    def draw(self,context) :
        layout = self.layout

        ob = context.object
        armature = ob.data
        SnappingChain = armature.SnappingChain

        self.bl_label = ob.name.split('_')[0].title()+' Properties'

        selected_bones = []

        if context.selected_pose_bones :
            selected_bones = sorted([bone.name for bone in context.selected_pose_bones])


        for i,chain in enumerate(SnappingChain.IKFK_bones.values()) :
            if chain.IK_last and self.is_active(bone_list(chain)):
                invert = int(not chain.invert_switch)
                ik_last = ob.pose.bones.get(chain.IK_last)

                col = layout.column(align=True)
                if ob.path_resolve(chain.switch_prop) == invert :
                    row = col.row(align=True)
                    snapFK = row.operator("snappingchain.snapping",text = 'To FK',icon='COLOR_BLUE')
                    snapFK.chain = repr(chain)
                    snapFK.way = 'to_FK'
                    snapFK.auto_switch = True

                else :
                    row = col.row(align=True)
                    snapIK = row.operator("snappingchain.snapping",text = 'To IK',icon='COLOR_RED')
                    snapIK.chain = repr(chain)
                    snapIK.way = 'to_IK'
                    snapIK.auto_switch = True

                keyframing_chain= row.operator('snappingchain.keyframing_chain',text='',icon ='KEY_HLT' )
                keyframing_chain.chain = repr(chain)
                row.prop(context.scene.SnappingChainPrefs,'IK_option',icon='SCRIPTWIN',text='')

                if context.scene.SnappingChainPrefs.IK_option :
                    box = col.box()
                    box_col = box.column()

                    snapIK = box_col.operator("snappingchain.snapping",text = 'Snap IK --> FK')
                    snapIK.chain = repr(chain)
                    snapIK.way = 'to_IK'
                    snapIK.auto_switch = False

                    snapFK = box_col.operator("snappingchain.snapping",text = 'Snap FK --> IK')
                    snapFK.chain = repr(chain)
                    snapFK.way = 'to_FK'
                    snapFK.auto_switch = False

                    resetIK = box_col.operator("snappingchain.reset_ik",text = 'Reset IK')
                    resetIK.chain = repr(chain)

                    lock_row = box_col.row()
                    lock_row.prop(ik_last,'lock_ik_y',text = 'Y')
                    lock_row.prop(ik_last,'lock_ik_z',text = 'Z')
                    #.box_col.prop(chain,'layer_switch',text = 'FK_IK_layer')


            if chain.get('pin_elbow') and chain.get('target_elbow') :
                if self.is_selected([chain.pin_elbow,chain.IK_tip]):
                    snap_elbow = layout.operator("snappingchain.elbow_snapping",text = 'Snap Elbow',icon='COLOR_RED')
                    snap_elbow.chain = repr(chain)



        for i,bone_prop in enumerate(SnappingChain.space_switch_Bones.values()) :
            bone = ob.pose.bones.get(bone_prop.name)


            if bone and bone.children and self.is_active([b.name for b in bone.children]):
                snapFK = layout.prop(bone_prop,'space')

        #display custom prop :
        for bone in selected_bones :
            bone = ob.pose.bones.get(bone)
            if bone.keys() :
                col = layout.column(align =True)
                for key in bone.keys() :
                    if not key.startswith('_') :
                        if bone.name.endswith(('.R','.L')) :
                            side = bone.name.split('.')[-1]
                            text = key.replace('_',' ').title()+' (%s) '%side
                            col.prop(bone,'["%s"]'%key,text = text)



class SnappingChainPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_label = "Snapping Chain"

    @classmethod
    def poll(self, context):
        return (context.object and context.object.type =='ARMATURE')

    def bone_field(self,layout,ob,chain,prop,text=None)  :
        subrow = layout.row(align=True)
        if text :
            subrow.prop_search(chain,prop,ob.pose,'bones',text=text)
        else :
            subrow.prop_search(chain,prop,ob.pose,'bones')
        eyedrop = subrow.operator("snappingchain.bone_eyedropper",text='',icon = 'EYEDROPPER')
        eyedrop.field = repr(chain)
        eyedrop.prop = prop

    def draw(self,context) :
        layout = self.layout

        ob = context.object
        armature = ob.data
        SnappingChain = armature.SnappingChain

        main_column = layout.column(align=True)

        tab = main_column.row(align=True)
        tab.prop(SnappingChain,'snap_type',expand=True)


        if SnappingChain.snap_type == 'IKFK' :
            tools_row = main_column.row(align=True)
            addChain = tools_row.operator("snappingchain.add_remove_field",text='Add FK IK Chain',icon = 'GROUP_BONE')
            addChain.values=str({'set':{'expand':True},'add':True,'prop':repr(SnappingChain.IKFK_bones)})
            tools_row.operator("snappingchain.copy_layers",text='',icon = 'COPYDOWN')
            tools_row.operator("snappingchain.paste_layers",text='',icon = 'PASTEDOWN')

            #addChain.prop = repr(SnappingChain.IKFK_bones)
            #addChain.add= True


            for i,chain in enumerate(SnappingChain.IKFK_bones.values()) :
                box = main_column.box()
                row = box.row(align=False)

                row.prop(chain,'expand',text='',icon = 'TRIA_DOWN' if chain.expand else 'TRIA_RIGHT',emboss=False)
                row.prop(chain,'name',text='')

                mirror_chain = row.operator("snappingchain.mirror_chain",icon ='MOD_MIRROR',text='')
                mirror_chain.index =i

                subrow = row.row(align=True)
                remove_bone = subrow.operator("snappingchain.add_remove_field",icon='ZOOMOUT',text='')
                remove_bone.values = str({'add':False,'prop':repr(chain.FK_mid),'index':len(chain.FK_mid)-1})

                add_bone = subrow.operator("snappingchain.add_remove_field",icon='ZOOMIN',text='')
                add_bone.values = str({'add':True,'prop':repr(chain.FK_mid)})

                removeChain = row.operator("snappingchain.add_remove_field",text='',icon = 'X',emboss = False)
                removeChain.values = str({'add':False,'prop':repr(SnappingChain.IKFK_bones),'index':i})


                if chain.expand :

                    #row = box.row(align=True)
                    col = box.column()
                    self.bone_field(col,ob,chain,'FK_root')

                    for i,bone in enumerate(chain.FK_mid) :
                        self.bone_field(col,ob,bone,'name',text='FK_mid_%02d'%(i+1))

                    self.bone_field(col,ob,chain,'FK_tip')

                    col.separator()
                    self.bone_field(col,ob,chain,'IK_last')

                    '''
                    for bone in chain.IK_mid :
                        self.bone_field(col,ob,bone,'name')
                        '''

                    for prop in ['IK_tip','IK_pole'] :
                        self.bone_field(col,ob,chain,prop)

                    col.separator()

                    subrow = col.row(align= True)
                    subrow.prop(chain,'FK_layer', text = 'FK_layer')
                    subrow.prop(chain,'IK_layer',text = 'IK_layer')

                    col.separator()
                    subrow = col.row()

                    subrow.prop(chain,'switch_prop')
                    subrow.prop(chain,'invert_switch',text='')



                    col.separator()

                    box = col.box()
                    box_col = box.column()
                    subrow = box_col.row(align=True)
                    subrow.prop(chain,"extra_settings",text='',icon = 'TRIA_DOWN' if chain.extra_settings else 'TRIA_RIGHT',emboss = False)
                    subrow.label('Extra settings')


                    if chain.extra_settings :

                        subrow = box_col.row(align=True)
                        subrow.prop_search(chain,'IK_stretch_last',ob.pose,'bones')
                        eyedrop=subrow.operator("snappingchain.bone_eyedropper",text='',icon = 'EYEDROPPER')
                        eyedrop.field = repr(chain)
                        eyedrop.prop = 'IK_stretch_last'

                        subrow = box_col.row(align=True)
                        subrow.prop_search(chain,'pin_elbow',ob.pose,'bones')
                        eyedrop=subrow.operator("snappingchain.bone_eyedropper",text='',icon = 'EYEDROPPER')
                        eyedrop.field = repr(chain)
                        eyedrop.prop = 'pin_elbow'

                        subrow = box_col.row(align=True)
                        subrow.prop_search(chain,'target_elbow',ob.pose,'bones')
                        eyedrop=subrow.operator("snappingchain.bone_eyedropper",text='',icon = 'EYEDROPPER')
                        eyedrop.field = repr(chain)
                        eyedrop.prop = 'target_elbow'

                        #subrow = box_col.row(align=True)
                        box_col.prop(chain,'full_snapping')




                main_column.separator()

        if SnappingChain.snap_type == 'SPACE_SWITCH' :
            add_bone = main_column.operator("snappingchain.add_remove_field",text='Add space switch bones')
            add_bone.values = str({'add':True,'prop':repr(SnappingChain.space_switch_Bones)})
            #add_bones.prop = repr(SnappingChain.space_switch_Bones)
            #add_bones.add = True
            box = main_column.box()
            col = box.column()
            for j,bone in enumerate (SnappingChain.space_switch_Bones) :
                row = col.row(align=True)
                row.prop_search(bone,'name',ob.pose,'bones',text= '')
                eyedrop=row.operator("snappingchain.bone_eyedropper",text='',icon = 'EYEDROPPER')
                eyedrop.field = repr(bone)
                eyedrop.prop = 'name'
                #eyedrop.bone = j

                remove_bone = row.operator("snappingchain.add_remove_field",text='',icon ='X')
                remove_bone.values = str({'index':j,'add':False,'prop':repr(SnappingChain.space_switch_Bones)})
                #remove_bone.prop = repr(SnappingChain.space_switch_Bones)
                #remove_bone.index = j
                #remove_bone.add = False
