import panda3d.core as p3d

from . import core as pman


def init(base):
    assetdir_rel = p3d.Filename('assets')
    config = None

    if not pman.is_frozen():
        config = pman.get_config()
        if config['run']['auto_build']:
            pman.build(config)
        assetdir_rel = p3d.Filename.from_os_specific(config['build']['export_dir'])

    # Add assets directory to model path
    assetdir = p3d.Filename(p3d.Filename.expand_from('$MAIN_DIR'), assetdir_rel)
    p3d.get_model_path().prepend_directory(assetdir)

    # Setup renderer
    pman.create_renderer(base, config)
