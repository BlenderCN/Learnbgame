import bpy
import os 
#class bgamemanager_fbx(bpy.types.Panel):
#    bl_idname = "bgamemanagernamefbx"
#    bl_label = "Export Select FBX"
#    bl_space_type = "VIEW_3D"
#    bl_region_type = "TOOLS"
#    bl_category = "BGManager"
#    #-----
#    
#    
#    def draw(self, context):
#        layout = self.layout
#        scene=context.scene
#        
#        row=layout.row(align=True)
#        
#        row.scale_x=0.1
#        row.scale_y=1.0
#        row.label("ParName:")
#        rowpn=row.row(align=True)
#        rowpn.scale_x=1.8
#        rowpn.scale_y=1.0
#        rowpn.prop(scene,"fbxcommonname")
#        layout.operator('my_operator.bgmexportfbx',text='Export Select FBX',icon="FILE_BLEND")
        
#-----------------------SP Function --------------------        


class bgamemanager_sp(bpy.types.Panel):
    bl_idname = "bgamemanagernamesp"
    bl_label = "To Substance Painter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "BL2SP"
    #------GET SP PATH---------
    
    
    #-------------------------
    
    def draw(self, context):
        layout= self.layout

        row=layout.row(align=True)
        row.scale_x=1.2
        row.scale_y=1.0
        row.label("SP EXE PATH:")
        row2=row.row(align=True) 
        row2.alignment='RIGHT'
        row2.scale_x=0.35
        row2.scale_y=1.0
        row2.operator('my_operator.bgmopenspexe',text="            ",icon="SCRIPTWIN")
        #------ADD MESH------
        
        scene=context.scene
        rowm=layout.row(align=True)
        rowm.prop(scene,"spmeshudmi")
        rowm.prop(scene,"spmeshseleted")
        
        #------ADD MESH------
        layout.label("Export Substance")
        layout.operator('my_operator.bgmbl2sp', text="To Substance Painter",icon="LINK_BLEND")
        layout.label("Replace MESH")
        layout.operator('my_operator.bgmbl2spchangemesh',text="Replace MESH",icon="LOAD_FACTORY")
        


    
