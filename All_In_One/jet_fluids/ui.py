
import bpy


class JetFluidDomainPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'DOMAIN'


class JetFluidColliderPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'COLLIDER'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'object_type')
        lay.prop(jet, 'friction_coefficient')


class JetFluidEmitterPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'EMITTER'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'object_type')
        lay.prop(jet, 'is_enable')
        lay.prop(jet, 'one_shot')
        lay.prop(jet, 'particles_count')
        lay.prop(jet, 'max_number_of_particles')
        lay.prop(jet, 'emitter_jitter')
        lay.prop(jet, 'emitter_seed')
        lay.prop(jet, 'allow_overlapping')
        lay.prop(jet, 'velocity')


class JetFluidSolversPanel(JetFluidDomainPanel):
    bl_label = "Jet Fluid Solvers"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        row = lay.row()

        # solvers
        lay.prop(jet, 'solver_type')
        lay.prop(jet, 'advection_solver_type')
        lay.prop(jet, 'diffusion_solver_type')
        lay.prop(jet, 'pressure_solver_type')

        # settings
        lay.prop(jet, 'max_cfl')
        lay.prop(jet, 'compressed_linear_system')

        # substeps
        lay.prop(jet, 'fixed_substeps')
        row = lay.row()
        if not jet.fixed_substeps:
            row.active = False
        row.prop(jet, 'fixed_substeps_count')


class JetFluidBoundaryPanel(JetFluidDomainPanel):
    bl_label = "Jet Fluid Boundary"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.label('Domain Close:')

        row = lay.row()
        row.prop(jet, 'bound_right')
        row.prop(jet, 'bound_left')

        row = lay.row()
        row.prop(jet, 'bound_front')
        row.prop(jet, 'bound_back')

        row = lay.row()
        row.prop(jet, 'bound_up')
        row.prop(jet, 'bound_down')

        # connectivity
        lay.label('Mesh Close:')

        row = lay.row()
        row.prop(jet, 'close_right')
        row.prop(jet, 'close_left')

        row = lay.row()
        row.prop(jet, 'close_front')
        row.prop(jet, 'close_back')

        row = lay.row()
        row.prop(jet, 'close_up')
        row.prop(jet, 'close_down')

        # connectivity
        lay.label('Mesh Connectivity:')

        row = lay.row()
        row.prop(jet, 'con_right')
        row.prop(jet, 'con_left')

        row = lay.row()
        row.prop(jet, 'con_front')
        row.prop(jet, 'con_back')

        row = lay.row()
        row.prop(jet, 'con_up')
        row.prop(jet, 'con_down')


class JetFluidWorldPanel(JetFluidDomainPanel):
    bl_label = "Jet Fluid World"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'viscosity')
        lay.prop(jet, 'gravity')


class JetFluidColorPanel(JetFluidDomainPanel):
    bl_label = "Jet Fluid Color"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'use_colors')
        if jet.use_colors:
            lay.prop(jet, 'simmulate_color_type')
            if jet.simmulate_color_type == 'SINGLE_COLOR':
                lay.prop(jet, 'particles_color')


class JetFluidCreatePanel(JetFluidDomainPanel):
    bl_label = "Jet Fluid Create"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements

        # mesh properties
        lay.prop(jet, 'create_mesh')
        if jet.create_mesh:
            lay.prop_search(jet, 'mesh_object', bpy.data, 'objects')

        # particles properties
        lay.prop(jet, 'create_particles')
        if jet.create_particles:
            lay.prop_search(jet, 'particles_object', bpy.data, 'objects')

        # standart particle system
        split = lay.split(percentage=0.75, align=True)
        split.operator('jet_fluid.create_particle_system')
        split.alert = True
        split.operator('jet_fluid.reset_physic_cache', text='Clear')


class JetFluidDebugPanel(JetFluidDomainPanel):
    bl_label = "Jet Fluid Debug"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'show_particles')
        if jet.show_particles:
            lay.prop(jet, 'particle_size')
            lay.prop(jet, 'color_type')
            row = lay.row()
            if jet.color_type != 'PARTICLE_COLOR':
                row.prop(jet, 'color_1', text='')
                if jet.color_type == 'VELOCITY':
                    row.prop(jet, 'color_2', text='')
                    lay.prop(jet, 'max_velocity')


class JetFluidCachePanel(JetFluidDomainPanel):
    bl_label = "Jet Fluid Cache"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'cache_folder')


class JetFluidMeshPanel(JetFluidDomainPanel):
    bl_label = "Jet Fluid Mesh"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        row = lay.row()

        # bake mesh
        split = lay.split(percentage=0.75, align=True)
        split.operator('jet_fluid.bake_mesh')
        split.alert = True
        split.operator('jet_fluid.reset_mesh', text="Reset")
        lay.prop(jet, 'resolution_mesh')


class JetFluidSimulatePanel(JetFluidDomainPanel):
    bl_label = "Jet Fluid Simulate"
    bl_options = set()

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements

        # object type
        lay.prop(jet, 'object_type')

        # bake particles
        split = lay.split(percentage=0.75, align=True)
        split.operator('jet_fluid.bake_particles')
        split.alert = True
        split.operator('jet_fluid.reset_particles', text="Reset")

        lay.prop(jet, 'resolution')

        # fps
        lay.label('Time:')
        lay.prop(jet, 'use_scene_fps')
        row = lay.row()
        if jet.use_scene_fps:
            row.active = False
            row.prop(context.scene.render, 'fps')
        else:
            row.prop(jet, 'fps')


class JetFluidPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'NONE'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'object_type')


def add_jet_fluid_button(self, context):
    obj = context.scene.objects.active
    if not obj.type == 'MESH':
        return

    column = self.layout.column(align=True)
    split = column.split(percentage=0.5)
    column_left = split.column()
    column_right = split.column()

    if obj.jet_fluid.is_active:
        column_right.operator(
            "jet_fluid.remove", 
            text="Jet Fluid", 
            icon='X'
        )
    else:
        column_right.operator(
            "jet_fluid.add", 
            text="Jet Fluid", 
            icon='MOD_FLUIDSIM'
        )


__CLASSES__ = [
    JetFluidPanel,
    JetFluidSimulatePanel,
    JetFluidMeshPanel,
    JetFluidSolversPanel,
    JetFluidBoundaryPanel,
    JetFluidCachePanel,
    JetFluidCreatePanel,
    JetFluidWorldPanel,
    JetFluidColorPanel,
    JetFluidDebugPanel,
    JetFluidEmitterPanel,
    JetFluidColliderPanel
]


def register():
    bpy.types.PHYSICS_PT_add.append(add_jet_fluid_button)
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        bpy.utils.unregister_class(class_)
    bpy.types.PHYSICS_PT_add.remove(add_jet_fluid_button)
