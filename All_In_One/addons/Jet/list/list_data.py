import bpy
from bpy.props import StringProperty, CollectionProperty, IntProperty, \
                      BoolProperty, PointerProperty, EnumProperty
from bpy.types import PropertyGroup, Object
from .. common_utils import select_obj_exclusive

class ItemPropertyGroup(PropertyGroup):
    """
    Stores the properties of a UIList item
    """
    object = PointerProperty(name="object", type=Object)

class HiObjListPropertyGroup(PropertyGroup):
    """
    Stores the properties of the hi-res UIList item
    """
    def update(self, context):
        if len(self.obj_list) == 0:
            return
        obj = self.obj_list[self.obj_list_index].object
        #Select the object
        obj.select = True
        #Make the object Active
        context.scene.objects.active = obj

    obj_list = CollectionProperty(type=ItemPropertyGroup)
    obj_list_index = IntProperty(name="Index", default=0, min=0, update=update)


class LowItemPropertyGroup(PropertyGroup):
    object = PointerProperty(name="object", type=Object)
    list_high_res = PointerProperty(type=HiObjListPropertyGroup)


class LowObjListPropertyGroup(PropertyGroup):
    """
    Stores the properties of the low-res UIList item
    """
    mode = EnumProperty(default='exclusive', items=[
                                            ('exclusive', 'Exclusive', 'Exclusive'),
                                            ('select', 'Select', 'Select'),
                                            ('no_select', 'NoSelect', 'NoSelect')])

    def select_hi_res_list(self, list):
        for hi_ob in list.obj_list:
            if not hasattr(hi_ob.object, "select"):
                continue
            hi_ob.object.select = True

    # When the outside updating property is set,
    # a flag is defined to distinguish from the inside updating property
    def set_select(self, value, mode):
        self.mode = mode
        self.obj_list_index = value
        self.mode = 'exclusive'

    def get(self):
        return self.obj_list_index

    def update(self, context):
        if len(self.obj_list) == 0:
            return
        wm = context.window_manager
        if not wm.Jet.timer:
            bpy.ops.wm.jet_modal_timer_op()
        obj = self.obj_list[self.obj_list_index].object
        # Select the object
        # Different behaviour depending on where the variable has been updated from
        if self.mode == 'exclusive':
            select_obj_exclusive(obj)
        elif self.mode == 'select':
            obj.select = True

        #Make the object Active
        context.scene.objects.active = obj

        #Select the linked hi-res list
        if context.scene.Jet.list_low_res.select_hi_rest_list and \
            self.mode != 'non_select':
            self.select_hi_res_list(self.obj_list[self.obj_list_index].list_high_res)

    obj_list = CollectionProperty(type=LowItemPropertyGroup)
    obj_list_index = IntProperty(name="Index", default=0, min=0, update=update)
    select_hi_rest_list = BoolProperty(default=True)

    # This property allows different behaviours when updating from outside or from inside
    obj_list_index_select = IntProperty(name="Index", default=0, min=0,
                                        set=lambda self, value: self.set_select(value, 'select'))
    obj_list_index_no_select = IntProperty(name="Index", default=0, min=0,
                                        set=lambda self, value: self.set_select(value, 'no_select'))
