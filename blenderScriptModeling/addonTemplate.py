bl_info = {
"name": "addonTest", #插件名字
"author": "HRW", #作者名字
"version": (1, 1), #插件版本
"blender": (2, 78, 0), #blender版本
"location": "3DView > Tools", #插件所在位置
"description": "addonDescription", #描述
"warning": "warning", #警告
"wiki_url": "http://tieba.baidu.com/"
"p/4927354024", #文档地址
"support": 'OFFICIAL', #支持??
"category": "Development", #分类
}
import bpy


class panel_2(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'title' #标题名字
    bl_label = "test1" #菜单名字
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'} # HIDE_HEADER 为隐藏菜单

def draw(self, context):
    layout = self.layout
    layout.operator(AddChain.bl_idname, text="按钮") #按钮名字


class AddChain(bpy.types.Operator):
    """提示信息"""
    bl_idname = "mesh.cs_add" # python 提示
    bl_label = "Interface"
    bl_options = {'REGISTER', 'UNDO'}


def execute(self, context): #点击按钮时候执行
    cs()
    return {'FINISHED'}


def register(): #启用插件时候执行
    #bpy.utils.register_class(panel_1) #注册一个类
    bpy.utils.register_module(__name__) #大概是注册这个模块
    print('zc')

def unregister(): #关闭插件时候执行
    #bpy.utils.unregister_class(panel_1) #注销一个类
    bpy.utils.unregister_module(__name__) #大概是注销这个模块
    print('zx')


def cs():
    bpy.ops.mesh.primitive_uv_sphere_add()




if __name__ == "__main__":
    register()