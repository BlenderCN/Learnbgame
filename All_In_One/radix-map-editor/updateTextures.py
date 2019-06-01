import bpy
import bmesh
from bpy.app.handlers import persistent

isRunning = False


def updateTexture(self):
  """Remap texture to match actual scale of the object on the Cube.obj"""
  global isRunning

  isRunning = True

  bpy.context.scene.objects.active = self
  bpy.ops.object.mode_set(mode='EDIT')
  me = self.data
  bm = bmesh.from_edit_mesh(me)
  scale = [0.0, 0.0, 0.0]

  scale[0] = abs(self.scale[0])  # X
  scale[1] = abs(self.scale[1])  # Y
  scale[2] = abs(self.scale[2])  # Z

  if hasattr(bm.faces, "ensure_lookup_table"):
    bm.faces.ensure_lookup_table()

  if bm.loops.layers.uv[0]:
    uv_layer = bm.loops.layers.uv[0]

    # Bottom - 1
    bm.faces[0].loops[0][uv_layer].uv = (scale[0], -scale[1])
    bm.faces[0].loops[1][uv_layer].uv = (scale[0], 0)
    bm.faces[0].loops[2][uv_layer].uv = (0, -scale[1])
    # Bottom - 2
    bm.faces[6].loops[0][uv_layer].uv = (scale[0], 0)
    bm.faces[6].loops[1][uv_layer].uv = (0, 0)
    bm.faces[6].loops[2][uv_layer].uv = (0, -scale[1])
    # Top - 1
    bm.faces[1].loops[0][uv_layer].uv = (0, 0)
    bm.faces[1].loops[1][uv_layer].uv = (0, -scale[1])
    bm.faces[1].loops[2][uv_layer].uv = (scale[0], 0)
    # Top - 2
    bm.faces[7].loops[0][uv_layer].uv = (scale[0], -scale[1])
    bm.faces[7].loops[1][uv_layer].uv = (scale[0], 0)
    bm.faces[7].loops[2][uv_layer].uv = (0, -scale[1])
    # Front - 1
    bm.faces[2].loops[0][uv_layer].uv = (scale[1], -scale[2])
    bm.faces[2].loops[1][uv_layer].uv = (scale[1], 0)
    bm.faces[2].loops[2][uv_layer].uv = (0, -scale[2])
    # Front - 2
    bm.faces[8].loops[0][uv_layer].uv = (scale[1], 0)
    bm.faces[8].loops[1][uv_layer].uv = (0, 0)
    bm.faces[8].loops[2][uv_layer].uv = (0, -scale[2])
    # Left - 1
    bm.faces[3].loops[0][uv_layer].uv = (scale[0], -scale[2])
    bm.faces[3].loops[1][uv_layer].uv = (scale[0], 0)
    bm.faces[3].loops[2][uv_layer].uv = (0, -scale[2])
    # Left - 2
    bm.faces[9].loops[0][uv_layer].uv = (scale[0], 0)
    bm.faces[9].loops[1][uv_layer].uv = (0, 0)
    bm.faces[9].loops[2][uv_layer].uv = (0, -scale[2])
    # Back - 1
    bm.faces[4].loops[0][uv_layer].uv = (scale[1], -scale[2])
    bm.faces[4].loops[1][uv_layer].uv = (scale[1], 0)
    bm.faces[4].loops[2][uv_layer].uv = (0, -scale[2])
    # Back - 2
    bm.faces[10].loops[0][uv_layer].uv = (scale[1], 0)
    bm.faces[10].loops[1][uv_layer].uv = (0, 0)
    bm.faces[10].loops[2][uv_layer].uv = (0, -scale[2])
    # Right - 1
    bm.faces[5].loops[0][uv_layer].uv = (0, 0)
    bm.faces[5].loops[1][uv_layer].uv = (0, -scale[2])
    bm.faces[5].loops[2][uv_layer].uv = (scale[0], 0)
    # Right - 2
    bm.faces[11].loops[0][uv_layer].uv = (0, -scale[2])
    bm.faces[11].loops[1][uv_layer].uv = (scale[0], -scale[2])
    bm.faces[11].loops[2][uv_layer].uv = (scale[0], 0)

  bmesh.update_edit_mesh(me)
  bm.free()
  bpy.ops.object.mode_set(mode='OBJECT')

  isRunning = False


@persistent
def sceneUpdater(scene):
  global isRunning
  object = scene.objects.active

  if not isRunning:
    if object is not None and object.is_updated:
      if object.radixTypes in {"wall", "volume"} and object.radixModel == "Cube.obj":
        object.updateTexture()
