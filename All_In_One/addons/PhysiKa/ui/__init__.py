if "bpy" in locals():
    import importlib
    reloadable_modules = [
        'animate_ui',
        
    ]
    for module_name in reloadable_modules:
        if module_name in locals():
            importlib.reload(locals()[module_name])

import bpy

# from . import(
#     constraint_ui,
#     simulate_ui,
#     animate_ui
# )


def append_to_PHYSICS_PT_add_panel(self, context):
    obj = context.scene.objects.active
    if not obj.type == 'MESH':
        return

    column = self.layout.column(align=True)
    split = column.split(percentage=0.5)
    column_left = split.column()
    column_right = split.column()

    if obj.physika.is_active:
        column_right.operator(
                "physika_operators.physika_remove", 
                 text="PhysiKa", 
                 icon='X'
                )

    else:
        column_right.operator(
            "physika_operators.physika_add", 
            text="PhysiKa", 
            icon='MOD_SOLIDIFY'
        )


def register():

    bpy.types.PHYSICS_PT_add.append(append_to_PHYSICS_PT_add_panel)

def unregister():

    bpy.types.PHYSICS_PT_add.remove(append_to_PHYSICS_PT_add_panel)

