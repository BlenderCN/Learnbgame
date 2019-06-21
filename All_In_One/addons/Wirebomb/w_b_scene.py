import bpy
import configparser
from .b_scene import BlenderScene
from . import w_var
from . import b_tools
from . import constants


class BlenderSceneW(BlenderScene):
    """A version of the class BlenderScene that is specific for this add-on.
    
    Attributes:
        name: The name of the scene.
        renderengine: The render engine used.
        original_scene: The scene object which was passed to initialize an instance of this class.
        original_use_simplify: A boolean representing the state of simplify in original scene.
        original_simplify_subdivision: An integer representing the simplify subdivision level in original scene.
    """

    def __init__(self, scene, new_scene, new_name=None, renderer=None):
        """Creates a full copy of scene if new_scene is set to True.

        Args:
            scene: A scene object which represents the scene to copy/work on. Later referred to as the 'original scene'.
            new_scene: A boolean that if True, a full copy of scene will be created.
            new_name: An optional string representing the (new) scene's name. Must be set if new_scene is set
                to True.
            renderer: An optional string representing the (new) scene's render engine, e.g. 'CYCLES'. Must be set if
                new_scene is set to True.
        """
        self.original_scene = scene

        # saves current states to restore in the end
        self.original_use_simplify = scene.render.use_simplify
        self.original_simplify_subdivision = scene.render.simplify_subdivision
        self.original_layers = list(scene.layers)

        if new_scene:
            self.name = self.copy_scene(scene, new_name, renderer)

        else:
            if new_name is not None:
                scene.name = new_name
            self.name = scene.name

            if renderer is not None:
                scene.render.engine = renderer
        
        self.renderengine = self.get_scene().render.engine

    def prepare_fast_setup(self, revert=False):
        """Prepares scene for a faster wireframe/clay setup.

        Args:
            revert: A boolean which if True instead reverts scene to its original state (before prepare_setup).
        """
        scene = self.set_as_active()

        if not revert:
            scene.render.use_simplify = True
            scene.render.simplify_subdivision = 0
            smallest_layer, _ = min(enumerate(self.get_layers_vert_counts()), key=lambda p: p[1])
            self.set_layers((smallest_layer,))

        else:
            scene.render.use_simplify = self.original_use_simplify
            scene.render.simplify_subdivision = self.original_simplify_subdivision
            scene.layers = self.original_layers

    def set_up_clay(self):
        """Sets up clay."""
        scene = self.set_as_active()

        # adds clay material to affected meshes and saves material name
        self.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        scene.wirebomb.data_material_clay = self.add_clay_to_selected().name

    def clear_materials(self):
        """Clears all materials."""
        self.set_as_active()

        # removes all materials from affected meshes
        self.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})
        self.clear_materials_on_selected()

    def set_up_all_ao(self):
        """Sets up all the AO."""
        self.set_as_active()
        
        # sets up ambient occlusion lighting
        self.set_up_world_ao()
        self.comp_add_ao()

    def set_up_clay_only(self):
        """Sets up clay only."""
        self.set_as_active()
        
        # sets up renderlayer named 'clay' instead of 'wireframe'
        self.set_up_rlayer('clay')

        # updates progress bar to 50 %
        bpy.context.window_manager.progress_update(50)

        if w_var.cb_clear_materials and w_var.is_any_affected:
            self.clear_materials()

        # updates progress bar to 75 %
        bpy.context.window_manager.progress_update(75)
        
        if w_var.is_any_affected:
            self.set_up_clay()

        # updates progress bar to 99 %
        bpy.context.window_manager.progress_update(99)

        if w_var.cb_ao:
            self.set_up_all_ao()

        # deselects all objects as a last thing to clean up
        self.select('DESELECT', objects={'ALL'})

    def set_up_wireframe_freestyle(self):
        """Sets up the complete wireframe using the freestyle setup."""
        scene = self.set_as_active()
        
        # sets up renderlayer(s) (depending on 'Composited wireframing' checkbox) and freestyle wireframing
        # also saves freestyle linestyle name
        self.set_up_rlayer('wireframe', rlname_other='other')
        scene.wirebomb.data_freestyle_linestyle = self.add_wireframe_freestyle().name

        # updates progress bar to 50 %
        bpy.context.window_manager.progress_update(50)

        if w_var.cb_clear_materials and w_var.is_any_affected:
            self.clear_materials()

        # updates progress bar to 75 %
        bpy.context.window_manager.progress_update(75)

        if w_var.cb_clay:
            self.set_up_clay()

        # updates progress bar to 99 %
        bpy.context.window_manager.progress_update(99)

        if w_var.cb_ao and not w_var.cb_composited:
            self.set_up_all_ao()

        elif w_var.cb_composited:

            # sets up composition for wireframe and sets up ambient occlusion lighting if used
            self.comp_add_wireframe_freestyle()
            
            if scene.render.engine == 'CYCLES':
                scene.cycles.film_transparent = True

            else:
                scene.render.alpha_mode = 'TRANSPARENT'

            if w_var.cb_ao:
                self.set_up_world_ao()

        # deselects all objects as a last thing to clean up
        self.select('DESELECT', objects={'ALL'})

    def set_up_wireframe_modifier(self):
        """Sets up the complete wireframe using the modifier setup.

        If the mesh(es) you apply this to have several materials each and you don't use clay, the material of the
        wireframe will not be the expected one as it depends on the material offset set in the wireframe modifier.
        """
        scene = self.set_as_active()
        
        if w_var.cb_clear_materials and w_var.is_any_affected:
            self.clear_materials()

        # updates progress bar to 50 %
        bpy.context.window_manager.progress_update(50)

        if w_var.cb_clay:

            # adding clay material before wireframe material for material offset in wireframe modifier to be correct
            self.set_up_clay()

        # updates progress bar to 75 %
        bpy.context.window_manager.progress_update(75)

        # sets up renderlayer and adds wireframe modifier/material to affected meshes and saves wireframe material
        self.set_up_rlayer('wireframe')
        scene.wirebomb.data_material_wire = self.add_wireframe_modifier().name

        # updates progress bar to 99 %
        bpy.context.window_manager.progress_update(99)

        if w_var.cb_ao:
            self.set_up_all_ao()

        # deselects all objects as a last thing to clean up
        self.select('DESELECT', objects={'ALL'})

    def select(self, mode, types=None, types_excluded=None, layers=None, layers_excluded=None,
               objects=None, objects_excluded=None):
        """Selects or deselects objects, a special version of BlenderScene's function.

        (De)selects specific objects or objects by object types and layers.

        Args:
            mode: A string representing the mode, either 'SELECT' to select objects or 'DESELECT' to deselect objects.
            types: An optional set consisting of strings representing the object types that are to be (de)selected.
                If none specified, all types count.
            types_excluded: An optional set consisting of strings representing the object types that are to be
                deselected or left out if mode is set to 'DESELECT', these types will not be included among the
                select_types.
            layers: An optional set consisting of integers representing the layers whose objects
                are up for (de)selection. If none specified, all layers count.
            layers_excluded: An optional set consisting of integers representing the layers whose objects
                will be deselected or left out if mode is set to 'DESELECT', these layers will not be included among
                the layers in the layers variable.
            objects: An optional set consisting of objects that are to be (de)selected, need to be set if types
                variable is not set. If set, types and layers variables will act as filters on those objects.
            objects_excluded: An optional set consisting of objects that are to be deselected or left out if mode is set
                to 'DESELECT', these objects will not be included among the objects in the objects variable.
        """
        scene = self.set_as_active()
        layer_numbers = set(constants.layer_numbers)
        obj_types = set(constants.obj_types)

        # setting up types and types excluded
        if types is None or 'ALL' in types:
            types = obj_types

        if types_excluded is None:
            types_excluded = set()

        elif 'ELSE' in types_excluded:
            types_excluded = obj_types - types

        types -= types_excluded

        # setting up layers and layers excluded
        if layers is None or 'ALL' in layers:
            layers = layer_numbers

        if layers_excluded is None:
            layers_excluded = set()

        elif 'ELSE' in layers_excluded:
            layers_excluded = layer_numbers - layers

        layers -= layers_excluded

        # setting up objects and objects excluded
        if objects is None:
            objects = w_var.objects_affected

        if objects_excluded is None:
            objects_excluded = set()

        objects -= objects_excluded

        previous_area = bpy.context.area.type

        # can't change object select property while in the 'PROPERTIES' area
        bpy.context.area.type = 'VIEW_3D'

        # much quicker than looping through objects
        if 'ALL' in objects and types == obj_types and layers == layer_numbers:
            bpy.ops.object.select_all(action=mode)

        elif mode == 'SELECT':
            if objects is not None:
                for obj in scene.objects:
                    if ((obj in objects or 'ALL' in objects) and
                            obj.type in types and self.object_on_layer(obj, layers)):
                        obj.select = True

                    elif (obj in objects_excluded or 'ELSE' in objects_excluded or
                          obj.type in types_excluded or self.object_on_layer(obj, layers_excluded)):
                        obj.select = False

            else:
                for obj in scene.objects:
                    if obj.type in types and self.object_on_layer(obj, layers):
                        obj.select = True

                    elif obj.type in types_excluded or self.object_on_layer(obj, layers_excluded):
                        obj.select = False

        elif mode == 'DESELECT':
            if objects is not None:
                for obj in scene.objects:
                    if ((obj in objects or 'ALL' in objects) and
                            obj.type in types and self.object_on_layer(obj, layers)):
                        obj.select = False

            else:
                for obj in scene.objects:
                    if obj.type in types and self.object_on_layer(obj, layers):
                        obj.select = False

        else:
            raise ValueError("No such mode as '{}'.".format(mode))

        bpy.context.area.type = previous_area
        self.set_active_object(types)

    def set_up_rlayer(self, rlname, rlname_other=None, include_layers=None,
                      exclude_layers=None, mask_layers=None):
        """Sets up one or two new render layers, a special version of BlenderScene's set_up_rlayer function.

        Args:
            rlname: A string representing the name of the render layer you want to set up.
            rlname_other: An optional string representing the name of the second render layer, which is needed if the
                wireframe type is 'Freestyle' and the 'Composited wires' checkbox is checked.
            include_layers: An optional list consisting of integers representing the layers
                you want to be included in the new render layer (specific for this render layer).
            exclude_layers: An optional list consisting of integers representing the layers
                you want to be excluded in the new render layer (specific for this render layer).
            mask_layers: An optional list consisting of integers representing the layers
                you want to be masked in the new render layer (specific for this render layer).
        """
        scene = self.set_as_active()
        layer_numbers = constants.layer_numbers
        w_var.rlname = rlname

        if include_layers is None:
            include_layers = w_var.layer_numbers_all_used

        if exclude_layers is None:
            exclude_layers = []

        if mask_layers is None:
            mask_layers = []

        if w_var.cb_clear_rlayers:
            for layer in scene.render.layers[:-1]:
                scene.render.layers.remove(layer)

            scene.render.layers.active.name = rlname
            scene.render.layers.active.use = True

            new_rlayer = scene.render.layers.active

        # if not clearing render layers: creates new one
        else:
            new_rlayer = scene.render.layers.new(rlname)
            scene.render.layers.active = new_rlayer

        # there needs to be two render layers in the same scene for freestyle compositing
        if w_var.cb_composited:
            w_var.rlname_other = rlname_other
            other_rlayer = scene.render.layers.new(rlname_other)
            other_rlayer.layers[19] = True
            scene.render.layers[rlname_other].layers_zmask = (False,) * 20

        if w_var.cb_ao:
            scene.render.layers[rlname].use_pass_ambient_occlusion = True

            if w_var.cb_composited:
                scene.render.layers[rlname_other].use_pass_ambient_occlusion = True

        # because I can't deactivate a layer if it is the only active one
        new_rlayer.layers[19] = True
        
        scene.render.layers[rlname].layers_exclude = (False,) * 20
        scene.render.layers[rlname].layers_zmask = (False,) * 20

        for i in layer_numbers:
            if w_var.cb_composited:
                if i in w_var.layer_numbers_affected:
                    scene.render.layers[rlname].layers[i] = True
                    scene.render.layers[rlname_other].layers_zmask[i] = True

                else:
                    scene.render.layers[rlname].layers[i] = False

                if i in w_var.layer_numbers_other:
                    scene.render.layers[rlname_other].layers[i] = True

                else:
                    scene.render.layers[rlname_other].layers[i] = False

            else:
                if i in include_layers:
                    scene.render.layers[rlname].layers[i] = True

                else:
                    scene.render.layers[rlname].layers[i] = False

                if i in mask_layers:
                    scene.render.layers[rlname].layers_zmask[i] = True

            if i in exclude_layers:
                scene.render.layers[rlname].layers_exclude[i] = True

    def comp_add_wireframe_freestyle(self):
        """Sets up the compositor nodes for the wireframe type 'Freestyle'."""
        scene = self.set_as_active()
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        # creating the nodes
        node_alphaover = tree.nodes.new('CompositorNodeAlphaOver')
        node_alphaover.location = -25, 50

        node_rlwire = tree.nodes.new('CompositorNodeRLayers')
        node_rlwire.location = -400, 250
        node_rlwire.scene = scene
        node_rlwire.layer = w_var.rlname

        node_rlclay = tree.nodes.new('CompositorNodeRLayers')
        node_rlclay.location = -400, -75
        node_rlclay.scene = scene
        node_rlclay.layer = w_var.rlname_other

        node_comp = tree.nodes.new('CompositorNodeComposite')
        node_comp.location = 400, 65

        node_viewer = tree.nodes.new('CompositorNodeViewer')
        node_viewer.location = 400, -125

        # connecting the nodes
        links = tree.links
        links.new(node_rlwire.outputs[0], node_alphaover.inputs[1])
        links.new(node_rlclay.outputs[0], node_alphaover.inputs[2])

        if w_var.cb_ao:
            node_mixcolor_wire = tree.nodes.new('CompositorNodeMixRGB')
            node_mixcolor_wire.location = -125, 150
            node_mixcolor_wire.blend_type = 'MULTIPLY'
            node_mixcolor_wire.inputs[0].default_value = 0.730

            node_mixcolor_clay = tree.nodes.new('CompositorNodeMixRGB')
            node_mixcolor_clay.location = -125, -100
            node_mixcolor_clay.blend_type = 'MULTIPLY'
            node_mixcolor_clay.inputs[0].default_value = 0.730

            node_alphaover.location = 125, 75

            links.new(node_rlwire.outputs[0], node_mixcolor_wire.inputs[1])
            links.new(node_rlwire.outputs[10], node_mixcolor_wire.inputs[2])

            links.new(node_rlclay.outputs[0], node_mixcolor_clay.inputs[1])
            links.new(node_rlclay.outputs[10], node_mixcolor_clay.inputs[2])

            links.new(node_mixcolor_wire.outputs[0], node_alphaover.inputs[1])
            links.new(node_mixcolor_clay.outputs[0], node_alphaover.inputs[2])

            links.new(node_alphaover.outputs[0], node_comp.inputs[0])
            links.new(node_alphaover.outputs[0], node_viewer.inputs[0])

        else:
            links.new(node_alphaover.outputs[0], node_comp.inputs[0])
            links.new(node_alphaover.outputs[0], node_viewer.inputs[0])

        for node in tree.nodes:
            node.select = False

    def comp_add_ao(self):
        """Sets up the compositor nodes for the ambient occlusion (AO) effect."""
        scene = self.set_as_active()
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        # creating the nodes
        node_rlayer = tree.nodes.new('CompositorNodeRLayers')
        node_rlayer.location = -300, 100
        node_rlayer.scene = scene
        node_rlayer.layer = w_var.rlname

        node_mixcolor = tree.nodes.new('CompositorNodeMixRGB')
        node_mixcolor.location = 0, 50
        node_mixcolor.blend_type = 'MULTIPLY'
        node_mixcolor.inputs[0].default_value = 0.730

        node_comp = tree.nodes.new('CompositorNodeComposite')
        node_comp.location = 300, 130

        node_viewer = tree.nodes.new('CompositorNodeViewer')
        node_viewer.location = 300, -100

        # connecting the nodes
        links = tree.links
        links.new(node_rlayer.outputs[0], node_mixcolor.inputs[1])
        links.new(node_rlayer.outputs[10], node_mixcolor.inputs[2])
        links.new(node_mixcolor.outputs[0], node_comp.inputs[0])
        links.new(node_mixcolor.outputs[0], node_viewer.inputs[0])

        for node in tree.nodes:
            node.select = False

    def add_clay_to_selected(self):
        """Creates and/or sets the clay material to all selected objects.
        
        Returns:
            The clay material data object.
        """
        scene = self.set_as_active()

        # if the user selected a material, use it
        if w_var.cb_mat_clay:
            clay_mat = bpy.data.materials[w_var.mat_clay_name]

        # else, create a new one with the color selected
        else:
            clay_color = w_var.color_clay

            # separating rgb and alpha
            clay_color_rgb = clay_color[0:3]
            clay_color_alpha = clay_color[-1]
            clay_mat = bpy.data.materials.new('clay')
            
            renderengine = scene.wirebomb.data_renderengine
            
            if renderengine == 'CYCLES':
                clay_mat.use_nodes = True
                tree = clay_mat.node_tree
                tree.nodes.clear()

                # creating the nodes
                node_transparent = tree.nodes.new('ShaderNodeBsdfTransparent')
                node_transparent.location = -300, 100

                node_diffuse = tree.nodes.new('ShaderNodeBsdfDiffuse')
                node_diffuse.location = -300, -100
                node_diffuse.inputs[0].default_value = clay_color_rgb + (1.0, )
                node_diffuse.color = clay_color_rgb
                node_diffuse.name = 'addon_clay_color'  # referencing to this ID in the real-time change

                node_mixshader = tree.nodes.new('ShaderNodeMixShader')
                node_mixshader.location = 0, 50
                node_mixshader.inputs[0].default_value = clay_color_alpha
                node_mixshader.name = 'addon_clay_alpha'  # referencing to this ID in the real-time change

                node_output = tree.nodes.new('ShaderNodeOutputMaterial')
                node_output.location = 300, 50

                # connecting the nodes
                tree.links.new(node_transparent.outputs[0], node_mixshader.inputs[1])
                tree.links.new(node_diffuse.outputs[0], node_mixshader.inputs[2])
                tree.links.new(node_mixshader.outputs[0], node_output.inputs[0])

                for node in tree.nodes:
                    node.select = False

                # sets the viewport color
                clay_mat.diffuse_color = clay_color_rgb
            
            elif renderengine == 'BLENDER_RENDER':
                clay_mat.diffuse_color = clay_color_rgb
                clay_mat.use_transparency = True
                clay_mat.alpha = clay_color_alpha

        previous_area = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'
        previous_layers = tuple(scene.layers)

        # can't enter edit mode on objects on inactive layers
        scene.layers = (True,)*20

        for obj in scene.objects:
            if obj.select:
                # only enters edit mode on active object
                scene.objects.active = obj
                obj.data.materials.append(clay_mat)
                clay_index = obj.data.materials.find(clay_mat.name)
                obj.active_material_index = clay_index

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.material_slot_assign()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.area.type = previous_area
        scene.layers = previous_layers

        return clay_mat

    def add_wireframe_modifier(self):
        """Creates and sets up the wireframe modifier and material in cycles.

        Returns:
            The wireframe material data object.
        """
        scene = self.set_as_active()

        # if the user selected a material, use it
        if w_var.cb_mat_wire:
            wireframe_mat = bpy.data.materials[w_var.mat_wire_name]

        # else, create a new one with the color selected
        else:
            color_wire = w_var.color_wire

            # separating rgb and alpha
            wireframe_color_rgb = color_wire[0:3]
            wireframe_color_alpha = color_wire[-1]
            wireframe_mat = bpy.data.materials.new('wireframe')

            renderengine = scene.wirebomb.data_renderengine
            
            if renderengine == 'CYCLES':
                wireframe_mat.use_nodes = True
                tree = wireframe_mat.node_tree
                tree.nodes.clear()

                # creating the nodes
                node_transparent = tree.nodes.new('ShaderNodeBsdfTransparent')
                node_transparent.location = -300, 100

                node_diffuse = tree.nodes.new('ShaderNodeBsdfDiffuse')
                node_diffuse.location = -300, -100
                node_diffuse.inputs[0].default_value = wireframe_color_rgb + (1.0,)
                node_diffuse.color = wireframe_color_rgb
                node_diffuse.name = 'addon_wireframe_color' # referencing to this ID in the real-time change

                node_mixshader = tree.nodes.new('ShaderNodeMixShader')
                node_mixshader.location = 0, 50
                node_mixshader.inputs[0].default_value = wireframe_color_alpha
                node_mixshader.name = 'addon_wireframe_alpha' # referencing to this ID in the real-time change

                node_output = tree.nodes.new('ShaderNodeOutputMaterial')
                node_output.location = 300, 50

                # connecting the nodes
                tree.links.new(node_transparent.outputs[0], node_mixshader.inputs[1])
                tree.links.new(node_diffuse.outputs[0], node_mixshader.inputs[2])
                tree.links.new(node_mixshader.outputs[0], node_output.inputs[0])

                for node in tree.nodes:
                    node.select = False

                # sets the viewport color
                wireframe_mat.diffuse_color = wireframe_color_rgb

            elif renderengine == 'BLENDER_RENDER':
                wireframe_mat.diffuse_color = wireframe_color_rgb
                wireframe_mat.use_transparency = True
                wireframe_mat.alpha = wireframe_color_alpha

        self.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})

        for obj in scene.objects:
            if obj.select:
                obj.data.materials.append(wireframe_mat)
                modifier_wireframe = obj.modifiers.new(name='Wireframe', type='WIREFRAME')
                modifier_wireframe.use_even_offset = False  # Causes spikes on some models
                modifier_wireframe.use_replace = False
                modifier_wireframe.thickness = w_var.slider_wt_modifier

                # arbitrary high number because wire material is always added to end
                modifier_wireframe.material_offset = 12345

                # referencing to this ID in the real-time change
                modifier_wireframe.name = 'addon_wireframe'

        return wireframe_mat

    def add_wireframe_freestyle(self):
        """Enables and sets up freestyle wireframing in cycles.

        Returns:
            The linestyle data object used in the freestyle rendering.
        """
        scene = self.set_as_active()
        previous_area = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'
        previous_layers = tuple(scene.layers)

        # can't enter edit mode on objects on inactive layers
        scene.layers = (True,)*20
        self.select('SELECT', {'MESH'}, objects_excluded={'ELSE'})

        for obj in scene.objects:
            if obj.select:
                scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.mark_freestyle_edge()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.area.type = previous_area
        scene.layers = previous_layers

        scene.render.use_freestyle = True
        scene.render.layers.active = scene.render.layers[w_var.rlname]

        for n in scene.render.layers.active.freestyle_settings.linesets:
            scene.render.layers.active.freestyle_settings.linesets.remove(n)

        lineset = scene.render.layers.active.freestyle_settings.linesets.new('wireframe')
        lineset.select_edge_mark = True
        lineset.select_crease = False

        wire_color = w_var.color_wire
        wire_thickness = w_var.slider_wt_freestyle

        wire_color_rgb = wire_color[0:3]
        wire_color_alpha = wire_color[-1]

        linestyle = bpy.data.linestyles.new('wire_style')
        linestyle.color = wire_color_rgb
        linestyle.alpha = wire_color_alpha
        linestyle.thickness = wire_thickness

        scene.render.layers.active.freestyle_settings.linesets.active.linestyle = linestyle

        return linestyle

    def set_up_world_ao(self):
        """Sets up a new world with the ambient occlusion (AO) effect in cycles."""
        scene = self.set_as_active()
        new_world = bpy.context.blend_data.worlds.new('World of Wireframe')
        scene.world = new_world
        new_world.light_settings.use_ambient_occlusion = True
        new_world.light_settings.ao_factor = 0.3

        renderengine = scene.wirebomb.data_renderengine

        if renderengine == 'CYCLES':
            new_world.use_nodes = True
            new_world.node_tree.nodes[1].inputs[0].default_value = (1, 1, 1, 1)

            for node in new_world.node_tree.nodes:
                node.select = False
        
        elif renderengine == 'BLENDER_RENDER':
            new_world.horizon_color = (1, 1, 1)

    def add_objects_used(self):
        """Adds all used objects to three sets in w_var variables: affected objects, other objects and all used objects.
        """
        scene = self.set_as_active()
        scene.wirebomb.data_objects_affected.clear()
        scene.wirebomb.data_objects_other.clear()
        scene.wirebomb.data_objects_all.clear()

        if w_var.cb_only_selected:
            for obj in scene.objects:
                if obj.select:
                    if obj.type == 'MESH':

                        # adding objects to blender session-temporary sets
                        w_var.objects_affected.add(obj)

                        # adding object names to "permanent" collection properties
                        scene.wirebomb.data_objects_affected.add().name = obj.name
                    
                    # if it's not a mesh but it's selected, add to other objects
                    else:
                        
                        # adding objects to blender session-temporary sets
                        w_var.objects_other.add(obj)

                        # adding object names to "permanent" collection properties
                        scene.wirebomb.data_objects_other.add().name = obj.name

                elif self.object_on_layer(obj, w_var.layer_numbers_other):

                    # adding objects to blender session-temporary sets
                    w_var.objects_other.add(obj)

                    # adding object names to "permanent" collection properties
                    scene.wirebomb.data_objects_other.add().name = obj.name

                w_var.objects_all_used.add(obj)
                scene.wirebomb.data_objects_all.add().name = obj.name

        else:
            for obj in scene.objects:
                if self.object_on_layer(obj, w_var.layer_numbers_affected):
                    if obj.type == 'MESH':

                        # adding objects to blender session-temporary sets
                        w_var.objects_affected.add(obj)

                        # adding object names to "permanent" collection properties
                        scene.wirebomb.data_objects_affected.add().name = obj.name
                    
                    # if it's not a mesh but on an affected layer, add to other objects
                    else:

                        # adding objects to blender session-temporary sets
                        w_var.objects_other.add(obj)

                        # adding objects' names to "permanent" collection properties
                        scene.wirebomb.data_objects_other.add().name = obj.name

                elif self.object_on_layer(obj, w_var.layer_numbers_other):

                    # adding objects to blender session-temporary sets
                    w_var.objects_other.add(obj)

                    # adding objects' names to "permanent" collection properties
                    scene.wirebomb.data_objects_other.add().name = obj.name

                w_var.objects_all_used.add(obj)
                scene.wirebomb.data_objects_all.add().name = obj.name
        
        if len(w_var.objects_affected) > 0:
            w_var.is_any_affected = True

    def wirebomb_error_check(self):
        """Checks for any possible errors."""
        scene = self.set_as_active()
        success = True
        error_msg = ""

        if (w_var.cb_only_selected and not self.check_any_selected('MESH') 
                and not len(w_var.layer_numbers_other) > 0):
            error_msg += "~ Checkbox 'Only selected' is activated but no mesh is selected and no other included layers are selected!\n"
            success = False

            # used for row alert in __init__.py
            w_var.error_101 = True

        if (not w_var.cb_only_selected and
                not len(w_var.layer_numbers_affected) > 0 and not len(w_var.layer_numbers_other) > 0):
            error_msg += "~ No layers selected! Maybe you forgot to use 'Only selected'?\n"
            success = False

        if w_var.cb_mat_wire and w_var.mat_wire_name == '':
            error_msg += '~ No wireframe material selected!\n'
            success = False

        if w_var.cb_mat_clay and w_var.mat_clay_name == '':
            error_msg += '~ No clay material selected!\n'
            success = False

        if len(w_var.scene_name_1) == 0 and w_var.cb_backup:
            error_msg += '~ No wireframe/clay scene name!\n'
            success = False

            # used for row alert in __init__.py
            w_var.error_301 = True

        return success, error_msg

    def wirebomb_config_load(self, filepath):
        """Loads an INI config file from filepath."""
        scene = self.set_as_active()

        config = configparser.ConfigParser()
        config.read(filepath)

        if 'WIREFRAME TYPE' in config and 'wireframe_method' in config['WIREFRAME TYPE']:
            scene.wirebomb.wireframe_method = config['WIREFRAME TYPE']['wireframe_method']

        if 'CHECKBOXES' in config:
            if 'cb_backup' in config['CHECKBOXES']:
                scene.wirebomb.cb_backup = eval(config['CHECKBOXES']['cb_backup'])

            if 'cb_clear_rlayers' in config['CHECKBOXES']:
                scene.wirebomb.cb_clear_rlayers = eval(config['CHECKBOXES']['cb_clear_rlayers'])

            if 'cb_clear_materials' in config['CHECKBOXES']:
                scene.wirebomb.cb_clear_materials = eval(config['CHECKBOXES']['cb_clear_materials'])

            if 'cb_composited' in config['CHECKBOXES']:
                scene.wirebomb.cb_composited = eval(config['CHECKBOXES']['cb_composited'])

            if 'cb_only_selected' in config['CHECKBOXES']:
                scene.wirebomb.cb_only_selected = eval(config['CHECKBOXES']['cb_only_selected'])

            if 'cb_ao' in config['CHECKBOXES']:
                scene.wirebomb.cb_ao = eval(config['CHECKBOXES']['cb_ao'])

            if 'cb_clay' in config['CHECKBOXES']:
                scene.wirebomb.cb_clay = eval(config['CHECKBOXES']['cb_clay'])

            if 'cb_clay_only' in config['CHECKBOXES']:
                scene.wirebomb.cb_clay_only = eval(config['CHECKBOXES']['cb_clay_only'])

            if 'cb_mat_wire' in config['CHECKBOXES']:
                scene.wirebomb.cb_mat_wire = eval(config['CHECKBOXES']['cb_mat_wire'])

            if 'cb_mat_clay' in config['CHECKBOXES']:
                scene.wirebomb.cb_mat_clay = eval(config['CHECKBOXES']['cb_mat_clay'])

        if 'COLORS SET' in config:
            if 'color_wireframe' in config['COLORS SET']:
                scene.wirebomb.color_wire = eval(config['COLORS SET']['color_wireframe'])

            if 'color_clay' in config['COLORS SET']:
                scene.wirebomb.color_clay = eval(config['COLORS SET']['color_clay'])

        if 'MATERIALS SET' in config:
            if 'wireframe' in config['MATERIALS SET']:
                if config['MATERIALS SET']['wireframe'] in bpy.data.materials:
                    scene.wirebomb.material_wire = config['MATERIALS SET']['wireframe']

            if 'clay' in config['MATERIALS SET']:
                if config['MATERIALS SET']['clay'] in bpy.data.materials:
                    scene.wirebomb.material_clay = config['MATERIALS SET']['clay']

        if 'SLIDERS' in config:
            if 'slider_wt_freestyle' in config['SLIDERS']:
                scene.wirebomb.slider_wt_freestyle = eval(config['SLIDERS']['slider_wt_freestyle'])

            if 'slider_wt_modifier' in config['SLIDERS']:
                scene.wirebomb.slider_wt_modifier = eval(config['SLIDERS']['slider_wt_modifier'])

        if 'LAYERS SELECTED' in config:
            if 'layers_affected' in config['LAYERS SELECTED']:
                scene.wirebomb.layers_affected = eval(config['LAYERS SELECTED']['layers_affected'])

            if 'layers_other' in config['LAYERS SELECTED']:
                scene.wirebomb.layers_other = eval(config['LAYERS SELECTED']['layers_other'])

        if 'SCENE NAME SET' in config:
            if 'scene_name_1' in config['SCENE NAME SET']:
                scene.wirebomb.scene_name_1 = config['SCENE NAME SET']['scene_name_1']

    def wirebomb_config_save(self, filepath):
        """Saves an INI config file to filepath."""
        scene = self.set_as_active()
        config = configparser.ConfigParser()

        config['WIREFRAME TYPE'] = {'wireframe_method': scene.wirebomb.wireframe_method}

        config['CHECKBOXES'] = {'cb_backup': scene.wirebomb.cb_backup,
                                'cb_clear_rlayers': scene.wirebomb.cb_clear_rlayers,
                                'cb_clear_materials': scene.wirebomb.cb_clear_materials,
                                'cb_composited': scene.wirebomb.cb_composited,
                                'cb_only_selected': scene.wirebomb.cb_only_selected,
                                'cb_ao': scene.wirebomb.cb_ao,
                                'cb_clay': scene.wirebomb.cb_clay,
                                'cb_clay_only': scene.wirebomb.cb_clay_only,
                                'cb_mat_wire': scene.wirebomb.cb_mat_wire,
                                'cb_mat_clay': scene.wirebomb.cb_mat_clay}

        config['COLORS SET'] = {'color_wireframe': list(scene.wirebomb.color_wire),
                                'color_clay': list(scene.wirebomb.color_clay)}

        config['MATERIALS SET'] = {'wireframe': scene.wirebomb.material_wire,
                                   'clay': scene.wirebomb.material_clay}

        config['SLIDERS'] = {'slider_wt_freestyle': scene.wirebomb.slider_wt_freestyle,
                             'slider_wt_modifier': scene.wirebomb.slider_wt_modifier}

        config['LAYERS SELECTED'] = {'layers_affected': list(scene.wirebomb.layers_affected),
                                     'layers_other': list(scene.wirebomb.layers_other)}

        config['SCENE NAME SET'] = {'scene_name_1': scene.wirebomb.scene_name_1}

        with open(filepath, 'w') as configfile:
            config.write(configfile)

    def wirebomb_set_variables(self):
        """Sets variables in w_var with data from the UI, also resets some variables."""
        scene = self.set_as_active()

        # resetting render layer names
        w_var.rlname = ''
        w_var.rlname_other = ''

        # resetting objects selected
        w_var.objects_affected = set()
        w_var.objects_other = set()
        w_var.objects_all_used = set()
        w_var.is_any_affected = False

        # from interface:
        # wireframe type
        w_var.wireframe_method = scene.wirebomb.wireframe_method

        # checkboxes
        w_var.cb_backup = scene.wirebomb.cb_backup
        w_var.cb_clear_rlayers = scene.wirebomb.cb_clear_rlayers
        w_var.cb_clear_materials = scene.wirebomb.cb_clear_materials
        w_var.cb_composited = w_var.cb_composited_active and scene.wirebomb.cb_composited
        w_var.cb_only_selected = scene.wirebomb.cb_only_selected
        w_var.cb_ao = scene.wirebomb.cb_ao
        w_var.cb_clay = scene.wirebomb.cb_clay
        w_var.cb_clay_only = w_var.cb_clay_only_active and scene.wirebomb.cb_clay_only
        w_var.cb_mat_wire = w_var.cb_mat_wire_active and scene.wirebomb.cb_mat_wire
        w_var.cb_mat_clay = w_var.cb_mat_clay_active and scene.wirebomb.cb_mat_clay

        # colors set
        w_var.color_wire = scene.wirebomb.color_wire
        w_var.color_clay = scene.wirebomb.color_clay

        # materials set (names)
        w_var.mat_wire_name = scene.wirebomb.material_wire
        w_var.mat_clay_name = scene.wirebomb.material_clay

        # sliders
        w_var.slider_wt_freestyle = scene.wirebomb.slider_wt_freestyle
        w_var.slider_wt_modifier = scene.wirebomb.slider_wt_modifier

        # layers selected
        layers_affected = self.set_layers_affected()
        layers_other = self.set_layers_other(layers_affected)
        w_var.layer_numbers_affected = b_tools.layerlist_to_numberset(layers_affected)
        w_var.layer_numbers_other = b_tools.layerlist_to_numberset(layers_other)

        # affected and other layers together, | is logical OR operator
        w_var.layer_numbers_all_used = w_var.layer_numbers_affected | w_var.layer_numbers_other

        # scene name set
        w_var.scene_name_1 = scene.wirebomb.scene_name_1

    def set_layers_affected(self):
        """Sets all layers who will be affected by wireframing and/or clay material, in a list.

        Returns:
            A list with booleans representing all the layers that will be affected affected by
                wireframing and/or clay material.
        """
        scene = self.set_as_active()

        if w_var.cb_only_selected:
            layers_affected = [False, ]*20

            for obj in scene.objects:
                if obj.select and obj.type == 'MESH':
                    layers_affected = b_tools.manipulate_layerlists('add', layers_affected, obj.layers)

        else:
            layers_affected = list(scene.wirebomb.layers_affected)

        return layers_affected

    def set_layers_other(self, layers_affected):
        """Sets all layers who will be included in the render layer just as they are, in a list.

        Args:
            layers_affected: An array consisting of booleans representing the 'Affected' layers.

        Returns:
            A list with booleans representing all the layers that will be included in the render layer just as they are.
        """
        scene = self.set_as_active()
        layers_other = list(scene.wirebomb.layers_other)

        for index in range(20):
            if layers_other[index] and layers_affected[index]:
                layers_other[index] = False

        return layers_other

