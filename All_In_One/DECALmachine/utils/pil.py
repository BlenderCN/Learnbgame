

def scale_image(imagepath, scale):
    from PIL import Image

    img = Image.open(imagepath)
    size = (int(img.size[0] * scale), int(img.size[1] * scale))

    resized = img.resize(size, Image.ANTIALIAS)
    resized.save(imagepath)
    del img


def crop_image(img=None, imagepath=None, cropbox=None, padding=0, debug=False):
    from PIL import Image

    if not img:
        img = Image.open(imagepath)

    if cropbox:
        cropped = img.crop(cropbox)

    else:
        # image bounds
        bbox = (0, 0, img.size[0], img.size[1])

        # image maximally cropped
        # getbbox only crops away transparent black pixel, but images often have non-black transparent pixels, in fact thats the encouraged way to create them to avoid bleeding
        # so for the bbox creation, the image should be premultiplied, which creates black transparent pixels, see https://stackoverflow.com/a/37942933/9350787
        cmaxbox = img.convert("RGBa").getbbox()

        if debug:
            print("image bounds:", bbox)
            print(" max cropped:", cmaxbox)

        # add padding
        xmin = cmaxbox[0] - padding if cmaxbox[0] - padding > 0 else 0
        ymin = cmaxbox[1] - padding if cmaxbox[1] - padding > 0 else 0
        xmax = cmaxbox[2] + padding if cmaxbox[2] + padding < img.size[0] else img.size[0]
        ymax = cmaxbox[3] + padding if cmaxbox[3] + padding < img.size[1] else img.size[1]

        cropbox = (xmin, ymin, xmax, ymax)

        if debug:
            print("     cropped:", cropbox)

        cropped = img.crop(cropbox)

    size = cropped.size

    cropped.save(imagepath)
    del img, cropped

    return size


def change_contrast(imagepath, contrast):
    from PIL import Image, ImageEnhance

    img = Image.open(imagepath)

    enhance = ImageEnhance.Contrast(img)
    img = enhance.enhance(contrast)

    img.save(imagepath)
    del img


def create_material2_mask(imagepath, width, height):
    from PIL import Image, ImageDraw

    img = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (width, int(height / 2))], fill=255)

    img.save(imagepath)

    del img


def fix_legacy_normals(imagepath):
    """
    replaces black in transparent areas of legacy normals with normal color
    """

    from PIL import Image, ImageDraw

    src = Image.open(imagepath)
    alpha = src.split()[3]

    nrmbg = Image.new('RGBA', src.size, (128, 128, 255, 255))

    nrm_alpha = Image.alpha_composite(nrmbg, src)
    nrm_alpha.putalpha(alpha)

    nrm_alpha.save(imagepath)

    del src, alpha, nrmbg, nrm_alpha


def text2img(savepath, text, font, fontsize=100, padding=(0, 0), offset=(0, 0), align='left', color=(1, 1, 1, 1), bgcolor=(1, 1, 1, 0), gamma=2.2):
    from PIL import Image, ImageFont, ImageDraw

    # convert args for PIL
    color = tuple(int(c * 255) for c in color)
    bgcolor = tuple(int(c * 255) for c in bgcolor)

    # create font object and determine size of textblock
    font = ImageFont.truetype(font, fontsize)
    textsize = font.getsize(text)

    splittext = text.split("\n")
    lines = len(splittext)

    # get size of the text block
    width = max([font.getsize(line)[0] for line in splittext])
    height = lines * textsize[1]
    size = (width + 2 * padding[0], height + 2 * padding[1])

    # create basic image using bgcolor
    img = Image.new("RGBA", size, bgcolor)

    # then draw the text on top
    draw = ImageDraw.Draw(img)
    draw.multiline_text((padding[0] + offset[0], padding[1] + offset[1]), text, color, font=font, align=align)

    if gamma != 1:
        set_gamma(img, gamma, 4)

    img.save(savepath)


def set_gamma(img, gamma, bandcount):
    """
    Fast gamma correction with PIL's image.point() method
    https://gist.github.com/mozbugbox/10cd35b2872628246140
    """
    invert_gamma = 1.0 / gamma
    lut = [pow(x / 255., invert_gamma) * 255 for x in range(256)]
    lut = lut * bandcount  # need one set of data for each band for RGB
    img = img.point(lut)
    return img
