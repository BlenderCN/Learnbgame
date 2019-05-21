import sys
import os

args = sys.argv

selfpath = args[0]
selfdir = os.path.dirname(selfpath)

import mdlackey
mdmacro = mdlackey.MDMacro

import simulation_config

def sim(avatar_path, animation_path, garment_path, result_path):
    mdmacro.new_file()
    if ".obj" in avatar_path:
        mdmacro.open_avatar(avatar_path)
        mdmacro.wait(0.5)
        mdmacro.add_mdd(animation_path)

    if ".abc" in avatar_path:
        mdmacro.open_avatar_abc(avatar_path)

    mdmacro.add_garment(garment_path)
    mdmacro.simulate(simulation_config.simulate_time)
    mdmacro.select_all()
    if ".obj" in result_path:
        mdmacro.export_obj(result_path, simulation_config.use_thickness)
    if ".abc" in result_path:
        mdmacro.export_abc(result_path, simulation_config.use_thickness)
    os.remove(avatar_path)
    os.remove(animation_path)
    os.remove(garment_path)

# md = mdmacro.set_up()
# if md.ver == "7":
#     pass
# else:
#     sim(args[1],args[2],args[3],args[4])
sim(args[1],args[2],args[3],args[4])

print("end")
