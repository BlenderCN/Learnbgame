import bpy

myFontCurve = bpy.data.curves.new(type="FONT",name="myFontCurve")
myFontOb = bpy.data.objects.new("myFontOb",myFontCurve)
myFontOb.data.body = "my text"
bpy.context.scene.objects.link(myFontOb)
bpy.context.scene.update()


#bpy.ops.object.text_add()
#ob=bpy.context.object
#ob.data.body = "my text"

