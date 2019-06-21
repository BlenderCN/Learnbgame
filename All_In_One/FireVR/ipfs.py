from subprocess import Popen, call, check_output, STDOUT, PIPE, CalledProcessError
from tempfile import TemporaryFile, NamedTemporaryFile, tempdir
import base64
import os

DEVNULL = open(os.devnull, "wb")

CALL_OPTIONS = {"stderr" : DEVNULL}
CALL_OPTIONS = {"stdout" : DEVNULL}

def init():
    call(["ipfs", "init"], stdout=DEVNULL, stderr=DEVNULL)

def daemon():
    try:
        Popen(["ipfs", "daemon"], stdout=DEVNULL, stderr=DEVNULL)
    except CalledProcessError:
        pass

def start():
    init()
    daemon()
  
def add(path, pin=True):
    if type(path)==str:
        output = check_output(["ipfs", "add", path]).decode("ascii")
    else:
        try:
            output = check_output(["ipfs", "add"], stdin=path).decode("ascii")
        except CalledProcessError as err:
            output = err.output
    """
    if pin:
        try:
            check_output(["ipfs", "pin", output.split(" ")[1]])
        except CalledProcessError as err:
            pass
    """
    return output.split(" ")[1]

def addRecursive(path):
    out = check_output(["ipfs", "add", "-r", path]).decode("utf-8")
    return [line.split(" ")[1] for line in out.split("\n") if len(line)>1]
     
def cat(path):
    check_output(["ipfs", "cat", path])
  
def get(path):
    try:
        output = check_output(["ipfs", "get", path], stderr=DEVNULL)
    except CalledProcessError as err:
        output = err.output
    return output.split(" ")[-1].strip()
    
def publish(path):
    return check_output(["ipfs", "name", "publish", path])
    
def resolve(path):
    return check_output(["ipfs", "name", "resolve", path])

def ls(path):
    return check_output(["ipfs", "ls", path])
  
def refs(path):
    return check_output(["ipfs", "refs", path])
    
def save(bytes):
    with TemporaryFile("wb+") as f:
        f.seek(0)
        f.write(bytes)
        f.flush()
        f.seek(0)
        return add(f)
    
def load(path):
    if os.path.isfile(path):
        with open(path, "rb+") as t:
            t.seek(0)#why is this necessary?
            d = t.read()

    else:
        #with NamedTemporaryFile("rb+") as f:
        #    err = get(path, f)
        #    print("ERR",err)
        #    f.seek(0)
        #    d = f.read()
        err = get(path)#tempdir
        with open(path,"rb+") as f:#~/.go-ipfs/datastore/"+
            d = f.read()
        
    return d
  
#start()
