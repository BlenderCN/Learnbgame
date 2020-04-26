import os
import json
import bpy

from unipipe import worker
from unipipe.core.objects import resource

from ..gui import popup

#TODO: Remove hard-coded project setting 'bug_and_dylan'
class UnipipeAppendPublishedModel(bpy.types.Operator):
    """ Import(append) a published model resource based on the current resource """
    bl_idname = "wm.unipipe_append_published_model"
    bl_label = "Append published model"

    @classmethod
    def poll(cls, context):
        if worker.ImportWorker().get_resource_from_context() is not None:
            return True

    def execute(self, context):
        imp_w = worker.ImportWorker()
        res = imp_w.get_resource_from_context()
        imp_w.import_published_resource(resource=res, maintain_links=False, type='model')

        popup.show_message_box(message="Appended model collection for resource: {}".format(res.name),
                               title='Success...',
                               icon='INFO')

        self.report({'INFO'}, "Appended model collection for resource: {}".format(res.name))

        return {'FINISHED'}


class UnipipeAppendPublishedMaterial(bpy.types.Operator):
    """ Import(append) a published material resource based on the current resource """
    bl_idname = "wm.unipipe_append_published_material"
    bl_label = "Append published material"

    @classmethod
    def poll(cls, context):

        if worker.ImportWorker().get_resource_from_context() is not None:
            return True

    def execute(self, context):

        # Remove old materials first
        for material in bpy.data.materials:
            material.user_clear()
            bpy.data.materials.remove(material)

        # Append new materials
        imp_w = worker.ImportWorker()
        res = imp_w.get_resource_from_context()
        imp_w.import_published_resource(resource=res, maintain_links=False, type='shader')

        # Process assignment file TODO

        popup.show_message_box(message="Appended materials for resource: {}".format(res.name),
                               title='Success...',
                               icon='INFO')

        self.report({'INFO'}, "Appended materials for resource: {}".format(res.name))

        return {'FINISHED'}


class UnipipeLinkPublishedFinal(bpy.types.Operator):
    """ Import(link) a published final resource """
    bl_idname = "wm.unipipe_link_published_final"
    bl_label = "Link published Final"
    bl_property = "resource_enum"

    @classmethod
    def poll(cls, context):
        return True

    def get_resource_items(self, context):
        """
        Returns a list of tuples for EnumProperty use

        """
        item_list = []
        idx = 0

        res_items = worker.ResourceWorker().get_all_resources(project='bug_and_dylan', resource_type='component')

        if not isinstance(res_items, (list, tuple)):
            res_items = [res_items]

        for each in res_items:
            item_list.append((each.name, each.name, ""))
            idx += 1

        return item_list

    resource_enum = bpy.props.EnumProperty(items=get_resource_items)

    def execute(self, context):

        name = self.resource_enum  # access selection

        # Create workers
        ctx_w = worker.ContextWorker()
        imp_w = worker.ImportWorker()

        # Instantiate a resource
        res = resource.Component(project='bug_and_dylan', name=name, type='final')

        # Check resource availability
        res_path = imp_w.construct_publish_path(resource=res, version=0, ext=ctx_w.app_interface.primary_extension)

        if not os.path.isfile(res_path):
            popup.show_message_box(message='No published final available for: "{}"'.format(name),
                                   title='File not available...',
                                   icon='INFO')
            return {'CANCELLED'}

        # Import the resource
        imp_w.import_published_resource(resource=res, maintain_links=True)

        self.report({'INFO'}, "Linked Final'd Resource: {}".format(name))

        return {'FINISHED'}

    def invoke(self, context, event):

        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

# TODO: This is almost an exact copy of UnipipeLinkPublishedFinal. Need to unify
class UnipipeLinkPublishedCollection(bpy.types.Operator):
    """ Import(link) a published final resource """
    bl_idname = "wm.unipipe_link_published_collection"
    bl_label = "Link published Collection"
    bl_property = "resource_enum"

    @classmethod
    def poll(cls, context):
        return True

    def get_resource_items(self, context):
        """
        Returns a list of tuples for EnumProperty use

        """
        item_list = []
        idx = 0

        res_items = worker.ResourceWorker().get_all_resources(project='bug_and_dylan', resource_type='context')

        if not isinstance(res_items, (list, tuple)):
            res_items = [res_items]

        for each in res_items:
            item_list.append((each.name, each.name, ""))
            idx += 1

        return item_list

    resource_enum = bpy.props.EnumProperty(items=get_resource_items)

    def execute(self, context):

        name = self.resource_enum  # access selection

        # Create workers
        ctx_w = worker.ContextWorker()
        imp_w = worker.ImportWorker()

        # Instantiate a resource
        res = resource.Context(project='bug_and_dylan', name=name, type='collection')

        # Check resource availability
        res_path = imp_w.construct_publish_path(resource=res, version=0, ext=ctx_w.app_interface.primary_extension)
        print(res_path)
        if not os.path.isfile(res_path):
            popup.show_message_box(message='No published collection available for: "{}"'.format(name),
                                   title='File not available...',
                                   icon='INFO')
            return {'CANCELLED'}

        # Import the resource
        imp_w.import_published_resource(resource=res, maintain_links=True)

        self.report({'INFO'}, "Linked Collection Resource: {}".format(name))

        return {'FINISHED'}

    def invoke(self, context, event):

        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}


class UnipipeBuildFinal(bpy.types.Operator):
    """ Build the final component from published sub-components """
    bl_idname = "wm.unipipe_build_final"
    bl_label = "Build published Final"

    @classmethod
    def poll(cls, context):

        res = worker.ImportWorker().get_resource_from_context()

        if res is not None and hasattr(res, 'type') and res.type == 'final':
            return True

    def execute(self, context):

        # Discover resource
        imp_w = worker.ImportWorker()
        res = imp_w.get_resource_from_context()

        # Append the rig
        imp_w.import_published_resource(resource=res, maintain_links=False, type='rig')

        # Append the shaders - remove old shaders first
        for material in bpy.data.materials:
            material.user_clear()
            bpy.data.materials.remove(material)

        try:
            imp_w.import_published_resource(resource=res, maintain_links=False, type='shader')

            # Process assignment file
            path = imp_w.construct_publish_path(resource=res, version=-1, type='shader', ext='json')
            if os.path.isfile(path):
                with open(path, 'r') as readFile:
                    data = json.loads(readFile.read())
                    process_assignment(data)

        except Exception as e:
            self.report({'INFO'}, "Successfully built final resource: {} without material. "
                                  "Mat Error: {}".format(res.name, str(e)))

            return {'FINISHED'}

        popup.show_message_box(message="Successfully built final resource: {}".format(res.name),
                               title='Success...',
                               icon='INFO')

        self.report({'INFO'}, "Successfully built final resource: {}".format(res.name))

        return {'FINISHED'}


def process_assignment(data):

    for each in bpy.data.objects:

        if each.type != 'MESH':
            continue

        geo_name = each.name

        if geo_name not in data.keys():
            print('skipping geo: "{}"'.format(geo_name))
            continue

        material_names = data[each.name]

        # remove old materials
        each.data.materials.clear()

        # add materials
        for mat_name in material_names:
            each.data.materials.append(bpy.data.materials[mat_name])


def register():
    bpy.utils.register_class(UnipipeAppendPublishedModel)
    bpy.utils.register_class(UnipipeAppendPublishedMaterial)
    bpy.utils.register_class(UnipipeBuildFinal)
    bpy.utils.register_class(UnipipeLinkPublishedFinal)
    bpy.utils.register_class(UnipipeLinkPublishedCollection)


def unregister():
    bpy.utils.unregister_class(UnipipeAppendPublishedModel)
    bpy.utils.unregister_class(UnipipeAppendPublishedMaterial)
    bpy.utils.unregister_class(UnipipeBuildFinal)
    bpy.utils.unregister_class(UnipipeLinkPublishedFinal)
    bpy.utils.unregister_class(UnipipeLinkPublishedCollection)

"""
TODO: To add in maybe?
import bpy
import json
#sel = bpy.context.selected_pose_bones

#for each in sel:
#    each.rotation_mode = 'YXZ'

def read_handles_to_file(path):
    
    armt = bpy.data.armatures['Dylan_armature']
    all_bones = armt.bones
    data = {}
    
    for each in all_bones:
        
        if each.bbone_segments > 1:
            # Found bendy bone
            print('found bbone: {}'.format(each.name))
            data[each.name] = {'bbone_custom_handle_start': None, 'bbone_custom_handle_end': None}
            
            if each.bbone_custom_handle_start:
                print('- start handle: {}'.format(each.bbone_custom_handle_start.name))
                data[each.name]['bbone_custom_handle_start'] = each.bbone_custom_handle_start.name
                
            if each.bbone_custom_handle_end:
                print('- end handle: {}'.format(each.bbone_custom_handle_end.name))
                data[each.name]['bbone_custom_handle_end'] = each.bbone_custom_handle_end.name
    
    with open(path, 'w') as outfile:
        json.dump(obj=data, fp=outfile, indent=4)
        
    print(json.dumps(data, indent=4, sort_keys=True))


def write_handles_from_file(path):
    armt = bpy.data.armatures['Dylan_armature']
    
    with open(path, 'r') as infile:
        data = json.loads(infile.read())
        
        for key, value in data.items():
            
            if value['bbone_custom_handle_start']:
                armt.bones[key].bbone_custom_handle_start = armt.bones[value['bbone_custom_handle_start']]
                
            if value['bbone_custom_handle_end']:
                armt.bones[key].bbone_custom_handle_end = armt.bones[value['bbone_custom_handle_end']]

fpath = '/tmp/test_handles.json'

#read_handles_to_file(path=fpath)
write_handles_from_file(path=fpath)
"""