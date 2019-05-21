import bpy
from . import constants


class BlenderScene:
    """Contains useful functions for manipulating a blender scene.

    Attributes:
        name: The name of the scene.
        original_scene: The scene object which was passed to initialize an instance of this class.
        renderengine: The render engine used.
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

        if new_scene:
            self.name = self.copy_scene(scene, new_name, renderer)

        else:
            if new_name is not None:
                scene.name = new_name
            self.name = scene.name

            if renderer is not None:
                scene.render.engine = renderer
        
        self.renderengine = self.get_scene().render.engine
        
    def __str__(self):
        return '<BlenderScene: {0}, original_scene: {1}>'.format(self.get_name(), self.get_original_scene.name)

    @staticmethod
    def copy_scene(scene, wanted_name, renderer=None):
        """Creates a full copy of the scene.

        Args:
            scene: A scene object which represents the scene to copy.
            wanted_name: A string representing the new scene's wanted name.
            renderer: A string representing the new scene's render engine, e.g. 'CYCLES'.

        Returns:
            A string that is the new scene's name.
        """
        
        # need to collect scene names before I copy the scene
        scene_names = [sc.name for sc in bpy.data.scenes]

        bpy.context.screen.scene = scene
        bpy.ops.scene.new(type='FULL_COPY')

        # this is for better handling of duplicate scene names when creating a new scene
        n = 1
        name = wanted_name

        while True: 
            if name not in scene_names:
                bpy.context.screen.scene.name = name
                break

            else:
                name = wanted_name + '.' + str(n).zfill(3)
                n += 1
        
        if renderer is not None:
            bpy.data.scenes[name].render.engine = renderer

        return name
    
    def get_name(self):
        """Returns the name of the scene."""
        return self.name
        
    def get_scene(self):
        """Returns the scene object linked to this instance."""
        return bpy.data.scenes[self.name]

    def get_original_scene(self):
        """Returns the scene object which was passed to initialize this instance."""
        return self.original_scene
    
    def get_renderengine(self):
        """Returns the scene's render engine."""
        return self.renderengine

    def set_as_active(self):
        """Sets the scene as active.

        Returns:
            The scene object.
        """
        scene = self.get_scene()
        bpy.context.screen.scene = scene

        return scene

    def set_layers(self, layers, deactivate_other=True):
        """Activates layer(s) passed in and deactivates other layer(s) depending on deactive_other variable.

        If you have an array of booleans you should instead use: scene.layers = array

        Args:
            layers: An array consisting of integers representing the layers to be activated.
            deactivate_other: A boolean which if True deactivates all other layers.
        """
        scene = self.set_as_active()

        if deactivate_other:
            new_layers = [False, ]*20

            for n in layers:
                new_layers[n] = True

            scene.layers = new_layers

        else:
            for n in layers:
                scene.layers[n] = True

    def get_layers_vert_counts(self):
        """Returns a list of integers where element i represents the number of vertices on layer i.

        Returns:
            A list of integers where element i represents the number of vertices on layer i.
        """
        scene = self.set_as_active()

        layers_vert_counts = [0, ] * 20

        for obj in scene.objects:
            if obj.type != 'MESH':
                continue

            for n, layer in enumerate(obj.layers):
                if layer:
                    layers_vert_counts[n] += len(obj.data.vertices)

        return layers_vert_counts

    def set_active_object(self, obj_types=constants.obj_types):
        """Sets the active object to be one among the selected objects.

        Args:
            obj_types: An optional array consisting of strings representing the object type(s)
                that the active object is allowed to be. If none specified, all types count.
        """
        scene = self.set_as_active()

        if 'ALL' in obj_types:
            obj_types = constants.obj_types

        for obj in scene.objects:
            if obj.select is True and obj.type in obj_types:
                scene.objects.active = obj
                break

    def object_on_layer(self, obj, layer_numbers):
        """Checks if an object is on any of the layers represented by layer_numbers.

        Args:
            obj: The object it will check.
            layer_numbers: A list consisiting of integers representing the layers that it will check
                if the object is on.

        Returns:
            True if the object is on any of the layers represented by layer_numbers, False otherwise.
        """
        scene = self.set_as_active()

        if obj.name in scene.objects:
            for n in layer_numbers:
                if obj.layers[n]:
                    return True

        return False

    def check_any_selected(self, obj_types=constants.obj_types):
        """Checks the scene if any object is selected.

        Args:
            obj_types: An optional array consisting of strings representing the object type(s)
                that the object is allowed to be. If none specified, all types count.

        Returns:
            True if any object is selected, False otherwise.
        """
        scene = self.set_as_active()

        if 'ALL' in obj_types:
            obj_types = constants.obj_types

        for obj in scene.objects:
            if obj.type in obj_types and obj.select is True:
                return True

        return False

    def select(self, mode, types=None, types_excluded=None, layers=None, layers_excluded=None,
               objects=None, objects_excluded=None):
        """Selects or deselects objects.

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
        if objects_excluded is None:
            objects_excluded = set()

        if objects is not None:
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

    def move_selected_to_layer(self, to_layer):
        """Moves the selected object(s) to the given layer(s) (to_layer).

        Args:
            to_layer: An array consisting of integers representing the layers to which the object(s) will be moved.
        """
        scene = self.set_as_active()
        previous_layers = tuple(scene.layers)
        previous_area = bpy.context.area.type

        layers = [False, ] * 20

        for i in to_layer:
            layers[i] = True

        # can't move objects from inactive layers
        scene.layers = (True,) * 20

        # can't use operators while in the 'PROPERTIES' area
        bpy.context.area.type = 'VIEW_3D'

        bpy.ops.object.move_to_layer(layers=layers)

        bpy.context.area.type = previous_area
        scene.layers = previous_layers

    def copy_selected_to_layer(self, to_layer):
        """Copies the selected object(s) to the given layer(s) (to_layer).

        Args:
            to_layer: An array consisting of integers representing the layers to which the object(s) will be copied.
        """
        scene = self.set_as_active()
        previous_layers = tuple(scene.layers)
        previous_area = bpy.context.area.type

        # can't duplicate objects on inactive layers
        scene.layers = (True,) * 20

        # can't use operators while in the 'PROPERTIES' area
        bpy.context.area.type = 'VIEW_3D'

        bpy.ops.object.duplicate()
        self.move_selected_to_layer(to_layer)

        bpy.context.area.type = previous_area
        scene.layers = previous_layers

    def copy_selected_to_scene(self, to_scene):
        """Copies the selected object(s) to the given scene (to_scene).

        Args:
            to_scene: A scene object representing the scene to which the objects will be copied.
        """
        scene = self.set_as_active()
        previous_layers = tuple(scene.layers)
        previous_area = bpy.context.area.type

        # can't duplicate objects on inactive layers
        scene.layers = (True,) * 20

        # can't use operators while in the 'PROPERTIES' area
        bpy.context.area.type = 'VIEW_3D'

        bpy.ops.object.duplicate()
        bpy.ops.object.make_links_scene(scene=to_scene)
        bpy.ops.object.delete()

        scene.layers = previous_layers
        bpy.context.area.type = previous_area

    def clear_materials_on_selected(self):
        """Removes all materials from all the selected objects in the scene."""
        scene = self.set_as_active()
        previous_area = bpy.context.area.type
        previous_layers = tuple(scene.layers)

        bpy.context.active_object.data.materials.clear()

        # can't use operators while in the 'PROPERTIES' area
        bpy.context.area.type = 'VIEW_3D'

        # can't copy materials to objects on inactive layers
        scene.layers = (True,) * 20

        bpy.ops.object.material_slot_copy()

        bpy.context.area.type = previous_area
        scene.layers = previous_layers

    def selected_objects_to_set(self, obj_types=constants.obj_types):
        """Puts all the selected objects in a set.

        Args:
            obj_types: An optional array consisting of strings representing the object type(s) it will affect
                of the selected objects. If none specified, all types count.

        Returns:
            A set containing the selected objects.
        """
        scene = self.set_as_active()
        selected_objects = set()

        if 'ALL' in obj_types:
            obj_types = constants.obj_types

        for obj in scene.objects:
            if obj.select and obj.type in obj_types:
                selected_objects.add(obj)

        return selected_objects

    def set_up_rlayer(self, new, rlname, visible_layers=None, include_layers=None,
                      exclude_layers=None, mask_layers=None):
        """Sets up a scene render layer.

        Args:
            new: A boolean which if True, a new render layer will be created. The name of this render layer is
                represented by rlname.
            rlname: A string representing the name of the render layer you want to set up.
            visible_layers: An optional list consisting of integers representing the layers you want to be visible
                -i.e. all layers you want to render, which will aslo be visible in the viewport-in the new render layer.
            include_layers: An optional list consisting of integers representing the layers
                you want to be included in the new render layer (specific for this render layer).
            exclude_layers: An optional list consisting of integers representing the layers
                you want to be excluded in the new render layer (specific for this render layer).
            mask_layers: An optional list consisting of integers representing the layers
                you want to be masked in the new render layer (specific for this render layer).
        """
        scene = self.set_as_active()
        layer_numbers = constants.layer_numbers

        if visible_layers is None:
            visible_layers = layer_numbers

        if include_layers is None:
            include_layers = layer_numbers

        if exclude_layers is None:
            exclude_layers = []

        if mask_layers is None:
            mask_layers = []

        if new:
            new_rlayer = scene.render.layers.new(rlname)
            scene.render.layers.active = new_rlayer

        # because I can't deactivate a layer if it is the only active one
        scene.layers[19] = True
        scene.render.layers[rlname].layers[19] = True

        for i in layer_numbers:
            if i in include_layers:
                scene.render.layers[rlname].layers[i] = True

            else:
                scene.render.layers[rlname].layers[i] = False

            if i in visible_layers:
                scene.layers[i] = True

            else:
                scene.layers[i] = False

            if i in exclude_layers:
                scene.render.layers[rlname].layers_exclude[i] = True

            else:
                scene.render.layers[rlname].layers_exclude[i] = False

            if i in mask_layers:
                scene.render.layers[rlname].layers_zmask[i] = True

            else:
                scene.render.layers[rlname].layers_zmask[i] = False

    def view3d_pivotpoint(self, action, pivotpoint=None):
        """Manipulates the 3D view's pivot point by setting it or getting it.

        Args:
            action: A string representing the action. Either 'set' to set the pivot point
                or 'get' to get the current pivot point.
            pivotpoint: If action equals 'set', this string represents the pivot point you want to set.

        Returns:
            If action equals 'get', returns a string representing the 3D view's current pivot point.
        """
        self.set_as_active()
        previous_area = bpy.context.area.type

        # can't change pivot point while in the 'PROPERTIES' area
        bpy.context.area.type = 'VIEW_3D'

        if action == 'set':
            bpy.context.space_data.pivot_point = pivotpoint
            bpy.context.area.type = previous_area

        elif action == 'get':
            pivotpoint = bpy.context.space_data.pivot_point
            bpy.context.area.type = previous_area
            return pivotpoint
