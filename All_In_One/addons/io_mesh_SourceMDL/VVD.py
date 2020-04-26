import sys

try:
    from .MDLIO_ByteIO import ByteIO
    from .VVD_DATA import SourceVvdFileData
except Exception:
    from MDLIO_ByteIO import ByteIO
    from VVD_DATA import SourceVvdFileData


class SourceVvdFile49:
    def __init__(self, path=None, file=None):
        if path:
            self.reader = ByteIO(path=path + ".vvd")
        elif file:
            self.reader = file
        self.file_data = SourceVvdFileData()
        self.file_data.read(self.reader)

    def test(self):
        for v in self.file_data.vertexes:
            print(v)


if __name__ == '__main__':
    with open('log.log', "w") as f:  # replace filepath & filename
        with f as sys.stdout:
            # model_path = r'.\test_data\xenomorph'
            # model_path = r'.\test_data\hard_suit'
            # model_path = r'.\test_data\l_pistol_noenv'
            model_path = r'G:\SteamLibrary\SteamApps\common\SourceFilmmaker\game\usermod\models\red_eye\tyranno\raptor'
            # MDL_edit('E:\\MDL_reader\\sexy_bonniev2')
            SourceVvdFile49(model_path).test()
