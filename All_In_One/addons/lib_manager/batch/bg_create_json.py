import sys
import bpy,os
import json
from os.path import join,dirname,realpath,basename,normpath,splitdrive

from pipe.utils import read_json
from pipe.display import set_display
#from pipe.utils import up_dir,to_folder
working_dir = dirname(dirname(realpath(__file__)))
settings = read_json(join(working_dir,"settings.json"))


args = eval(sys.argv[-1])

files = args['files']

print('########################')
print(files)

print('########################')

folder = args.get('folder')

lib_path = settings['path']

scene = bpy.context.scene

areas = bpy.context.screen.areas
viewports = sorted([(a,a.width*a.height) for a in areas if a.type == 'VIEW_3D'],key = lambda x : x[1])

if viewports :
    override = {'area': viewports[-1][0], 'region': viewports[-1][0].regions[-1]}

viewports[-1][0].spaces[0].region_3d.view_perspective = 'CAMERA'

set_display('solid')

sensor = scene.camera.data.sensor_width

for f in files :
    print(normpath(f),normpath(settings['root']))

    root = splitdrive(normpath(settings['root']))[1]
    path = splitdrive(normpath(f))[1]

    print(root,path)
    short_path = path.replace(root,'')[1:]

    print(short_path)

    with bpy.data.libraries.load(f, link=True) as (data_src, data_dst):
        data_dst.groups = data_src.groups

    for g in data_dst.groups :
        empty = bpy.data.objects.new(g.name,None)
        scene.objects.link(empty)

        empty.dupli_type ='GROUP'
        empty.dupli_group = g

        empty.select = True

        bpy.ops.view3d.camera_to_view_selected(override)
        #scene.camera.location[1] -=0.4
        scene.camera.data.sensor_width *=1.1

        if len(data_dst.groups)> 1 :
            asset_folder = join(lib_path,basename(folder),basename(f).split('_')[0],g.name)

        else :
            asset_folder = join(lib_path,basename(folder),basename(f).split('_')[0])

        if not os.path.exists(asset_folder):
            os.makedirs(asset_folder)

        asset_info={
            "type" : "group",
            "asset" : g.name,
            "image" : "./%s.png"%(g.name+"_image"),
            "icon" : "./%s.png"%(g.name+"_icon"),
            "tags" : "",
            "path": short_path,
            "description" : ""
                    }

        json_path = join(asset_folder,g.name+'.json')
        with open(json_path, 'w') as outfile:
            json.dump(asset_info, outfile)


        image_path = os.path.join(asset_folder,'%s_image.png'%g.name)
        scene.render.resolution_x = 256
        scene.render.resolution_y = 256
        scene.render.filepath = image_path

        bpy.ops.render.opengl(write_still = True)

        icon_path = os.path.join(asset_folder,'%s_icon.png'%g.name)
        scene.render.resolution_x = 32
        scene.render.resolution_y = 32
        scene.render.filepath = icon_path

        bpy.ops.render.opengl(write_still = True)

        bpy.data.objects.remove(empty,True)
        bpy.data.groups.remove(g,True)

        scene.camera.data.sensor_width = sensor



bpy.ops.wm.quit_blender()
