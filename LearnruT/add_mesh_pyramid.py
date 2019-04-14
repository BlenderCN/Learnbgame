import bpy #加载bpy，这个是必须有的 
from bpy.props import FloatProperty, FloatVectorProperty, BoolProperty 

#定义添加网格的方法 
def Add_Pyramid(self, context, height = 2): 
    h = height #四棱锥高度 
    
    #顶点 
    verts = [(1,1,0), 
             (-1,1,0), 
             (-1,-1,0), 
             (1,-1,0), 
             (0,0,h)] 
    
    #边 
    edges = [(0,1), 
             (1,2), 
             (2,3), 
             (3,0), 
             (0,4), 
             (1,4), 
             (2,4), 
             (3,4)] 
    
    #面 
    faces = [(0,1,4), 
             (1,2,4), 
             (2,3,4), 
             (3,0,4), 
             (0,1,2,3)] 
    
    mesh = bpy.data.meshes.new('Pyramid_Mesh') #新建网格 
    mesh.from_pydata(verts, edges, faces) #载入网格数据 
    mesh.update() #更新网格数据 
    
    from bpy_extras import object_utils 
    object_utils.object_data_add(context, mesh, operator=self) 
    # pyramid=bpy.data.objects.new('Pyramid', mesh) #新建物体“Pyramid”，并使用“mesh”网格数据 
    # scene=bpy.context.scene 
    # scene.objects.link(pyramid) #将物体链接至场景 
#添加一个Operator类AddPyramid 
class AddPyramid(bpy.types.Operator): 
    bl_idname = 'mesh.primitive_pyramid_add' #定义ID名称 
    bl_label= 'Pyramid' #定义显示的标签名 
    bl_options = {'REGISTER', 'UNDO'} 
    
    view_align = BoolProperty( 
                    name="Align to View", 
                    default=False, 
                    ) 
    
    height = FloatProperty( 
                    name = 'Height', 
                    description = 'Pyramid Height', 
                    min = 0.0, 
                    default = 2.0
                    ) 
    
    location = FloatVectorProperty( 
                    name = 'Location', 
                    subtype = 'TRANSLATION'
                    ) 
    
    rotation = FloatVectorProperty( 
                    name="Rotation", 
                    subtype='EULER', 
                    ) 
                    
    def execute(self, context): 
        Add_Pyramid(self, context, self.height) #调用Add_Pyramid()方法 
        return {'FINISHED'} #执行结束后返回值 
        
class AddPyramidPanel(bpy.types.Panel): 
    bl_idname = 'OBJECT_PT_Pyramid' 
    bl_space_type = 'VIEW_3D' 
    bl_region_type = 'TOOLS' 
    bl_category = 'Create' 
    bl_context = 'objectmode' 
    bl_label = 'Add Pyramid' 
    
    def draw(self, context): 
        layout = self.layout 
        layout.label(text = 'Height:') 
        layout.operator(AddPyramid.bl_idname) 
#定义添加菜单方法 
def menu_func(self, context): 
   self.layout.operator(AddPyramid.bl_idname, icon = 'MESH_CONE') 

#定义注册类方法 
def register(): 
    bpy.utils.register_class(AddPyramid) 
    #注册面板 
    #bpy.utils.register_class(AddPyramidPanel) 
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func) #添加菜单 

#定义取消注册类方法 
def unregister(): 
    bpy.utils.unregister_class(AddPyramid) 
    #bpy.utils.register_class(AddPyramidPanel) 
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func) #移除菜单 
    
#直接执行py文件时，注册Operator 
if __name__ == '__main__': 
    register()