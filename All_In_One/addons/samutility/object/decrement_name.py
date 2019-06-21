import bpy
import re

def decrement_name(ob, rx):
    old = ob.name
    if not bpy.data.objects.get(ob.name[:-4]):
        #rename
        ob.name = ob.name[:-4]
        print(old, '>>', ob.name)
        return(ob.name)
    else:
        num = int(ob.name[-3:])
        #maybe start at 0 to take case '.000' (but supposely covered previously)
        for i in range(1, num):
            new = ob.name[:-3] + str(i).zfill(3)
            if not bpy.data.objects.get(new):
                ob.name = new
                print(old, '>>', new)#, ' - from num', num, 'to', i)
                return(ob.name)
    print(ob.name, 'impossible to decrement')
    return


class Decrement_name_OP(bpy.types.Operator):
    bl_idname = "samutils.decrement_name"
    bl_label = "Decrement name"
    bl_description = "Decrement the name if possible when suffixed '.001' or more"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print('-- Decrement name --')
        rx = re.compile(r'(.*)(.\d{3})$')
        i = 0
        for ob in context.selected_objects:
            if rx.match(ob.name):
                res = decrement_name(ob, rx)
                if res:
                    i+=1

        if i:
            mess = str(i) + ' object renamed'
            self.report({'INFO'}, mess)#WARNING, ERROR

        else:
            mess = 'NO object to decrement'
            self.report({'WARNING'}, mess)#INFO, ERROR


        return {"FINISHED"}
