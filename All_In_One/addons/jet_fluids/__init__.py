
bl_info = {
    'name': 'Jet-Fluids',
    'author': 'Pavel_Blend',
    'version': ('Demo', 0, 0, 4),
    'blender': (2, 79, 0),
    'category': 'Animation',
    'location': 'Properties > Physics > Jet Fluid',
    'warning': 'Demo version',
    'wiki_url': 'https://github.com/PavelBlend/blender_jet_fluids_addon',
    'tracker_url': 'https://github.com/PavelBlend/blender_jet_fluids_addon/issues'
}


from .addon import register, unregister
