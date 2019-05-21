import bpy
import os
from os.path import basename,splitext,join
import re

from pipe.load import load_group as pipe_load_group
from ...functions import get_versions

def load_group(self,ThumbnailList,item_info,link=True):

    #print('offset',ThumbnailList.offset)
    scene = self.context.scene
    location = scene.cursor_location.copy()
    location[0] += ThumbnailList.offset

    #print('#####')
    #print(get_versions(item_info['path']))
    #print('#####')

    if re.search('[\d][\d][\d]',basename(item_info['path'])) :
        versions = get_versions(item_info['path'])
        if not versions :
            print('Asset no longer exist')
            return
        blend_path = versions[-1]

    else :
        blend_path = item_info['path']
    #print(blend_path)

    group,empty,proxy = pipe_load_group(blend_path,item_info['asset'],instantiate = True, make_proxy = True,link=link)

    if proxy :
        roots = [b for b in proxy.pose.bones if not b.parent and not b.constraints]

        if roots :
            roots[0].location = location


    '''
    if os.path.exists(blend_path) :
        with bpy.data.libraries.load(blend_path, link=link) as (data_src, data_dst):
            data_dst.groups = [item_info['asset']]

        group = data_dst.groups[0]

        empty = bpy.data.objects.new(item_info['asset'],None)
        scene.objects.link(empty)
        empty.dupli_type ='GROUP'
        empty.dupli_group = group


        armatures = [o.find_armature() for o in group.objects if o.find_armature()]

        armatures +=[o.parent for o in group.objects if o.parent and o.parent.type == 'ARMATURE']

        if armatures :

            rig = max(set(armatures), key=armatures.count)

            scene.objects.active = empty
            override = self.context.copy()
            override['object'] =empty
            override['active_object'] = empty
            #context['window_manager']= bpy.data.window_managers['WinMan']
            #context['window']= bpy.data.window_managers['WinMan'].windows[0]
            print('#####################')
            #print(override)
            print(self.context)
            bpy.ops.object.proxy_make(override,object=rig.name)

            print('#####################')
            print(dir(self.context))
            #print(override)
            #scene = override['scene']

            #print(scene.objects.active)
            proxy = scene.objects.active

            roots = [b for b in proxy.pose.bones if not b.parent and not b.constraints]

            if roots :
                roots[0].location = location

        else :
            empty.location = location
    else :
        print("Le chemin suivant n'existe pas :")
        print(blend_path)
        '''
