# blender批量导入OBJ文件的
# http://tieba.baidu.com/p/4709956823?pid=95475220119&cid=0#95475220119
import bpy,os


a='C:\\Users\\tiger\\Desktop\\CS'


b=os.listdir(a)


for i in b:
    bpy.ops.import_scene.obj(filepath="{0}/{1}".format(a,i))