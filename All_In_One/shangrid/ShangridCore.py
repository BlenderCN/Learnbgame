'''
Created on 2016/10/23

@author: take
'''

import bpy
import bmesh
import threading
import time
import socket
import json
import re

def createInitialTable(meshObj,selectedOnly):
    mesh=meshObj.data
    body={}
    body["header_row"]=[ vg.name for vg in meshObj.vertex_groups]
    rows=[]
    if selectedOnly:
        editMesh=bmesh.from_edit_mesh(mesh)
    for i in range(len(mesh.vertices)):
        if selectedOnly:
            if not editMesh.verts[i].select:
                continue
        row={"name":"v[{0}]".format(i)}

        rowData=[]
        for vg in meshObj.vertex_groups:
            value=0.0
            try:
                value=vg.weight(i)
            except:
                pass
            rowData.append(value)
        row["data"]=rowData
        rows.append(row)
    body["rows"]=rows
    root={"type":0}
    root["body"]=body
    return root

class ShangridCore:
    def __init__(self):
        self.__client=None

    def start(self,meshObj,selectedOnly):
        if self.__client:
            raise RuntimeError("Started")
        self.__meshObj=meshObj
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__client.connect(("localhost",10502))
        except:
            self.__client=None
            return
#         self.__thread=threading.Thread()
        initData=json.dumps(createInitialTable(meshObj,selectedOnly))

        self.__sendMessage(initData)
        self.__socketfile=self.__client.makefile()
        self.__thread=ShangridCoreThread(self)
        self.__loop=True
        self.__thread.start()

    def updateSelected(self,meshObj,selectedOnly):
        if self.__client is not None:
            self.__meshObj=meshObj
            initData=json.dumps(createInitialTable(meshObj, selectedOnly))
            self.__sendMessage(initData)

    def stop(self):
        self.__loop=False
        self.__client.close()
#         if not self.__thread is None:
#             self.__thread.join()

    def polling(self):
        print("==Shangrid START==")
        while(self.__loop):
            line=""
            try:
                line=self.__socketfile.readline()
            except:
                break
            print(line)
            if line=="":
                break
            try:
                self.__applyCommand(line)
            except Exception as e:
                print(e)
                break

            time.sleep(0.1)
        print("==Shangrid FINISH==")
        self.__socketfile.close()
        self.__client.close()
        self.__client=None
        self.__meshObj=None
        self.__thread=None

    def __exit__(self):
        self.stop()


    def __sendMessage(self,message):
        message=message+"\n"
        self.__client.sendall(message.encode(encoding='utf_8'))

    def __applyCommand(self,command):
        commandData=json.loads(command)
        body=commandData["body"]
        vgs=self.__meshObj.vertex_groups
        for c in body["changed"]:
            vg=vgs[c["col"]]
            m=re.search(r"v\[(\d+)\]",c["row"])
            index=int(m.group(1))
            vg.add([index],c["value"],'REPLACE')

        self.__meshObj.data.update()


class ShangridCoreThread(threading.Thread):
    def __init__(self,core):
        self.__core=core
        threading.Thread.__init__(self)
    def run(self):
        self.__core.polling()