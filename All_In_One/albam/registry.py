try:
    import bpy
except ImportError:
    bpy = None


class AlbamRegistry:

    def __init__(self):
        self.import_registry = {}
        self.export_registry = {}

        self._blender_panels = set()
        self._blender_operators = set()
        self._blender_props = {}  # (bpy.type, custom_name, bpy_prop): cls
        self._blender_prop_groups = {}  # XXX hackish. class_name: class

    def register_function(self, func_type, identifier):
        def decorator(f):
            if func_type == 'import':
                self.import_registry[identifier] = f
            elif func_type == 'export':
                self.export_registry[identifier] = f
            else:
                raise TypeError('func_type {} not valid.'.format(func_type))
            return f
        return decorator

    def blender_panel(self):
        def decorator(cls):
            self._blender_panels.add(cls)
        return decorator

    def blender_prop(self, bpy_type, bpy_type_name, bpy_prop):
        def decorator(data_cls):
            self._blender_props[(bpy_type, bpy_type_name, bpy_prop)] = data_cls
        return decorator

    def blender_prop_group(self):
        def decorator(cls):
            self._blender_prop_groups[cls.__name__] = cls
        return decorator

    def blender_operator(self):
        def decorator(cls):
            self._blender_operators.add(cls)
        return decorator

    def blender_init(self, action='register'):
        if not bpy:
            return
        if action == 'register':
            do_register = bpy.utils.register_class
        else:
            do_register = bpy.utils.unregister_class

        # The order is important
        for cls in self._blender_prop_groups.values():
            do_register(cls)

        for (bpy_type, bpy_type_name, bpy_prop), data_cls in self._blender_props.items():
            #print(bpy_type, bpy_type_name, bpy_prop, data_cls, data_cls.kwargs)
            #print('    ')
            # XXX ultra hack
            if bpy_prop.__name__ in ('PointerProperty', 'CollectionProperty'):
                cls_name = data_cls.kwargs['type']  # XXX yes, it's a string of the name of the class.
                the_type = self._blender_prop_groups[cls_name]
                setattr(bpy_type, bpy_type_name, bpy_prop(type=the_type))

            else:
                setattr(bpy_type, bpy_type_name, bpy_prop(**data_cls.kwargs))


        for panel_cls in self._blender_panels:
            do_register(panel_cls)

        for operator_cls in self._blender_operators:
            do_register(operator_cls)


# For blender
def register():
    albam_registry.blender_init('register')


def unregister():
    albam_registry.blender_init('unregister')

if __name__ == '__main__':
    albam_registry = AlbamRegistry()
    register()
