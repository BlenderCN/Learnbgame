import logging
import weakref

import bpy

from . import aud
from .aud import audGeom, audLux
from pprint import pprint

logging.basicConfig()
logger = logging.getLogger('aud-blender')
logger.setLevel(logging.DEBUG)

class WeakList(list):

    def add_prim_node(self, prim, node):
        s = weakref.WeakSet()
        s.add(prim)
        s.add(node)
        self.append(s)


class AUDExporter(object):
    def __init__(self,
                 context=None,
                 selected=False,
                 animation=False,
                 geocache=False,
                 cameras=False,
                 lights=False):
        super(AUDExporter, self).__init__()
        self.only_selected = selected
        self.context = context
        self.stage = None
        self.animation = animation
        self.geocache = geocache and animation
        self.export_cameras = cameras
        self.export_lights = lights
        self.animated_objects = WeakList()

    def write(self, filepath):
        # Exit edit mode before exporting, so current object states are exported properly.
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        scene = self.context.scene
        current_frame = scene.frame_current

        if self.animation:
            # If we're exporting animation, then we need to go to the start first
            scene.frame_set(scene.frame_start)

        try:
            self._write(filepath)
        finally:
            if self.stage:
                self.stage.save(location=filepath)
            self.stage = None  # clear it out when we're done writing
            scene.frame_set(current_frame)

        logger.info("Finished writing to %s", filepath)
        return {'FINISHED'}

    def _write(self, filepath):

        self.stage = aud.Stage()

        self.configure_stage()
        self.write_hierarchy()
        if self.animation:
            self.write_animation()

    def configure_stage(self):
        if not self.stage:
            return

        scene = self.context.scene

        self.stage.set_up_axis('Z')  # Blender is hardcoded to Z up

        if self.animation:
            self.stage.set_frame_range(scene.frame_start, scene.frame_end)
            self.stage.set_framerate(scene.render.fps)

    def write_hierarchy(self):

        if self.only_selected:
            objects = self.context.selected_objects
        else:
            objects = self.context.scene.objects

        for obj in objects:
            self.add_node(obj, parent=self.stage)

    def add_node(self, node, parent):
        nname = node.name
        ntype = node.type

        prim = None
        if ntype == 'MESH':
            prim = self.mesh(node)
        elif ntype == 'LIGHT':
            if self.export_lights:
                prim = self.light(node)
        elif ntype == 'CAMERA':
            if self.export_cameras:  # Put this deeper so we can still have the error below
                prim = self.camera(node)
        elif ntype == 'EMPTY':
            prim = self.transform(node)
        else:
            logger.error('Object "%s" of type "%s" is not supported', nname, ntype)
            return

        if not prim:
            return

        parent.add_child(prim)
        self.apply_transforms(node, prim)

        for child in node.children:
            self.add_node(child, prim)

    def write_animation(self):
        scene = self.context.scene

        for frame in range(scene.frame_start, scene.frame_end+1, 2):
            for prim, node in self.animated_objects:
                ntype = node.type

                if ntype == 'MESH':
                    if self.geocache:
                        self.mesh(node, frame=frame, prim=prim)
                elif ntype == 'LIGHT':
                    self.light(node, frame=frame, prim=prim)
                elif ntype == 'CAMERA':
                    self.camera(node, frame=frame, prim=prim)

                self.apply_transforms(node, prim=prim, frame=frame)


    def mesh(self, node, frame=None, prim=None):
        prim = prim or audGeom.Mesh(node.name)
        if frame:
            logger.warning("Mesh type doesn't support animated write outs")

        depsgraph = self.context.depsgraph
        mesh = node.to_mesh(depsgraph, apply_modifiers=True)

        vertices = mesh.vertices[:]
        polygons = mesh.polygons[:]
        loops = mesh.loops[:]

        positions = []
        normals = []

        for vert in vertices:
            pos = vert.co
            norm = vert.normal
            positions.append((pos.x, pos.y, pos.z))
            normals.append((norm.x, norm.y, norm.z))

        vertCounts = []
        vertIndices = []
        for poly in polygons:
            verts = poly.vertices
            vertCounts.append(len(verts))

            for l in poly.loop_indices:
                loop = loops[l]
                vertIndices.append(loop.vertex_index)

        prim.set_attribute('faceVertexCounts', vertCounts, as_type='int[]')
        prim.set_attribute('faceVertexIndices', vertIndices, as_type='int[]')

        prim.set_attribute('points', positions, as_type='point3f[]')
        normAttr = prim.set_attribute('primvars:normals', normals, as_type='normal3f[]')
        normAttr.set_property('interpolation', 'faceVarying')

        return prim

    def light(self, node, frame=None, prim=None):
        light = bpy.data.lights.get(node.name)

        prim = prim or {
            'SUN': audLux.DistantLight
        }.get(light.type, audLux.Light)(node.name)

        if not prim.as_type:
            prim.as_type = 'Light'  # Technically incorrect but just as a fallback

        if frame:
            logger.warning("Light type doesn't support animated write outs")
        prim.set_attribute('color',
                           (light.color.r, light.color.g, light.color.b),
                           as_type='color3f')
        prim.set_attribute('intensity', light.energy, as_type='float')
        return prim

    def camera(self, node: bpy.types.Object, frame=None, prim=None):
        cam: bpy.types.Camera = bpy.data.cameras.get(node.name)
        prim = prim or audGeom.Camera(node.name)
        if frame:
            logger.warning("Camera type doesn't support animated write outs")

        projection = {
            'PERSP': 'perspective',
            'ORTHO': 'orthographic'
        }.get(cam.type)
        prim.set_attribute('projection', projection)
        prim.set_attribute('clippingRange',
                           (cam.clip_start, cam.clip_end))
        prim.set_attribute('horizontalAperture', cam.sensor_width)
        prim.set_attribute('horizontalApertureOffset', cam.shift_x)
        prim.set_attribute('verticalAperture', cam.sensor_height)
        prim.set_attribute('verticalApertureOffset', cam.shift_y)
        prim.set_attribute('focalLength', cam.lens)

        return prim

    def transform(self, node, frame=None, prim=None):
        prim = prim or audGeom.Xform(node.name)
        if frame:
            self.apply_transforms(node, prim, frame=frame)
        return prim

    def apply_transforms(self, node: bpy.types.Object, prim: aud.Prim, frame=None):
        location = node.location
        location = (location.x, location.y, location.z)

        rotation = node.rotation_euler
        rotation = (rotation.x, rotation.y, rotation.z)

        scale = node.scale
        scale = (scale.x, scale.y, scale.z)

        attrMap = (
            ('xformOp:translate', location),
            ('xformOp:rotateXYZ', rotation),
            ('xformOp:scale', scale)
        )

        if frame is None:
            prim.set_xform_order()
        for attr, val in attrMap:
            if frame is None:
                prim.set_attribute(attr, val, as_type='double3')
                continue

            attr = prim.get_attribute(attr)
            attr.set_keyframe(frame, val)
