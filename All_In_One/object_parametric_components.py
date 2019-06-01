bl_info = {
    "name": "Parametric Components",
    "author": "Nesvarbu",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "World Properties > Components",
    "warning": "",
    "description": "",
    "wiki_url": "http://wiki.digidone3d.com/index.php/Main_Page",
    "category": "Learnbgame",
}

import bpy


def parcomp_objprop_obj_items(self, context):
    actobj = context.active_object
    return [(obj.name, obj.name, '', i) for i, obj in enumerate(actobj.children)]


parcomp_objprop_prop_items = [
    ('location.x'      , 'Location X' , '', 0),
    ('location.y'      , 'Location Y' , '', 1),
    ('location.z'      , 'Location Z' , '', 2),
    ('rotation_euler.x', 'Rotation X' , '', 3),
    ('rotation_euler.y', 'Rotation Y' , '', 4),
    ('rotation_euler.z', 'Rotation Z' , '', 5),
    ('dimensions.x'    , 'Dimension X', '', 6),
    ('dimensions.y'    , 'Dimension Y', '', 7),
    ('dimensions.z'    , 'Dimension Z', '', 8),
]


parcomp_param_type_items = [
    ('FLOAT'  , 'Float'  , '', 0),
    ('INTEGER', 'Integer', '', 1),
    ('BOOLEAN', 'Boolean', '', 2),
    ('STRING' , 'String' , '', 3),
]


def parcomp_param_value_update(self, context):
    actobj = context.active_object
    comp = context.scene.world.parcomp_components[actobj.parcomp_component_name]
    comptype = comp.types[actobj.parcomp_component_type]
    for compobj in bpy.data.collections[comptype.collname].objects:
        objitems = compobj.children
        for a in self.assigned_props:
            iobj = a.get('obj', 0)
            iprop = a.get('prop', 0)
            obj = objitems[iobj]
            (prop, axis) = parcomp_objprop_prop_items[iprop][0].split('.')
            attr = getattr(obj, prop)
            setattr(attr, axis, self['value_FLOAT'])


def parcomp_comp_name_items(self, context):
    return [(comp.name, comp.name, '', i) for i, comp in enumerate(context.scene.world.parcomp_components)]


def parcomp_comp_type_items(self, context):
    actobj = context.active_object
    comp = context.scene.world.parcomp_components[actobj.parcomp_component_name]
    return [(comptype.name, comptype.name, '', i) for i, comptype in enumerate(comp.types)]


class parcomp_ObjectProperty(bpy.types.PropertyGroup):
    obj: bpy.props.EnumProperty(name='Object', items=parcomp_objprop_obj_items)
    prop: bpy.props.EnumProperty(name='Property', items=parcomp_objprop_prop_items)


class parcomp_Parameter(bpy.types.PropertyGroup):
    ptype:  bpy.props.EnumProperty(name='Parameter Type', items=parcomp_param_type_items)
    name: bpy.props.StringProperty(name='Parameter Name')
    group: bpy.props.StringProperty(name='Parameter Group')
    value_FLOAT: bpy.props.FloatProperty(name='Parameter Value', update=parcomp_param_value_update)
    value_INTEGER: bpy.props.IntProperty(name='Parameter Value')
    value_BOOLEAN: bpy.props.BoolProperty(name='Parameter Value')
    value_STRING: bpy.props.StringProperty(name='Parameter Value')
    assigned_props: bpy.props.CollectionProperty(type=parcomp_ObjectProperty)


class parcomp_ComponentType(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Component Type')
    collname: bpy.props.StringProperty(name='Collection Name')


class parcomp_ComponentObject(bpy.types.PropertyGroup):
    objtype: bpy.props.StringProperty(name='Object Type')
    objdata: bpy.props.StringProperty(name='Object Data')
    location_x: bpy.props.FloatProperty(name='Location X')
    location_y: bpy.props.FloatProperty(name='Location Y')
    location_z: bpy.props.FloatProperty(name='Location Z')
    rotation_x: bpy.props.FloatProperty(name='Rotation X')
    rotation_y: bpy.props.FloatProperty(name='Rotation Y')
    rotation_z: bpy.props.FloatProperty(name='Rotation Z')
    dimension_x: bpy.props.FloatProperty(name='Dimension X')
    dimension_y: bpy.props.FloatProperty(name='Dimension Y')
    dimension_z: bpy.props.FloatProperty(name='Dimension Z')


class parcomp_Component(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Component Name')
    params: bpy.props.CollectionProperty(type=parcomp_Parameter)
    types: bpy.props.CollectionProperty(type=parcomp_ComponentType)
    nexttypenum: bpy.props.IntProperty(name='Next Type Number')
    objs: bpy.props.CollectionProperty(type=parcomp_ComponentObject)


class OBJECT_OT_parcomp_component_create(bpy.types.Operator):
    bl_idname = "object.parcomp_component_create"
    bl_label = "Create Component"

    def execute(self, context):
        selobjs = list(context.selected_objects)
        actobj = context.active_object
        bpy.ops.object.empty_add(
            type='PLAIN_AXES',
            view_align=False,
            location=tuple(actobj.location),
            rotation=(0, 0, 0),
            #layers=current_layers,
        )
        actobj = context.active_object
        actobj['parcomp_is_parametric'] = True
        for obj in selobjs:
            obj.select_set(True)
        actobj.select_set(False)
        actobj.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT')
        world = context.scene.world
        comp = world.parcomp_components.add()
        comp.name = 'Comp.%d' % (world.parcomp_nextcompnum,)
        world.parcomp_nextcompnum += 1
        actobj.name = comp.name
        actobj['parcomp_component_name_skip'] = True
        actobj.parcomp_component_name = comp.name
        actobj.parcomp_component_name_sel = comp.name
        comptype = comp.types.add()
        comptype.name = 'Type.0'
        comp.nexttypenum = 1
        actobj['parcomp_component_type_skip'] = True
        actobj.parcomp_component_type = comptype.name
        actobj.parcomp_component_type_sel = comptype.name
        for obj in actobj.children:
            obj.use_fake_user = True
            compobj = comp.objs.add()
            compobj.objtype = obj.type
            if compobj.objtype == 'MESH':
                compobj.objdata = obj.data.name
            compobj.location_x = obj.location.x
            compobj.location_y = obj.location.y
            compobj.location_z = obj.location.z
            compobj.rotation_x = obj.rotation_euler.x
            compobj.rotation_y = obj.rotation_euler.y
            compobj.rotation_z = obj.rotation_euler.z
            compobj.dimension_x = obj.dimensions.x
            compobj.dimension_y = obj.dimensions.y
            compobj.dimension_z = obj.dimensions.z
        coll = bpy.data.collections.new('coll')
        comptype.collname = coll.name
        coll.objects.link(actobj)
        return {'FINISHED'}


class OBJECT_OT_parcomp_component_add(bpy.types.Operator):
    bl_idname = "object.parcomp_component_add"
    bl_label = "Add Component"

    comp: bpy.props.EnumProperty(name='Component', items=parcomp_comp_name_items)
    comptype: bpy.props.EnumProperty(name='Type', items=parcomp_comp_type_items)

    def execute(self, context):
        if not self.comp:
            return {'CANCELLED'}
        comp = context.scene.world.parcomp_components[self.comp]
        comptype = comp.types[self.comptype]
        coll = bpy.data.collections[comptype.collname]
        obj = coll.objects[0]
        obj.select_set(True)
        bpy.ops.object.select_more()
        obj.select_set(True)
        bpy.ops.object.duplicate_move_linked()
        obj = context.active_object
        obj.location = context.scene.cursor.location
        coll.objects.link(obj)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_component_save(bpy.types.Operator):
    bl_idname = "object.parcomp_component_save"
    bl_label = "Save As New Component"

    name: bpy.props.StringProperty(name='Component Name')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        actobj = context.active_object
        world = context.scene.world
        comp = world.parcomp_components[actobj.parcomp_component_name]
        newcomp = world.parcomp_components.add()
        newcomp.name = self.name
        params = comp.get('params')
        if params:
            newcomp['params'] = params.copy()
        objs = comp.get('objs')
        if objs:
            newcomp['objs'] = objs.copy()
        world.parcomp_nextcompnum += 1
        comptype = comp.types[actobj.parcomp_component_type]
        bpy.data.collections[comptype.collname].objects.unlink(actobj)
        actobj.name = newcomp.name
        actobj['parcomp_component_name_skip'] = True
        actobj.parcomp_component_name = newcomp.name
        actobj.parcomp_component_name_sel = newcomp.name
        comptype = newcomp.types.add()
        comptype.name = 'Type.0'
        newcomp.nexttypenum = 1
        actobj['parcomp_component_type_skip'] = True
        actobj.parcomp_component_type = comptype.name
        actobj.parcomp_component_type_sel = comptype.name
        coll = bpy.data.collections.new('coll')
        comptype.collname = coll.name
        coll.objects.link(actobj)
        return {'FINISHED'}

    def invoke(self, context, event):
        world = context.scene.world
        self.name = 'Comp.%d' % (world.parcomp_nextcompnum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_comptype_save(bpy.types.Operator):
    bl_idname = "object.parcomp_comptype_save"
    bl_label = "Save As New Type"

    name: bpy.props.StringProperty(name='Component Type')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        actobj = context.active_object
        comp = context.scene.world.parcomp_components[actobj.parcomp_component_name]
        comptype = comp.types[actobj.parcomp_component_type]
        bpy.data.collections[comptype.collname].objects.unlink(actobj)
        comptype = comp.types.add()
        comptype.name = self.name
        comp.nexttypenum += 1
        actobj['parcomp_component_type_skip'] = True
        actobj.parcomp_component_type = comptype.name
        actobj.parcomp_component_type_sel = comptype.name
        coll = bpy.data.collections.new('coll')
        comptype.collname = coll.name
        coll.objects.link(actobj)
        return {'FINISHED'}

    def invoke(self, context, event):
        comp = context.scene.world.parcomp_components[context.active_object.parcomp_component_name]
        self.name = 'Type.%d' % (comp.nexttypenum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_duplicate_component(bpy.types.Operator):
    bl_idname = "object.parcomp_duplicate_component"
    bl_label = "Duplicate Component"

    name: bpy.props.StringProperty(name='Component Name')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        obj = context.active_object
        bpy.ops.object.parcomp_component_add(comp=obj.parcomp_component_name, comptype=obj.parcomp_component_type)
        bpy.ops.object.parcomp_component_save(name=self.name)
        return {'FINISHED'}

    def invoke(self, context, event):
        world = context.scene.world
        self.name = 'Comp.%d' % (world.parcomp_nextcompnum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_duplicate_comptype(bpy.types.Operator):
    bl_idname = "object.parcomp_duplicate_comptype"
    bl_label = "Duplicate Type"

    name: bpy.props.StringProperty(name='Component Type')

    def execute(self, context):
        if not self.name:
            return {'CANCELLED'}
        obj = context.active_object
        bpy.ops.object.parcomp_component_add(comp=obj.parcomp_component_name, comptype=obj.parcomp_component_type)
        bpy.ops.object.parcomp_comptype_save(name=self.name)
        return {'FINISHED'}

    def invoke(self, context, event):
        comp = context.scene.world.parcomp_components[context.active_object.parcomp_component_name]
        self.name = 'Type.%d' % (comp.nexttypenum,)
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_component_addparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_addparam"
    bl_label = "Add Parameter"

    def execute(self, context):
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params.add()
        return {'FINISHED'}


class OBJECT_OT_parcomp_component_delparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_delparam"
    bl_label = "Remove Parameter"

    index: bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        comp.params.remove(idx)
        return {'FINISHED'}


class OBJECT_OT_parcomp_component_editparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_editparam"
    bl_label = "Edit Parameter"

    index: bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})
    name: bpy.props.StringProperty(name='Parameter Name')
    ptype:  bpy.props.EnumProperty(name='Parameter Type', items=parcomp_param_type_items)
    group: bpy.props.StringProperty(name='Parameter Group')

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params[idx]
        param.name = self.name
        param.ptype = self.ptype
        param.group = self.group
        for win in context.window_manager.windows:
            for area in win.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        idx = self.index
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params[idx]
        self.name = param.name
        self.ptype = param.ptype
        self.group = param.group
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_parcomp_component_assignparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_assignparam"
    bl_label = "Assign Parameter"

    index: bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params[idx]
        param.assigned_props.add()
        return {'FINISHED'}


class OBJECT_OT_parcomp_component_unassignparam(bpy.types.Operator):
    bl_idname = "object.parcomp_component_unassignparam"
    bl_label = "Remove Parameter Assignment"

    index: bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})
    propindex: bpy.props.IntProperty(name='Property Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        pidx = self.propindex
        if (idx < 0) or (pidx < 0):
            return {'CANCELLED'}
        obj = context.active_object
        comp = context.scene.world.parcomp_components[obj.parcomp_component_name]
        param = comp.params[idx]
        param.assigned_props.remove(pidx)
        return {'FINISHED'}


class WORLD_PT_parcomp_components(bpy.types.Panel):
    bl_idname = "WORLD_PT_parcomp_components"
    bl_label = "Components"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    #@classmethod
    #def poll(cls, context):
    #    return True

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        actobj = context.active_object
        layout.prop(world, 'parcomp_mode', expand=True)
        editmode = (parcomp_modes[world.get('parcomp_mode') or 0][0] == 'EDIT')
        if editmode:
            layout.operator('object.parcomp_component_create')
            if (actobj is None) or (not actobj.get('parcomp_is_parametric')):
                return
            layout.operator('object.parcomp_duplicate_component')
            layout.operator('object.parcomp_duplicate_comptype')
            row = layout.row(align=True)
            row.prop(actobj, 'parcomp_component_name_sel', text='', icon='TRIA_DOWN', icon_only=True)
            row.prop(actobj, 'parcomp_component_name', text='')
            row = layout.row(align=True)
            row.prop(actobj, 'parcomp_component_type_sel', text='', icon='TRIA_DOWN', icon_only=True)
            row.prop(actobj, 'parcomp_component_type', text='')
            row = layout.row(align=True)
            row.operator('object.parcomp_component_addparam')
            row.operator('object.parcomp_component_addparam', text='', icon='PLUS')
            comp = world.parcomp_components[actobj.parcomp_component_name]
            for i, param in enumerate(comp.params):
                row = layout.row()
                row.column().prop(param, 'name', text='')
                row = row.column().row(align=True)
                op = row.operator('object.parcomp_component_editparam', text='Edit')
                op.index = i
                op = row.operator('object.parcomp_component_delparam', text='', icon='CANCEL')
                op.index = i
                row = layout.row(align=True)
                op = row.operator('object.parcomp_component_assignparam', text='', icon='PLUS')
                op.index = i
                for j, prop in enumerate(param.assigned_props):
                    row = layout.row(align=True)
                    row.prop(prop, 'obj', text='')
                    row.prop(prop, 'prop', text='')
                    op = row.operator('object.parcomp_component_unassignparam', text='', icon='CANCEL')
                    op.index = i
                    op.propindex = j
        else:
            row = layout.row(align=True)
            row.operator('object.parcomp_component_add')
            row.operator('object.parcomp_component_add', text='', icon='PLUS')
            if (actobj is None) or (not actobj.get('parcomp_is_parametric')):
                return
            layout.prop(actobj, 'parcomp_component_name_sel', text='')
            layout.prop(actobj, 'parcomp_component_type_sel', text='')
            #layout.template_ID(context.scene.objects, 'parcomp_test') # TODO
            comp = context.scene.world.parcomp_components[actobj.parcomp_component_name]
            for param in comp.params:
                pname = param.get('name')
                if not pname:
                    continue
                layout.prop(param, 'value_%s' % (param.ptype,), text=pname)


def parcomp_comp_name_select(self, context):
    obj = context.active_object
    compname = parcomp_comp_name_items(self, context)[obj['parcomp_component_name_sel']][1]
    if obj.parcomp_component_name == compname:
        return
    bpy.ops.object.select_more()
    obj.select_set(True)
    loc = tuple(obj.location)
    rot = tuple(obj.rotation_euler)
    bpy.ops.object.delete() # use_global=False/True
    children = []
    comp = context.scene.world.parcomp_components[compname]
    for compobj in comp.objs:
        bpy.ops.object.add(
            type=compobj.objtype,
            location=(compobj.location_x, compobj.location_y, compobj.location_z),
            rotation=(compobj.rotation_x, compobj.rotation_y, compobj.rotation_z),
        )
        obj = context.active_object
        obj.dimensions = (compobj.dimension_x, compobj.dimension_y, compobj.dimension_z)
        if obj.type == 'MESH':
            obj.data = bpy.data.meshes[compobj.objdata]
        children.append(obj)
    bpy.ops.object.empty_add(
        type='PLAIN_AXES',
        view_align=False,
        location=tuple(children[-1].location),
        rotation=(0, 0, 0),
        #layers=current_layers,
    )
    actobj = context.active_object
    actobj['parcomp_is_parametric'] = True
    for obj in children:
        obj.select_set(True)
    actobj.select_set(False)
    actobj.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT')
    actobj.location = loc
    actobj.rotation_euler = rot
    actobj['parcomp_component_name_skip'] = True
    actobj.parcomp_component_name = compname
    actobj.parcomp_component_name_sel = compname
    comptype = comp.types[0]
    actobj['parcomp_component_type_skip'] = True
    actobj.parcomp_component_type = comptype.name
    actobj.parcomp_component_type_sel = comptype.name
    bpy.data.collections[comptype.collname].objects.link(actobj)


def parcomp_comp_name_update(self, context):
    obj = context.active_object
    if obj['parcomp_component_name_skip']:
        obj['parcomp_component_name_skip'] = False
        return
    scene = context.scene
    compname = parcomp_comp_name_items(self, context)[obj['parcomp_component_name_sel']][1]
    scene.world.parcomp_components[compname].name = obj.parcomp_component_name
    obj.name = obj.parcomp_component_name


def parcomp_comp_type_select(self, context):
    obj = context.active_object
    compname = parcomp_comp_name_items(self, context)[obj['parcomp_component_name_sel']][1]
    comptype = parcomp_comp_type_items(self, context)[obj['parcomp_component_type_sel']][1]
    if obj.parcomp_component_type == comptype:
        return
    bpy.ops.object.select_more()
    obj.select_set(True)
    loc = tuple(obj.location)
    bpy.ops.object.delete() # use_global=False/True
    comp = context.scene.world.parcomp_components[compname]
    obj = bpy.data.collections[comp.types[comptype].collname].objects[0]
    obj.select_set(True)
    bpy.ops.object.select_more()
    obj.select_set(True)
    bpy.ops.object.duplicate_move_linked()
    obj = context.active_object
    obj.location = loc


def parcomp_comp_type_update(self, context):
    obj = context.active_object
    if obj['parcomp_component_type_skip']:
        obj['parcomp_component_type_skip'] = False
        return
    scene = context.scene
    compname = parcomp_comp_name_items(self, context)[obj['parcomp_component_name_sel']][1]
    comptype = parcomp_comp_type_items(self, context)[obj['parcomp_component_type_sel']][1]
    scene.world.parcomp_components[compname].types[comptype].name = obj.parcomp_component_type


parcomp_modes = [
    ('OBJECT', 'Object', '', 0),
    ('EDIT'  , 'Edit'  , '', 1),
]


class VIEW3D_OT_parcomp_component_select(bpy.types.Operator):
    bl_idname = 'view3d.parcomp_component_select'
    bl_label = 'Select Component'

    x: bpy.props.IntProperty()
    y: bpy.props.IntProperty()

    def execute(self, context):
        bpy.ops.view3d.select(location=(self.x, self.y))
        if not context.active_object:
            return {'FINISHED'}
        if context.mode != 'OBJECT':
            return {'FINISHED'}
        editmode = (parcomp_modes[bpy.context.scene.world.get('parcomp_mode') or 0][0] == 'EDIT')
        if editmode:
            return {'FINISHED'}
        bpy.ops.object.select_hierarchy()
        bpy.ops.object.select_more()
        return {'FINISHED'}

    def invoke(self, context, event):
        self.x = event.mouse_region_x
        self.y = event.mouse_region_y
        return self.execute(context)


addon_keymaps = []


def register():
    bpy.utils.register_class(parcomp_ObjectProperty)
    bpy.utils.register_class(parcomp_Parameter)
    bpy.utils.register_class(parcomp_ComponentType)
    bpy.utils.register_class(parcomp_ComponentObject)
    bpy.utils.register_class(parcomp_Component)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_create)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_add)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_save)
    bpy.utils.register_class(OBJECT_OT_parcomp_comptype_save)
    bpy.utils.register_class(OBJECT_OT_parcomp_duplicate_component)
    bpy.utils.register_class(OBJECT_OT_parcomp_duplicate_comptype)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_addparam)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_delparam)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_editparam)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_assignparam)
    bpy.utils.register_class(OBJECT_OT_parcomp_component_unassignparam)
    bpy.utils.register_class(WORLD_PT_parcomp_components)
    bpy.utils.register_class(VIEW3D_OT_parcomp_component_select)
    bpy.types.World.parcomp_components = bpy.props.CollectionProperty(type=parcomp_Component)
    bpy.types.World.parcomp_nextcompnum = bpy.props.IntProperty(name='Next Component Number')
    bpy.types.World.parcomp_mode = bpy.props.EnumProperty(name='Mode', items=parcomp_modes)
    bpy.types.Object.parcomp_is_parametric = bpy.props.BoolProperty(name='Is Parametric')
    bpy.types.Object.parcomp_component_name_skip = bpy.props.BoolProperty(name='Skip Name Update')
    bpy.types.Object.parcomp_component_name = bpy.props.StringProperty(name='Component Name', update=parcomp_comp_name_update)
    bpy.types.Object.parcomp_component_name_sel = bpy.props.EnumProperty(name='Component Name', items=parcomp_comp_name_items, update=parcomp_comp_name_select)
    bpy.types.Object.parcomp_component_type_skip = bpy.props.BoolProperty(name='Skip Type Update')
    bpy.types.Object.parcomp_component_type = bpy.props.StringProperty(name='Type', update=parcomp_comp_type_update)
    bpy.types.Object.parcomp_component_type_sel = bpy.props.EnumProperty(name='Type', items=parcomp_comp_type_items, update=parcomp_comp_type_select)
    kc = bpy.context.window_manager.keyconfigs
    if kc:
        #km = kc.addon.keymaps.new(name='Component Select', space_type='VIEW_3D')
        km = kc.default.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(VIEW3D_OT_parcomp_component_select.bl_idname, 'LEFTMOUSE', 'PRESS', head=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(parcomp_ObjectProperty)
    bpy.utils.unregister_class(parcomp_Parameter)
    bpy.utils.unregister_class(parcomp_ComponentType)
    bpy.utils.unregister_class(parcomp_ComponentObject)
    bpy.utils.unregister_class(parcomp_Component)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_create)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_add)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_save)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_comptype_save)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_duplicate_component)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_duplicate_comptype)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_addparam)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_delparam)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_editparam)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_assignparam)
    bpy.utils.unregister_class(OBJECT_OT_parcomp_component_unassignparam)
    bpy.utils.unregister_class(WORLD_PT_parcomp_components)
    bpy.utils.unregister_class(VIEW3D_OT_parcomp_component_select)


if __name__ == "__main__":
    register()
