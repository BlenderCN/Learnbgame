# Blender用python控制物体运动动画

import bpy,time,threading


x=0
ob=bpy.context.object


def fc(a):
    global x
    while x<5:
        time.sleep(0.1)
        x+=0.1
        ob.location[0]=x




t=threading.Thread(target=fc,args=(5,))
t.start()