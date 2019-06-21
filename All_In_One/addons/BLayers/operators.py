import bpy

from .functions import *
from .utils import source_layers,update_col_index,sort_layer

class LayerPresetManagment(bpy.types.Operator) :
    """Layer Preset Management"""
    bl_idname = "blayers.layer_preset_management"
    bl_label = "Add or Remove Layers Preset"

    operation = bpy.props.StringProperty()
    preset = bpy.props.StringProperty()
    preset_name = bpy.props.StringProperty()

    def draw(self,context) :
        layout = self.layout

        layout.prop(self,"preset_name")

    def execute(self, context):
        operation = self.operation
        ob = context.object

        BLayers = ob.data.BLayers

        sorted_layers = sort_layer([l for l in BLayers.layers if l.UI_visible])
        selected_layers =  [l for l in BLayers.layers if l.type == 'LAYER' and l.move]

        if not BLayers.get("presets"):
            BLayers["presets"] = {}

        if operation == 'ADD' :
            BLayers["presets"][self.preset_name] = [l.index for l in BLayers.layers if l.UI_visible and l.move]

        elif operation == 'REMOVE' :
            BLayers["presets"].pop(self.preset)

        elif operation == 'APPLY' :
            layers_to_show =  list(BLayers["presets"][self.preset])
            print('###')
            print(layers_to_show)
            for i,l in enumerate(context.object.data.layers):
                if i in layers_to_show :
                    context.object.data.layers[i] = True
                else :
                    context.object.data.layers[i] = False

        redraw_areas()
        return {'FINISHED'}

    def invoke(self,context,event) :
        wm = context.window_manager
        if self.operation == 'ADD' :
            return wm.invoke_props_dialog(self)
        else :
            return self.execute(context)

class LayerSeparator(bpy.types.Operator) :
    """Layer Separator"""
    bl_idname = "blayers.layer_separator"
    bl_label = "Add Layer separator"

    operation = bpy.props.StringProperty()

    def execute(self, context):
        operation = self.operation
        ob = context.object

        BLayers = ob.data.BLayers.layers

        sorted_layers = sort_layer([l for l in BLayers if l.UI_visible])
        selected_layers =  [l for l in BLayers if l.type == 'LAYER' and l.move]

        if operation == 'ADD' :
            for l in selected_layers :
                l.v_separator = True

        else :
            for l in selected_layers :
                l.v_separator = False

        return {'FINISHED'}


class MoveRigLayers(bpy.types.Operator) :
    """Move rig layers"""
    bl_idname = "blayers.move_rig_layers"
    bl_label = "Move Rig Layers"

    operation = bpy.props.StringProperty()


    def execute(self, context):
        operation = self.operation
        ob = context.object

        BLayers = ob.data.BLayers.layers

        sorted_layers = sort_layer([l for l in BLayers if l.UI_visible])
        selected_layers =  [l for l in BLayers if l.type == 'LAYER' and l.move]

        if operation == 'UP' :
            for i,row in enumerate(sorted_layers) :
                index = row[0].column
                above_layer = sorted_layers[i-1]
                above_index = above_layer[0].column

                if len([l for l in BLayers if l.column == index and l.move]): # if at least one layer in the row is selected
                    for layer in row :
                        layer.column = above_index

                    for layer in above_layer :
                        layer.column = index
                    break


        elif operation == 'DOWN' :
            for i,row in enumerate(sorted_layers) :
                index = row[0].column
                above_layer = sorted_layers[i+1]
                above_index = above_layer[0].column

                if len([l for l in BLayers if l.column == index and l.move]): # if at least one layer in the row is selected
                    for layer in row :
                        layer.column = above_index

                    for layer in above_layer :
                        layer.column = index
                    break

        elif operation == 'LEFT' :
            for row in sorted_layers :
                for i,l in enumerate(row) :
                    if l.move :
                        index = l.row
                        left_layer = row[i-1]
                        l.row = left_layer.row
                        left_layer.row = index

        elif operation == 'RIGHT' :
            for row in sorted_layers :
                for i,l in enumerate(row) :
                    if l.move :
                        index = l.row
                        left_layer = row[i+1]
                        l.row = left_layer.row
                        left_layer.row = index

        elif operation == 'MERGE' :
            for i,row in enumerate(sorted_layers) :
                for l in row :
                    if l.move :
                        print('### lalal')
                        print([l.row for l in sorted_layers[i+1]])

                        l.row = max([l.row for l in sorted_layers[i+1]])+1
                        l.column = sorted_layers[i+1][0].column


        elif operation == 'EXTRACT' :
            for i,row in enumerate(sorted_layers) :
                if len([l for l in row if l.move]) : # if a layer is selected
                    for below_row in [r for j,r in enumerate(sorted_layers) if j>i] :
                        for l in below_row :
                            l.column+=1
                    for l in [l for l in row if not l.move] :
                        l.column+=1
                        l.row = 0


        return {'FINISHED'}

        '''
    def invoke(self, context, event):
        scene = context.scene
        ob = context.object
        layout = self.layout

        BLayers = ob.data.BLayers.layers
        for l in [l for l in BLayers if l.type == 'LAYER'] :
            l.move = False

        return self.execute(context)
        '''


class AddLayerToPanel(bpy.types.Operator) :
    """Add layer to the right panel"""
    bl_idname = "blayers.add_layer_to_panel"
    bl_label = "Add Layer to the right panel"

    @classmethod
    def poll(self,context) :
        return context.object.type == 'ARMATURE'


    def draw(self,context) :
        scene = context.scene
        ob = context.object
        layout = self.layout
        BLayers = ob.data.BLayers.layers

        col = layout.column(align=True)
        for l in [l for l in BLayers if l.type == 'LAYER'] :
            col.prop(l,'move',toggle = True,text = l.name)

    def execute(self, context):
        scene = context.scene
        ob = context.object
        BLayers = ob.data.BLayers.layers

        for l in BLayers :
            if l.move :
                if not l.UI_visible :
                    l.UI_visible= True
                    l.column = max([l.column for l in BLayers if l.type == 'LAYER'])+1
            else :
                l.UI_visible= False
                l.column = 0


        redraw_areas()
        return {'FINISHED'}

    def invoke(self, context, event):
        scene = context.scene
        ob = context.object
        layout = self.layout

        BLayers = ob.data.BLayers.layers

        for l in BLayers :
            if l.UI_visible :
                l.move = True
            else :
                l.move = False


        wm = context.window_manager
        return wm.invoke_props_dialog(self,width=150)


class LayerPreset(bpy.types.Operator):
    """Display layers from preset"""
    bl_idname = 'blayers.layer_preset'
    bl_label = "BLayer Preset"

    preset = bpy.props.StringProperty()

    presets = {
        "BASIC" : [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "COMPLET" : [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }

    def execute(self, context):
        preset = self.preset
        ob = context.object

        ob.data.layers  = [bool(l) for l in self.presets[preset]]


        return {'FINISHED'}



class CopyLayers(bpy.types.Operator):
    """Change BLayers to clipboard"""
    bl_idname = "blayers.copy_layers"
    bl_label = "Copy BLayer"

    def execute(self, context):
        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        Layers = {}
        Layers['presets'] = BLayersSettings['presets'].to_dict()
        Layers['objects'] = {}
        for ob in objects :
            Layers['objects'][ob.name] = list(ob.layers)

        Layers['layers'] = []
        for l in BLayers :
            Layers['layers'].append({   'name' :l.name,
                                        'type':l.type,
                                        'index':l.index,
                                        'id' : l.id,
                                        'column':l.column,
                                        'row' : l.row,
                                        'UI_visible':l.UI_visible,
                                        'v_separator':l.v_separator})


        context.window_manager.clipboard = str(Layers)

        return {'FINISHED'}

class PasteLayers(bpy.types.Operator):
    """Past BLayers from clipboard"""

    bl_idname = "blayers.paste_layers"
    bl_label = "Copy BLayer"

    def execute(self, context):
        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        #delete_layer
        for i in range(len(BLayers)) :
            #print(i)
            BLayers.remove(0)

        try :
            Layers = eval(context.window_manager.clipboard)

            BLayersSettings['presets'] = Layers['presets']

            if layers_from == 'ARMATURE' :
                for o,layers in BLayersSettings['objects'].items() :
                    bone = context.object.data.bones.get(o)
                    if bone:
                        bone.layers = layers


            for layer_info in Layers['layers'] :
                layer = BLayers.add()
                for attr,value in layer_info.items() :
                    setattr(layer,attr,value)

            redraw_areas()
        except :
            self.report({'ERROR'},"Wrong ClipBoard")

        return {'FINISHED'}


class ChangeShortcut(bpy.types.Operator):
    """Change BLayers shortcut"""
    bl_idname = "blayers.change_shorcut"
    bl_label = "Change Shortcut"

    def execute(self, context):
        wm = context.window_manager
        keyconfig = wm.keyconfigs.user.keymaps.get('Object Mode')
        #print('check')
        if keyconfig and keyconfig.keymap_items.get('object.move_to_layer'):
            move_to_layer = keyconfig.keymap_items.get('object.move_to_layer')
            move_to_layer.active = False

        return {'FINISHED'}

class SynchroniseLayers(bpy.types.Operator):
    """Create missings layers"""
    bl_idname = "blayers.synchronise_layers"
    bl_label = "Synchronise Layers"

    def execute(self, context):
        scene = context.scene
        ob = context.object

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        full_layers = []
        existing_indexes = [l.index for l in BLayers if l.type =='LAYER']

        for ob in objects :
            for i,l in enumerate(ob.layers) :
                if l and i not in full_layers:
                    full_layers.append(i)

        for free_index in full_layers :
            if not free_index in existing_indexes :
                layer = BLayers.add()
                existing_number = [int(l.name[-2:]) for l in BLayers if l.name.startswith('Layer_') and l.name[-2:].isnumeric()]

                free_number = max(existing_number)+1 if existing_number else 1
                for i in existing_number :
                    if not i+1 in existing_number :
                        free_number = i+1
                        break

                layer.name = 'Layer_%02d'%free_number
                layer.index = free_index
                layer.type = 'LAYER'

        update_col_index(BLayers)
        return {'FINISHED'}


class ObjectsToLayer(bpy.types.Operator):
    """Move objects to layers"""
    bl_idname = "blayers.objects_to_layer"
    bl_label = "Objects To Layer"

    layer_index = bpy.props.IntProperty()

    @classmethod
    def poll(self,context) :
        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()
        return True if selected and len(BLayers) else False

    def draw(self,context) :
        scene = context.scene
        layout = self.layout

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        col = layout.column(align=True)
        for l in [l for l in BLayers if l.type == 'LAYER'] :
            col.prop(l,'move',toggle = True,text = l.name)


    def execute(self, context):
        scene = context.scene
        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        if not self.dst_layers :
            self.dst_layers = [l.index for l in BLayers if l.move]

        print(selected)

        for ob in selected :
            for i in self.dst_layers :
                ob.layers[i]=True

            if not self.shift :
                for i in self.src_layers :
                    if i not in self.dst_layers :
                        ob.layers[i]=False

        return {'FINISHED'}

    def invoke(self, context, event):
        scene = context.scene
        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()
        index = BLayersSettings.active_index

        self.shift = event.shift

        self.src_layers = []
        for ob in selected :
            for i,l in enumerate(ob.layers) :
                if l and i not in self.src_layers :
                    self.src_layers.append(i)

        #print(self.src_layers)
        if index in range(len(BLayers)):
            BLayers[index].move = True
            for l in BLayers :
                if l.index in self.src_layers :
                    l.move = True
                else :
                    l.move = False

        if event.type == 'M' :
            self.dst_layers = []
            wm = context.window_manager
            return wm.invoke_props_dialog(self,width=175)
        else :
            self.dst_layers = [self.layer_index]
            return self.execute(context)


class SelectObjects(bpy.types.Operator):
    """Select objects on layer"""
    bl_idname = "blayers.select_objects"
    bl_label = "Select all objects on active layer"

    def execute(self, context):
        scene = context.scene
        ob = context.object
        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        active_layer = BLayers[BLayersSettings.active_index]
        active_index = active_layer.index

        if active_layer.type == 'LAYER' :
            layers = [active_index]
        else :
            layers = [l.index for l in BLayers if l.id == active_layer.id]

        for ob in objects :
            for index in layers :
                if ob.layers[index] :
                    ob.select = True
                    objects.active = ob


        update_col_index(BLayers)
        return {'FINISHED'}

class ToggleLayer(bpy.types.Operator):
    """Isolate property"""
    bl_idname = "blayers.toogle_layer"
    bl_label = "Toggle Layer Render"

    prop = bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        active_layer = BLayers[BLayersSettings.active_index]
        passive_layers = [l for l in BLayers if l !=active_layer]

        prop = self.prop

        if active_layer.type == 'GROUP' :
            passive_layers = [l for l in BLayers if l.type =='LAYER' and l !=active_layer and l.id != active_layer.id]
        else :
            passive_layers = [l for l in BLayers if l.type =='LAYER' and l !=active_layer]

        true_layers = [l for l in BLayers if l !=active_layer and l.type =='LAYER' and getattr(l,prop)]
        toogle = False if len(true_layers)==len(passive_layers) else True

        groups = [g for g in BLayers if g.type =='GROUP' and g.id != active_layer.id]
        #scene.layers[active_index] = True

        setattr(active_layer,prop,False)

        for g in groups :
            setattr(g,prop,toogle)

        for l in passive_layers:
            if l.type == 'LAYER' :
                setattr(l,prop,toogle)


        return {'FINISHED'}


class ToogleLayerHide(bpy.types.Operator):
    """Isolate Layer"""
    bl_idname = "blayers.toogle_layer_hide"
    bl_label = "Toggle Layer Hide"

    def execute(self, context):
        scene = context.scene

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        active_layer = BLayers[BLayersSettings.active_index]
        active_index = active_layer.index

        if active_layer.type == 'GROUP' :
            layers_index = [l.index for l in BLayers if l.type =='LAYER' and l.index !=active_index and l.id != active_layer.id]
        else :
            layers_index = [l.index for l in BLayers if l.type =='LAYER' and l.index !=active_index]

        hide_layers = [i for i in layers_index if not layers_from.layers[i]]

        toogle = True if len(hide_layers)==len(layers_index) else False

        groups = [g for g in BLayers if g.type =='GROUP' and g.id != active_layer.id]
        layers[active_index] = True

        for index in layers_index:
            layers[index] = toogle

        for g in groups :
            g.visibility = toogle

        return {'FINISHED'}


class MoveLayer(bpy.types.Operator):
    """Move Layer up or down"""
    bl_idname = "blayers.layer_move"
    bl_label = "Move Layer"

    step = bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        ob = context.object

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        col_index = BLayersSettings.active_index
        active_layer = BLayers[col_index]

        same_group = same_prop(BLayers,col_index,'id')

        #if active_layer.type == 'LAYER' :
        #    if col_index == max(same_group) and self.step > 0 or col_index == min(same_group)+1 and self.step < 0:
        #        active_layer.id = -1

        if self.step > 0 : #DOWN
            new_index = move_layer_down(BLayers,col_index)

            if active_layer.type == 'LAYER' or (active_layer.type == 'GROUP' and len(same_group)==1):
                if active_layer.type == 'LAYER' and active_layer.id!=-1 and col_index == max(same_group) :
                    active_layer.id = -1
                    new_index = col_index
                else :
                    BLayers.move(col_index,new_index)

            else : # it's a group with layers
                j=0
                for i in reversed(same_group) :
                    BLayers.move(i,new_index+j)
                    j-=1

                new_index = new_index+j+1
        elif self.step < 0 : #UP
            new_index = move_layer_up(BLayers,col_index)
            if active_layer.type == 'LAYER' or (active_layer.type == 'GROUP' and len(same_group)==1):
                if active_layer.type == 'LAYER' and active_layer.id!=-1 and col_index == min(same_group)+1 :
                    active_layer.id = -1
                BLayers.move(col_index,new_index)

            else  :
                for i in range(len(same_group)) :
                    BLayers.move(max(same_group),new_index)

                    #new_index = move_layer_up(collection,i)
                #new_index = move_group_up(BLayers.layers,col_index)

        BLayersSettings.active_index = new_index

        update_col_index(BLayers)
        redraw_areas()
        return {'FINISHED'}


class RemoveLayer(bpy.types.Operator):
    """Remove Layer"""
    bl_idname = "blayers.remove_layer"
    bl_label = "Remove Gpencil Layer"

    def execute(self, context):
        scene = context.scene
        ob = context.object

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        col_index = BLayersSettings.active_index
        layer = BLayers[col_index]

        if layer.type == 'GROUP' or not [o for o in objects if o.layers[layer.index]] :
            if layer.type == 'GROUP' :
                for l in [l for l in BLayers if l.id == layer.id] :
                    l.id = -1
            BLayers.remove(col_index)
            BLayersSettings.active_index = col_index-1

        else :
            self.report({'ERROR'},'You only can delete empty layer')

        update_col_index(BLayers)
        redraw_areas()
        return {'FINISHED'}

'''
class AddGroup(bpy.types.Operator):
    """Remove Parent"""
    bl_idname = "blayers.add_group"
    bl_label = "Add Gpencil Layer"

    def execute(self, context):
        scene = context.scene
        BLayers = scene.BLayers
        active_index = BLayers.active_index

        group = BLayers.layers.add()

        existing_number = [int(l.name[-2:]) for l in BLayers.layers if l.name.startswith('GROUP_') and l.name[-2:].isnumeric()]
        free_number = max(existing_number)+1 if existing_number else 1
        for i in existing_number :
            if not i+1 in existing_number :
                free_number = i+1
                break

        group.name = 'GROUP_%02d'%free_number
        group.type = 'GROUP'
        scene.BLayers.id_count +=1
        group.id = BLayers.id_count
        #print(group.id)
        BLayers.active_index = len(BLayers.layers)-1
        redraw_areas()

        return {'FINISHED'}
    '''

class MoveInGroup(bpy.types.Operator):
    """Put layer in the group"""
    bl_idname = "blayers.move_in_group"
    bl_label = "Add Gpencil Layer"

    index = bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        ob = context.object

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        col_index = BLayersSettings.active_index
        layer = BLayers[col_index]

        if layer.type =='LAYER' :
            group = BLayers[self.index]
            offset = 1 if col_index > self.index else 0
            layer.id = group.id
            BLayers.move(col_index,self.index+offset)
            BLayersSettings.active_index = self.index+offset
        redraw_areas()

        update_col_index(BLayers)
        return {'FINISHED'}

class AddLayer(bpy.types.Operator):
    """Add Layer"""
    bl_idname = "blayers.add_layer"
    bl_label = "Add Gpencil Layer"

    type = bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        ob = context.object

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        existing_indexes = [l.index for l in BLayers if l.type =='LAYER']

        if self.type == 'GROUP' :
            group = BLayers.add()

            existing_number = [int(l.name[-2:]) for l in BLayers if l.name.startswith('GROUP_') and l.name[-2:].isnumeric()]
            free_number = max(existing_number)+1 if existing_number else 1
            for i in existing_number :
                if not i+1 in existing_number :
                    free_number = i+1
                    break

            group.name = 'GROUP_%02d'%free_number
            group.type = 'GROUP'
            scene.BLayers.id_count +=1
            group.id = scene.BLayers.id_count
            BLayersSettings.active_index = len(BLayers)-1

        else :
            if len(existing_indexes)<len(layers) :
                free_index =  0
                for i in range(len(layers)-1) :
                    if not i in existing_indexes :
                        free_index = i
                        break

                layer = BLayers.add()
                existing_number = [int(l.name[-2:]) for l in BLayers if l.name.startswith('Layer_') and l.name[-2:].isnumeric()]
                free_number = max(existing_number)+1 if existing_number else 1
                for i in existing_number :
                    if not i+1 in existing_number :
                        free_number = i+1
                        break


                layer.name = 'Layer_%02d'%free_number
                layer.index = free_index
                layer.type = 'LAYER'
                BLayersSettings.active_index = len(BLayers)-1
                layers[free_index] = True

                if self.type == 'LAYER_FROM_SELECTED' :
                    empty_layers = [False]*len(layers)
                    empty_layers[free_index] = True
                    for ob in selected :
                        ob.layers = empty_layers

        update_col_index(BLayers)
        redraw_areas()
        return {'FINISHED'}
