import os
import bpy
import bge_netlogic

class TreeCodeWriterOperator(bpy.types.Operator):
    bl_idname = "bgenetlogic.treecodewriter_operator"
    bl_label = "Timed code writer"
    timer = None

    def modal(self, context, event):
        if event.type == "TIMER":
            bge_netlogic._consume_update_tree_code_queue()
        return {'PASS_THROUGH'}

    def execute(self, context):
        if context.window == None:
            bge_netlogic._tree_code_writer_started = False
            return {"FINISHED"}
        if context.window_manager == None:
            bge_netlogic._tree_code_writer_started = False
            return {"FINISHED"}
        if self.timer is not None:
            return {'FINISHED'}
        self.timer = context.window_manager.event_timer_add(1.0, context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


class WaitForKeyOperator(bpy.types.Operator):
    bl_idname = "bge_netlogic.waitforkey"
    bl_label = "Press a Key"
    keycode = bpy.props.StringProperty()
    def __init__(self):
        self.socket = None
        self.node = None
        pass
    def __del__(self): pass
    def execute(self, context):
        return {'FINISHED'}
    def cleanup(self, context):
        if self.socket.value == "Press a key...":
            self.socket.value = ""
        self.socket = None
        self.node = None
        context.region.tag_redraw()
    pass
    def modal(self, context, event):
        if event.type == "MOUSEMOVE":
            dx = event.mouse_x - event.mouse_prev_x
            dy = event.mouse_y - event.mouse_prev_y
            if dx != 0 or dy != 0:
                self.cleanup(context)
                return {'FINISHED'}
        if event.value == "PRESS":
            if event.value == "LEFTMOUSE":
                return {'FINISHED'}
            else:
                value = event.type
                if(self.socket): self.socket.value = value
                else: self.node.value = value
                self.cleanup(context)
                return {'FINISHED'}
        return {'PASS_THROUGH'}
    def invoke(self, context, event):
        self.socket = context.socket
        self.node = context.node
        if(not self.socket) and (not self.node): 
            print("no socket or node")
            return {'FINISHED'}
        if(self.socket):
            self.socket.value = "Press a key..."
        else:
            self.node.value = "Press a key..."
        context.region.tag_redraw()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class NLImportProjectNodes(bpy.types.Operator):
    bl_idname = "bge_netlogic.import_nodes"
    bl_label = "Import Logic Nodes"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        tree_type = context.space_data.tree_type
        return tree_type == bge_netlogic.ui.BGELogicTree.bl_idname

    def _create_directories(self):
        local_bge_netlogic_folder = bpy.path.abspath("//bgelogic")
        if not os.path.exists(local_bge_netlogic_folder):
            os.mkdir(local_bge_netlogic_folder)
        local_cells_folder = bpy.path.abspath("//bgelogic/cells")
        if not os.path.exists(local_cells_folder):
            os.mkdir(local_cells_folder)
        local_nodes_folder = bpy.path.abspath("//bgelogic/nodes")
        if not os.path.exists(local_nodes_folder):
            os.mkdir(local_nodes_folder)
        return local_cells_folder, local_nodes_folder

    def _entry_filename(self, p):
        ws = p.rfind("\\")
        us = p.rfind("/")
        if us >= 0 and us > ws:
            return p.split("/")[-1]
        if ws >= 0 and ws > us:
            return p.split("\\")[-1]
        return p

    def _generate_unique_filename(self, output_dir, file_name):
        dot_index = file_name.rfind(".")
        name_part = file_name[:dot_index]
        ext_part = file_name[dot_index + 1:]
        path = os.path.join(output_dir, file_name)
        index = 0
        while os.path.exists(path):
            name = '{}_{}.{}'.format(name_part, index, ext_part)
            path = os.path.join(output_dir, name)
            index += 1
            if index > 100: raise RuntimeError("I give up: can't find a unique name for {}".format(file_name))
        return path

    def _zipextract(self, zip, entry_name, output_dir):
        import shutil
        with zip.open(entry_name) as entry:
            out_file = self._generate_unique_filename(output_dir, self._entry_filename(entry_name))
            with open(out_file, "wb") as f:
                shutil.copyfileobj(entry, f)

    def execute(self, context):
        import zipfile
        if not self.filepath: return {"FINISHED"}
        if not self.filepath.endswith(".zip"): return {"FINISHED"}
        if not zipfile.is_zipfile(self.filepath): return {"FINISHED"}
        with zipfile.ZipFile(self.filepath, "r") as f:
            entries = f.namelist()
            cells = [x for x in entries if x.startswith("bgelogic/cells/") and x.endswith(".py")]
            nodes = [x for x in entries if x.startswith("bgelogic/nodes/") and x.endswith(".py")]
            if cells or nodes:
                local_cells_folder, local_nodes_folder = self._create_directories()
                for cell in cells: self._zipextract(f, cell, local_cells_folder)
                for node in nodes: self._zipextract(f, node, local_nodes_folder)
        _do_load_project_nodes(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def _do_load_project_nodes(context):
    print("loading project nodes and cells...")
    current_file = context.blend_data.filepath
    file_dir = os.path.dirname(current_file)
    netlogic_dir = os.path.join(file_dir, "bgelogic")
    cells_dir = os.path.join(netlogic_dir, "cells")
    nodes_dir = os.path.join(netlogic_dir, "nodes")
    if os.path.exists(nodes_dir):
        bge_netlogic.remove_project_user_nodes()
        bge_netlogic.load_nodes_from(nodes_dir)


class NLLoadProjectNodes(bpy.types.Operator):
    bl_idname = "bge_netlogic.load_nodes"
    bl_label = "Reload Project Nodes"
    bl_description = "Reload the custom nodes' definitions found in the ../netlogic subdirectory"

    @classmethod
    def poll(cls, context):
        current_file = context.blend_data.filepath
        if not current_file: return False
        if not os.path.exists(current_file): return False
        tree = context.space_data.edit_tree
        if not tree: return False
        if not (tree.bl_idname == bge_netlogic.ui.BGELogicTree.bl_idname): return False
        return context.space_data.edit_tree is not None

    def execute(self, context):
        _do_load_project_nodes(context)
        return {"FINISHED"}


class NLSelectTreeByNameOperator(bpy.types.Operator):
    bl_idname = "bge_netlogic.select_tree_by_name"
    bl_label = "Edit"
    bl_description = "Edit"
    tree_name = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assert self.tree_name is not None
        assert len(self.tree_name) > 0
        blt_groups = [g for g in bpy.data.node_groups if (g.name == self.tree_name) and (g.bl_idname == bge_netlogic.ui.BGELogicTree.bl_idname)]
        if len(blt_groups) != 1: print("Something went wrong here...")
        for t in blt_groups: context.space_data.node_tree = t
        return {'FINISHED'}


class NLRemoveTreeByNameOperator(bpy.types.Operator):
    bl_idname = "bge_netlogic.remove_tree_by_name"
    bl_label = "Remove"
    bl_description = "Remove the tree from the selected objects"
    tree_name = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        import bge_netlogic.utilities as tools
        stripped_tree_name = tools.strip_tree_name(self.tree_name)
        py_module_name = tools.py_module_name_for_stripped_tree_name(stripped_tree_name)
        for ob in [x for x in context.scene.objects if x.select and tools.object_has_treeitem_for_treename(x, self.tree_name)]:
            gs = ob.game
            controllers = [c for c in gs.controllers if py_module_name in c.name]
            actuators = [a for a in gs.actuators if py_module_name in a.name]
            sensors = [s for s in gs.sensors if py_module_name in s.name]
            for c in controllers:
                bge_netlogic.debug("remove", c.name, "from", ob.name)
                bpy.ops.logic.controller_remove(controller=c.name, object=ob.name)
            for a in actuators:
                bge_netlogic.debug("remove", a.name, "from", ob.name)
                bpy.ops.logic.actuator_remove(actuator=a.name, object=ob.name)
            for s in sensors:
                bge_netlogic.debug("remove", s.name, "from", ob.name)
                bpy.ops.logic.sensor_remove(sensor=s.name, object=ob.name)
            bge_netlogic.utilities.remove_tree_item_from_object(ob, self.tree_name)
            bge_netlogic.utilities.remove_network_initial_status_key(ob, self.tree_name)
        return {'FINISHED'}

    def remove_tree_from_object_pcoll(self, ob, treename):
        index = None
        i = 0
        for item in ob.bgelogic_treelist:
            if item.tree_name == treename:
                index = i
                break
            i += 1
        if index is not None:
            bge_netlogic.debug("remove tree", treename, "from object", ob.name)
            ob.bgelogic_treelist.remove(index)


class NLApplyLogicOperator(bpy.types.Operator):
    bl_idname = "bge_netlogic.apply_logic"
    bl_label = "Apply Logic"
    bl_description = "Apply the current tree to the selected objects of the current scene"
    owner = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        tree = context.space_data.edit_tree
        if not tree: return False
        if not (tree.bl_idname == bge_netlogic.ui.BGELogicTree.bl_idname): return False
        scene = context.scene
        for ob in scene.objects:
            if ob.select: return True
        return False

    def execute(self, context):
        current_scene = context.scene
        tree = context.space_data.edit_tree
        tree.use_fake_user = True
        py_module_name = bge_netlogic.utilities.py_module_name_for_tree(tree)
        selected_objects = [ob for ob in current_scene.objects if ob.select]
        initial_status = bge_netlogic.utilities.compute_initial_status_of_tree(tree.name, selected_objects)
        initial_status = True if initial_status is None else False
        for obj in selected_objects:
            bge_netlogic.debug("Apply operator to object", obj.name, self.owner)
            self._setup_logic_bricks_for_object(tree, py_module_name, obj, context)
            tree_collection = obj.bgelogic_treelist
            contains = False
            for t in tree_collection:
                if t.tree_name == tree.name:
                    contains = True
                    break
            if not contains:
                new_entry = tree_collection.add()
                new_entry.tree_name = tree.name
                #this will set both new_entry.tree_initial_status and add a game property that makes the status usable at runtime
                bge_netlogic.utilities.set_network_initial_status_key(obj, tree.name, initial_status)
        return {'FINISHED'}

    def _setup_logic_bricks_for_object(self, tree, py_module_name, obj, context):
        game_settings = obj.game
        #TODO: allow custom sensors (like one time, on mouse press... things like that)
        sensor_name = "NLP" + py_module_name
        sensor = None
        for s in game_settings.sensors:
            if s.name == sensor_name:
                sensor = s
                break
        if sensor is None:
            bpy.ops.logic.sensor_add(type="DELAY", object=obj.name)
            sensor = game_settings.sensors[-1]
        sensor.pin = True
        sensor.name = sensor_name
        sensor.type = "DELAY"
        sensor.use_repeat = True
        sensor.delay = 0
        sensor.duration = 0
        #create the controller
        controller_name = "NLC" + py_module_name
        controller = None
        for c in game_settings.controllers:
            if c.name == controller_name:
                controller = c
                break
        if controller is None:
            bpy.ops.logic.controller_add(type="PYTHON", object=obj.name)
            controller = game_settings.controllers[-1]
        controller.name = controller_name
        controller.type = "PYTHON"
        controller.mode = "MODULE"
        controller.module = bge_netlogic.utilities.py_controller_module_string(py_module_name)
        #link the brick
        sensor.link(controller)
        pass
    pass


class NLGenerateLogicNetworkOperator(bpy.types.Operator):
    bl_idname = "bge_netlogic.generate_logicnetwork"
    bl_label = "Generate LogicNetwork"
    bl_description = "Create the code needed to execute the current logic tree"

    @classmethod
    def poll(cls, context):
        tree = context.space_data.edit_tree
        if not tree: return False
        if not (tree.bl_idname == bge_netlogic.ui.BGELogicTree.bl_idname): return False
        return context.space_data.edit_tree is not None

    def __init__(self):
        pass

    def _create_external_text_buffer(self, context, buffer_name):
        file_path = bpy.path.abspath("//{}".format(buffer_name))
        return FileTextBuffer(file_path)

    def _create_text_buffer(self, context, buffer_name, external=False):
        if external is True: return self._create_external_text_buffer(context, buffer_name)
        blender_text_data_index = bpy.data.texts.find(buffer_name)
        blender_text_data = None
        if blender_text_data_index < 0:
            blender_text_data = bpy.data.texts.new(name=buffer_name)
        else:
            blender_text_data = bpy.data.texts[blender_text_data_index]
        return BLTextBuffer(blender_text_data)

    def execute(self, context):
        #ensure that the local "bgelogic" folder exists
        local_bgelogic_folder = bpy.path.abspath("//bgelogic")
        if not os.path.exists(local_bgelogic_folder):
            try:
                os.mkdir(local_bgelogic_folder)
            except PermissionError:
                print("Cannot generate the code because the blender file has not been saved or the user has no write permission for the containing folder.")
                return {"FINISHED"}
        #write the current tree in a python module, in the directory of the current blender file
        if (context is None) or (context.space_data is None) or (context.space_data.edit_tree is None):
            print("NLGenerateLogicNetworkOperator.execute: no context, space_data or edit_tree. Abort writing tree.")
            return {"FINISHED"}
        tree = context.space_data.edit_tree
        tree_code_generator.TreeCodeGenerator().write_code_for_tree(tree)
        return {"FINISHED"}

class NLSwitchInitialNetworkStatusOperator(bpy.types.Operator):
    bl_idname = "bge_netlogic.switch_network_status"
    bl_label = "Enable/Disable at start"
    bl_description = "Enables of disables the logic tree at start for the selected objects"
    tree_name = bpy.props.StringProperty()
    current_status = bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        current_status = self.current_status
        new_status = not current_status
        tree_name = self.tree_name
        scene = context.scene
        updated_objects = [ob for ob in scene.objects if ob.select and bge_netlogic.utilities.object_has_treeitem_for_treename(ob, tree_name)]
        for ob in updated_objects:
            bge_netlogic.utilities.set_network_initial_status_key(ob, tree_name, new_status)
        bge_netlogic.update_current_tree_code()
        return {'FINISHED'}	

#Popup the code templates for custom nodes and cells
class NLPopupTemplatesOperator(bpy.types.Operator):
    bl_idname = "bge_netlogic.popup_templates"
    bl_label = "Show Custom Node Templates"
    bl_description = "Load the template code for custom nodes and cells in the text editor"
    @classmethod
    def poll(cls, context): return True
    def execute(self, context):
        node_code = self.get_or_create_text_object("my_custom_nodes.py")
        cell_code = self.get_or_create_text_object("my_custom_cells.py")
        self.load_template(node_code, "my_custom_nodes.txt")
        self.load_template(cell_code, "my_custom_cells.txt")
        self.report({"INFO"}, "Templates available in the text editor")
        return {'FINISHED'}
    def load_template(self, text_object, file_name):
        import os
        this_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(this_dir)
        templates_dir = os.path.join(parent_dir, "templates")
        template_file = os.path.join(templates_dir, file_name)
        text_data = "Error Reading Template File"
        with open(template_file, "r") as f: text_data = f.read()
        text_object.from_string(text_data)
    def get_or_create_text_object(self, name):
        index = bpy.data.texts.find(name)
        if index < 0:
            bpy.ops.text.new()
            result = bpy.data.texts[-1]
            result.name = name
            return result
        else:
            return bpy.data.texts[index]
        pass