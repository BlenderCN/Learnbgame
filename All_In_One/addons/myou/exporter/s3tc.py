import os, subprocess, tempfile, shutil, gzip

COMPRESSED_RGB_PVRTC_4BPPV1_IMG      = 0x8C00
COMPRESSED_RGB_PVRTC_2BPPV1_IMG      = 0x8C01
COMPRESSED_RGBA_PVRTC_4BPPV1_IMG     = 0x8C02
COMPRESSED_RGBA_PVRTC_2BPPV1_IMG     = 0x8C03

plugin_dir = os.path.realpath(__file__).rsplit(os.sep,2)[0]
# TODO: detect platform
crunch_binary = os.path.join(plugin_dir,'bin','crunch_x64.exe')

def encode_s3tc(in_path, out_path, use_alpha):
    cwd = os.getcwd()
    command = [crunch_binary, '-file', in_path, '-fileformat', 'dds',
    '-yflip']
    if use_alpha:
        command += ['-DXT5']
    else:
        command += ['-DXT1']
    if 0: # fast quality
        command += ['-dxtQuality', 'superfast']
    process = subprocess.Popen(command+['-out', out_path])
    process.wait()
    if process.returncode != 0:
        raise Exception(' '.join([str(x) for x in
            ["Crunch failed with return code",process.returncode,"when encoding",in_path]]))
    # compress
    with open(out_path, 'rb') as f_in, gzip.open(out_path+'.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
