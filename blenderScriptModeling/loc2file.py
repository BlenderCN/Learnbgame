# blender记录物体动画位置 输出到txt
# https://tieba.baidu.com/p/5054332482?red_tag=0159780658
import bpy,time,threading,os


x=bpy.context.scene.frame_end
bpy.context.scene.frame_current = bpy.context.scene.frame_start
ob=bpy.context.object
f=open("am.txt","w")

def fc():
    global x
    while x>0:
        time.sleep(0.1)
        x-=1
        f=open("am.txt","a")
        f.write("frame {0} X={1} Y={2} Z={3} \n".format(bpy.context.scene.frame_current,ob.location[0],ob.location[1],ob.location[2]))
        bpy.context.scene.frame_current = bpy.context.scene.frame_current +1
    else:
        print(0)
        os.popen('subl am.txt')




t=threading.Thread(target=fc)
t.start()
