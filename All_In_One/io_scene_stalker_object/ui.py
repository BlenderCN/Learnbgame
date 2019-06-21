
import bpy


class StalkerObjectPanel(bpy.types.Panel):
    bl_label = 'S.T.A.L.K.E.R. Object'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object and not context.object.parent

    def draw(self, context):
        layout = self.layout
        s = context.object.stalker
        layout.prop(s, 'object_type')
        if s.object_type == 'OTHER':
            layout.label('Object Flags:')
            row1 = layout.row(align=True)
            row2 = layout.row(align=True)
            row1.prop(s, 'flagDynamic', toggle=True)
            row1.prop(s, 'flagProgressive', toggle=True)
            row1.prop(s, 'flagUsingLOD', toggle=True)
            row2.prop(s, 'flagHOM', toggle=True)
            row2.prop(s, 'flagMultipleUsage', toggle=True)
            row2.prop(s, 'flagSoundOccluder', toggle=True)
        layout.prop(s, 'user_data')
        layout.prop(s, 'motion_reference')
        layout.prop(s, 'lod_reference')


class StalkerMaterialPanel(bpy.types.Panel):
    bl_label = 'S.T.A.L.K.E.R.'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.material

    def draw(self, context):
        layout = self.layout
        split1 = layout.split(percentage=0.3)
        split1.label('Shader:')
        row1 = split1.row(align=True)
        row1.prop(context.material.stalker, 'engine_shader', text='')
        row1.menu('Shader_Menu', text='', icon='TRIA_DOWN')

        split2 = layout.split(percentage=0.3)
        split2.label('Compiler:')
        row2 = split2.row(align=True)
        row2.prop(context.material.stalker, 'compiler_shader', text='')
        row2.menu('Compiler_Menu', text='', icon='TRIA_DOWN')

        split3 = layout.split(percentage=0.3)
        split3.label('Material:')
        row3 = split3.row(align=True)
        row3.prop(context.material.stalker, 'game_material', text='')
        row3.menu('Game_Material_Menu', text='', icon='TRIA_DOWN')

        layout.prop(context.material.stalker, 'two_sided')
