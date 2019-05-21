import os, subprocess, tempfile, shutil, gzip

COMPRESSED_RGB_PVRTC_4BPPV1_IMG      = 0x8C00
COMPRESSED_RGB_PVRTC_2BPPV1_IMG      = 0x8C01
COMPRESSED_RGBA_PVRTC_4BPPV1_IMG     = 0x8C02
COMPRESSED_RGBA_PVRTC_2BPPV1_IMG     = 0x8C03

plugin_dir = os.path.realpath(__file__).rsplit(os.sep,2)[0]
# TODO: detect platform
pvrtex_binary = os.path.join(plugin_dir,'bin','PVRTexToolCLI/Windows_x86_64/PVRTexToolCLI.exe')

def encode_pvrtc(in_path, out_path, use_fast, use_alpha, use_2bpp, use_smaller):
    cwd = os.getcwd()
    format = 'PVRTC1_2' if use_2bpp else 'PVRTC1_4'
    if not use_alpha:
        format += '_RGB'
    format += ',UB' # TODO: UBN or SBN for normals?
    format += ',lRGB' # TODO: sRGB
    quality = 'pvrtcveryfast' if use_fast else 'pvrtcbest'

    square = '+'
    if use_smaller:
        square = '-'
    # dither?
    command = [pvrtex_binary, '-i', in_path, '-f', format, '-mfilter', 'cubic',
        '-squarecanvas', square, '-m', '-flip', 'y', '-legacypvr', '-o', out_path]
    process = subprocess.Popen(command)
    process.wait()
    os.chdir(cwd)
    if process.returncode != 0:
        raise Exception(' '.join([str(x) for x in
            ["PVRTexTool failed with return code",process.returncode,"when encoding",in_path]]))
    # compress
    with open(out_path, 'rb') as f_in, gzip.open(out_path+'.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

def get_pvrtc_format_enum(sRGB, use_alpha, use_2bpp):
    if use_2bpp:
        if use_alpha:
            format = COMPRESSED_RGBA_PVRTC_2BPPV1_IMG
        else:
            format = COMPRESSED_RGB_PVRTC_2BPPV1_IMG
    else:
        if use_alpha:
            format = COMPRESSED_RGBA_PVRTC_4BPPV1_IMG
        else:
            format = COMPRESSED_RGB_PVRTC_4BPPV1_IMG
    return format
