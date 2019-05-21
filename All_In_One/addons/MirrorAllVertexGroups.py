bl_info = {
		'name': 'Mirror All Vertex Groups',
		'author': 'mathiasA, updated to 2.80 by bay raitt',
		'version': (0, 1),
		'blender': (2, 80, 0),	
		'category': 'Animation',
		'location': 'Mesh > Vertex Group Menu',
		'wiki_url': ''}


import bpy, bmesh
import datetime
from bpy.props import *
from bpy.types import Operator, Panel



def copy_mirror_weight(Axis,Way,Pattern,special_pattern,left_side,right_side,tolerance):
    start = (datetime.datetime.now())
    print('start')
    bpy.ops.object.mode_set(mode='OBJECT')

    
    
    #items = [('4', '_l and _r', '4'),('3', '_L and _R', '3'),('2', '.l and .r', '2'),('1', '.L and .R', '1')])
    L_side=''
    R_side=''
    ori_side=''
    dest_side=''

    if Pattern=='1':
        L_side='.L'
        R_side='.R'     
    if Pattern=='2':
        L_side='.l'
        R_side='.r' 
    if Pattern=='3':
        L_side='_L'
        R_side='_R'
    if Pattern=='4':
        L_side='_l'
        R_side='_r' 

    if special_pattern==True:
        ori_side=left_side
        dest_side=right_side 
    
    obj = bpy.context.active_object
    mesh = bpy.data.objects[obj.name].data.name
    
    x_multiply = 1
    y_multiply = 1
    z_multiply = 1
    
    if Axis == 'X':
        axis_num = 0
        x_multiply = -1
    if Axis == 'Y':
        axis_num = 1
        y_multiply = -1
    if Axis == 'Z':
        axis_num = 2
        z_multiply = -1
    
    
    ## create the dict for the groups attache the index to the name
    DictGroup = {} ##ask the index it will give you the name
    DictGroupINV = {} ## ask the name, it will give you the index
    i=0
    for group in bpy.context.active_object.vertex_groups:
        DictGroup[i]=group.name
        i+=1

    for item in DictGroup:
        DictGroupINV[DictGroup[item]]=item
    
    
    #for each vertices of the mesh
    DictVertexOri = {}
    DictVertexDest = {}
    DictMirror = {}
    L_side_count = 0
    R_side_count = 0
    for vertex in bpy.data.meshes[mesh].vertices:
        #create the dicts for the good side
        #print (vertex.co[axis_num])
        if (vertex.co[axis_num]>tolerance and Way=='normal') or (vertex.co[axis_num]<-tolerance and Way=='reverse'): #compare with the tolerance and position of the origin  
            
            DictVertexOri[vertex.index]=vertex.co
        
        #create the dicts for the mirror side
        if (vertex.co[axis_num]<tolerance and Way=='normal') or (vertex.co[axis_num]>-tolerance and Way=='reverse'):#compare with the tolerance and position of the origin
            #print("MIRROR")
            DictVertexDest[vertex.index]=vertex.co

    for vertex in DictVertexOri:      
        
        for groups in bpy.data.meshes[mesh].vertices[vertex].groups: #when it's the automatic pattern, it checks the most used on the original side .L or .R and assign them after
            
            if obj.vertex_groups[groups.group].name.find(L_side)>-1:
                L_side_count+=1
            if obj.vertex_groups[groups.group].name.find(R_side)>-1:
                R_side_count+=1
                
        if L_side_count>R_side_count and special_pattern==False:
            ori_side=L_side
            dest_side=R_side    
        if R_side_count>L_side_count and special_pattern==False:        
            ori_side=R_side
            dest_side=L_side    
                    
                        
        vertexCoXOri = DictVertexOri[vertex][0]
        vertexCoYOri = DictVertexOri[vertex][1]
        vertexCoZOri = DictVertexOri[vertex][2]
        
        for vertexMirror in DictVertexDest: #check the coordinates of each axis, the multiply is inversing the mirror axes from -x.xxxx to x.xxxx so that the side doesn't matter
            if vertexCoXOri-tolerance<DictVertexDest[vertexMirror][0]*x_multiply<vertexCoXOri+tolerance:
                if vertexCoYOri-tolerance<DictVertexDest[vertexMirror][1]*y_multiply<vertexCoYOri+tolerance:
                    if vertexCoZOri-tolerance<DictVertexDest[vertexMirror][2]*z_multiply<vertexCoZOri+tolerance:
                        DictMirror[vertex]=vertexMirror
                        
        

    for vertex in DictMirror:
        myGroupVertex = {}
        myMirrorGroupVertex = {}
        for groups in bpy.data.meshes[mesh].vertices[vertex].groups:
            myGroupVertex[groups.group] = groups.weight #create a dictionary nameGroup = weight
            
            for OneGroup in myGroupVertex: #create a new dictionnary with the name mirror
                if obj.vertex_groups[OneGroup].name.find(ori_side)>-1:
                    mirror_normal_group_name = obj.vertex_groups[OneGroup].name.replace(ori_side,dest_side)
                    if mirror_normal_group_name in DictGroupINV:
                        myMirrorGroupVertex[DictGroupINV[mirror_normal_group_name]] = myGroupVertex[OneGroup]
                    else:
                        #if this group doesn't exist yet add it to the group and the dictionnary                                                    
                        length=len(DictGroup)
                        bpy.context.active_object.vertex_groups.new(name=mirror_normal_group_name)
                        DictGroup[length] = mirror_normal_group_name
                        DictGroupINV[mirror_normal_group_name]=length
                       

                if obj.vertex_groups[OneGroup].name.find(dest_side)>-1:
                    mirror_normal_group_name = obj.vertex_groups[OneGroup].name.replace(dest_side,ori_side)
                    if mirror_normal_group_name in DictGroupINV:
                        myMirrorGroupVertex[DictGroupINV[mirror_normal_group_name]] = myGroupVertex[OneGroup]
                    else:
                        #if this group doesn't exist yet add it to the group and the dictionnary                                                    
                        length=len(DictGroup)
                        bpy.context.active_object.vertex_groups.new(name=mirror_normal_group_name)
                        DictGroup[length] = mirror_normal_group_name
                        DictGroupINV[mirror_normal_group_name]=length

 
                if obj.vertex_groups[OneGroup].name.find(ori_side)==-1 and obj.vertex_groups[OneGroup].name.find(dest_side)==-1:
                    myMirrorGroupVertex[OneGroup] = myGroupVertex[OneGroup]
    
        
        ##remove the older group
        for group in bpy.data.meshes[mesh].vertices[DictMirror[vertex]].groups:
            print(DictGroup[group.group])
            print(DictMirror[vertex])
            obj.vertex_groups[DictGroup[group.group]].remove([DictMirror[vertex]])

        
        #add the new ones
        for OneGroupVertex in myMirrorGroupVertex.keys():
            obj.vertex_groups[DictGroup[OneGroupVertex]].add([DictMirror[vertex]],myMirrorGroupVertex[OneGroupVertex],'REPLACE')
                                            

                        
                
    print('end')
    end = (datetime.datetime.now())
    timing = end-start
    print(timing)
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')


class BR_OT_mirror_all_vertex_groups(bpy.types.Operator):
    """Mirror All Vertex groups"""
    bl_idname = "object.mirror_all_vertexgroups"
    bl_label = "Mirror All Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}
    action = bpy.props.StringProperty()
 
    enum_Axis = EnumProperty(name="On Which Axis?", default='X',
        items = [('Z', 'Z axis', 'Z'),('Y', 'Y axis', 'Y'),('X', 'X axis', 'X')])

    enum_Way = EnumProperty(name="Which Way?", default='normal',
        items = [('reverse', '(-) to (+)', 'reverse'),('normal', '(+) to (-)', 'normal')])

    enum_Pattern = EnumProperty(name="Which Pattern?", default='3',
        items = [('4', '_l and _r', '4'),('3', '_L and _R', '3'),('2', '.l and .r', '2'),('1', '.L and .R', '1')])

    special_pattern = BoolProperty(name="or... Use my own patter")      
        
    left_side = StringProperty(name="My own Patter, Left Side",default=".Left")
    right_side = StringProperty(name="My own Patter, Right Side",default=".Right")
            
    tolerance = FloatProperty(name="Tolerance", min=0, max=100, precision=3, default=0.001)

 
    def execute(self, context):
        copy_mirror_weight(self.enum_Axis,self.enum_Way,self.enum_Pattern,self.special_pattern,self.left_side,self.right_side,self.tolerance)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
 
        

def menu_draw(self, context):
    self.layout.separator()
    self.layout.operator(BR_OT_mirror_all_vertex_groups.bl_idname, text="Mirror all vertex groups", icon='ARROW_LEFTRIGHT')

    bpy.ops.object.dialog_operator('INVOKE_DEFAULT')



classes = (
    BR_OT_mirror_all_vertex_groups,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.MESH_MT_vertex_group_context_menu.append(menu_draw)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.MESH_MT_vertex_group_context_menu.remove(menu_draw)


if __name__ == "__main__":
    register()
