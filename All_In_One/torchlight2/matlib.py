import bpy
import pickle
import pathlib as pl
from .utils import get_addon_pref

class TL2_MaterialLib:
    def __init__(self):
        self.media = ""
        self.materials = None
        self.initialized = False

    def init(self):
        addon_dir = pl.Path(__file__).parent
        cache_mat_list = addon_dir.joinpath("tl2_materials.txt")
        cache_mat_dict = addon_dir.joinpath("tl2_mat_dict.pickle")

        self.media = pl.Path(get_addon_pref(bpy.context).tl2_media_dir)

        if not cache_mat_list.exists():
            print("Create Materials List")

            self.materials = [mat.relative_to(self.media) for mat in self.media.glob("**/*.MATERIAL")]
            with cache_mat_list.open("w") as fobj:
                for mat in self.materials:
                    fobj.write(str(mat) + "\n")

        else:
            with cache_mat_list.open() as fobj:
                self.materials = tuple(pl.Path(txt_line[:-1]) for txt_line in fobj)

        if not cache_mat_dict.exists():
            print("Create Material Dictionary")
            self.mat_dict = dict()

            for index, mat in enumerate(self.materials):
                with (self.media / mat).open() as fobj:
                    for txt_line in fobj:
                        if txt_line.startswith("material"):
                            mat_name = txt_line.split(" ")[1][:-1]

                            value = self.mat_dict.get(mat_name, None)
                            if value is None:
                                self.mat_dict[mat_name] = index
                            elif isinstance(value, int):
                                self.mat_dict[mat_name] = [value, index]
                            else:
                                self.mat_dict[mat_name].append(index)

            with cache_mat_dict.open("wb") as fobj:
                pickle.dump(self.mat_dict, fobj, pickle.HIGHEST_PROTOCOL, fix_imports=False)

        else:
            with cache_mat_dict.open("rb") as fobj:
                self.mat_dict = pickle.load(fobj)

        self.initialized = True
        print("Material Library Initialized")

    def choose_mat(self, mesh_file, mat_name, file_indices):
        mat_files = [self.media / self.materials[fi] for fi in file_indices]
        mat_path = pl.Path(mesh_file).relative_to(self.media).with_suffix(".MATERIAL")
        dir_path = mat_path.parent

        def key(i):
            result = 0
            for a, b in zip(mat_files[i].parts, mat_path.parts):
                if a == b:
                    result += 1
                else:
                    break

            return result

        by_coverage = sorted(
            range(len(mat_files)),
            key=key
        )

        return file_indices[by_coverage[0]]


    def get_files(self, mesh_input, mat_names):
        if not self.initialized: self.init()

        files = set()
        for mat_name in mat_names:
            value = self.mat_dict.get(mat_name)
            if value is None:
                continue
            if isinstance(value, list):
                value = self.choose_mat(mesh_input, mat_name, value)
            files.add(value)

        return tuple(str(self.media / self.materials[f]) for f in files)

matlib = TL2_MaterialLib()
