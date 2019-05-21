bl_info = {
    "name": "Dial and Scale",
    "author": "stacker, sambler",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "location": "3DView > Add > Curve > Dial and Scale",
    "description": "Add an array of text number objects or watch dials.",
    "warning": "",
    "wiki_url": "https://github.com/3dbug/blender/blob/master/DialScale.py",
    "tracker_url": "https://github.com/3dbug/blender/issues",
    "category": "Learnbgame",
    }

import bpy,math
import mathutils

from bpy.props import IntProperty,FloatProperty,StringProperty,EnumProperty,BoolProperty

fonts_list = []

def getFonts(self, context):
    fonts_list = []
    for afont in bpy.data.fonts:
        fonts_list.append(( afont.name, afont.name,""))
    if len(fonts_list) == 0:
        fonts_list.append(("Bfont","Bfont",""))
    return fonts_list

class DialScale(bpy.types.Operator):
    """ Creates an array of text elements"""
    bl_idname = "curve.dial_scale"
    bl_label = "Create Dials and Scales"
    bl_options = {'REGISTER', 'UNDO'}

    start : IntProperty(name="Start",description="Start value",min=-10000, max=10000,default=1 )
    count : IntProperty(name="Count",description="Number of items to create",min=1, max=100, default=12  )
    step : IntProperty(name="Step",description="Increment of number",min=-10000, max=10000, default=1  )
    offset : FloatProperty(name="Offset",description="Distance",min=0.01, max=100.0, default=2.5 )
    dialType : EnumProperty( name="Dial Type",description="Basis of creating the dial", items=[("circular","circular","A round dial"),("horizontal","horizontal","A horizontal scale"),("vertical","vertical","A vertical scale")], default="circular")
    rotate : FloatProperty(name="Rotation",description="Start rotation of first item",min=-360.0, max=360.0, default=0.0 )
    segment : FloatProperty(name="Segment",description="Circle Segment",min=-360.0, max=360.0, default=360.0 )
    ticks : IntProperty(name="Ticks",description="Number of ticks between numbers",min=0, max=100, default=5  )
    tickOffset : FloatProperty(name="Tick Offset",description="Distance to offset the Ticks",min=-100.0, max=100.0, default=1.3 )

    font : EnumProperty( name="Fonts",items=getFonts)

    def execute(self, context):
        x = -self.offset
        y = 0.0
        angle = math.radians( self.rotate ) - math.pi/2
        angle_step = -math.radians( self.segment ) / self.count
        angle = angle - angle_step
        pos = self.start - 1
        num = self.start
        end = self.count + self.start - 1

        while pos < end:
            if self.dialType == "circular":
                vec3d = mathutils.Vector((self.offset, 0, 0))
                vpos = vec3d @ mathutils.Matrix.Rotation( angle , 3, 'Z')
            elif self.dialType == "horizontal":
                x = x + self.offset
                vpos=(x,0,0)
            else:
                y = y + self.offset
                vpos = (0,y,0)

            bpy.ops.object.text_add()
            ob=bpy.context.object
            ob.data.body = str(num)
            ob.data.font = bpy.data.fonts[ self.font ]
            ob.data.align_x = ob.data.align_y = 'CENTER'
            bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
            bpy.ops.transform.translate(value=vpos)

            for t in range(0,self.ticks):
                bpy.ops.mesh.primitive_plane_add(size=.04 if t == 0 else .02)
                if self.dialType == "circular":
                    tick_step = angle_step / self.ticks
                    vec3d = mathutils.Vector((self.offset*self.tickOffset, 0, 0))
                    tpos = vec3d @ mathutils.Matrix.Rotation( (angle + (t*tick_step)) , 3, 'Z')
                    bpy.ops.transform.resize(value=(6,1,1))
                    bpy.ops.transform.rotate(value= angle + t*tick_step, axis=(0, 0, 1))
                elif self.dialType == "horizontal" and pos < end-1:
                    tick_step = self.offset / self.ticks
                    tpos=(x+t*tick_step,self.tickOffset,0)
                    bpy.ops.transform.resize(value=(1,6,1))
                elif pos < end -1:
                    tick_step = self.offset / self.ticks
                    tpos=(self.tickOffset,y+t*tick_step,0)
                    bpy.ops.transform.resize(value=(6,1,1))
                bpy.ops.transform.translate(value=tpos)

            angle = angle - angle_step
            pos = pos + 1
            num = num + self.step
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(DialScale.bl_idname, icon='PLUGIN')

def register():
    bpy.utils.register_class(DialScale)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(DialScale)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)

if __name__ == "__main__":
    register()

