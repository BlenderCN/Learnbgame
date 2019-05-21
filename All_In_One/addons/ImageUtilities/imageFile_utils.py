class ImageFormatEnum:
    items = (('jpg', "JPG", "jpg"),
             ('png', "PNG", "png"),
             ('tif', "TIFF", "tif"),
             ('tga', "TGA", "tga"),
             ('psd', "PSD", "psd"),
             ('exr', "EXR", "exr"),
             )

    @staticmethod
    def getList():
        enumList = list()
        for ent in ImageFormatEnum.items:
            enumList.append(ent[0])

        return enumList

    @staticmethod
    def getTuple():
        return tuple(ImageFormatEnum.getList())