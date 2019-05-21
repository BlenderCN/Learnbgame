import bpy, mathutils

import dsf.path_util
import dsf.geom_create
import dsf.geom_writer
import dsf.scene_writer
import json, math
import urllib.parse as urp

class prop_writer (object):
  """write props for a single export-operation.
  """
  def __init__ (self, filepath, transform, scene):
    """initialize state for writing to the given scene-file.
    """
    self.lib = dsf.path_util.daz_library (filepath = filepath)
    self.scene = scene
    self.duf_libpath = self.lib.get_libpath (filepath)
    self.transform = transform
  @classmethod
  def get_selected_objects (self, scene):
    """return the selected objects of the scene.
    """
    objects = [obj for obj in scene.objects if obj.select]
    return objects

  @classmethod
  def get_selected_objects_by_data (self, scene):
    """get one object for each unique data instance.
    """
    all_objs = self.get_selected_objects (scene)
    groups = dsf.geom_create.group_objects_by_mesh (all_objs)
    objs = [obj[0] for obj in groups]
    return objs

  def create_data_file (self, ctx):
    objects = self.get_selected_objects_by_data (ctx.scene)
    gcreator = dsf.geom_create.geom_creator (ctx.scene, self.transform)
    geometry_datas = [gcreator.create_geometry_and_uvs (obj) for obj in objects]
    for gdata in geometry_datas:
      geo = gdata.geometry
      uvs = gdata.uvs
      if uvs:
        geo['default_uv_set'] = '#' + urp.quote (uvs[0]['id'])
    data = {
      "asset_info": {},
      "geometry_library": [g.geometry for g in geometry_datas],
      "uv_set_library": sum ([g.uvs for g in geometry_datas], [])
    }
    return data

  def write_json (self, libpath, data):
    ofh = self.lib.create_output_stream (libpath)
    json.dump (data, ofh, indent = 2, sort_keys = True)

  def write_geometries (self, objs):
    """write the geometry definitions for the given objects.
       returns a mapping from obj-data to url.
    """
    geom_writer = dsf.geom_writer.geom_writer\
      (self.lib, self.scene, self.transform)
    data_dic = geom_writer.write_meshes_for_objects (objs)
    return data_dic

  def write_objects (self, objs, data_dic):
    """write the scene-file.
       data-dic contains a mapping from object data to url.
    """
    scene_writer = dsf.scene_writer.scene_writer (self.transform, data_dic)
    data = scene_writer.create_scene_file (objs)
    self.lib.write_local_file (data, self.duf_libpath)

  def write_scene (self, ctx):
    """write the scene file and all geometry files.
    """
    scene = ctx.scene
    objs = self.get_selected_objects (self.scene)
    data_dic = self.write_geometries (objs)
    self.write_objects (objs, data_dic)

def make_transform (scale, rotate):
  if rotate:
    trans = scale * mathutils.Euler ([-math.pi/2, 0, 0], 'XYZ').to_matrix ()
  else:
    trans = scale * mathutils.Matrix.Identity (3)
  return trans.to_4x4 ()

def export_prop (ctx, filepath, group, scale, rotate):
  """export the active object to the filepath.
     group is a hint for the subdirectory.
     scale is a scale factor that is applied to exported objects.
     if rotate is true, rotate geometry by 90degrees around x.
  """
  scene = ctx.scene
  transform = make_transform (scale, rotate)
  writer = prop_writer (filepath, transform, scene)
  writer.write_scene (ctx)
