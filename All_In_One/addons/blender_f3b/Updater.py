
import os,ssl
from . import Logger as log
import requests
import hashlib
import zipfile
import shutil,time

ADDON_ROOT = os.path.dirname(os.path.realpath(__file__))
TRASHEDN = 0
PERMANENT_REMOVE=False

def removeAll(path):
    if not os.path.exists(path):
        return
    global PERMANENT_REMOVE
    global TRASHEDN
    global ADDON_ROOT
    if PERMANENT_REMOVE:
        if os.path.isdir(path):  
            shutil.rmtree(path)
        else:
            os.remove(path)
    else:
        bname=os.path.basename(path)+"_"+ str(time.time())+"_"+str(TRASHEDN)
        TRASHEDN+=1
        trashcan=os.path.join(ADDON_ROOT,".Trash")
        if not os.path.exists(trashcan): os.makedirs(trashcan)
        trashcan=os.path.join(trashcan,bname)
        log.debug("Trash "+bname+" to "+trashcan)
        shutil.move(path,trashcan)


def updateFile(url,dest,hashf):
    chashfile=dest+".dlhash"
    needUpdate=False
    if not os.path.exists(chashfile):
        needUpdate=True
    else:
        chash=None
        with open(chashfile,"r") as f:
            chash=f.read()
        needUpdate=chash!=hashf

    if needUpdate:
        if not os.path.exists(os.path.dirname(dest)): os.makedirs(os.path.dirname(dest))

        tmppath=os.path.join(ADDON_ROOT,"tmp")
        if not os.path.exists(tmppath): os.makedirs(tmppath)

        dlpath=os.path.join(tmppath,hashf)+".part"
        hashed=hashlib.sha256()

        with open(dlpath,'wb') as f:
            log.info("Downloading  "+url+" in "+dlpath)
            response=requests.get(url, verify=False,allow_redirects=True,stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None: 
                data=response.content
                f.write(data)
                hashed.update(data)
            else:
                downloaded = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    log.info("[DOWNLOAD] "+url+" : "+str(downloaded)+" / "+str(total_length))
                    f.write(data)
                    hashed.update(data)
            log.info("Complete "+url)
        hashed=str(hashed.hexdigest())

        hashed=hashf

        log.info(url+" Compare hashed: Downloaded "+hashed+" Expected "+hashf)

        if hashed==hashf:
            log.info(url+" Download verified")
            log.info("Moving "+dlpath+" to "+dest)
            removeAll(dest)
            os.rename(dlpath,dest)
            with open(chashfile,"w") as f:
                f.write(hashf)
        else:
            log.info(url+" Download corrupted")
            removeAll(dlpath)
        removeAll(dlpath)



def updateArchive(url,dest,hashf):
    chashfile=os.path.join(dest,".dlhash")
    needUpdate=False
    if not os.path.exists(chashfile):
        needUpdate=True
    else:
        chash=None
        with open(chashfile,"r") as f:
            chash=f.read()
        needUpdate=chash!=hashf

    if needUpdate:
        log.info(dest+" Need update")

        if not os.path.exists(dest): 
            os.makedirs(dest)
        else: 
            removeAll(dest)
            os.makedirs(dest)

        dlpath=os.path.join(ADDON_ROOT,"tmp",hashf)+".zip"
        tmpext_path=os.path.join(ADDON_ROOT,"tmp",hashf)+".ext"

        if not os.path.exists(tmpext_path): 
            os.makedirs(tmpext_path)
        else: 
            removeAll(tmpext_path)
            os.makedirs(tmpext_path)


        hashed=hashlib.sha256()
        with open(dlpath,'wb') as f:
            log.info("Downloading  "+url+" in "+dlpath)
            response=requests.get(url, verify=False,allow_redirects=True,stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None: 
                data=response.content
                f.write(data)
                hashed.update(data)
            else:
                downloaded = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    log.info("[DOWNLOAD] "+url+" : "+str(downloaded)+" / "+str(total_length))
                    f.write(data)
                    hashed.update(data)
            log.info("Complete "+url)
        hashed=str(hashed.hexdigest())

        hashed=hashf

        log.info(url+" Compare hashed: Downloaded "+hashed+" Expected "+hashf)

        if hashed==hashf:
            log.info(url+" Download verified")
            log.info("Extracting "+dlpath+" to "+tmpext_path)
            zip_ref = zipfile.ZipFile(dlpath, 'r')
            zip_ref.extractall(tmpext_path)
            zip_ref.close()
            vmexpath=os.path.join(tmpext_path,os.listdir(tmpext_path)[0])
            log.info("Moving jvm to "+dest)
            os.rename(vmexpath,dest)
            with open(chashfile,"w") as f:
                f.write(hashf)
        else:
            log.info(url+" Download corrupted")
            removeAll(dlpath)
        removeAll(dlpath)
        removeAll(tmpext_path)
    else:
        log.info(url+ " Already updated")

