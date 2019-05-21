import bpy
import tempfile
import shutil
import os
import os.path
import json
import time
import zipfile
import math
from mathutils import Vector, Matrix
from bl_ui import properties_scene

from . import base
from .render import W_PT_renderer, W_PT_integrator
from .material import W_PT_material
from .camera import W_PT_camera
from .world import W_PT_world
from .mesh import write_object_mesh
from .lamp import W_PT_lamp
from .texture import W_PT_texture

base.compatify_all(properties_scene, 'SCENE_PT')

@base.register_menu_item(bpy.types.INFO_MT_file_export, text='Tungsten Scene (.zip/.json)')
class W_OT_export(bpy.types.Operator):
    """Export a scene and all components as Tungsten JSON"""
    bl_label = "Export Tungsten Scene"
    bl_idname = 'tungsten.export'

    # FIXME folder filter via FileSelectParams
    use_filter = True
    use_filter_folder = True

    filepath = bpy.props.StringProperty(subtype='FILE_PATH')
    
    self_contained = bpy.props.BoolProperty(
        name='Self-Contained',
        description='Self-Contained',
        default=True,
    )

    zip = bpy.props.BoolProperty(
        name='Use Zip',
        description='Use Zip Format',
        default=True,
    )

    compress = bpy.props.BoolProperty(
        name='Compress',
        description='Compress Zip File',
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'TUNGSTEN'

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'self_contained')
        if self.self_contained:
            layout.prop(self, 'zip')
            if self.zip:
                layout.prop(self, 'compress')

    def execute(self, context):
        path = self.filepath
        if os.path.exists(path):
            if self.zip and not os.path.isfile(path):
                self.report({'WARNING'}, 'Please select a file, not a directory.')
                return {'CANCELLED'}
            elif not self.zip and not os.path.isdir(path):
                self.report({'WARNING'}, 'Please select a directory, not a file.')
                return {'CANCELLED'}

        if self.zip:
            s = TungstenScene(self_contained=self.self_contained)
            s.add_all(context.scene)
            s.save()
            s.to_zip(path, compress=self.compress)
        else:
            s = TungstenScene(clean_on_del=False, self_contained=self.self_contained, path=path)
            s.add_all(context.scene)
            s.save()
        
        return {'FINISHED'}

def lefthandify(m):
    # flip +z to -z, and then compensate along x
    m *= Matrix.Scale(-1, 4, Vector((0, 0, 1)))
    m *= Matrix.Scale(-1, 4, Vector((1, 0, 0)))
    return m

def reset_scale(m):
    # remove all scaling while preserving other bits
    s = m.to_scale()
    m *= Matrix.Scale(abs(1/s[0]), 4, Vector((1, 0, 0)))
    m *= Matrix.Scale(abs(1/s[1]), 4, Vector((0, 1, 0)))
    m *= Matrix.Scale(abs(1/s[2]), 4, Vector((0, 0, 1)))
    return m

def orientify(m):
    # tungsten uses x right, y up, z forward
    # blender uses x right, y forward, z up
    # this sticks a bit on the front of m to get tungsten prims oriented
    return m * Matrix([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
    ])

class TungstenScene:
    def __init__(self, clean_on_del=True, self_contained=False, path=None):
        self.dir = path
        if path is None:
            self.dir = tempfile.mkdtemp(suffix='w')
        else:
            if not os.path.exists(path):
                os.mkdir(path)
        
        self.clean_on_del = clean_on_del
        self.self_contained = self_contained
        self.scene = {
            'media': [],
            'bsdfs': [
            ],
            'primitives': [],
            'camera': {},
            'integrator': {
            },
            'renderer': {
                'output_file': 'scene.png',
                'overwrite_output_files': True,
                'enable_resume_render': False,
                'checkpoint_interval': "0",
            },
        }
        self.mats = {}
        self.images = {}
        self.meshes = {}
        self.scenefile = self.path('scene.json')

        self.default_mat = '__default_mat'
        self.scene['bsdfs'].append({
            'name': self.default_mat,
            'type': 'lambert',
            'albedo': 0.8,
        })

    def __del__(self):
        if self.clean_on_del:
            shutil.rmtree(self.dir)

    def to_zip(self, outpath, compress=True):
        flags = zipfile.ZIP_DEFLATED if compress else 0

        start = time.time()
        with zipfile.ZipFile(outpath, 'w', flags) as zipf:
            for root, dirs, files in os.walk(self.dir):
                relroot = os.path.relpath(root, self.dir)
                if relroot != '.':
                    zipf.write(root, relroot)
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename):
                        arcname = os.path.join(relroot, file)
                        zipf.write(filename, arcname)
        end = time.time()
        print('compressed zip in', end - start, 's')

    @property
    def outputfile(self):
        return self.path(self.scene['renderer']['output_file'])

    @property
    def width(self):
        return self.scene['camera']['resolution'][0]

    @property
    def height(self):
        return self.scene['camera']['resolution'][1]

    def path(self, *args):
        return os.path.join(self.dir, *args)

    def save(self):
        with open(self.scenefile, 'w') as f:
            json.dump(self.scene, f, indent=4)

    def add_all(self, scene, preview=False):
        start = time.time()
        
        d = W_PT_renderer.to_scene_data(self, scene)
        self.scene['renderer'].update(d)

        d = W_PT_integrator.to_scene_data(self, scene)
        self.scene['integrator'].update(d)

        if scene.world:
            self.add_world(scene.world)
        self.add_camera(scene, scene.camera)

        for o in scene.objects.values():
            if any(a and b for a, b in zip(scene.layers, o.layers)):
                self.add_object(scene, o)

        if preview:
            self.munge_preview(scene)

        end = time.time()
        print('wrote scene in', end - start, 's')

    def munge_preview(self, scene):
        def lookup(ln, n, default=None):
            l = self.scene[ln]
            r = [x for x in l if x.get('name') == n]
            if r:
                return r[0]
            return default

        self.scene['renderer']['spp'] = 48
        self.scene['integrator']['enable_two_sided_shading'] = False
        
        to_remove = []
        for p in self.scene['primitives']:
            name = p.get('name', '')
            if p['type'] == 'infinite_sphere':
                to_remove.append(p)
            if name.startswith('Lamp') and p['type'] == 'sphere':
                p['emission'] = 100000
            if name.startswith('Lamp') and p['type'] == 'infinite_sphere_cap':
                p['emission'] = 150
            if name.startswith('Lamp') and p['type'] == 'disk':
                p['emission'] = 60000
            if name.startswith('checkers'):
                try:
                    n = int(name.split('.')[1])
                except:
                    n = 0
                if n in [7, 4]:
                    to_remove.append(p)
                else:
                    b = lookup('bsdfs', p['bsdf'])
                    b['albedo'] = {'type': 'checker'}
            if name == 'texture':
                o = scene.objects['texture']
                t = o.material_slots[0].material.texture_slots[0].texture
                b = lookup('bsdfs', p['bsdf'])
                b['albedo'] = W_PT_texture.to_scene_data(self, t)

        for p in to_remove:
            self.scene['primitives'].remove(p)

    def add_world(self, world):
        p = W_PT_world.to_scene_data(self, world)
        p['transform'] = []
        for v in orientify(Matrix()):
            p['transform'] += list(v)
        self.scene['primitives'].append(p)

    def add_camera(self, scene, camera):
        # look_at and friends are right-handed, but tungsten at
        # large is left-handed, for... reasons...
        transform = lefthandify(reset_scale(camera.matrix_world))

        scale = scene.render.resolution_percentage / 100
        # FIXME scene.render.pixel_aspect_x/y ?
        # FIXME border / crop
        width = int(scene.render.resolution_x * scale)
        height = int(scene.render.resolution_y * scale)

        self.scene['camera'] = {
            'transform': [],
            'resolution': [width, height],
        }

        for v in transform:
            self.scene['camera']['transform'] += list(v)

        d = W_PT_camera.to_scene_data(self, camera)
        self.scene['camera'].update(d)

    def _save_image_as(self, im, dest, fmt):
        # FIXME ewww
        start = time.time()
        if im.source == 'FILE' and im.file_format == fmt:
            # abuse image properties for saving
            oldfp = im.filepath_raw
            try:
                im.filepath_raw = self.path(dest)
                im.save()
            finally:
                im.filepath_raw = oldfp
        else:
            # abuse render settings for conversion
            s = bpy.context.scene
            oldff = s.render.image_settings.file_format
            try:
                s.render.image_settings.file_format = fmt
                im.save_render(self.path(dest), s)
            finally:
                s.render.image_settings.file_format = oldff
        end = time.time()
        print('wrote', dest, 'in', end - start, 's')

    def add_image(self, im):
        if im.name in self.images:
            return self.images[im.name]

        IMAGE_FORMATS = {
            'BMP': '.bmp',
            'PNG': '.png',
            'JPEG': '.jpg',
            'TARGA': '.tga',
            'TARGA_RAW': '.tga',
            'HDR': '.hdr',
        }

        if im.file_format in IMAGE_FORMATS:
            ext = IMAGE_FORMATS[im.file_format]
            
            # use native format
            path = bpy.path.abspath(im.filepath)
            if im.library:
                path = bpy.path.abspath(im.filepath, library=im.library)
            
            if path and os.path.exists(path) and not self.self_contained:
                # use existing file
                try:
                    p = os.path.relpath(path, self.dir)
                    self.images[im.name] = p
                    return p
                except ValueError:
                    self.images[im.name] = path
                    return path
            else:
                # save file
                path = im.name + ext
                self._save_image_as(im, path, im.file_format)
                self.images[im.name] = path
                return path
        else:
            # save as png
            path = im.name + '.png'
            self._save_image_as(im, path, 'PNG')
            self.images[im.name] = path
            return path

    def add_material(self, m):
        if m.name in self.mats:
            return self.mats[m.name]

        obj, mat = W_PT_material.to_scene_data(self, m)
        if mat:
            self.scene['bsdfs'].append(mat)
        self.mats[m.name] = obj
        return obj

    def add_mesh(self, scene, o):
        if o.type == 'MESH' and not o.is_modified(scene, 'RENDER'):
            # unmodified meshes get export directly, as a m_file
            outname = 'm_' + o.data.name + '.wo3'
        else:
            # modified meshes and other geometry get a o_file
            outname = 'o_' + o.name + '.wo3'

        if outname in self.meshes:
            return self.meshes[outname]
        fulloutname = self.path(outname)

        start = time.time()
        verts, tris = write_object_mesh(scene, o, fulloutname)
        end = time.time()
        print('wrote', outname, 'in', end - start, 's -', verts, 'verts,', tris, 'tris')

        self.meshes[outname] = outname
        return outname

    def add_object(self, scene, o):
        dat = {
            'name': o.name,
        }

        matrix_world = o.matrix_world
        if o.type in {'LAMP'} and o.data:
            dat.update(W_PT_lamp.to_scene_data(scene, o.data))
            # we used to reset_scale here, but area lights *need* scale
            #matrix_world = orientify(reset_scale(matrix_world))
            matrix_world = orientify(matrix_world)
        elif not o.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
            # no geometry
            return
        else:
            # mesh!
            dat['type'] = 'mesh'
            dat['smooth'] = True
            dat['file'] = self.add_mesh(scene, o)

            if len(o.material_slots) > 0 and o.material_slots[0].material: # FIXME matid
                obj = self.add_material(o.material_slots[0].material)
                dat.update(obj)
            else:
                dat['bsdf'] = self.default_mat

        # handle transforms
        transform = dat.get('transform', Matrix())
        transform = matrix_world * transform
        dat['transform'] = []
        for v in transform:
            dat['transform'] += list(v)

        self.scene['primitives'].append(dat)
