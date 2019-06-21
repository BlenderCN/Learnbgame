import bpy


class physika_obstacle_list_operators(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "physika_operators.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}
    
    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        obj = context.scene.objects.active
        obj_name = obj.name.replace('.','_')
        obta_props = obj.physika.obstacles
        idx = obta_props.index

        try:
            item = obta_props.objs[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(obta_props.objs) - 1:
                item_next = obta_props.objs[idx+1].name
                obta_props.objs.move(idx, idx+1)
                obta_props.index += 1
                info = 'Item "%s" moved to position %d' % (item.name, obta_props.index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = obta_props.objs[idx-1].name
                obta_props.objs.move(idx, idx-1)
                obta_props.index -= 1
                info = 'Item "%s" moved to position %d' % (item.name, obta_props.index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (obta_props.objs[idx].name)
                obta_props.index -= 1
                obta_props.objs.remove(idx)
                self.report({'INFO'}, info)
                
        if self.action == 'ADD':
            if obta_props.chosen_obj and eval("obj.physika." + obj_name +  "_obstacle == False"):
                chosen_obj = obta_props.chosen_obj
                item = obta_props.objs.add()
                item.name = chosen_obj.name
                print(item.name)
                item.obj_ptr = chosen_obj
                obta_props.index = len(obta_props.objs)-1
                
                # chosen_obj.physika.is_obstacle = True
                eval("obj.physika." + obj_name +  "_obstacle == True")
                
                info = '"%s" added to list' % (item.name)
                self.report({'INFO'}, info)

                chosen_obj = None
            else:
                self.report({'INFO'}, "Nothing selected in the Viewport")
        return {"FINISHED"}



def register():
    bpy.utils.register_class(physika_obstacle_list_operators)

def unregister():
    bpy.utils.unregister_class(physika_obstacle_list_operators)
