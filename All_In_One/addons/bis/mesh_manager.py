# Nikita Akimov
# interplanety@interplanety.org

import json
import os
import re
import sys
import tempfile
import bpy
import zipfile
from mathutils import Vector
from .WebRequests import WebRequest
from .bis_items import BISItems
from .addon import Addon
from .mesh_modifiers import MeshModifierCommon
from . import cfg
from .bl_types_conversion import BLVector


class MeshManager:

    _mesh_limit_vert_count = 50000      # max number of vertices im mesh
    _mesh_limit_file_size = 3145728     # max exported to obj and zipped file size (3 Mb)

    @staticmethod
    def items_from_bis(context, search_filter, page, update_preview):
        # get page of items list from BIS
        rez = None
        request = WebRequest.send_request({
            'for': 'get_items',
            'search_filter': search_filter,
            'page': page,
            'storage': __class__.storage_type(context),
            'update_preview': update_preview
        })
        if request:
            request_rez = json.loads(request.text)
            rez = request_rez['stat']
            if request_rez['stat'] == 'OK':
                preview_to_update = BISItems.update_previews_from_data(data=request_rez['data']['items'], list_name=__class__.storage_type(context))
                if preview_to_update:
                    request = WebRequest.send_request({
                        'for': 'update_previews',
                        'preview_list': preview_to_update,
                        'storage': __class__.storage_type(context)
                    })
                    if request:
                        previews_update_rez = json.loads(request.text)
                        if previews_update_rez['stat'] == 'OK':
                            BISItems.update_previews_from_data(data=previews_update_rez['data']['items'], list_name=__class__.storage_type(context))
                BISItems.create_items_list(request_rez['data']['items'], __class__.storage_type(context))
                context.window_manager.bis_get_meshes_info_from_storage_vars.current_page = page
                context.window_manager.bis_get_meshes_info_from_storage_vars.current_page_status = request_rez['data']['status']
        return rez

    @staticmethod
    def storage_type(context=None):
        if context:
            return context.area.spaces.active.type
        else:
            return 'VIEW_3D'

    @staticmethod
    def to_bis(mesh_list=[], name='', tags=''):
        rez = {"stat": "ERR", "data": {"text": "Error to save"}}
        if mesh_list:
            if not name:
                name = mesh_list[0].name
            meshes_in_json = {
                'obj_file_name': name,
                'meshes': []
            }
            for i, mesh in enumerate(mesh_list):
                # remove animation data
                mesh.animation_data_clear()
                # mesh to json
                mesh_in_json = {
                    'bis_mesh_uid': i,   # uid = number in "meshes" list
                    'origin': BLVector.to_json(mesh.location),
                    'modifiers': []
                }
                # modifiers stack
                mesh.name += '<bis_mesh_uid>' + str(i) + '</bis_mesh_uid>'    # add bis_mesh_uid for mesh to connect with saved modifiers stack
                mesh_in_json['modifiers'] = __class__.modifiers_to_json(mesh)
                meshes_in_json['meshes'].append(mesh_in_json)
            with tempfile.TemporaryDirectory() as temp_dir:
                mesh_obj_path = __class__.export_to_obj(mesh_list=mesh_list, name=name, export_to=temp_dir)
                if mesh_obj_path and os.path.exists(mesh_obj_path):
                    tags += (';' if tags else '') + '{0[0]}.{0[1]}'.format(bpy.app.version)
                    request = WebRequest.send_request(data={
                        'for': 'add_item',
                        'storage': __class__.storage_type(),
                        'item_body': json.dumps(meshes_in_json),
                        'item_name': name,
                        'item_tags': tags,
                        'addon_version': Addon.current_version()
                    }, files={
                        'mesh_file': open(mesh_obj_path, 'rb')
                    })
                    if request:
                        rez = json.loads(request.text)
                        if rez['stat'] == 'OK':
                            for mesh in mesh_list:
                                mesh['bis_uid'] = rez['data']['id']
                                mesh['bis_uid_name'] = name
                        else:
                            bpy.ops.message.messagebox('INVOKE_DEFAULT', message=rez['stat'] + ': ' + rez['data']['text'])
            if cfg.to_server_to_file:
                with open(os.path.join(os.path.dirname(bpy.data.filepath), 'send_to_server.json'), 'w') as currentFile:
                    json.dump(meshes_in_json, currentFile, indent=4)
            # remove bis_uid from meshes names
            for mesh in mesh_list:
                mesh.name = re.sub('<bis_mesh_uid>.*</bis_mesh_uid>', '', mesh.name)
        else:
            rez['data']['text'] = 'No selected mesh to save'
        return rez

    @staticmethod
    def from_bis(context, bis_item_id):
        rez = {"stat": "ERR", "data": {"text": "No Id", "content": None}}
        if bis_item_id:
            request = WebRequest.send_request({
                'for': 'get_item',
                'storage': __class__.storage_type(),
                'id': bis_item_id
            })
            if request:
                request_rez = json.loads(request.text)
                if request_rez['stat'] == 'OK':
                    item_in_json = json.loads(request_rez['data']['item'])
                    if 'file_attachment' in item_in_json and 'link_type' in item_in_json['file_attachment']:
                        with tempfile.TemporaryDirectory() as temp_dir:
                            if item_in_json['file_attachment']['link_type'] == 'internal':
                                request_file = WebRequest.send_request({
                                    'for': 'get_item_file_attachment',
                                    'storage': __class__.storage_type(),
                                    'id': bis_item_id
                                })
                                if request_file:
                                    zip_file_name = str(bis_item_id) + '.zip'
                                    zip_file_path = os.path.join(temp_dir, zip_file_name)
                                    with open(zip_file_path, 'wb') as temp_item_file_attachment:
                                        temp_item_file_attachment.write(request_file.content)
                                    if cfg.from_server_to_file:
                                        from shutil import copyfile
                                        copyfile(zip_file_path, os.path.join(os.path.dirname(bpy.data.filepath), zip_file_name))
                                    __class__._deselect_all(context)
                                    __class__.import_from_obj(context, zip_file_path, obj_file_name=item_in_json['obj_file_name'])
                                    # add mesh data from json to mesh
                                    for mesh in context.selected_objects:
                                        if '<bis_mesh_uid>' in mesh.name:
                                            mesh_bis_uid = int(re.search('<bis_mesh_uid>(.*)</bis_mesh_uid>', mesh.name).group(1))
                                            # origin
                                            mesh_origin = Vector((0, 0, 0))
                                            BLVector.from_json(mesh_origin, item_in_json['meshes'][mesh_bis_uid]['origin'])
                                            __class__._set_mesh_origin(context=context, mesh=mesh, to=mesh_origin)
                                            # modifiers
                                            __class__.modifiers_from_json(mesh=mesh, modifiers_in_json=item_in_json['meshes'][mesh_bis_uid]['modifiers'])
                                            # remove bis_mesh_uid from meshes names
                                            mesh.name = re.sub('<bis_mesh_uid>.*</bis_mesh_uid>', '', mesh.name)
                                            # set uid
                                            mesh['bis_uid'] = bis_item_id
                                            mesh['bis_uid_name'] = BISItems.get_item_name_by_id(item_id=bis_item_id, storage=__class__.storage_type())
                            elif item_in_json['file_attachment']['link_type'] == 'external':
                                # external links - not supports at present
                                pass
        else:
            bpy.ops.message.messagebox('INVOKE_DEFAULT',  message=rez['stat'] + ': ' + rez['data']['text'])
        return rez

    @staticmethod
    def update_in_bis(bis_uid, mesh_list=[], name=''):
        rez = {"stat": "ERR", "data": {"text": "Error to update"}}
        if mesh_list:
            if bis_uid:
                if not name:
                    name = mesh_list[0].name
                meshes_in_json = {
                    'obj_file_name': name,
                    'meshes': []
                }
                for i, mesh in enumerate(mesh_list):
                    # remove animation data
                    mesh.animation_data_clear()
                    # mesh to json
                    mesh_in_json = {
                        'bis_mesh_uid': i,   # uid = number in "meshes" list
                        'origin': BLVector.to_json(mesh.location),
                        'modifiers': []
                    }
                    # modifiers stack
                    mesh.name += '<bis_mesh_uid>' + str(i) + '</bis_mesh_uid>'    # add bis_mesh_uid for mesh to connect with saved modifiers stack
                    mesh_in_json['modifiers'] = __class__.modifiers_to_json(mesh)
                    meshes_in_json['meshes'].append(mesh_in_json)
                with tempfile.TemporaryDirectory() as temp_dir:
                    mesh_obj_path = __class__.export_to_obj(mesh_list=mesh_list, name=name, export_to=temp_dir)
                    if mesh_obj_path and os.path.exists(mesh_obj_path):
                        request = WebRequest.send_request(data={
                            'for': 'update_item',
                            'storage': __class__.storage_type(),
                            'item_body': json.dumps(meshes_in_json),
                            'item_name': name,
                            'item_id': bis_uid,
                            'addon_version': Addon.current_version()
                        }, files={
                            'mesh_file': open(mesh_obj_path, 'rb')
                        })
                        if request:
                            rez = json.loads(request.text)
                            if rez['stat'] == 'OK':
                                for mesh in mesh_list:
                                    mesh['bis_uid'] = rez['data']['id']
                                    mesh['bis_uid_name'] = name
                            else:
                                bpy.ops.message.messagebox('INVOKE_DEFAULT', message=rez['stat'] + ': ' + rez['data']['text'])
                if cfg.to_server_to_file:
                    with open(os.path.join(os.path.dirname(bpy.data.filepath), 'send_to_server.json'), 'w') as currentFile:
                        json.dump(meshes_in_json, currentFile, indent=4)
                # remove bis_uid from meshes names
                for mesh in mesh_list:
                    mesh.name = re.sub('<bis_mesh_uid>.*</bis_mesh_uid>', '', mesh.name)
            else:
                rez['data']['text'] = 'Can not update unsaved mesh group. Save it first.'
        else:
            rez['data']['text'] = 'No selected mesh to save'
        return rez

    @staticmethod
    def export_to_obj(mesh_list, name, export_to):
        # saves mesh to the export_to directory in obj format and zip it. Returns full path to file.
        rez = None
        if mesh_list:
            vertices_in_meshes = 0
            for mesh in mesh_list:
                vertices_in_meshes += len(mesh.data.vertices)
            if vertices_in_meshes <= __class__._mesh_limit_vert_count:
                obj_file_name = name + '.obj'
                obj_file_path = os.path.join(export_to, obj_file_name)
                bpy.ops.export_scene.obj(
                    filepath=obj_file_path,
                    check_existing=False,
                    axis_forward='Y',
                    axis_up='Z',
                    use_selection=True,
                    use_mesh_modifiers=False,
                    use_edges=False,
                    use_normals=False,
                    use_uvs=True,
                    use_materials=False
                )
                if os.path.exists(obj_file_path):
                    zip_file_name = name + '.zip'
                    zip_file_path = os.path.join(export_to, zip_file_name)
                    zip_file = zipfile.ZipFile(zip_file_path, 'w')
                    zip_file.write(obj_file_path, compress_type=zipfile.ZIP_DEFLATED, arcname=obj_file_name)
                    zip_file.close()
                    if os.path.exists(zip_file_path):
                        if cfg.to_server_to_file:
                            from shutil import copyfile
                            copyfile(zip_file_path, os.path.join(os.path.dirname(bpy.data.filepath), zip_file_name))
                        if os.stat(zip_file_path).st_size < __class__._mesh_limit_file_size:
                            rez = zip_file_path
                        else:
                            bpy.ops.message.messagebox('INVOKE_DEFAULT', message='ERR: Saving meshes must be less 3 Mb after zip export')
            else:
                bpy.ops.message.messagebox('INVOKE_DEFAULT', message='ERR: Saving meshes must be less 50 000 vertices at all')
        else:
            bpy.ops.message.messagebox('INVOKE_DEFAULT', message='ERR: No meshes to save')
        return rez

    @staticmethod
    def import_from_obj(context, zip_fipe_path, obj_file_name):
        # add meshes to scene from zipped archive with obj file
        if context.active_object and context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
        __class__._deselect_all(context)
        if os.path.exists(zip_fipe_path):
            obj_file_path = os.path.dirname(zip_fipe_path)
            obj_file_name = os.path.join(obj_file_path, obj_file_name + '.obj')
            zip_file = zipfile.ZipFile(file=zip_fipe_path)
            zip_file.extractall(path=obj_file_path)
            if os.path.exists(obj_file_name):
                bpy.ops.import_scene.obj(
                    filepath=obj_file_name,
                    axis_forward='Y',
                    axis_up='Z',
                    use_image_search=False
                )

    @staticmethod
    def modifiers_to_json(mesh):
        # convert mesh modifiers stack to json
        modifiers_in_json = []
        for modifier in mesh.modifiers:
            modifier_class = MeshModifierCommon
            if hasattr(sys.modules[__package__+'.mesh_modifiers'], 'MeshModifier' + modifier.type):
                modifier_class = getattr(sys.modules[__package__+'.mesh_modifiers'], 'MeshModifier' + modifier.type)
            modifiers_in_json.append(modifier_class.to_json(modifier))
        return modifiers_in_json

    @staticmethod
    def modifiers_from_json(mesh, modifiers_in_json):
        # recreate modifiers from json to mesh
        if mesh:
            for modifier_json in modifiers_in_json:
                modifier_class = MeshModifierCommon
                if hasattr(sys.modules[__package__+'.mesh_modifiers'], 'MeshModifier' + modifier_json['type']):
                    modifier_class = getattr(sys.modules[__package__+'.mesh_modifiers'], 'MeshModifier' + modifier_json['type'])
                modifier_class.from_json(mesh=mesh, modifier_json=modifier_json)
        return mesh

    @staticmethod
    def _deselect_all(context):
        # deselect all selected meshes
        for mesh in context.selected_objects:
            mesh.select = False

    @staticmethod
    def _set_mesh_origin(context, mesh, to: Vector):
        # move "mesh" origin to coordinates "to"
        if mesh:
            cursor_location = context.scene.cursor_location.copy()
            context.scene.cursor_location = to
            current_selection = context.selected_objects[:]
            __class__._deselect_all(context=context)
            mesh.select = True
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            __class__._deselect_all(context=context)
            for mesh in current_selection:
                mesh.select = True
            context.scene.cursor_location = cursor_location
