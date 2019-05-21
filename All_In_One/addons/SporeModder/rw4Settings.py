import bpy
import bmesh
import os
import sporemodder.pyperclip as pyperclip
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       CollectionProperty
                       )

from sporemodder import RW4Enums
from sporemodder.RW4Enums import generateDefaultStates

# UI




def DirectXEnumItems(enumDict, itemList, listIndex, self):
    #item = itemList[listIndex]
    prop = enumDict[self.PropertyName]
    #matData = context.material.rw4
    #print(self)
    if not self.PropertyEnumsAlreadySet and len(self.EnumPropertyToSet) > 0:
        self.PropertyEnumsAlreadySet = True
        self.PropertyValueEnum = self.EnumPropertyToSet

    if prop[1] != int and prop[1] != float and prop[1] != 'COLOR':
        return sorted([(x, x, x) for x in prop[1]])


def DirectXEnumItems_Render(self, context):
    if context.active_object.active_material is not None:
        matData = context.active_object.active_material.rw4
        return DirectXEnumItems(RW4Enums.D3DRENDERSTATETYPE, matData.RenderStateProperties, matData.RenderStateIndex,
                                self)


def DirectXEnumItems_Sampler(self, context):
    if context.active_object.active_material is not None:
        matData = context.active_object.active_material.rw4
        return DirectXEnumItems(RW4Enums.D3DSAMPLERSTATETYPE, matData.SamplerStateProperties, matData.SamplerStateIndex,
                                self)


def DirectXEnumItems_Texture(self, context):
    # if context.material is not None:
    if context.active_object.active_material is not None:
        # matData = context.material.rw4
        matData = context.active_object.active_material.rw4
        return DirectXEnumItems(
            RW4Enums.D3DTEXTURESTAGESTATETYPE, matData.TextureStateProperties, matData.TextureStateIndex, self)


# def get_enum(self):
#     # print("Method being got")
#     print(self)
#     return self["PropertyValueEnum"]


# To avoid read-only property
# def set_enum(self, value):
#     self["PropertyValueEnum"] = value
#     self.PropertyValueEnumStr = self.PropertyValueEnum
#     print(self.PropertyValueEnum)
#     print(self.PropertyValueEnumStr)
#     # print(self.PropertyName)
#     # print(value)


def update_enum(self, context):
    self.PropertyValueEnumStr = self.PropertyValueEnum
    # print(self.PropertyValueEnum)
    # print(self.PropertyValueEnumStr)


def get_str(self):
    return self.PropertyValueEnum


def set_str(self, arg):
    self["PropertyValueEnumStr"] = arg


def registerDirectXState(cls, enumDict, enumValueFunction):
    cls.PropertyName = EnumProperty(
        name="Property name",
        items=sorted([(prop, prop, prop) for prop in enumDict])
        #items=[]
    )
    cls.PropertyValueInt = IntProperty(
        name="Property value"
    )
    cls.PropertyValueFloat = FloatProperty(
        name="Property value"
    )
    cls.PropertyValueEnum = EnumProperty(
        name="Property value",
        items=enumValueFunction,  # We will fill them later
        # get=get_enum,
        # set=set_enum
        update=update_enum
    )
    cls.PropertyValueColor = FloatVectorProperty(
        name="Property value",
        subtype='COLOR',
        default=[1.0, 1.0, 1.0, 1.0],
        min=0,
        max=1,
        size=4
    )
    # For when importing properties, set the enum value after its items have been set
    cls.EnumPropertyToSet = StringProperty()
    cls.PropertyEnumsAlreadySet = BoolProperty()
    # For when exporting enum properties, for some reason the value is lost
    cls.PropertyValueEnumStr = StringProperty(get=get_str, set=set_str)


class DirectXRenderState(bpy.types.PropertyGroup):
    def __init__(self, name=None, valueInt=None, valueFloat=None, valueEnum=None, valueColor=None):
        self.PropertyName = name
        self.PropertyValueInt = valueInt
        self.PropertyValueFloat = valueFloat
        self.PropertyValueEnum = valueEnum
        self.PropertyValueColor = valueColor

    @classmethod
    def register(cls):
        registerDirectXState(cls, RW4Enums.D3DRENDERSTATETYPE, DirectXEnumItems_Render)


class DirectXSamplerState(bpy.types.PropertyGroup):
    def __init__(self, name=None, valueInt=None, valueFloat=None, valueEnum=None, valueColor=None):
        self.PropertyName = name
        self.PropertyValueInt = valueInt
        self.PropertyValueFloat = valueFloat
        self.PropertyValueEnum = valueEnum
        self.PropertyValueColor = valueColor

    @classmethod
    def register(cls):
        registerDirectXState(cls, RW4Enums.D3DSAMPLERSTATETYPE, DirectXEnumItems_Sampler)


class DirectXTextureState(bpy.types.PropertyGroup):
    def __init__(self, name=None, valueInt=None, valueFloat=None, valueEnum=None, valueColor=None):
        self.PropertyName = name
        self.PropertyValueInt = valueInt
        self.PropertyValueFloat = valueFloat
        self.PropertyValueEnum = valueEnum
        self.PropertyValueColor = valueColor

    @classmethod
    def register(cls):
        registerDirectXState(cls, RW4Enums.D3DTEXTURESTAGESTATETYPE, DirectXEnumItems_Texture)


# To update enums when importing
class PropertyToSet(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        cls.PropertyType = StringProperty()
        cls.PropertyName = StringProperty()
        cls.PropertyValue = StringProperty()


# def alphaTypeSetter(self, value):
#     print(self)
#     self["AlphaType"] = value
#     print(self["AlphaType"])
#     # bpy.ops.directx_state.generate_default(args='RENDER ' + self.AlphaType)


def update_alphaType(self, context):
    bpy.ops.directx_state.generate_default(args='RENDER ' + self.AlphaType)


def advancedOptionsUpdate(self, context):
    if not self.Initialized:
        bpy.ops.directx_state.generate_default(args='RENDER ' + self.AlphaType)
        bpy.ops.directx_state.generate_default(args='TEXTURE')
        bpy.ops.directx_state.generate_default(args='SAMPLER')
        self.Initialized = True


class RW4MaterialProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Material.rw4 = PointerProperty(type=cls)

        cls.overrideColor = FloatVectorProperty(
            name="Color",
            subtype='COLOR',
            default=[1.0, 1.0, 1.0, 1.0],
            min=0,
            max=1,
            size=4
        )
        cls.MaterialType = EnumProperty(
            name="Material type",
            description="The type of this mesh material",
            items=[
                # Same as GameModel
                # ('BACKGROUNDFLOOR', "Background floor", "A raw painting model (building, vehicle and UFO editor)"),

                # Same as Background, but with alpha properties; we can set them with the RenderStates
                #('BACKGROUNDALPHA', "Background transparent", "A raw painting model (building, vehicle and UFO editor)"),
                # ('TDBACKGROUND', "Test drive background", "A raw painting model (building, vehicle and UFO editor)"),
                # ('TDBACKGROUNDA', "Test drive background transparent", "A raw painting model (building, vehicle and UFO editor)"),
                ('SKINPAINT', "Skinpaint part", "A part for the Cell, Creature, Outfit, and Flora editors."),
                # ('RAWPAINT', "Raw painting part", "A raw painting model (building, vehicle and UFO editor)"),
                ('GAMEMODEL', "Object model",
                 "A simple model which allows normal maps, used for props, backgrounds, etc"),
                ('NO_MATERIAL', "No material",
                 "The model has no special material properties, like deform handles."),
                # ('BUILD1', "Build 1", "An \"in-game\" model, with normal maps"),
                # ('BUILD2', "Build 2", "An \"in-game\" model, with normal maps"),
                # ('BUILD3', "Build 3", "An \"in-game\" model, with normal maps"),
                ('BUILDDYN', "Mineralpaint part", "A part, for the Vehicle, Building, UFO, and Cake editors.")],
            default='SKINPAINT'
        )
        cls.DiffuseTexture = StringProperty(
            name="Diffuse texture",
            description="The diffuse texture of this material (leave empty if no texture desired)",
            default="",
            subtype='FILE_PATH'
        )
        cls.NormalTexture = StringProperty(
            name="Normal texture",
            description="The normal texture of this material (leave empty if no texture desired)",
            default="",
            subtype='FILE_PATH'
        )
        cls.specularExponent = FloatProperty(
            name="Specular exponent",
            default=10.0
        )
        cls.unkFloat1 = FloatProperty(
            name="Specular strength",
            default=1.0
        )
        cls.unkFloat2 = FloatProperty(
            name="Gloss",
            default=1.0
        )
        cls.unkFloat3 = FloatProperty(
            name="unkFloat3",
            default=0.0
        )
        cls.paintingMode = IntProperty(
            name="Projection mode",
            default=1  # 8 or higher won't work
        )  # boxmap, cylinder, sphere, planar, disc
        cls.tilingX = FloatProperty(
            name="X",
            default=0.5
        )
        cls.tilingY = FloatProperty(
            name="Y",
            default=0.5
        )
        cls.matGroup = IntProperty(
            name="Material Group",
            default=0
        )
        cls.usePaintTexture = BoolProperty(
            name="Use paint's texture",
            default=True
        )
        cls.unk = IntProperty(
            name="Unk 1",
            default=4
        )
        cls.unk2 = IntProperty(
            name="Unk 2",
            default=0
        )
        cls.unk3 = IntProperty(
            name="Unk 3",
            default=0
        )
        cls.unk4 = IntProperty(
            name="Unk 4",
            default=4
        )
        cls.unk5 = IntProperty(
            name="Unk 5",
            default=0
        )
        cls.unk6 = IntProperty(
            name="Unk 6",
            default=22
        )
        cls.unk7 = IntProperty(
            name="Unk 7",
            default=0
        )
        cls.unk8 = IntProperty(
            name="Unk 8",
            default=0
        )
        cls.unk9 = IntProperty(
            name="Unk 9",
            default=0
        )

        cls.RenderStateProperties = CollectionProperty(
            name="DirectX RenderState Properties",
            type=DirectXRenderState
        )
        # Selected item's index from the list
        cls.RenderStateIndex = IntProperty(
            default=0
        )
        cls.SamplerStateProperties = CollectionProperty(
            name="DirectX SamplerState Properties",
            type=DirectXSamplerState
        )
        cls.SamplerStateIndex = IntProperty(
            default=0
        )
        cls.TextureStateProperties = CollectionProperty(
            name="DirectX TextureStageState Properties",
            type=DirectXTextureState,
            # default=[DirectXTextureState(name='D3DTSS_COLOROP', valueEnum='D3DTOP_MODULATE'),
            #          DirectXTextureState(name='D3DTSS_COLORARG1', valueEnum='D3DTA_TEXTURE'),
            #          DirectXTextureState(name='D3DTSS_COLORARG2', valueEnum='D3DTA_DIFFUSE'),
            #          DirectXTextureState(name='D3DTSS_ALPHAOP', valueEnum='D3DTOP_MODULATE'),
            #          DirectXTextureState(name='D3DTSS_ALPHAARG1', valueEnum='D3DTA_TEXTURE'),
            #          DirectXTextureState(name='D3DTSS_ALPHAARG2', valueEnum='D3DTA_DIFFUSE')]
        )
        cls.TextureStateIndex = IntProperty(
            default=0
        )
        cls.AdvancedOptions = BoolProperty(
            name="Advanced options",
            update=advancedOptionsUpdate,
            default=False
        )
        cls.AlphaType = EnumProperty(
            name="Material alpha",
            items=[('NOALPHA', "Opaque", "The material has no transparency."),
                   ('ALPHA', "Alpha", "The material can have transparency, determined by the texture's alpha channel."),
                   ('EXCLUDING', "Excluding", "Pixels with transpareny < 127 won't be rendered.")],
            default='NOALPHA',
            # set=alphaTypeSetter
            update=update_alphaType
        )
        # TODO This is really ugly
        cls.Initialized = BoolProperty(
            default=False
        )
        # Identifier to difference in add/remove buttons
        # cls.CalledList = EnumProperty(
        #     items=['SAMPLER', 'TEXTURE', 'RENDER'],
        #     default='RENDER'
        # )

    @classmethod
    def unregister(cls):
        del bpy.types.Material.rw4


class RW4DirectXStateLIST(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.PropertyName, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon=custom_icon)


class LIST_OT_NewItem(bpy.types.Operator):
    bl_idname = "directx_state.new_item"
    bl_label = "+"#"Add a new item"

    calledList = StringProperty()

    def execute(self, context):
        if context.material is not None:
            #calledList = context.material.rw4.CalledList
            if self.calledList == 'RENDER':
                context.material.rw4.RenderStateProperties.add()
            elif self.calledList == 'TEXTURE':
                context.material.rw4.TextureStateProperties.add()
            elif self.calledList == 'SAMPLER':
                context.material.rw4.SamplerStateProperties.add()

            return {'FINISHED'}


class LIST_OT_DeleteItem(bpy.types.Operator):
    bl_idname = "directx_state.delete_item"
    bl_label = "-"#"Deletes an item"

    calledList = StringProperty()

    @classmethod
    def poll(self, context):
        #print("poll being called")
        """ Enable if there's something in the list """
        if context.material is not None:
            # if self.calledList == 'RENDER':
            #     return len(context.material.rw4.RenderStateProperties) > 0
            # elif self.calledList == 'TEXTURE':
            #     return len(context.material.rw4.TextureStateProperties) > 0
            # else:
            #     return len(context.material.rw4.SamplerStateProperties) > 0
            return True

        else:
            return False

    def execute(self, context):
        if context.material is not None:
            #calledList = context.material.rw4.CalledList
            if self.calledList == 'RENDER':
                stateList = context.material.rw4.RenderStateProperties
                index = context.material.rw4.RenderStateIndex
            elif self.calledList == 'TEXTURE':
                stateList = context.material.rw4.TextureStateProperties
                index = context.material.rw4.TextureStateIndex
            else:
                stateList = context.material.rw4.SamplerStateProperties
                index = context.material.rw4.SamplerStateIndex

            if len(stateList) > 0:
                stateList.remove(index)
                if index > 0:
                    if self.calledList == 'RENDER':
                        context.material.rw4.RenderStateIndex = index - 1
                    elif self.calledList == 'TEXTURE':
                        context.material.rw4.TextureStateIndex = index - 1
                    else:
                        context.material.rw4.SamplerStateIndex = index - 1

            return {'FINISHED'}


class OT_GenerateDefaultStates(bpy.types.Operator):
    bl_idname = "directx_state.generate_default"
    bl_label = "Generate default states"

    args = StringProperty()

    def execute(self, context):
        if context.material is not None:
            splits = self.args.split(" ")
            stateType = splits[0]
            if len(splits) > 1:
                generateType = splits[1]
            else:
                generateType = 'OPAQUE'  # by default

            generateDefaultStates(context.material.rw4, stateType, generateType)

            # if stateType == "RENDER":
            #     if len(splits) > 1:
            #         generateType = splits[1]
            #     else:
            #         generateType = 'OPAQUE'  # by default
            #
            #     context.active_material.rw4.RenderStateProperties.clear()
            #     if generateType == "ALPHA":
            #         states = RW4Enums.DefaultMaterialRender_Alpha
            #     elif generateType == "EXCLUDING":
            #         states = RW4Enums.DefaultMaterialRender_ExcludingAlpha
            #     else:
            #         states = RW4Enums.DefaultMaterialRender_NoAlpha
            #
            #     for s in states:
            #         setStateValue(context.material.rw4.RenderStateProperties.add(), s, RW4Enums.D3DRENDERSTATETYPE[s[0]])
            #
            # elif stateType == 'TEXTURE':
            #     context.material.rw4.TextureStateProperties.clear()
            #     for s in RW4Enums.DefaultTextureStageStates:
            #         setStateValue(context.material.rw4.TextureStateProperties.add(), s,
            #                       RW4Enums.D3DTEXTURESTAGESTATETYPE[s[0]])
            # else:
            #     context.material.rw4.SamplerStateProperties.clear()
            #     for s in RW4Enums.DefaultSamplerStates:
            #         setStateValue(context.material.rw4.SamplerStateProperties.add(), s,
            #                       RW4Enums.D3DSAMPLERSTATETYPE[s[0]])

        return {'FINISHED'}


def displayStateData(lay, matData, dataType):
    if dataType == 'RENDER':
        dataList = matData.RenderStateProperties
        dataIndex = matData.RenderStateIndex
        dataEnum = RW4Enums.D3DRENDERSTATETYPE
    elif dataType == 'TEXTURE':
        dataList = matData.TextureStateProperties
        dataIndex = matData.TextureStateIndex
        dataEnum = RW4Enums.D3DTEXTURESTAGESTATETYPE
    else:
        dataList = matData.SamplerStateProperties
        dataIndex = matData.SamplerStateIndex
        dataEnum = RW4Enums.D3DSAMPLERSTATETYPE

    if dataIndex >= len(dataList):
        dataIndex = 0

    if len(dataList) > 0:
        item = dataList[dataIndex]

        row = lay.row()
        row.prop(item, 'PropertyName')

        row = lay.row()
        prop = dataEnum[item.PropertyName]
        if prop[1] == int:
            row.prop(item, 'PropertyValueInt')
            # if len(prop) > 2:
            #     item.PropertyValueInt = prop[2]

        elif prop[1] == float:
            row.prop(item, 'PropertyValueFloat')

        elif prop[1] == 'COLOR':
            row.prop(item, 'PropertyValueColor')

        else:  # It uses an enum
            #item.PropertyValueEnum.items = [x for x in prop[1]]
            row.prop(item, 'PropertyValueEnum')


class MaterialPanel(bpy.types.Panel):
    bl_label = "RenderWare4 Material Config"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    
    def draw(self, context):
        lay = self.layout
        if context.material is not None:
            matData = context.material.rw4
            # if not matData.Initialized:
            #     bpy.ops.directx_state.generate_default(args="RENDER")
            #     bpy.ops.directx_state.generate_default(args="TEXTURE")
            #     bpy.ops.directx_state.generate_default(args="SAMPLER")
            #     matData.Initialized = True

            row = lay.row()
            row.prop(matData, 'MaterialType')
            row = lay.row()
            row.prop(matData, 'overrideColor')

            if matData.MaterialType != 'HANDLE':
                row = lay.row()
                row.prop(matData, 'DiffuseTexture')

            if matData.MaterialType == 'GAMEMODEL' or matData.MaterialType == 'BACKGROUNDFLOOR':
                row = lay.row()
                row.prop(matData, 'NormalTexture')

            if matData.MaterialType == 'GAMEMODEL':
                row = lay.row()
                row.prop(matData, 'specularExponent')
                row = lay.row()
                row.prop(matData, 'unkFloat1')
                row = lay.row()
                row.prop(matData, 'unkFloat2')
                row = lay.row()
                row.prop(matData, 'unkFloat3')

            if matData.MaterialType == 'BUILDDYN':
                row = lay.row()
                row.prop(matData, 'matGroup')
                row = lay.row()
                row.prop(matData, 'usePaintTexture')
                if matData.usePaintTexture:
                    row = lay.row()
                    row.prop(matData, 'paintingMode')
                    row = lay.row()
                    row.label("Tiling")
                    row.prop(matData, 'tilingX')
                    row.prop(matData, 'tilingY')

            row = lay.row()
            row.prop(matData, 'AlphaType')

            row = lay.row()
            row.prop(matData, 'AdvancedOptions')

            if matData.AdvancedOptions:
                # if matData.MaterialType == 'SKINPAINT':
                #     row = lay.row()
                #     row.prop(matData, 'unk')
                #     row.prop(matData, 'unk2')
                #     row = lay.row()
                #     row.prop(matData, 'unk3')
                #     row.prop(matData, 'unk4')
                #     row = lay.row()
                #     row.prop(matData, 'unk5')
                #     row.prop(matData, 'unk6')
                #     row = lay.row()
                #     row.prop(matData, 'unk7')
                #     row.prop(matData, 'unk8')
                #     row = lay.row()
                #     row.prop(matData, 'unk9')

                row = lay.row()
                row.label("DirectX RenderStates")
                row = lay.row()
                #split = row.split(0.8)
                #row.template_list("RW4RenderStateLIST", "The_List", bpy.data, "actions", context.scene, "rw4ListIndex")
                row.template_list("RW4DirectXStateLIST", "RenderStatesList", matData, "RenderStateProperties", matData,
                                  "RenderStateIndex", rows=1)
                #row = lay.row()
                #split = row.split(0.2)
                #box = split.box()
                col = row.column(align=True)
                col.operator("directx_state.new_item", icon='ZOOMIN', text="").calledList = "RENDER"
                col.operator("directx_state.delete_item", icon='ZOOMOUT', text="").calledList = "RENDER"
                row = lay.row()
                row.operator("directx_state.generate_default", text="Default values").args = 'RENDER NO_ALPHA'
                row.operator("directx_state.generate_default", text="Default values (alpha)").args = 'RENDER ALPHA'
                row.operator("directx_state.generate_default", text="Default values (excluding alpha)").\
                    args = 'RENDER EXCLUDING'
                displayStateData(lay, matData, 'RENDER')

                row = lay.row()
                row.label("DirectX SamplerStates")
                row = lay.row()
                row.template_list("RW4DirectXStateLIST", "SamplerStatesList", matData, "SamplerStateProperties", matData,
                                  "SamplerStateIndex", rows=1)
                col = row.column()
                col.operator("directx_state.new_item", icon='ZOOMIN', text="").calledList = "SAMPLER"
                col.operator("directx_state.delete_item", icon='ZOOMOUT', text="").calledList = "SAMPLER"
                row = lay.row()
                row.operator("directx_state.generate_default", text="Default values").args = 'SAMPLER NONE'
                displayStateData(lay, matData, 'SAMPLER')

                row = lay.row()
                row.label("DirectX TextureStageStates")
                row = lay.row()
                row.template_list("RW4DirectXStateLIST", "TextureStatesList", matData, "TextureStateProperties", matData,
                                  "TextureStateIndex", rows=1)
                col = row.column()
                col.operator("directx_state.new_item", icon='ZOOMIN', text="").calledList = "TEXTURE"
                col.operator("directx_state.delete_item", icon='ZOOMOUT', text="").calledList = "TEXTURE"
                row = lay.row()
                row.operator("directx_state.generate_default", text="Default values").args = 'TEXTURE NONE'
                displayStateData(lay, matData, 'TEXTURE')


class RW4AnimProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Action.rw4 = PointerProperty(type=RW4AnimProperties)

        cls.UseAsHandle = BoolProperty(
            name="Use this animation as a morph handle",
            description="Check if you want this animation to be a morph handle and not a normal animation",
            default=False
        )
        cls.HandlePos = FloatVectorProperty(
            name="Initial position",
            subtype='XYZ',
            precision=3,
            description="Handle initial position"
        )
        cls.HandleEndPos = FloatVectorProperty(
            name="Final position",
            subtype='XYZ',
            precision=3,
            description="Handle final position"
        )
        cls.HandleDefaultFrame = IntProperty(
            name="Default frame",
            default=0,
            min=0
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Action.rw4


# def action_editor_update(context):
#     ob = bpy.context.object
#     action_index = bpy.data.actions.find(ob.animation_data.action.name)
#     if action_index != ob.action_list_index:
#         ob.action_list_index = action_index
#
#
# # select the new action when there is a new selection in the ui list and go to the first frame
# def update_action_list(self, context):
#     ob = bpy.context.object
#     ob.animation_data.action = bpy.data.actions[ob.action_list_index]
#     bpy.context.scene.frame_current = 1


class RW4AnimUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name, icon=custom_icon)  # bpy.data.actions[item.Index]

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(item.name, icon=custom_icon)


class AnimPanel(bpy.types.Panel):
    # bl_label = "RenderWare4 Animations Config"
    # bl_space_type = 'NLA_EDITOR'
    # bl_region_type = 'UI'
    # bl_context = 'object.animation_data.nla_tracks.active.strips[0]'

    bl_label = "RenderWare4 Animation Config"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        lay = self.layout

        row = lay.row()
        # row.template_list("RW4AnimUIList", "The_List", context.scene, "rw4_list", context.scene, "rw4ListIndex" )
        row.template_list("RW4AnimUIList", "The_List", bpy.data, "actions", context.scene, "rw4ListIndex")

        if len(bpy.data.actions) > 0:
            item = bpy.data.actions[context.scene.rw4ListIndex].rw4
            # item = bpy.data.actions[bpy.data.actions.find(context.scene.rw4CurrentAction)].rw4

            row = lay.row()
            row.prop(item, 'UseAsHandle')

            if item.UseAsHandle:
                row = lay.row()
                row.prop(item, 'HandlePos')

                row = lay.row()
                row.prop(item, 'HandleEndPos')

                row = lay.row()
                row.prop(item, 'HandleDefaultFrame')
        

class MESH_OT_CheckDeforming(bpy.types.Operator):
    bl_idname = "mesh.check_deforming"
    bl_label = "Check deformation"


    # @classmethod
    # def poll(self, context):
    #     """ Enable if there's something in the list """
    #     return True  # len(context.scene.my_list) > 0

    def execute(self, context):
        def feq(a,b):
            if abs(a-b)<0.0000001:
                return 0
            else:
                return 1

        def packBW(w):
            return int(round(w * 255))

        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        for v, vert in enumerate(obj.data.vertices):
            if len(vert.groups) > 4:
                bm.verts[v].select = True

            val = 0
            for gr in vert.groups:
                name = obj.vertex_groups[gr.group].name
                for bone in bpy.data.armatures[0].bones:
                    if bone.name == name:
                        val += packBW(gr.weight)
                        break

            if val != 255:
                # print(val)
                #vert.select = True
                bm.verts[v].select = True
                # if val == 0:
                #     print("VERTEX %i IS 0" % v)
                # else:
                #     print("VERTEX %i IS %f" % (v, val))

        bmesh.update_edit_mesh(obj.data, True)

        return{'FINISHED'}


class MESH_OT_FixDeforming(bpy.types.Operator):
    bl_idname = "mesh.fix_deforming"
    bl_label = "Fix deformation"


    # @classmethod
    # def poll(self, context):
    #     """ Enable if there's something in the list """
    #     return True  # len(context.scene.my_list) > 0

    def execute(self, context):
        def packBW(w):
            return int(round(w * 255))

        obj = context.edit_object
        ind = 0
        bpy.ops.object.mode_set()
        for vertex in obj.data.vertices:
            value = 0
            for gr in vertex.groups:
                value += packBW(gr.weight)

            print(value)

            if value < 255:
                # What each group weight has to increment
                increment = (255 - value) // len(vertex.groups)
                if increment == 0:  # if the increment is too low
                    # we'll increment only the biggest group
                    biggest = 0
                    for g in range(len(vertex.groups)):
                        if vertex.groups[g].weight > vertex.groups[biggest].weight:
                            biggest = g

                    vertex.groups[biggest].weight = (packBW(vertex.groups[biggest].weight) + (255 - value)) / 255
                    obj.vertex_groups[vertex.groups[biggest].group].add([ind], vertex.groups[biggest].weight, 'REPLACE')

                else:
                    newMax = 0
                    for gr in vertex.groups:
                        gr.weight = packBW(gr.weight) + increment
                        newMax += packBW(gr.weight)
                    if newMax < 255:
                        # It's still not exact so we'll add the remainder to the biggest weight
                        biggest = 0
                        for g in range(len(vertex.groups)):
                            if vertex.groups[g].weight > biggest:
                                biggest = g

                            weight = (packBW(vertex.groups[biggest].weight) + (255 - newMax)) / 255
                            obj.vertex_groups[vertex.groups[biggest].group].add([ind], weight, 'REPLACE')

            elif value > 255:
                decrement = (value - 255) // len(vertex.groups)

                if decrement == 0:  # if the decrement is too low
                    # we'll decrement only the biggest group
                    biggest = 0
                    for g in range(len(vertex.groups)):
                        if vertex.groups[g].weight > vertex.groups[biggest].weight:
                            biggest = g

                    weight = (packBW(vertex.groups[biggest].weight) - (value - 255)) / 255
                    obj.vertex_groups[vertex.groups[biggest].group].add([ind], weight, 'REPLACE')

                else:
                    newMax = 0
                    for gr in vertex.groups:
                        weight = packBW(gr.weight) + decrement
                        obj.vertex_groups[gr.group].add([ind], weight, 'REPLACE')
                        newMax += packBW(weight)
                    if newMax != 255:
                        # It's still not exact so we'll substract the remainder to the biggest weight
                        biggest = 0
                        for g in range(len(vertex.groups)):
                            if vertex.groups[g].weight > biggest:
                                biggest = g

                            weight = (packBW(vertex.groups[biggest].weight) + (newMax - 255)) / 255
                            obj.vertex_groups[vertex.groups[biggest].group].add([ind], weight, 'REPLACE')

            ind += 1

        bpy.ops.object.mode_set(mode='EDIT')
        return{'FINISHED'}


class MESH_OT_Unk2(bpy.types.Operator):
    bl_idname = "mesh.unk2"
    bl_label = "Print unk2"

    def execute(self, context):
        max = 0
        for vertex in context.edit_object.data.vertices:
            if len(vertex.groups) > max:
                max = len(vertex.groups)
        bpy.ops.error.message('INVOKE_DEFAULT', type="Unk 2", message=str(max))

        return{'FINISHED'}


class BONE_OT_IsYAligned(bpy.types.Operator):
    bl_idname = "bone.is_y_aligned"
    bl_label = "Is +Y aligned?"

    def execute(self, context):
        bone = context.active_bone

        bpy.ops.error.message('INVOKE_DEFAULT', type="\"Is +Y aligned?\"", message=str(
            bone.head.x == bone.tail.x and bone.head.z == bone.tail.z and bone.head.y < bone.tail.y
        ))

        return{'FINISHED'}


class BonePanel(bpy.types.Panel):
    # bl_label = "RenderWare4 Animations Config"
    # bl_space_type = 'NLA_EDITOR'
    # bl_region_type = 'UI'
    # bl_context = 'object.animation_data.nla_tracks.active.strips[0]'

    bl_label = "RenderWare4 Bone"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'

    def draw(self, context):
        lay = self.layout

        row = lay.row()
        row.operator("bone.is_y_aligned", BONE_OT_IsYAligned.bl_label)


class MessageOperator(bpy.types.Operator):
    bl_idname = "error.message"
    bl_label = "Message"
    type = StringProperty()
    message = StringProperty()

    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)

    def draw(self, context):
        self.layout.label("A " + self.type.lower() + " has arrived")
        row = self.layout.split(0.9)
        # row.prop(self, "type")
        # row.prop(self, "message")
        row.label(self.type + ": " + self.message)
        row = self.layout.split(0.80)
        row.label("")
        props = row.operator("error.copy")
        props.text = self.message

#
#   The OK button in the error dialog
#


class OkOperator(bpy.types.Operator):
    bl_idname = "error.copy"
    bl_label = "Copy"

    text = StringProperty()

    def execute(self, context):

        pyperclip.copy(self.text)

        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(MESH_OT_CheckDeforming.bl_idname, text=MESH_OT_CheckDeforming.bl_label, icon='PLUGIN')
    self.layout.operator(MESH_OT_FixDeforming.bl_idname, text=MESH_OT_FixDeforming.bl_label, icon='PLUGIN')
    self.layout.operator(MESH_OT_Unk2.bl_idname, text=MESH_OT_Unk2.bl_label, icon='PLUGIN')

# REGISTER #

# bpy.app.handlers.scene_update_post.append(action_editor_update)


def register():
    # bpy.utils.register_class(RW4RenderStateLIST)
    bpy.utils.register_class(PropertyToSet)
    bpy.utils.register_class(DirectXRenderState)
    bpy.utils.register_class(DirectXSamplerState)
    bpy.utils.register_class(DirectXTextureState)
    bpy.utils.register_class(RW4AnimProperties)
    bpy.utils.register_class(RW4MaterialProperties)
    #bpy.utils.register_class(DirectXStateProperty)
    bpy.utils.register_class(LIST_OT_NewItem)
    bpy.utils.register_class(LIST_OT_DeleteItem)
    bpy.utils.register_class(OT_GenerateDefaultStates)
    #bpy.utils.register_class(RW4_DX_RenderState_LIST)
    bpy.utils.register_class(MESH_OT_CheckDeforming)
    bpy.utils.register_class(MESH_OT_FixDeforming)
    bpy.utils.register_class(MESH_OT_Unk2)
    bpy.utils.register_class(BONE_OT_IsYAligned)
    bpy.utils.register_class(OkOperator)
    bpy.utils.register_class(MessageOperator)
    bpy.types.Scene.rw4ListIndex = IntProperty(name="Index for rw4_list", default=0)  # , update=update_action_list)
    # bpy.types.VIEW3D_MT_edit_mesh.append(add_object_button)

    # bpy.app.handlers.scene_update_post.append(action_editor_update)
    # bpy.ops.add(LIST_OT_Update)
    # bpy.utils.register_class(RW4AnimUIList)


def unregister():
    bpy.utils.unregister_class(PropertyToSet)
    bpy.utils.unregister_class(DirectXRenderState)
    bpy.utils.unregister_class(DirectXSamplerState)
    bpy.utils.unregister_class(DirectXTextureState)
    bpy.utils.unregister_class(RW4MaterialProperties)
    bpy.utils.unregister_class(RW4AnimProperties)
    bpy.utils.unregister_class(LIST_OT_NewItem)
    bpy.utils.unregister_class(LIST_OT_DeleteItem)
    bpy.utils.unregister_class(OT_GenerateDefaultStates)
    #bpy.utils.unregister_class(RW4AnimProperties)
    #bpy.utils.unregister_class(RW4MaterialProperties)
    #bpy.utils.unregister_class(RW4_DX_RenderState_LIST)
    bpy.utils.unregister_class(MESH_OT_CheckDeforming)
    bpy.utils.unregister_class(MESH_OT_FixDeforming)
    bpy.utils.unregister_class(MESH_OT_Unk2)
    bpy.utils.unregister_class(BONE_OT_IsYAligned)
    bpy.utils.unregister_class(OkOperator)
    bpy.utils.unregister_class(MessageOperator)

    del bpy.types.Scene.rw4ListIndex
    # bpy.types.VIEW3D_MT_edit_mesh.remove(add_object_button)
