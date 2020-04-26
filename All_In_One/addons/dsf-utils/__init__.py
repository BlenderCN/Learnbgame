# union module for inclusion of all dsf-related modules into
# one directory. This should be the only module directly
# included/executed from blender.
#

import logging

logging.basicConfig (level = logging.INFO)
log = logging.getLogger ('dsf')

try:
  from . import dsf_geom_import
  from . import dsf_morph_import
  from . import dsf_uvset_import
  from . import dsf_morph_export
  from . import dsf_arm_import
  from . import dsf_pose_import
  from . import dsf_wm_import
  from . import dsf_geom_export
  from . import dsf_prop_export
except ImportError as e:
  # if the error is something like 'no module named bpy', this
  # file is not included from within blender. Do not abort in this
  # case, because parts of this module are still useful.
  if str (e).find ('bpy') >= 0:
    log.warn ("import error ignored: %s", e)
  else:
    raise


bl_info = {
  'name': 'dsf-utils',
  'description': 'scripts for dsf files.',
  'author': 'millighost',
  'version': (1, 0),
  'blender': (2,6,3),
  "category": "Learnbgame",
  'warning': '',
  'wiki_url': 'http://nonexistent',
}

def register ():
  """call register functions of the submodules.
  """
  dsf_geom_import.register ()
  dsf_morph_import.register ()
  dsf_morph_export.register ()
  dsf_uvset_import.register ()
  dsf_arm_import.register ()
  dsf_pose_import.register ()
  dsf_wm_import.register ()
  dsf_geom_export.register ()
  dsf_prop_export.register ()

def unregister ():
  """call unregister functions of the submodules in
     reverse order.
  """
  dsf_prop_export.unregister ()
  dsf_geom_export.unregister ()
  dsf_wm_import.unregister ()
  dsf_pose_import.unregister ()
  dsf_arm_import.unregister ()
  dsf_uvset_import.unregister ()
  dsf_morph_export.unregister ()
  dsf_morph_import.unregister ()
  dsf_geom_import.unregister ()
