import os
import os.path
import subprocess
import shutil
import json
import tempfile
import urllib.request

class Tungsten:
    def __init__(self, exe, scenefile, port=14889, threads=None):
        self.port = port

        fd, self.preview_f = tempfile.mkstemp(suffix='.png')
        os.close(fd)

        args = [exe, scenefile]
        args += ['--port', str(port)]
        if threads:
            args += ['--threads', str(threads)]
        
        self.proc = subprocess.Popen(args)

    def __del__(self):
        if os.path.exists(self.preview_f):
            os.unlink(self.preview_f)

    def finish(self):
        self.proc.wait()
        return self.proc.returncode

    def cancel(self):
        self.proc.terminate()

    @property
    def running(self):
        return self.proc.poll() is None

    def get_url(self, leaf):
        return urllib.request.urlopen('http://localhost:{0}{1}'.format(self.port, leaf))
    
    def get_render(self):
        with self.get_url('/render') as img:
            with open(self.preview_f, 'wb') as tmp:
                shutil.copyfileobj(img, tmp)
        return self.preview_f

    def get_status(self):
        with self.get_url('/status') as f:
            d = f.read().decode('utf-8')
            return json.loads(d)
