import bpy

class ObjectCopyCustomProperties(bpy.types.Operator):
    bl_idname = "object.copy_custom_properties"
    bl_label = "Copy custom object properties"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and len(context.selected_editable_objects) >= 2

    def execute(self, context):
        selected = context.selected_editable_objects
        active = context.active_object
        properties = self.get_properties(active)
        if not properties:
            self.report({'WARNING'}, "Object has no custom properties")
        else:
            for obj in selected:
                if obj != active:
                    for p in properties.keys():
                        self.copy_property(active, obj, p)
            self.report({'INFO'}, "{0} properties copied".format(len(properties.keys())))
        return {'FINISHED'}

    def get_properties(self, obj):
        try:
            return obj['_RNA_UI']
        except AttributeError:
            return { }

    def copy_property(self, source, target, name):
        target[name] = source[name] # copy property value
        if '_RNA_UI' not in target.keys():
            target['_RNA_UI'] = {}
        target['_RNA_UI'][name] = self.get_properties(source)[name].to_dict() # copy min, max, etc
