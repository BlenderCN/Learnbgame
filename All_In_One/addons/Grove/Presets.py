# coding=utf-8

""" Miscellaneous functionality.
    Copyright (c) 2016 - 2018, Wybren van Keulen, The Grove. """


from os.path import join, exists, dirname
from os import listdir, remove
from operator import itemgetter


def presets_path():
    """ Find out where the presets are stored. """

    path = join(dirname(__file__), "Seeds")
    if exists(path):
        return path
    else:
        return ""


def enumerate_presets():
    """ Fill the presets menu. """
    presets = []
    preset_names = [a[:-5] for a in sorted(listdir(presets_path())) if a[-5:] == '.seed']
    for i, name in enumerate(preset_names):
        presets.append((name, name, ""))
    presets.sort(key=itemgetter(1))
    return presets


def write_preset(name, settings):
    """ Write preset file. Only save a selection of parameters, others like Profile Resolution are
        not related to a tree species. """

    f = open(join(presets_path(), name + '.seed'), 'w')

    for parameter in dir(settings):
        if parameter in ['shade_leaf_area', 'shade_samples', 'shade_sensitivity',
                         'favor_current', 'favor_current_reach', 'shade_avoidance', 'branching_inefficiency',
                         'favor_healthy', 'favor_rising', 'gravitropism_buds', 'gravitropism_buds_randomness',
                         'peak_height', 'apical_bud_fatality',
                         'drop_shaded', 'drop_relatively_weak', 'keep_dead', 'drop_low', 'keep_thick',
                         'branching', 'branch_chance', 'branch_chance_light_required', 'bud_life',
                         'branch_chance_only_terminal',
                         'regenerative_branch_chance', 'regenerative_branch_chance_light_required',
                         'grow_length', 'grow_nodes', 'shade_elongation',
                         'phototropism', 'gravitropism', 'gravitropism_shade', 'plagiotropism', 'plagiotropism_buds',
                         'twist', 'branch_angle', 'random_pitch', 'random_heading',
                         'tip_thickness', 'tip_decrease', 'internode_gain', 'join_branches',
                         'root_scale', 'root_shape', 'root_bump',
                         'branch_weight', 'leaf_weight', 'bake_bend', 'fatigue',
                         'lateral_twig_chance', 'lateral_twig_limit', 
                         'flower_power', 'scale_to_twig']:

            if isinstance(getattr(settings, parameter), str):
                # Write a string.
                f.write(parameter + ' = "' + str(getattr(settings, parameter)) + '"\n')
            else:
                # Write a number or a boolean.
                f.write(parameter + " = " + str(getattr(settings, parameter)) + "\n")
    f.close()

    # Make sure the newly added preset is selected in the drop down.
    presets = enumerate_presets()
    for preset in presets:
        if preset[1] == name:
            settings.presets_menu = preset[0]
            break


def read_preset(name, settings):
    """ Read preset file and return a dictionary with all settings inside the preset. """

    name = join(presets_path(), name + ".seed")
    preset = {}

    try:
        with open(name, 'r') as f:
            for line in f:
                if len(line.split('=')) != 2:
                    continue
                parameter, value = line.split('=')
                parameter = parameter.strip()
                value = value.strip()

                if parameter in dir(settings):
                    if value == "True":
                        value = True
                    elif value == "False":
                        value = False
                    elif value[0] == value[-1] and value[0] == '"':
                        value = str(value[1:-1])
                    else:
                        try:
                            value = int(value)
                        except:
                            pass
                        try:
                            value = float(value)
                        except:
                            pass

                    preset[parameter] = value

                # Backward compatibility
                elif parameter == 'branching_thickness_exponent':
                    settings.join_branches = (float(value) - 4.0) / -2.0
                elif parameter == 'watershoots':
                    settings.regenerative_branch_chance = float(value)
                elif parameter == 'watershoots_light_threshold':
                    settings.regenerative_branch_chance_light_required = float(value)
                elif parameter == 'branch_chance_light_threshold':
                    settings.branch_chance_light_required = float(value)
                elif parameter == 'twig_threshold':
                    settings.lateral_twig_limit = float(value)

    except IOError:
        print("Failed loading preset " + name)
        return

    for parameter, value in preset.items():
        try:
            setattr(settings, parameter, value)
        except TypeError:
            print("Load Preset - Skipping parameter " + parameter + ", it has the wrong type.")


def rename_preset(name, new_name, settings):
    """ Remove the named preset and write a new preset. """

    remove_preset(name, settings)
    write_preset(new_name, settings)

    # Make sure the newly added preset is selected in the drop down.
    presets = enumerate_presets()
    for preset in presets:
        if preset[1] == new_name:
            settings.presets_menu = preset[0]
            settings.preset_name = preset[1]
            break


def remove_preset(name, settings):
    """ Remove the named preset file. """

    path = join(presets_path(), name + ".seed")
    if exists(path):
        try:
            remove(path)
        except:
            print("OS Error: Could not delete preset file. It may be in use.")

    # After removing the preset, select preset number 0.
    settings.presets_menu = enumerate_presets()[0][0]
    settings.preset_name = enumerate_presets()[0][1]
