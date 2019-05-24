bl_info = {
    "name": "Destructability Editor",
    "author": "scorpion81, plasmasolutions(Tester)",
    "version": (1, 3),
    "blender": (2, 66, 0),
    "location": "Physics > Destruction",
    "description": "Define how game engine shall handle destruction of objects",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Object/Destructability",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=30567&group_id=153&atid=467",
    "category": "Learnbgame",
}


if not __name__ in "__main__":
    if "bpy" in locals():
       import imp
       imp.reload(destruction_gui)
    else:
       from object_destruction import destruction_gui as dg

import bpy
from bpy.app.handlers import persistent

from bpy.types import Context
StructRNA = bpy.types.Struct.__bases__[0]
olddraw = None
oldcopy = None

i18n_default_ctxt = bpy.app.translations.contexts.default

#override some methods here, no need to change the original files this way
def copy(self):
    from types import BuiltinMethodType
    new_context = {}
    generic_attrs = (list(StructRNA.__dict__.keys()) +
                     ["bl_rna", "rna_type", "copy"])
    for attr in dir(self):
        if not (attr.startswith("_") or attr in generic_attrs):
            if hasattr(self, attr):
                value = getattr(self, attr)
                if type(value) != BuiltinMethodType:
                    new_context[attr] = value

    return new_context


def physics_add(self, layout, md, name, type, typeicon, toggles):
    sub = layout.row(align=True)
    if md:
        sub.context_pointer_set("modifier", md)
        sub.operator("object.modifier_remove", text=name, text_ctxt=i18n_default_ctxt, icon='X')
        if(toggles):
            sub.prop(md, "show_render", text="")
            sub.prop(md, "show_viewport", text="")
    else:
        sub.operator("object.modifier_add", text=name, text_ctxt=i18n_default_ctxt, icon=typeicon).type = type


def physics_add_special(self, layout, data, name, addop, removeop, typeicon):
    sub = layout.row(align=True)
    if data:
        sub.operator(removeop, text=name, text_ctxt=i18n_default_ctxt, icon='X')
    else:
        sub.operator(addop, text=name, text_ctxt=i18n_default_ctxt, icon=typeicon)
                
        
def draw(self, context):
    ob = context.object

    layout = self.layout
    layout.label("Enable physics for:")
    split = layout.split()
    col = split.column()

    if(context.object.field.type == 'NONE'):
        col.operator("object.forcefield_toggle", text="Force Field", icon='FORCE_FORCE')
    else:
        col.operator("object.forcefield_toggle", text="Force Field", icon='X')

    if(ob.type == 'MESH'):
        physics_add(self, col, context.collision, "Collision", 'COLLISION', 'MOD_PHYSICS', False)
        physics_add(self, col, context.cloth, "Cloth", 'CLOTH', 'MOD_CLOTH', True)
        physics_add(self, col, context.dynamic_paint, "Dynamic Paint", 'DYNAMIC_PAINT', 'MOD_DYNAMICPAINT', True)
    
    #destruction    
    if dg.isMesh(context) or dg.isParent(context):
        
        if not context.object.destEnabled:
            icon = 'MOD_EXPLODE'
        else:
            icon = 'X'
            
        col.operator("destruction.enable", text="Destruction", icon=icon)

    col = split.column()

    if(ob.type == 'MESH' or ob.type == 'LATTICE'or ob.type == 'CURVE'):
        physics_add(self, col, context.soft_body, "Soft Body", 'SOFT_BODY', 'MOD_SOFT', True)

    if(ob.type == 'MESH'):
        physics_add(self, col, context.fluid, "Fluid", 'FLUID_SIMULATION', 'MOD_FLUIDSIM', True)
        physics_add(self, col, context.smoke, "Smoke", 'SMOKE', 'MOD_SMOKE', True)  
    
    if(ob.type == 'MESH'):
        physics_add_special(self, col, ob.rigid_body, "Rigid Body",
                                "rigidbody.object_add",
                                "rigidbody.object_remove",
                                'MESH_ICOSPHERE')  # XXX: need dedicated icon

        # all types of objects can have rigid body constraint
    physics_add_special(self, col, ob.rigid_body_constraint, "Rigid Body Constraint",
                            "rigidbody.constraint_add",
                            "rigidbody.constraint_remove",
                            'CONSTRAINT')  # RB_TODO needs better icon
    
#a hacky solution
#Context.copy = copy

def setOp(it, name):
    it.idname = name    

def changeKeymap(name):
     km = bpy.context.window_manager.keyconfigs.active.keymaps.find("Object Mode")
     [setOp(it, name) for it in km.keymap_items if it.name == "Start Game Engine"]


@persistent
def load_handler(dummy):
   # print("Load Handler")
    if hasattr(bpy.context.object, "destEnabled"):
        changeKeymap("game.start")
    else:
        changeKeymap("view3d.game_start")
    

@persistent
def save_handler(dummy):
    #print("Save Handler")
    if hasattr(bpy.context.object, "destEnabled"):
        changeKeymap("game.start")
    else:
        changeKeymap("view3d.game_start")
    

def register():
    bpy.utils.register_module(__name__)
    #unregister some panels again manually
    bpy.types.Object.destEnabled = bpy.props.BoolProperty(name = "destEnabled", default = False)
    
#    bpy.utils.unregister_class(dg.DestructionFracturePanel)
#    bpy.utils.unregister_class(dg.DestructionPhysicsPanel)
#    bpy.utils.unregister_class(dg.DestructionSetupPanel)
#    bpy.utils.unregister_class(dg.DestructionHierarchyPanel)
#    bpy.utils.unregister_class(dg.DestructionRolePanel)
    
    global olddraw
    global oldcopy
    
    olddraw = bpy.types.PHYSICS_PT_add.draw
    oldcopy = Context.copy
    
    bpy.types.PHYSICS_PT_add.draw = draw
    Context.copy = copy
    
    #change keymap here
    changeKeymap("game.start")
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.save_post.append(save_handler)
   
    
def unregister():
    
    #and restore old op here
    del bpy.types.Object.destEnabled
    
    changeKeymap("view3d.game_start")
    
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.save_post.remove(save_handler)
    
    global olddraw
    global oldcopy
    
    bpy.types.PHYSICS_PT_add.draw = olddraw
    Context.copy = oldcopy
    
    bpy.utils.unregister_module(__name__)
   
if __name__ == "__main__":
    print("IN INITPY MAIN")
    from object_destruction import destruction_gui
    #destruction_gui.register()