
# imports
import bpy
import re
from bpy.types import Panel
from .. import storage
from . import icon

# addon
addon = bpy.context.user_preferences.addons.get(__name__.partition('.')[0])

# tools name
class toolsName(Panel):
    '''
        Name panel.
    '''
    bl_idname = 'VIEW3D_PT_TOOLS_name'
    bl_space_type = 'VIEW_3D'
    bl_label = 'Name'
    bl_region_type = 'TOOLS'
    bl_category = 'Name'

    # draw
    def draw(self, context):
        '''
            Name panel body.
        '''

        # main
        main(self, context)

# UI name
class UIName(Panel):
    '''
        Name panel.
    '''
    bl_idname = 'VIEW3D_PT_UI_name'
    bl_space_type = 'VIEW_3D'
    bl_label = 'Name'
    bl_region_type = 'UI'

    # draw
    def draw(self, context):
        '''
            Name panel body.
        '''

        # main
        main(self, context)

# main
def main(self, context):
    '''
        Name panel main.
    '''

    # layout
    layout = self.layout

    # panel
    panel = context.scene.NamePanel

    # column
    column = layout.column(align=True)

    # filter
    filters(self, context, column, panel)

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # is mode selected
    if panel.mode == 'SELECTED':

        # member
        member = gather(context, {object.name: [] for object in context.selected_objects}) if panel.search != '' else {}

    # isnt mode selected
    else:

        # member
        member = gather(context, {object.name: [] for object in context.scene.objects if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]}) if panel.search != '' else {}

    # is pin active object
    if panel.pinActiveObject:

        # is active object
        if context.active_object:

            # datablock
            datablock = context.active_object

            # is search
            if search == '' or re.search(search, datablock.name, re.I) or [re.search(search, item, re.I) for item in member[datablock.name] if re.search(search, item, re.I) != None]:

                # populate
                populate(self, context, layout, datablock, panel)

        # is display names
        if panel.displayNames:

            # is mode selected
            if panel.mode == 'SELECTED':

                # objects
                objects = [[object.name, object] for object in context.selected_objects]

                # sorted
                for datablock in sorted(objects):

                    # isnt active object
                    if datablock[1] != context.active_object:

                        # is search
                        if search == '' or re.search(search, datablock[1].name, re.I) or [re.search(search, item, re.I) for item in member[datablock[1].name] if re.search(search, item, re.I) != None]:

                            # populate
                            populate(self, context, layout, datablock[1], panel)

            # isnt mode selected
            else:

                # objects
                objects = [[object.name, object] for object in context.scene.objects if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]]

                # sorted
                for datablock in sorted(objects):

                    # isnt active object
                    if datablock[1] != context.active_object:

                        # local
                        local = False

                        # for area
                        for area in context.screen.areas:

                            # isnt view 3d
                            if area.type == 'VIEW_3D':

                                # is local view
                                if area.spaces.active.local_view:

                                    # local
                                    local = True

                        # is local
                        if local:

                            # is layers local
                            if True in datablock[1].layers_local_view[:]:

                                # datablock
                                datablock = datablock[1]

                            # isnt layers local
                            else:

                                # datablock
                                datablock = None

                        # isnt local
                        else:

                            # datablock
                            datablock = datablock[1]

                        # is datablock
                        if datablock:

                            # is search
                            if search == '' or re.search(search, datablock.name, re.I) or [re.search(search, item, re.I) for item in member[datablock.name] if re.search(search, item, re.I) != None]:

                                # populate
                                populate(self, context, layout, datablock, panel)

    # isnt pin active object
    else:

        # is display names
        if panel.displayNames:

            # is mode selected
            if panel.mode == 'SELECTED':

                # objects
                objects = [[object.name, object] for object in context.selected_objects]

                # for sorted datablock
                for datablock in sorted(objects):

                    # is search
                    if search == '' or re.search(search, datablock[1].name, re.I) or [re.search(search, item, re.I) for item in member[datablock[1].name] if re.search(search, item, re.I) != None]:

                        # populate
                        populate(self, context, layout, datablock[1], panel)

            # isnt mode selected
            else:

                # objects
                objects = [[object.name, object] for object in context.scene.objects if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]]

                # for sorted datablock
                for datablock in sorted(objects):

                    # local
                    local = False

                    # for area
                    for area in context.screen.areas:

                        # is view 3d
                        if area.type == 'VIEW_3D':

                            # is local view
                            if area.spaces.active.local_view:

                                # local
                                local = True

                    # is local
                    if local:

                        # is layers local
                        if True in datablock[1].layers_local_view[:]:

                            # datablock
                            datablock = datablock[1]

                        # isnt layers local
                        else:

                            # datablock
                            datablock = None

                    # isnt local
                    else:

                        # datablock
                        datablock = datablock[1]

                    # is datablock
                    if datablock:

                        # search
                        if search == '' or re.search(search, datablock.name, re.I) or [re.search(search, item, re.I) for item in member[datablock.name] if re.search(search, item, re.I) != None]:

                            # populate
                            populate(self, context, layout, datablock, panel)

        # isnt display names
        else:

            # is search
            if search == '' or re.search(search, context.active_object.name, re.I) or [re.search(search, item, re.I) for item in member[context.active_object.name] if re.search(search, item, re.I) != None]:

                # populate
                populate(self, context, layout, context.active_object, panel)

# filters
def filters(self, context, layout, panel):
    '''
        The name panel filters
    '''

    # row
    row = layout.row(align=True)

    # scale y
    row.scale_y = 1.25

    # icon toggle
    iconToggle = 'RADIOBUT_ON' if panel.filters else 'RADIOBUT_OFF'

    # filters
    row.prop(panel, 'filters', text='Filters', icon=iconToggle, toggle=True)

    # shortcuts
    row.prop(panel, 'shortcuts', text='', icon='SETTINGS')

    # menu; name panel specials
    row.menu('VIEW3D_MT_name_panel_specials', text='', icon='COLLAPSEMENU')

    # is filters
    if panel.filters:

        # separate
        layout.separator()

        # row
        row = layout.row(align=True)

        # scale x
        row.scale_x = 5 # hack: forces buttons to line up correctly

        # groups
        row.prop(panel, 'groups', text='', icon='GROUP')

        # grease pencil
        row.prop(panel, 'greasePencil', text='', icon='GREASEPENCIL')

        # action
        row.prop(panel, 'action', text='', icon='ACTION')

        # constraints
        row.prop(panel, 'constraints', text='', icon='CONSTRAINT')

        # modifiers
        row.prop(panel, 'modifiers', text='', icon='MODIFIER')

        # bone groups
        row.prop(panel, 'boneGroups', text='', icon='GROUP_BONE')

        # bone constraints
        row.prop(panel, 'boneConstraints', text='', icon='CONSTRAINT_BONE')

        # row
        row = layout.row(align=True)

        # scale x
        row.scale_x = 5 # hack: forces buttons to line up correctly

        # vertex groups
        row.prop(panel, 'vertexGroups', text='', icon='GROUP_VERTEX')

        # shapekeys
        row.prop(panel, 'shapekeys', text='', icon='SHAPEKEY_DATA')

        # uvs
        row.prop(panel, 'uvs', text='', icon='GROUP_UVS')

        # vertex colors
        row.prop(panel, 'vertexColors', text='', icon='GROUP_VCOL')

        # materials
        row.prop(panel, 'materials', text='', icon='MATERIAL')

        # textures
        row.prop(panel, 'textures', text='', icon='TEXTURE')

        # particles systems
        row.prop(panel, 'particleSystems', text='', icon='PARTICLES')

    # isnt hide find
    if not panel.hideFind:

        if panel.filters or not panel.hideReplace:

            # separate
            layout.separator()

        # row
        row = layout.row(align=True)

        # find
        row.prop(panel, 'search', text='', icon='VIEWZOOM')


        # sub
        sub = row.split(align=True)

        # scale x
        sub.scale_x = 0.1

        # regex
        sub.prop(panel, 'regex', text='.*', toggle=True)

        # hide replace
        if panel.hideReplace:

            # operator; batch name
            op = row.operator('wm.batch_name', text='', icon='SORTALPHA')
            op.simple = False
            op.quickBatch = True

        else:

            # row
            row = layout.row(align=True)

            # replace
            row.prop(context.window_manager.BatchName, 'replace', text='', icon='FILE_REFRESH')

            # sub
            sub = row.split(align=True)

            # scale x
            sub.scale_x = 0.15

            # operator; batch name
            op = sub.operator('wm.batch_name', text='OK')
            op.simple = True
            op.quickBatch = True

            # operator; batch name
            op = row.operator('wm.batch_name', text='', icon='SORTALPHA')
            op.simple = False
            op.quickBatch = True

    # is dispay names
    if panel.displayNames:

        # separate
        layout.separator()

        # row
        row = layout.row()

        # mode
        row.prop(panel, 'mode', expand=True)

# gather
def gather(context, member):
    '''
        Creates a object datablock dictionary for name panel.
    '''

    # panel
    panel = context.scene.NamePanel

    # is member
    if member:

        # is display names
        if panel.displayNames:

            # is mode selected
            if panel.mode == 'SELECTED':

                # for object
                for object in context.selected_objects:

                    # sort
                    sort(context, member, object)

            # isnt mode selected
            else:

                # for object
                for object in context.scene.objects:

                    # is layer
                    if True in [x&y for (x,y) in zip(object.layers, context.scene.layers)]:

                        # sort
                        sort(context, member, object)

        # isnt display names
        else:

            # sort
            sort(context, member, context.active_object)

    # member
    return member

# sort
def sort(context, member, object):
    '''
        Sorts object related datablocks for search panel population.
    '''

    # panel
    panel = context.scene.NamePanel

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # is group
    if panel.groups:

        # for group
        for group in bpy.data.groups:

            # for group object
            for groupobject in group.objects:

                # is object group
                if groupobject == object:

                    # is search
                    if search == '' or re.search(search, group.name, re.I):

                        # member
                        member[object.name].append(group.name)

    # is grease pencil
    if panel.greasePencil:

        # has name
        if hasattr(object.grease_pencil, 'name'):

            # layers
            layers = [layer.info for layer in bpy.data.objects[object.name].grease_pencil.layers]

            # is search
            if search == '' or re.search(search, object.grease_pencil.name, re.I) or [re.search(search, item, re.I) for item in layers if re.search(search, item, re.I) != None]:

                # member append
                member[object.name].append(object.grease_pencil.name)

                # for layer
                for layer in bpy.data.objects[object.name].grease_pencil.layers:

                    # is search
                    if search == '' or re.search(search, layer.info, re.I):

                        # member append
                        member[object.name].append(layer.info)

    # is action
    if panel.action:

        # has action
        if hasattr(object.animation_data, 'action'):

            # has name
            if hasattr(object.animation_data.action, 'name'):

                # is search
                if search == '' or re.search(search, object.animation_data.action.name, re.I):

                    # member append
                    member[object.name].append(object.animation_data.action.name)

    # is constraints
    if panel.constraints:

        # for constraint
        for constraint in object.constraints:

            # is search
            if search == '' or re.search(search, constraint.name, re.I):

                # member append
                member[object.name].append(constraint.name)

    # is modifiers
    if panel.modifiers:

        # for modifier
        for modifier in object.modifiers:

            # is type particle system
            if modifier.type == 'PARTICLE_SYSTEM':

                # particle
                particle = [modifier.particle_system.name, modifier.particle_system.settings.name]

                # texture
                texture = [slot.texture.name for slot in modifier.particle_system.settings.texture_slots if slot != None]

            # is type displace or warp
            elif modifier.type in {'DISPLACE', 'WARP'}:

                # is texture
                if modifier.texture:

                    # texture
                    texture = [modifier.texture.name]

            # is type vertex weight mix or vertex weight edit or vertex weight proximity
            elif modifier.type in {'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_PROXIMITY'}:

                # is mask texture
                if modifier.mask_texture:

                    # texture
                    texture = [modifier.mask_texture.name]

            # isnt type particle system or displace or warp or vertex weight mix or vertex weight edit or vertex weight proximity
            else:

                # particle
                particle = []

                # texture:
                texture = []

            # is search
            if search == '' or re.search(search, modifier.name, re.I) or [re.search(search, item, re.I) for item in particle if re.search(search, item, re.I) != None] or [re.search(search, item, re.I) for item in texture if re.search(search, item, re.I) != None]:

                # member append
                member[object.name].append(modifier.name)

                # is particle systems
                if panel.particleSystems:

                    # is type particle system
                    if modifier.type in 'PARTICLE_SYSTEM':

                        # is search
                        if search == '' or re.search(search, particle[0], re.I) or re.search(search, particle[1], re.I) or [re.search(search, item, re.I) for item in texture if re.search(search, item, re.I) != None]:

                            # member append
                            member[object.name].append(modifier.particle_system.name)

                            # is search
                            if search == '' or re.search(search, modifier.particle_system.settings.name, re.I) or [re.search(search, item, re.I) for item in texture if re.search(search, item, re.I) != None]:

                                # member append
                                member[object.name].append(modifier.particle_system.settings.name)

                                # for slot
                                for slot in modifier.particle_system.settings.texture_slots:

                                    # isnt none
                                    if slot != None:

                                        # search
                                        if search == '' or re.search(search, slot.texture.name, re.I):

                                            # member append
                                            member[object.name].append(slot.texture.name)

    # is materials
    if panel.materials:

        # for slot
        for slot in object.material_slots:

            # isnt none
            if slot.material != None:

                # textures
                textures = [tslot.texture.name for tslot in slot.material.texture_slots if hasattr(tslot, 'texture')]

                # is search
                if search == '' or re.search(search, slot.material.name, re.I) or [re.search(search, item, re.I) for item in textures if re.search(search, item, re.I) != None]:

                    # member append
                    member[object.name].append(slot.material.name)

                    # is textures
                    if panel.textures:

                        # is blender render or blender game
                        if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:

                            # for tslot
                            for tslot in slot.material.texture_slots:

                                # has texture
                                if hasattr(tslot, 'texture'):

                                    # isnt none
                                    if tslot.texture != None:

                                        # is search
                                        if search == '' or re.search(search, tslot.texture.name, re.I):

                                            # member append
                                            member[object.name].append(tslot.texture.name)

    # isnt empty
    if object.type != 'EMPTY':

        # is search
        if search == '' or re.search(search, object.data.name, re.I):

            # member append
            member[object.name].append(object.data.name)

    # is vertex groups
    if panel.vertexGroups:

        # has vertex group
        if hasattr(object, 'vertex_groups'):

            # for group
            for group in object.vertex_groups:

                # is search
                if search == '' or re.search(search, group.name, re.I):

                    # member append
                    member[object.name].append(group.name)

    # is shapekeys
    if panel.shapekeys:

        # has shape keys
        if hasattr(object.data, 'shape_keys'):

            # has key blocks
            if hasattr(object.data.shape_keys, 'key_blocks'):

                # for key
                for key in object.data.shape_keys.key_blocks:

                    # is search
                    if search == '' or re.search(search, key.name, re.I):

                        # member append
                        member[object.name].append(key.name)

    # is uvs
    if panel.uvs:

        # is type mesh
        if object.type in 'MESH':

            # for uv
            for uv in object.data.uv_textures:

                # search
                if search == '' or re.search(search, uv.name, re.I):

                    # member append
                    member[object.name].append(uv.name)

    # is vertex colors
    if panel.vertexColors:

        # is type mesh
        if object.type in 'MESH':

            # for vertexColor
            for vertexColor in object.data.vertex_colors:

                # is search
                if search == '' or re.search(search, vertexColor.name, re.I):

                    # member append
                    member[object.name].append(vertexColor.name)

    # is bone groups
    if panel.boneGroups:

        # is type armature
        if object.type in 'ARMATURE':

            # for group
            for group in object.pose.bone_groups:

                # is search
                if search == '' or re.search(search, group.name, re.I):

                    # member append
                    member[object.name].append(group.name)

    # is active object
    if object == context.active_object:

        # is type armature
        if object.type in 'ARMATURE':

            # is mode in pose or edit
            if object.mode in {'POSE', 'EDIT'}:

                # constraints
                try: constraints = [item.name for item in context.active_pose_bone.constraints]
                except: constraints = []

                # is search
                if search == '' or re.search(search, context.active_bone.name, re.I) or [re.search(search, item, re.I) for item in constraints if re.search(search, item, re.I) != None]:

                    # member append
                    member[object.name].append(context.active_bone.name)

                # is bone constraints
                if panel.boneConstraints:

                    # is mode pose
                    if object.mode in 'POSE':

                        # for constraint
                        for constraint in context.active_pose_bone.constraints:

                            # is search
                            if search == '' or re.search(search, constraint.name, re.I):

                                # member append
                                member[object.name].append(constraint.name)

                # is display bones
                if panel.displayBones:

                    # is mode pose
                    if object.mode in 'POSE':

                        # bones
                        bones = object.pose.bones

                    # is mode edit
                    elif object.mode == 'EDIT':

                        # bones
                        bones = object.data.edit_bones

                    # isnt mode pose
                    else:

                        # bones
                        bones = object.data.bones

                    # for bone
                    for bone in bones:

                        # isnt active bone
                        if bone != context.active_bone:

                            # constraints
                            try: constraints = [constraint.name for constraint in object.pose.bones[bone.name].constraints[:]]
                            except: constraints = []

                            # is search
                            if search == '' or re.search(search, bone.name, re.I) or [re.search(search, item, re.I) for item in constraints if re.search(search, item, re.I) != None]:

                                # member append
                                member[object.name].append(bone.name)

                            # is bone constraints
                            if panel.boneConstraints:

                                # is mode pose
                                if object.mode in 'POSE':

                                    # for constraint
                                    for constraint in bone.constraints:

                                        # is search
                                        if search == '' or re.search(search, constraint.name, re.I):

                                            # member append
                                            member[object.name].append(constraint.name)

    # member
    return member

# populate
def populate(self, context, layout, object, panel):
    '''
        Populates the name panel with datablock names.
    '''

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # is object
    if object:

        # column
        column = layout.column()

        # object
        Object(self, context, column, object, panel)

        # group
        block.object.group(self, context, column, object, panel)

        # grease pencil
        block.object.greasePencil(self, context, column, object, panel)

        # action
        block.object.action(self, context, column, object, panel)

        # constraint
        block.object.constraint(self, context, column, object, panel)

        # modifier
        block.object.modifier(self, context, column, object, panel)

        # material
        block.object.material(self, context, column, object, panel)

        # object data
        ObjectData(self, context, column, object, panel)

        # vertex group
        block.objectData.vertexGroup(self, context, column, object, panel)

        # shapekey
        block.objectData.shapekey(self, context, column, object, panel)

        # uv
        block.objectData.uv(self, context, column, object, panel)

        # vertex color
        block.objectData.vertexColor(self, context, column, object, panel)

        # material
        block.objectData.material(self, context, column, object, panel)

        # bone group
        block.objectData.boneGroup(self, context, column, object, panel)

        # row
        row = column.row()

        # separate
        row.separator()

        # is active object
        if object == context.active_object and context.active_bone:

            # bone
            block.bone(self, context, column, object, panel)

# block
class block:
    '''
        contains classes;
            object
            objectData

        contains functions;
            bone
            material
    '''

    # object
    class object:
        '''
            contains functions;
                group
                action
                greasepencil
                constraint
                modifier
                material
        '''

        # group
        def group(self, context, layout, object, panel):
            '''
                group related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is groups
            if panel.groups:

                # is shortcuts and not search
                if panel.shortcuts and not panel.search:

                    # row
                    row = layout.row(align=True)

                    # context pointer set
                    row.context_pointer_set('object', object)

                    # sub
                    sub = row.row()

                    # scale x
                    sub.scale_x = 1.6

                    # label
                    sub.label(icon='GROUP')

                    # is groups
                    if bpy.data.groups:

                        # group link
                        row.operator('object.group_link', text='Add to Group')

                        # group add
                        row.operator('object.group_add', text='', icon='ZOOMIN')

                    # isnt groups
                    else:

                        # group add
                        row.operator('object.group_add', text='Add Group')

                # for group
                for group in bpy.data.groups:

                    # for group object
                    for groupObject in group.objects:

                        # is object group
                        if groupObject == object:

                            # is search
                            if search == '' or re.search(search, group.name, re.I):

                                # group
                                Group(self, context, layout, group, object, panel)

        # greasePencil
        def greasePencil(self, context, layout, object, panel):
            '''
                grease pencil related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is grease pencil
            if panel.greasePencil:

                # has name
                if hasattr(object.grease_pencil, 'name'):

                    # layers
                    layers = [layer.info for layer in bpy.data.objects[object.name].grease_pencil.layers]

                    # is search
                    if search == '' or re.search(search, object.grease_pencil.name, re.I) or [re.search(search, item, re.I) for item in layers if re.search(search, item, re.I) != None]:

                        # grease pencil
                        GreasePencil(self, context, layout, object.grease_pencil, object, panel)

                        # for layer
                        for layer in bpy.data.objects[object.name].grease_pencil.layers:

                            # is search
                            if search == '' or re.search(search, layer.info, re.I):

                                # pencil layer
                                PencilLayer(self, context, layout, object.grease_pencil, layer, object, panel)

        # action
        def action(self, context, layout, object, panel):
            '''
                action related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is action
            if panel.action:

                # has action
                if hasattr(object.animation_data, 'action'):

                    # has name
                    if hasattr(object.animation_data.action, 'name'):

                        # is search
                        if search == '' or re.search(search, object.animation_data.action.name, re.I):

                            # action
                            Action(self, context, layout, object.animation_data.action, object, panel)

        # constraint
        def constraint(self, context, layout, object, panel):
            '''
                Constraint related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is constraints
            if panel.constraints:

                # is shortcuts and not search
                if panel.shortcuts and not panel.search:

                    # row
                    row = layout.row(align=True)

                    # context pointer set
                    row.context_pointer_set('object', object)

                    # sub
                    sub = row.row()

                    # scale x
                    sub.scale_x = 1.6

                    # label
                    sub.label(icon='CONSTRAINT')

                    # operator menu enum
                    row.operator_menu_enum('object.constraint_add', 'type', text='Add Constraint')

                # for constraint
                for constraint in object.constraints:

                    # is search
                    if search == '' or re.search(search, constraint.name, re.I):

                        # constraint
                        Constraint(self, context, layout, constraint, object, None, panel)

        # modifier
        def modifier(self, context, layout, object, panel):
            '''
                Modifier related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is modifiers
            if panel.modifiers:

                # is shortcuts and not search
                if panel.shortcuts and not panel.search and object.type in {'CURVE', 'SURFACE', 'MESH', 'LATTICE'}:

                    # row
                    row = layout.row(align=True)

                    # context pointer set
                    row.context_pointer_set('object', object)

                    # sub
                    sub = row.row()

                    # scale x
                    sub.scale_x = 1.6

                    # label
                    sub.label(icon='MODIFIER')

                    # operator menu enum
                    row.operator_menu_enum('object.modifier_add', 'type', text='Add Modifier')

                # for modifier
                for modifier in object.modifiers:

                    # particle
                    particle = []

                    # texture:
                    texture = []

                    # is type particle system
                    if modifier.type == 'PARTICLE_SYSTEM':

                        # particle
                        particle = [modifier.particle_system.name, modifier.particle_system.settings.name]

                        # texture
                        texture = [slot.texture.name for slot in modifier.particle_system.settings.texture_slots if slot != None]

                    # is type displace or warp
                    if modifier.type in {'DISPLACE', 'WARP'}:

                        # is texture
                        if modifier.texture:

                            # texture
                            texture = [modifier.texture.name]

                    # is type vertex weight mix or vertex weight edit or vertex weight proximity
                    if modifier.type in {'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_PROXIMITY'}:

                        # is mask texture
                        if modifier.mask_texture:

                            # texture
                            texture = [modifier.mask_texture.name]

                    # member
                    member = particle + texture

                    # is search
                    if search == '' or re.search(search, modifier.name, re.I) or [re.search(search, item, re.I) for item in member if re.search(search, item, re.I) != None]:

                        # modifier
                        Modifier(self, context, layout, modifier, object, panel)

                        # is texture
                        if panel.textures:

                            # is tyoe displace warp
                            if modifier.type in {'DISPLACE', 'WARP'}:

                                # is texture
                                if modifier.texture:

                                    # is search
                                    if search == '' or re.search(search, modifier.texture.name, re.I):

                                        # texture
                                        Texture(self, context, layout, modifier, object, panel)

                            # is type vertex weight mix or vertex weight edit or vertex weight proximity
                            elif modifier.type in {'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_PROXIMITY'}:

                                # is mask texture
                                if modifier.mask_texture:

                                    # is search
                                    if search == '' or re.search(search, modifier.mask_texture.name, re.I):

                                        # mask texture
                                        MaskTexture(self, context, layout, modifier, object, panel)

                        # is particle systems
                        if panel.particleSystems:

                            # is type particle system
                            if modifier.type in 'PARTICLE_SYSTEM':

                                # is search
                                if search == '' or re.search(search, particle[0], re.I) or re.search(search, particle[1], re.I) or [re.search(search, item, re.I) for item in texture if re.search(search, item, re.I) != None]:

                                    # particle
                                    Particle(self, context, layout, modifier, object, panel)

                                    # is textures
                                    if panel.textures:

                                        # for slot
                                        for slot in modifier.particle_system.settings.texture_slots:

                                            # has texture
                                            if hasattr(slot, 'texture'):

                                                # is texture
                                                if slot.texture:

                                                    # is search
                                                    if search == '' or re.search(search, slot.texture.name, re.I):

                                                        # texture
                                                        Texture(self, context, layout, slot, object, panel)

            # isnt modifiers
            else:

                # is particle system
                if context.scene.NamePanel.particleSystems != 0:

                    # particle systems
                    context.scene['NamePanel']['particleSystems'] = 0

        # material
        def material(self, context, layout, object, panel):
            '''
                Material related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is materials
            if panel.materials:

                # for slot
                for slot in object.material_slots:

                    # is link object
                    if slot.link == 'OBJECT':

                        # isnt none
                        if slot.material != None:

                            # textures
                            textures = [tslot.texture.name for tslot in slot.material.texture_slots if hasattr(tslot, 'texture')]

                            # is search
                            if search == '' or re.search(search, slot.material.name, re.I) or [re.search(search, item, re.I) for item in textures if re.search(search, item, re.I) != None]:

                                # material
                                Material(self, context, layout, slot, object, panel)

                                # is textures
                                if panel.textures:

                                    # is engine in blender render or blender game
                                    if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:

                                        # for tslot
                                        for tslot in slot.material.texture_slots:

                                            # has texture
                                            if hasattr(tslot, 'texture'):

                                                # isnt none
                                                if tslot.texture != None:

                                                    # is search
                                                    if search == '' or re.search(search, tslot.texture.name, re.I):

                                                        # texture
                                                        Texture(self, context, layout, tslot, object, panel)

    # object data
    class objectData:
        '''
            Constains Functions;
                vertexGroup
                shapekey
                uv
                vertexColor
                material
                boneGroup
        '''

        # vertex group
        def vertexGroup(self, context, layout, object, panel):
            '''
                Vertex group related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is vertex groups
            if panel.vertexGroups:

                # is shortcuts and not search
                if panel.shortcuts and not panel.search and object.type in {'MESH', 'LATTICE'}:

                    # row
                    row = layout.row(align=True)

                    # context pointer set
                    row.context_pointer_set('object', object)

                    # sub
                    sub = row.row()

                    # scale x
                    sub.scale_x = 1.6

                    # label
                    sub.label(icon='GROUP_VERTEX')

                    # operator menu enum
                    row.operator('object.vertex_group_add', text='Add Vertex Group')

                # has vertex groups
                if hasattr(object, 'vertex_groups'):

                    # for group
                    for group in object.vertex_groups:

                        # search
                        if search == '' or re.search(search, group.name, re.I):

                            # vertex group
                            VertexGroup(self, context, layout, group, object, panel)

        # shapekey
        def shapekey(self, context, layout, object, panel):
            '''
                Shapekey related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # shapekeys
            if panel.shapekeys:

                # is shortcuts and not search
                if panel.shortcuts and not panel.search and object.type in {'CURVE', 'SURFACE', 'MESH', 'LATTICE'}:

                    # row
                    row = layout.row(align=True)

                    # context pointer set
                    row.context_pointer_set('object', object)

                    # sub
                    sub = row.row()

                    # scale x
                    sub.scale_x = 1.6

                    # label
                    sub.label(icon='SHAPEKEY_DATA')

                    # operator menu enum
                    op = row.operator('object.shape_key_add', text='Add Shapekey')
                    op.from_mix = False

                # has shape keys
                if hasattr(object.data, 'shape_keys'):

                    # has key blocks
                    if hasattr(object.data.shape_keys, 'key_blocks'):

                        # for key
                        for key in object.data.shape_keys.key_blocks:

                            # is search
                            if search == '' or re.search(search, key.name, re.I):

                                # shapekey
                                Shapekey(self, context, layout, key, object, panel)

        # uv
        def uv(self, context, layout, object, panel):
            '''
                UV related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is uvs
            if panel.uvs:

                # is type mesh
                if object.type in 'MESH':

                    # is shortcuts and not search
                    if panel.shortcuts and not panel.search:

                        # row
                        row = layout.row(align=True)

                        # context pointer set
                        row.context_pointer_set('object', object)

                        # sub
                        sub = row.row()

                        # scale x
                        sub.scale_x = 1.6

                        # label
                        sub.label(icon='GROUP_UVS')

                        # operator menu enum
                        row.operator('mesh.uv_texture_add', text='Add UV Map')

                    # for uv
                    for uv in object.data.uv_textures:

                        # is search
                        if search == '' or re.search(search, uv.name, re.I):

                            # uv
                            UV(self, context, layout, uv, object, panel)

        # vertex color
        def vertexColor(self, context, layout, object, panel):
            '''
                Vertex color related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is vertex colors
            if panel.vertexColors:

                # is type mesh
                if object.type in 'MESH':

                    # is shortcuts and not search
                    if panel.shortcuts and not panel.search:

                        # row
                        row = layout.row(align=True)

                        # context pointer set
                        row.context_pointer_set('object', object)

                        # sub
                        sub = row.row()

                        # scale x
                        sub.scale_x = 1.6

                        # label
                        sub.label(icon='GROUP_VCOL')

                        # operator menu enum
                        row.operator('mesh.vertex_color_add', text='Add Vertex Color')

                    # for vertex color
                    for vertexColor in object.data.vertex_colors:

                        # is search
                        if search == '' or re.search(search, vertexColor.name, re.I):

                            # vertex color
                            VertexColor(self, context, layout, vertexColor, object, panel)

        # material
        def material(self, context, layout, object, panel):
            '''
                Material related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # is materials
            if panel.materials:

                # for slot
                for slot in object.material_slots:

                    # is link data
                    if slot.link == 'DATA':

                        # isnt none
                        if slot.material != None:

                            # textures
                            textures = [tslot.texture.name for tslot in slot.material.texture_slots if hasattr(tslot, 'texture')]

                            # is search
                            if search == '' or re.search(search, slot.material.name, re.I) or [re.search(search, item, re.I) for item in textures if re.search(search, item, re.I) != None]:

                                # material
                                Material(self, context, layout, slot, object, panel)

                                # is textures
                                if panel.textures:

                                    # is engine blender render or blender game
                                    if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:

                                        # for tslot
                                        for tslot in slot.material.texture_slots:

                                            # has texture
                                            if hasattr(tslot, 'texture'):

                                                # isnt none
                                                if tslot.texture != None:

                                                    # is search
                                                    if search == '' or re.search(search, tslot.texture.name, re.I):

                                                        # texture
                                                        Texture(self, context, layout, tslot, object, panel)

        # bone groups
        def boneGroup(self, context, layout, object, panel):
            '''
                Bone group related code block.
            '''

            # search
            search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

            # bone groups
            if panel.boneGroups:

                # is type armature
                if object.type in 'ARMATURE':

                    # is shortcuts and not search
                    if panel.shortcuts and not panel.search and context.mode == 'POSE':

                        # row
                        row = layout.row(align=True)

                        # context pointer set
                        row.context_pointer_set('object', object)

                        # sub
                        sub = row.row()

                        # scale x
                        sub.scale_x = 1.6

                        # label
                        sub.label(icon='GROUP_BONE')

                        # operator menu enum
                        row.operator('pose.group_add', text='Add Bone Group')

                    # for group
                    for group in object.pose.bone_groups:

                        # is search
                        if search == '' or re.search(search, group.name, re.I):

                            # bone group
                            BoneGroup(self, context, layout, group, object)

    # bones
    def bone(self, context, layout, object, panel):
        '''
            Bone related code block.
        '''

        # option
        option = context.scene.NamePanel

        # search
        search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

        # is type armature
        if object.type in 'ARMATURE':

            # is mode pose or edit
            if object.mode in {'POSE', 'EDIT'}:

                # is display bones
                if panel.displayBones:

                        # row
                        row = layout.row()

                        # bone mode
                        row.prop(panel, 'boneMode', expand=True)

                        # separate
                        layout.separator()

                # isnt display bones
                else:

                    # bone
                    Bone(self, context, layout, context.active_bone, context.active_object, panel)

            # is pin active bone
            if option.pinActiveBone and panel.displayBones:

                # is mode pose or edit
                if object.mode in {'POSE', 'EDIT'}:

                    # is active bone
                    if context.active_bone:

                        # constraints
                        try: constraints = [item.name for item in context.active_pose_bone.constraints]
                        except: constraints = []

                        # is search
                        if search == '' or re.search(search, context.active_bone.name, re.I) or [re.search(search, item, re.I) for item in constraints if re.search(search, item, re.I) != None]:

                            # bone
                            Bone(self, context, layout, context.active_bone, object, panel)

                            # is bone constraints
                            if panel.boneConstraints:

                                # is mode pose
                                if object.mode in 'POSE':

                                    # bone
                                    bone = context.active_pose_bone

                                    # is bone
                                    if bone:

                                        # for constraint
                                        for constraint in bone.constraints:

                                            # is search
                                            if search == '' or re.search(search, constraint.name, re.I):

                                                # constraint
                                                Constraint(self, context, layout, constraint, object, bone, panel)

                                        # is constraints
                                        if constraints != []:

                                            # row
                                            row = layout.row()

                                            # separate
                                            row.separator()

                        # display bones
                        if panel.displayBones:

                            # is mode pose
                            if object.mode in 'POSE':

                                # bones
                                bones = object.data.bones

                            # isnt mode pose
                            else:

                                # bones
                                bones = object.data.edit_bones

                            # is bone mode selected
                            if panel.boneMode == 'SELECTED':

                                # bones
                                bones = [[bone.name, bone] for bone in bones if bone.select]

                            # isnt bone mode selected
                            else:

                                # bones
                                bones = [[bone.name, bone] for bone in bones if True in [x&y for (x, y) in zip(bone.layers, object.data.layers)]]

                            # for sorted bone
                            for bone in sorted(bones):

                                # isnt active bone
                                if bone[1] != context.active_bone:

                                    # constraints
                                    try: constraints = [item.name for item in object.pose.bones[bone[1].name].constraints]
                                    except: constraints = []

                                    # is search
                                    if search == '' or re.search(search, bone[1].name, re.I) or [re.search(search, item, re.I) for item in constraints if re.search(search, item, re.I) != None]:

                                        # bone
                                        Bone(self, context, layout, bone[1], object, panel)

                                        # is bone constraints
                                        if panel.boneConstraints:

                                            # is mode pose
                                            if object.mode in 'POSE':

                                                # for constaint
                                                for constraint in object.pose.bones[bone[1].name].constraints:

                                                    # is search
                                                    if search == '' or re.search(search, constraint.name, re.I):

                                                        # constraint
                                                        Constraint(self, context, layout, constraint, object, bone[1], panel)

                                                    # isnt search
                                                    else:

                                                        # constraints remove
                                                        constraints.remove(constraint.name)

                                                # is constraints
                                                if constraints != []:

                                                    # row
                                                    row = layout.row()

                                                    # separate
                                                    row.separator()

            # isnt pin active bone
            else:

                # is display bones
                if panel.displayBones:

                    # is mode pose
                    if object.mode in 'POSE':

                        # bones
                        bones = object.data.bones

                    # isnt mode pose
                    else:

                        # bones
                        bones = object.data.edit_bones

                    # is bone mode selected
                    if panel.boneMode == 'SELECTED':

                        # bones
                        bones = [[bone.name, bone] for bone in bones if bone.select]

                    # isnt bone mode selected
                    else:

                        # bones
                        bones = [[bone.name, bone] for bone in bones if True in [x&y for (x, y) in zip(bone.layers, object.data.layers)]]

                    # for sorted bone
                    for bone in sorted(bones):

                        # constraints
                        try: constraints = [item.name for item in object.pose.bones[bone[1].name].constraints]
                        except: constraints = []

                        # is search
                        if search == '' or re.search(search, bone[1].name, re.I) or [re.search(search, item, re.I) for item in constraints if re.search(search, item, re.I) != None]:

                            # bone
                            Bone(self, context, layout, bone[1], object, panel)

                            # is bone constraints
                            if panel.boneConstraints:

                                # is mode pose
                                if object.mode in 'POSE':

                                    # for constraint
                                    for constraint in object.pose.bones[bone[1].name].constraints:

                                        # is search
                                        if search == '' or re.search(search, constraint.name, re.I):

                                            # constraint
                                            Constraint(self, context, layout, constraint, object, bone[1], panel)

                                        # isnt search
                                        else:

                                            # constraints remove
                                            constraints.remove(constraint.name)

                                    # is constraints
                                    if constraints != []:

                                        # row
                                        row = layout.row()

                                        # separate
                                        row.separator()

# object
def Object(self, context, layout, datablock, panel):
    '''
        The object name row.
    '''
    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # is active object
    if datablock == context.active_object:

        # row
        row = layout.row(align=True)

        # active
        row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

        # sub
        sub = row.row(align=True)

        # scale x
        sub.scale_x = 1.6

        # display names
        sub.prop(panel, 'displayNames', text='', icon=icon.object(datablock))

        # name
        row.prop(datablock, 'name', text='')

        # is shortcuts
        if panel.shortcuts:

            # hide
            row.prop(datablock, 'hide', text='')

            # hide select
            row.prop(datablock, 'hide_select', text='')

            # hide render
            row.prop(datablock, 'hide_render', text='')

    # isnt active object
    else:

        # row
        row = layout.row(align=True)

        # active
        row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

        # sub
        sub = row.row(align=True)

        # scale x
        sub.scale_x = 1.6

        # operator; name panel icon
        op = sub.operator('view3d.name_panel_icon', text='', icon=icon.object(datablock))
        op.owner = datablock.name
        op.target = datablock.name
        op.context = 'OBJECT'

        # object
        row.prop(datablock, 'name', text='')

        # is shortcuts
        if panel.shortcuts:

            # hide
            row.prop(datablock, 'hide', text='')

            # hide select
            row.prop(datablock, 'hide_select', text='')

            # hide render
            row.prop(datablock, 'hide_render', text='')

# group
def Group(self, context, layout, datablock, object, panel):
    '''
        The object group name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP', emboss=False)
    op.owner = object.name
    op.target = datablock.name
    op.context = 'GROUP'

    # name
    row.prop(datablock, 'name', text='')

    # shortcuts
    if panel.shortcuts:

        # context pointer set
        row.context_pointer_set('group', datablock)

        # remove
        row.operator('object.group_remove', text='', icon='X')

# grease pencil
def GreasePencil(self, context, layout, datablock, object, panel):
    '''
        The object grease pencil name row.
    '''

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # row
    row = layout.row(align=True)

    # active
    row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='GREASEPENCIL', emboss=False)
    op.owner = object.name
    op.target = datablock.name
    # op.context = 'GREASE_PENCIL'

    # name
    row.prop(datablock, 'name', text='')

# pencil layer
def PencilLayer(self, context, layout, owner, datablock, object, panel):
    '''
        The object pencil layer name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row(align=True)

    # scale x
    sub.scale_x = 1.6

    # # color
    # sub.prop(datablock, 'color', text='')
    #
    # # fill color
    # sub.prop(datablock, 'fill_color', text='')

    # label
    sub.label(icon='DOT')

    # info
    row.prop(datablock, 'info', text='')

    # is shortcuts
    if panel.shortcuts:

        # lock
        row.prop(datablock, 'lock', text='')

        # hide
        row.prop(datablock, 'hide', text='')

# action
def Action(self, context, layout, datablock, object, panel):
    '''
        The object action name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='ACTION', emboss=False)
    op.owner = object.name
    op.target = datablock.name
    op.context = 'ACTION'

    # name
    row.prop(datablock, 'name', text='')

# constraint
def Constraint(self, context, layout, datablock, object, bone, panel):
    '''
        The object or pose bone constraint name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='CONSTRAINT', emboss=False)
    op.owner = object.name if not bone else bone.name
    op.target = datablock.name
    op.context = 'CONSTRAINT' if not bone else 'BONE_CONSTRAINT'

    # name
    row.prop(datablock, 'name', text='')

    # is shortcuts
    if panel.shortcuts:

        # isnt rigid body joint or null
        if datablock.type not in {'RIGID_BODY_JOINT', 'NULL'}:

            # sub
            sub = row.row(align=True)

            # scale x
            sub.scale_x = 0.17

            # influence
            sub.prop(datablock, 'influence', text='')

        # icon view
        iconView = 'RESTRICT_VIEW_ON' if datablock.mute else 'RESTRICT_VIEW_OFF'

        # mute
        row.prop(datablock, 'mute', text='', icon=iconView)

# modifier
def Modifier(self, context, layout, datablock, object, panel):
    '''
        The object modifier name row.
    '''

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # row
    row = layout.row(align=True)

    # active
    row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon=icon.modifier(datablock), emboss=False)
    op.owner = object.name
    op.target = datablock.name
    op.context = 'MODIFIER'

    # name
    row.prop(datablock, 'name', text='')

    # is shortcuts
    if panel.shortcuts:

        # isnt collision or soft body
        if datablock.type not in {'COLLISION', 'SOFT_BODY'}:

            # icon render
            iconRender = 'RESTRICT_RENDER_OFF' if datablock.show_render else 'RESTRICT_RENDER_ON'

            # show render
            row.prop(datablock, 'show_render', text='', icon=iconRender)

            # icon view
            iconView = 'RESTRICT_VIEW_OFF' if datablock.show_viewport else 'RESTRICT_VIEW_ON'

            # show viewport
            row.prop(datablock, 'show_viewport', text='', icon=iconView)

# object data
def ObjectData(self, context, layout, datablock, panel):
    '''
        The object data name row.
    '''

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # row
    row = layout.row(align=True)

    # isnt empty
    if datablock.type != 'EMPTY':

        # active
        row.active = (search == '' or re.search(search, datablock.data.name, re.I) != None)

        # sub
        sub = row.row()

        # scale x
        sub.scale_x = 1.6

        # operator; name panel icon
        op = sub.operator('view3d.name_panel_icon', text='', icon=icon.objectData(datablock), emboss=False)
        op.owner = datablock.name
        op.target = datablock.name
        op.context = 'OBJECT_DATA'

        # name
        row.prop(datablock.data, 'name', text='')

        if datablock.data.users > 1 and panel.shortcuts:

            sub = row.row(align=True)
            sub.enabled = False
            sub.scale_x = 0.1

            sub.prop(panel, 'userCount', toggle=True, text=str(datablock.data.users))

        # is type lamp
        if datablock.type == 'LAMP':

            # row
            row = layout.row(align=True)

            # sub
            sub = row.row()

            # scale x
            sub.scale_x = 1.6

            # operator; name panel icon
            # add texture here

# vertex group
def VertexGroup(self, context, layout, datablock, object, panel):
    '''
        The object data vertex group name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP_VERTEX', emboss=False)
    op.owner = object.name
    op.target = datablock.name
    op.context = 'VERTEX_GROUP'

    # name
    row.prop(datablock, 'name', text='')

    # is shortcuts
    if panel.shortcuts:

        # icon lock
        iconLock = 'LOCKED' if datablock.lock_weight else 'UNLOCKED'

        # lock weight
        row.prop(datablock, 'lock_weight', text='', icon=iconLock)

# shapekey
def Shapekey(self, context, layout, datablock, object, panel):
    '''
        The object animation data data shapekey name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='SHAPEKEY_DATA', emboss=False)
    op.owner = object.name
    op.target = datablock.name
    op.context = 'SHAPEKEY'

    # name
    row.prop(datablock, 'name', text='')

    # is shortcuts
    if panel.shortcuts:

        # isnt basis
        if datablock != object.data.shape_keys.key_blocks[0]:

            # sub
            sub = row.row(align=True)

            # scale x
            sub.scale_x = 0.17

            # value
            sub.prop(datablock, 'value', text='')

        # mute
        row.prop(datablock, 'mute', text='', icon='RESTRICT_VIEW_OFF')

# uv
def UV(self, context, layout, datablock, object, panel):
    '''
        The object data uv name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP_UVS', emboss=False)
    op.owner = object.name
    op.target = datablock.name
    op.context = 'UV'

    # name
    row.prop(datablock, 'name', text='')

    # is shortcuts
    if panel.shortcuts:

        # icon active
        iconActive = 'RESTRICT_RENDER_OFF' if datablock.active_render else 'RESTRICT_RENDER_ON'

        # active render
        row.prop(datablock, 'active_render', text='', icon=iconActive)

# vertex color
def VertexColor(self, context, layout, datablock, object, panel):
    '''
        The object data vertex color name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP_VCOL', emboss=False)
    op.owner = object.name
    op.target = datablock.name
    op.context = 'VERTEX_COLOR'

    # name
    row.prop(datablock, 'name', text='')

    # is shortcuts
    if panel.shortcuts:

        # icon active
        iconActive = 'RESTRICT_RENDER_OFF' if datablock.active_render else 'RESTRICT_RENDER_ON'

        # active_render
        row.prop(datablock, 'active_render', text='', icon=iconActive)

# material
def Material(self, context, layout, datablock, object, panel):
    '''
        The object material name row.
    '''

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # row
    row = layout.row(align=True)

    # active
    row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # label
    sub.label(icon='MATERIAL')

    # operator; name panel icon
    # op = sub.operator('view3d.name_panel_icon', text='', icon='MATERIAL', emboss=False)
    # op.owner = object.name
    # op.target = datablock.name
    # op.context = 'MATERIAL'

    # name
    row.prop(datablock.material, 'name', text='')

# texture
def Texture(self, context, layout, datablock, object, panel):
    '''
        The texture name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # label
    sub.label(icon='TEXTURE')

    # operator; name panel icon
    # op = sub.operator('view3d.name_panel_icon', text='', icon='TEXTURE', emboss=False)
    # op.owner = object.name
    # op.target = datablock.name
    # op.context = 'TEXTURE'

    # name
    row.prop(datablock.texture, 'name', text='')

    # is shortcuts
    if panel.shortcuts:

        # has use
        if hasattr(datablock, 'use'):

            # icon toggle
            iconToggle = 'RADIOBUT_ON' if datablock.use else 'RADIOBUT_OFF'

            # use
            row.prop(datablock, 'use', text='', icon=iconToggle)

# mask texture
def MaskTexture(self, context, layout, datablock, object, panel):
    '''
        The mask texture name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # label
    sub.label(icon='TEXTURE')

    # icon
    # op = sub.operator('view3d.name_panel_icon', text='', icon='TEXTURE', emboss=False)
    # op.owner = object.name
    # op.target = datablock.name
    # op.context = 'TEXTURE'

    # name
    row.prop(datablock.mask_texture, 'name', text='')

    # is shortcuts
    if panel.shortcuts:

        # has use
        if hasattr(datablock, 'use'):

            # icon toggle
            iconToggle = 'RADIOBUT_ON' if datablock.use else 'RADIOBUT_OFF'

            # use
            row.prop(datablock, 'use', text='', icon=iconToggle)

# particle
def Particle(self, context, layout, datablock, object, panel):
    '''
        The modifier particle system and setting name row.
    '''

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # row
    row = layout.row(align=True)

    # active
    row.active = (search == '' or re.search(search, datablock.particle_system.name, re.I) != None)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # label
    sub.label(icon='PARTICLES')

    # operator; name panel icon
    # op = sub.operator('view3d.name_panel_icon', text='', icon='PARTICLES', emboss=False)
    # op.owner = object.name
    # op.target = datablock.particle_system.name
    # op.context = 'PARTICLE_SYSTEM'

    # name
    row.prop(datablock.particle_system, 'name', text='')

    # is search
    if search == '' or re.search(search, datablock.particle_system.settings.name, re.I):

        # row
        row = layout.row(align=True)

        # sub
        sub = row.row()

        # scale
        sub.scale_x = 1.6

        # label
        sub.label(icon='DOT')

        # operator; name panel icon
        # op = sub.operator('view3d.name_panel_icon', text='', icon='DOT', emboss=False)
        # op.owner = object.name
        # op.target = datablock.particle_system.settings.name
        # op.context = 'PARTICLE_SETTING'

        # name
        row.prop(datablock.particle_system.settings, 'name', text='')

# bone group
def BoneGroup(self, context, layout, datablock, object):
    '''
        The armature data bone group name row.
    '''

    # row
    row = layout.row(align=True)

    # sub
    sub = row.row()

    # scale x
    sub.scale_x = 1.6

    # operator; name panel icon
    op = sub.operator('view3d.name_panel_icon', text='', icon='GROUP_BONE', emboss=False)
    op.owner = object.name
    op.target = datablock.name
    op.context = 'BONE_GROUP'

    # name
    row.prop(datablock, 'name', text='')

# bone
def Bone(self, context, layout, datablock, object, panel):
    '''
        The object data bone.
    '''

    # search
    search = context.scene.NamePanel.search if panel.regex else re.escape(context.scene.NamePanel.search)

    # row
    row = layout.row(align=True)

    # active
    row.active = (search == '' or re.search(search, datablock.name, re.I) != None)

    # sub
    sub = row.row(align=True)

    # scale x
    sub.scale_x = 1.6

    # is active bone
    if datablock == context.active_bone:

        # display bones
        sub.prop(panel, 'displayBones', text='', icon='BONE_DATA')

    # is pose mode
    if object.mode in 'POSE':

        # isnt active bone
        if not datablock == context.active_bone:

            # operator; name panel icon
            op = sub.operator('view3d.name_panel_icon', text='', icon='BONE_DATA')
            op.owner = object.name
            op.target = datablock.name
            op.context = 'BONE'

            # name
            row.prop(datablock, 'name', text='')

        # is active bone
        else:

            # name
            row.prop(datablock, 'name', text='')

        # is shortcuts
        if panel.shortcuts:

            # icon view:
            iconView = 'RESTRICT_VIEW_ON' if datablock.hide else 'RESTRICT_VIEW_OFF'

            # hide
            row.prop(datablock, 'hide', text='', icon=iconView)

            # icon hide select
            iconSelect = 'RESTRICT_SELECT_ON' if datablock.hide_select else 'RESTRICT_SELECT_OFF'

            # hide select
            row.prop(datablock, 'hide_select', text='', icon=iconSelect)

    # isnt pose mode
    else:

        # name
        if not datablock == context.active_bone:

            # icon
            op = sub.operator('view3d.name_panel_icon', text='', icon='BONE_DATA')
            op.owner = object.name
            op.target = datablock.name
            op.context = 'BONE'

        # name
        row.prop(datablock, 'name', text='')

        # is shortcuts
        if panel.shortcuts:

            # icon view
            iconView = 'RESTRICT_VIEW_ON' if datablock.hide else 'RESTRICT_VIEW_OFF'

            # hide
            row.prop(datablock, 'hide', text='', icon=iconView)

            # icon select
            iconSelect = 'RESTRICT_SELECT_ON' if datablock.hide_select else 'RESTRICT_SELECT_OFF'

            # hide select
            row.prop(datablock, 'hide_select', text='', icon=iconSelect)

            # icon lock
            iconLock = 'LOCKED' if datablock.lock else 'UNLOCKED'

            # lock
            row.prop(datablock, 'lock', text='', icon=iconLock)

    # is edit mode
    if object.mode in 'EDIT':

        # row
        row = layout.row()

        # separate
        row.separator()

    # is pose mode
    elif object.mode in 'POSE':

        # constraints
        constraints = [constraint.name for constraint in context.active_object.pose.bones[datablock.name].constraints]

        # isn't bone constraints
        if not panel.boneConstraints or constraints == []:

            # row
            row = layout.row()

            # separate
            row.separator()
