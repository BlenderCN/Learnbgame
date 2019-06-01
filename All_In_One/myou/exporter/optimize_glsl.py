
import tempfile, subprocess, os
tempdir = tempfile.gettempdir()
plugin_dir = os.path.realpath(__file__).rsplit(os.sep,2)[0]
glsl_optimizer_binary = os.path.join(plugin_dir,'bin','glsl_optimizer.exe')

def optimize_glsl(parts, type="fragment", target="opengl-es2"):
    f = tempfile.NamedTemporaryFile(suffix=".glsl", delete=False)
    for part in parts:
        f.write(part.encode())
    f.close()
    out, err = subprocess.Popen([glsl_optimizer_binary, '--'+type, '--'+target, f.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if out:
        out = out.decode().replace('\r\n','\n').strip()
    os.unlink(f.name)
    if not out:
        if not err:
            err = b'Unknown error'
        raise Exception("Failed optimizing shader:\n"+err.decode().replace('\r\n','\n'))
    return out
