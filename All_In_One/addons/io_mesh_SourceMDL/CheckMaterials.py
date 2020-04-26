import os
import sys
from ctypes import windll
from pathlib import Path
from shutil import copy2

k32 = windll.LoadLibrary('kernel32.dll')
setConsoleModeProc = k32.SetConsoleMode
setConsoleModeProc(k32.GetStdHandle(-11), 0x0001 | 0x0002 | 0x0004)

import MDL
import ValveUtils
from ValveUtils import GameInfoFile, KeyValueFile

if __name__ == '__main__':
    # model = Path(
    #     r"G:\SteamLibrary\SteamApps\common\SourceFilmmaker\game\Furry\models\red_eye\creepychimera\lewdsangheili.mdl")
    # dump_path = Path(r'E:\PACKED_MODELS\LewdSangheili')
    # dump_path = None
    if len(sys.argv) == 3:
        dump_path = Path(sys.argv[1])
        models = [Path(arg) for arg in sys.argv[1:]]
    else:
        dump_path = Path(input('Path where model should be copied: '))
        model = Path(input('Path to model: '))
        models = [model]
    for model in models:
        if not model.exists():
            print('\033[91mMODEL NOT FOUND\033[0m')
            exit()
        print('\033[94mReading \033[95m{}\033[0m'.format(model))
        mod_path = ValveUtils.get_mod_path(model)
        game_info_path = mod_path / 'gameinfo.txt'
        if not game_info_path.exists():
            raise FileNotFoundError("Failed to find gameinfo file")
        gi = GameInfoFile(game_info_path)
        textures = []
        used_textures = []
        materials = []
        temp = ValveUtils.get_mod_path(model)
        other_files = [
            (model, Path(model).relative_to(temp)),
            (model.with_suffix('.vvd'), Path(model.with_suffix('.vvd')).relative_to(temp))]
        if model.with_suffix('.dx90.vtx').exists():
            other_files.append((model.with_suffix('.dx90.vtx'), Path(model.with_suffix('.dx90.vtx')).relative_to(temp)))
        if model.with_suffix('.dx80.vtx').exists():
            other_files.append((model.with_suffix('.dx80.vtx'), Path(model.with_suffix('.dx80.vtx')).relative_to(temp)))
        if model.with_suffix('.sw.vtx').exists():
            other_files.append((model.with_suffix('.sw.vtx'), Path(model.with_suffix('.sw.vtx')).relative_to(temp)))

        print('Trying to find used textures and materials')
        print('Searching in:')
        for path in gi.get_search_paths_recursive():
            print('\t\x1b[95m{}\x1b[0m'.format(path))
        if model.exists():
            # other_files.append(model)
            mdl = MDL.SourceMdlFile49(filepath=str(model.with_name(model.stem)), read=False)
            mdl.read_skin_families()
            mdl.read_texture_paths()
            mdl.read_textures()
            # print(mdl.file_data.textures)
            for texture in mdl.file_data.textures:
                for tex_path in mdl.file_data.texture_paths:
                    if tex_path and (tex_path[0] == '/' or tex_path[0] == '\\'):
                        tex_path = tex_path[1:]
                    if tex_path:
                        mat = gi.find_material(Path(tex_path) / texture.path_file_name, use_recursive=True)
                        if mat:
                            temp = ValveUtils.get_mod_path(mat)
                            materials.append((Path(mat), Path(mat).relative_to(temp)))
                ...

            for mat in materials:
                kv = KeyValueFile(mat[0])
                for v in list(kv.as_dict.values())[0].values():
                    if '/' in v or '\\' in v:
                        used_textures.append(Path(v))
                        tex = gi.find_texture(v, True)
                        if tex:
                            temp = ValveUtils.get_mod_path(tex)
                            textures.append((Path(tex), Path(tex).relative_to(temp)))
                # print(kv.as_dict)
            print('\033[94m', '*' * 10, 'MATERIALS', '*' * 10, '\033[0m')
            for texture in mdl.file_data.textures:
                exist = False
                found_path = None
                for mat in materials:
                    if mat[1].stem == texture.path_file_name:
                        exist = True
                        found_path = mat[0]
                        break
                if exist:
                    print('>>>\033[94m', texture.path_file_name, '-> \033[92mFound here \033[0m>', '\033[95m',
                          found_path,
                          '\033[0m')
                else:
                    print('>>>\033[94m', texture.path_file_name, '-> \033[91mNot found!', '\033[0m')
                # print()

            print('\033[94m', '*' * 10, 'TEXTURES', '*' * 10, '\033[0m')
            for used_texture in used_textures:
                exist = False
                found_path = None
                for tex in textures:
                    if tex[1].stem == used_texture.stem:
                        exist = True
                        found_path = tex[0]
                        break
                if exist:
                    print('>>>\033[94m', used_texture, '-> \033[92mFound here \033[0m>', '\033[95m', found_path,
                          '\033[0m')
                else:
                    print('>>>\033[94m', used_texture, '-> \033[91mNot found!', '\033[0m')
                # print()
        textures = list(set(textures))
        materials = list(set(materials))
        other_files = list(set(other_files))
        if dump_path:
            os.makedirs(dump_path, exist_ok=True)
            if dump_path.exists():
                for file in textures + materials + other_files:
                    try:
                        os.makedirs((dump_path / file[1]).parent, exist_ok=True)
                    except:
                        pass
                    copy2(file[0], dump_path / file[1])
                    print('from\033[94m', file[0], '\033[0mto\033[95m', dump_path / file[1], '\033[0m')
        else:
            input('Press Enter to exit')
    # print('*'*10,'MATERIALS','*'*10)
    # pprint(materials)
    # print('*'*10,'TEXTURES','*'*10)
    # pprint(textures)
