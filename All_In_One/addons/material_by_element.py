''' revision: 2-5-12
    
    MaterialByElement:
    this addon is designed to suppy some tool for materials management
    and use
    - separate geometry
    - delete material from scene
    - delete list
    - create list
    - select list members
    - remove unused materials
    - assign list randomly
    - select objects with no material
    
    Pietro Grandi - www.pietrograndi.eu 
    skype: pietro.grandi
    mobile: 0039 3889219633 (phone/viber/whatsapp) 
    mail: pietro.grandi.3d@gmail.com

    Found on http://pietro3d.blogspot.co.uk/2012/04/material-by-element-09.html
    License: GPLv2 ("The script is released under GPL 2.0, feel free to reuse/modify/cook/freeze/blend... but please let me know :-) I'm curious.")
'''

bl_info = {
    'name': 'Material by Element',
    'author': 'Pietro Grandi',
    'version': (0, 9, 0 ),
    'blender': (2, 6, 3),
    "location": "View3D > UI panel > Material by Element",
    'description': 'Tools for material editing and use.',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    "category": "Learnbgame",
}

import bpy
import random
import re
    
    
#   Layout panel
class MaterialByElement(bpy.types.Panel):
    bl_label = "Material by Element "
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"
    
    #sourcemat=bpy.context.active_object.active_material #takes active material
    #mbe_KAOS=bpy.props.FloatProperty(name="Some Floating Point")
    #sourcemat['mbe_KAOS']=20        #kaos number
    #sourcemat['mbe_NMATS']=6        #n° of material
    bpy.context.scene['mbe_KAOS']=20        #kaos number
    bpy.context.scene['mbe_NMATS']=6        #n° of material
            
    def draw(self, context):
        scn=bpy.context.scene
        layout = self.layout        
        
        #separate geometry button
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("mbel.separate", text="Separate geometry", icon='MOD_EXPLODE')
        
        #show the current target material and let you chose it
        row=layout.row()
        row.label(text="Target material:", icon='NODE')
        row=layout.row()
        row.prop(bpy.context.active_object, "active_material", icon='MATERIAL')
        #erase materials buttons
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("mbel.delmat", text="Del MBE bro")      
        row.operator("mbel.delmatone", text="Delete single")   
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("mbel.selectorphans", text="Select orphans")      
        row.operator("mbel.purge", text="Remove unused")   
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("mbel.selmatted", text="Select MBE objects")      
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("mbel.fillslot", text="Fill slots")
        row.operator("mbel.clearslot", text="Clear slots")
        row = layout.row()
        box = row.box()
        box.operator("mbel.creatematlist", text="Create Material's List", icon='NEW')        
        #box.prop('mbe_KAOS')
        box.prop(bpy.context.scene, '["mbe_KAOS"]')
        box.prop(bpy.context.scene, '["mbe_NMATS"]')
        row = layout.row()
        row.operator("mbel.assignmat", text="Assign to selected!", icon='PASTEFLIPUP')
        row = layout.row()
        row = layout.row()
        row.operator("mbel.assignsubs", text="Assign to polygons", icon='PASTEFLIPUP')
        row = layout.row()
        row.label("2012 (C) Pietro Grandi")
        


'''********************************************************************
    mbelGetMbeList(basename='nome')
    returns material's list corresponding to 'nome'
     
'''
def mbelGetMbeList(basename='nome') :
    matter=[]   #material's list
        #compiling material's list:
    for m in bpy.data.materials :
        #regex:
        #'.mbe-' is the marker, after it we'll chek for one to three integer and the EOS
        a=re.search(r'.mbe-\d?\d?\d?$',m.name)
        if a :      #if it's MBE material
            if m.name[0:a.start()] == basename :    #checking basename
                matter.append(m)                    #append it to the list
        #mbelist=['pietra.mbe-0','pietra.mbe-1','pietra.mbe-2','pietra.mbe-3','pietra.mbe-4']    
    return(matter)


        
'''********************************************************************
    mbelFillSlot
     
'''
class OBJECT_OT_mbelFillSlot(bpy.types.Operator):
    bl_idname = "mbel.fillslot"
    bl_label = "Fill material slots with current list's material"
    
    def execute(self, context):
        
        #checking wether active object is a mesh
        if bpy.context.active_object.type != 'MESH' :
            self.report({'ERROR'}, "Works with MESH only")
            return{'CANCELLED'}
        
        sourcemat=bpy.context.active_object.active_material 
        mats=bpy.data.materials
        b=re.search('.mbe-',sourcemat.name) #checking for marker
        
        try:
            basename=sourcemat.name[0:b.start()]    #basename
        except:         #not MBE material? mmmm
            self.report({'ERROR'}, "MBE material not found")
            return{'CANCELLED'}
               
        obj=bpy.context.active_object
        mbelist=mbelGetMbeList(basename)
        N=len(mbelist)
        for i in range(1,N) :
            bpy.ops.object.material_slot_add()
            obj.material_slots[i].material=mbelist[i]
        
        return{'FINISHED'}
    
    
'''********************************************************************
    mbelClearSlot
     
'''
class OBJECT_OT_mbelClearSlot(bpy.types.Operator):
    bl_idname = "mbel.clearslot"
    bl_label = "Clear material slots"
    
    def execute(self, context):
        
        #checking wether active object is a mesh
        if bpy.context.active_object.type != 'MESH' :
            self.report({'ERROR'}, "Works with MESH only")
            return{'CANCELLED'}
        
        obj=bpy.context.active_object
        for i in range(1,len(obj.material_slots)) :
            bpy.ops.object.material_slot_remove()
        
        return{'FINISHED'}
    
    

'''********************************************************************
    mbelAssignSubs
    assign material ID to polygons (subobject)
'''
class OBJECT_OT_mbelAssignSubs(bpy.types.Operator):
    bl_idname = "mbel.assignsubs"
    bl_label = "Assign random material ID to polygons"
    
    def execute(self, context):

        #checking wether active object is a mesh
        if bpy.context.active_object.type != 'MESH' :
            self.report({'ERROR'}, "Works with MESH only")
            return{'CANCELLED'}
 
        mesh=bpy.context.active_object.data
        N=5
        
        for p in mesh.polygons :
            p.material_index=random.randint(0,N)
            print("polygon "+str(p.index)+" has now "+str(p.material_index))
        
        self.report({'INFO'}, str(N)+" materials assigned to "+str(p.index)+" polygons")
        return{'FINISHED'}           
        
        
        

'''********************************************************************
    mbelCreateMatList
     -  takes active material, check wether it's MBE material,
        find out basename
     -  compile material's list
     -  apply it randomly to all meshes selected
'''
class OBJECT_OT_mbelCreateMatList(bpy.types.Operator):
    bl_idname = "mbel.creatematlist"
    bl_label = "Create Material's List"
    
    def execute(self, context):
        
        #checking wether active object is a mesh
        if bpy.context.active_object.type != 'MESH' :
            self.report({'ERROR'}, "Works with MESH only")
            return{'CANCELLED'}
        
        marker=".mbe-"
        sourcemat=bpy.context.active_object.active_material 
        mats=bpy.data.materials
        basename=sourcemat.name
   
        try:
            N=bpy.context.scene['mbe_NMATS']    #n. of material you want to be created
            K=bpy.context.scene['mbe_KAOS']   #KAOS - N*5 gives more contrast - N*20 is regular 
        except:         #no custom parameters? 
            self.report({'WARNING'}, "No custom parameters found, switching to default")
            N=6
            K=20
            return{'CANCELLED'}                      
        
        r=sourcemat.diffuse_color[0]
        g=sourcemat.diffuse_color[1]
        b=sourcemat.diffuse_color[2]
        
        #creates new material set
        for i in range(1,N): 
            k=sourcemat.copy()          #make original material's copy
            materialname=basename+marker+str(i)
            k.name=materialname
        	#this is to have more difference between objects, changing diffuse value
            if i%2==0:
                k.diffuse_color=(
                    r+(random.randint(0,K)/1000),
                    g+(random.randint(0,K)/1000),
                    b+(random.randint(0,K)/1000)
                    )
            else:
                k.diffuse_color=(
                    r-(random.randint(0,K)/1000),
                    g-(random.randint(0,K)/1000),
                    b-(random.randint(0,K)/1000)
                    )
        
        sourcemat.name = basename+marker+'0'  
        self.report({'INFO'}, basename+" material list created")
        return{'FINISHED'}
            
        
'''********************************************************************
    mbelAssignMat
     -  takes active material, check wether it's MBE material,
        find out basename
     -  compile material's list
     -  apply it randomly to all meshes selected
'''
class OBJECT_OT_mbelAssignMat(bpy.types.Operator):
    bl_idname = "mbel.assignmat"
    bl_label = "Assign Materials"
    
    def execute(self, context):
        
        #checking wether active object is a mesh
        if bpy.context.active_object.type != 'MESH' :
            self.report({'ERROR'}, "Works with MESH only")
            return{'CANCELLED'}
        
        sourcemat=bpy.context.active_object.active_material 
        mats=bpy.data.materials
        b=re.search('.mbe-',sourcemat.name) #checking for marker
        
        try:
            basename=sourcemat.name[0:b.start()]    #basename
        except:         #not MBE material? mmmm
            self.report({'ERROR'}, "MBE material not found")
            return{'CANCELLED'}
                    
        matter=[]   #material's list
        
        #compiling material's list:
        for m in mats :
            #regex:
            #'.mbe-' is the marker, after it we'll chek for one to three integer and the EOS
            a=re.search(r'.mbe-\d?\d?\d?$',m.name)
            if a :      #if it's MBE material
                if m.name[0:a.start()] == basename :    #checking basename
                    matter.append(m)                    #append it to the list
                    
        N=len(matter)    #n. of material
        
        i=0 #counter
        #assign materials to objects...
        for obj in context.selected_objects:                       #for every object in selection
            if obj.type=='MESH' :                                  #if it's a mesh
                i+=0
                bpy.context.scene.objects.active = obj             #makes it active
                for mat in obj.material_slots:
                    bpy.ops.object.material_slot_remove()             #remove all materials
                bpy.ops.object.material_slot_add()                    #add ONE material
                obj.data.materials[0]=matter[random.randint(0,N-1)]   #assign one of the N material
        
        self.report({'INFO'}, basename+" material applyied to "+str(N)+" objects")
        
        return{'FINISHED'}



'''********************************************************************
    SelMatted()
    select all objects with the same MBE list
'''
class OBJECT_OT_mbelSelMatted(bpy.types.Operator):
    bl_idname = "mbel.selmatted"
    bl_label = "Select objects with the same MBE list"
    
    def execute(self, context):
        
        #checking wether active object is a mesh
        if bpy.context.active_object.type != 'MESH' :
            self.report({'ERROR'}, "Works with MESH only")
            return{'CANCELLED'}
        
        sourcemat=bpy.context.active_object.active_material 
        mats=bpy.data.materials
        b=re.search('.mbe-',sourcemat.name) #looking for marker
        matter=[]
        
        #name of sourcemat is changed to avoid deleting
        if b :  #if it's a MBE material
            basename=sourcemat.name[0:b.start()]        #get the basename
        else :  #if it's not
            self.report({'ERROR'}, "MBE material not found")
            return{'CANCELLED'}
                    
        i=0 #counter
        for m in mats :
            #regex:
            #'.mbe-' is the marker, after it we'll chek for one to three integer and the EOS
            a=re.search(r'.mbe-\d?\d?\d?$',m.name)
            if a :  #if is an MBE material
                if m.name[0:a.start()] == basename :    #check basename
                    matter.append(m)
                    
        for obj in bpy.context.scene.objects :
            if obj.type == 'MESH' :
                if re.search(basename+'.mbe-', obj.material_slots[0].name) :
                    obj.select=True
                    i+=1
        
        self.report({'INFO'}, str(i)+" object selected")
        return{'FINISHED'}


'''********************************************************************
    mbelPurge
    remove all materials without users
'''
class OBJECT_OT_mbelPurge(bpy.types.Operator):
    bl_idname = "mbel.purge"
    bl_label = "Delete unused materials"
    
    def execute(self, context):
        mats=bpy.data.materials        
        for m in mats :
            if m.users == 0 :   #if no user found
                bpy.data.materials.remove(m)   #remove mat
        return{'FINISHED'}                

'''********************************************************************
    mbelSelectOrphans
    select all objects (meshes) without material applyed
'''
class OBJECT_OT_mbelSelectOrphans(bpy.types.Operator):
    bl_idname = "mbel.selectorphans"
    bl_label = "Select objects with no material"
    
    def execute(self, context):
        
        i=0 #counter
        for obj in bpy.data.objects :
            if (obj.type=='MESH') and (len(obj.material_slots)==0) :
                obj.select=True
                i+=1

        self.report({'INFO'}, str(i)+" objects selected")
        return{'FINISHED'}



'''********************************************************************
    mbelDelMatOne
    unlink current material and remove it completely from scene
'''
class OBJECT_OT_mbelDelMatOne(bpy.types.Operator):
    bl_idname = "mbel.delmatone"
    bl_label = "Delete Material"
    
    def execute(self, context):
        
        #checking wether active object is a mesh
        if bpy.context.active_object.type != 'MESH' :
            self.report({'ERROR'}, "Works with MESH only")
            return{'CANCELLED'}
        
        sourcemat=bpy.context.active_object.active_material 
        sourcemat.user_clear()                 #unlink
        bpy.data.materials.remove(sourcemat)   #remove "matter" from materials slot"""

        self.report({'INFO'}, sourcemat.name+" removed")
        return{'FINISHED'}



'''********************************************************************
    mbelDelMat()
    unlink all MBE materials with setted basename and deletes them
'''
class OBJECT_OT_mbelDelMat(bpy.types.Operator):
    bl_idname = "mbel.delmat"
    bl_label = "Delete Materials"
    
    def execute(self, context):
        
        #checking wether active object is a mesh
        if bpy.context.active_object.type != 'MESH' :
            self.report({'ERROR'}, "Works with MESH only")
            return{'CANCELLED'}
        
        sourcemat=bpy.context.active_object.active_material 
        mats=bpy.data.materials
        b=re.search('.mbe-',sourcemat.name) #looking for marker
        
        #name of sourcemat is changed to avoid deleting
        if b :  #if it's a MBE material
            basename=sourcemat.name[0:b.start()]        #get the basename
            sourcemat.name=sourcemat.name[0:b.start()]  #and reset marker+counter
        else :  #if it's not
            basename=sourcemat.name                 #basename 
            sourcemat.name=sourcemat.name+"-000"    #change name
            
        i=0 #counter
        
        for m in mats :
            #regex:
            #'.mbe-' is the marker, after it we'll chek for one to three integer and the EOS
            a=re.search(r'.mbe-\d?\d?\d?$',m.name)
            if a :  #if is an MBE material
                if m.name[0:a.start()] == basename :    #check basename
                    i+=1                           #counter +1
                    m.user_clear()                 #unlink
                    bpy.data.materials.remove(m)   #remove "matter" from materials slot"""
        
        self.report({'INFO'}, str(i)+" materials removed")
        return{'FINISHED'}



''' **************************************************************
    mbelSeparate()
    separates active object into more objects, checking wether
    you are into editmode or not and if active object is a mesh.
'''
class OBJECT_OT_mbelSeparate(bpy.types.Operator):
    bl_idname = "mbel.separate"
    bl_label = "Separate"

    def execute(self, context):
        
        #checking wether active object is a mesh
        if bpy.context.active_object.type != 'MESH' :
            self.report({'ERROR'}, "Works with MESH only")
            return{'CANCELLED'}
        
        if bpy.context.mode != 'EDIT':            #if not in edit mode
            bpy.ops.object.editmode_toggle()      #enters in edit mode
            bpy.ops.mesh.separate(type='LOOSE')   #separate it by loose parts
            bpy.ops.object.editmode_toggle()      #exit edit mode
        else :                                    #else
            bpy.ops.mesh.separate(type='LOOSE')   #separate it by loose parts
        
        self.report({'INFO'}, "Mesh separated")
        return{'FINISHED'}

    
#    Registration

def register():
    bpy.utils.register_module(__name__)
 
def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register()
