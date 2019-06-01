"""
Manage user connections to opensim.
"""

import sys
import logging
logger = logging.getLogger('b2rex.simconnection')

if sys.version_info[0] == 2:
    import xmlrpclib
    import httplib
else:
    import xmlrpc.client as xmlrpclib
    import http.client as httplib

class PersistTransport(xmlrpclib.Transport):
    '''Provides a Transport for the xmlrpclib that uses httplib
    supporting persistent connections
    Does not close the connection after each request.
    '''
    connection = None

    def request(self, host, handler, request_body, verbose=0):
        if not self.connection:
            host, extra_headers, x509 = self.get_host_info(host)
            self.connection = httplib.HTTPConnection(host)
            self.headers = {"User-Agent" : self.user_agent,
                           "Content-Type" : "text/xml",
                            "Accept": "text/xml"}
            if extra_headers:
                for key, item in extra_headers:
                    self.headers[key] = item

            self.headers["Content-Length"] = str(len(request_body))
            self.connection.request('POST', handler, request_body,
            self.headers)
            r = self.connection.getresponse()
            if r.status != 200:
                self.connection.close()
                self.connection = None
                raise xmlrpclib.ProtocolError( host + handler, r.status,
            r.reason, '' )
            data = r.read()
            p, u = self.getparser()
            p.feed(data)
            p.close()
            return u.close()

class SimConnection(object):
    def __init__(self):
        self.session_id = None
        self._con = None
        self.avatar_uuid = None

    def connect(self, url):
        """
        Connect to the xmlrpc server.
        """
        self._con = xmlrpclib.Server(url, transport=PersistTransport())

    def login(self, first, last, passwd):
        """
        Login with user credentials.
        """
        r = self._con.login_to_simulator({'first':first, 'last':last,
                                      'web_login_key':'unknownrex',
                                          'passwd':passwd,
                                          'start':'home'})
        self.session_id = r['session_id']
        self.avatar_uuid = r['agent_id']
        return r

    def sceneUpload(self, region_uuid, pack_name, file_name):
        """
        Upload given scene to the server.
        """
        f = open(file_name, "r")
        r = self._con.ogrescene_upload({"AgentID": pack_name,
                                    "RegionID": region_uuid,
                                    "AvatarURL": xmlrpclib.Binary(f.read()),
                                    "PackName": pack_name})
        f.close()
        return r

    def sceneClear(self, region_uuid, pack_name):
        """
        Clear all objects from the given scene.
        """
        r = self._con.ogrescene_clear({"AgentID": pack_name,
                                   "RegionID": region_uuid,
                                   "PackName": pack_name})
        return r



if __name__ == "__main__":
    con = SimConnection()
    logger.debug(con.connect("http://taigalife.ath.cx:8002"))
    login_info = con.login("Blender", "b2rex", "B2rex")
    print(login_info["sim_ip"], login_info["sim_port"])
    sys.exit()
    logger.debug(con.connect("http://10.66.66.79:8002"))
    logger.debug(con._con.get_user_by_name({"avatar_name":"caedes caedes"}))
    logger.debug(con._con.get_user_by_uuid({"avatar_uuid":"01581bd0-a8c3-485a-9b23-4959c98673ad"}))
    #a = con._con.search_for_region_by_name({"name":"Taiga"})
    #print con._con.user_alert({"name":"Taiga"})
    #print con._con.check({})
    scenedata = con._con.ogrescene_list({"RegionID":"0a1b14b9-ca02-481d-bf77-9cbeca1ab050"})
    last_asset = None
    for groupid, scenegroup in scenedata['res'].iteritems():
        #print " *", scenegroup["name"],scenegroup["asset"],   scenegroup["groupid"], scenegroup["primcount"],"\n"
        logger.debug(groupid,scenegroup)
        last_asset = scenegroup["asset"]
        assetdata = con._con.ogrescene_getasset({"assetid":last_asset})
        #print assetdata["res"]
        if assetdata:
            assetdata = assetdata["res"]
            logger.debug((" *", scenegroup["name"], assetdata["name"],
                          assetdata["type"], len(assetdata["asset"].data),
                          last_asset))
        else:
            logger.debug((" *", scenegroup["name"]))
        if False: #"materials" in scenegroup:
            for mat in scenegroup['materials'].values():
                if isinstance(mat, xmlrpclib.Binary):
                    #                   print mat.decode()
                    logger.debug(mat.data)
    assetdata = con._con.ogrescene_getasset({"assetid":last_asset})
    logger.debug(assetdata["res"])
    #a = con._con.admin_create_region({"password":"unknownrex",
    #                                  "region_name":"test2", "region_master_first":"caedes","region_master_last":"caedes","region_master_password":"caedes","external_address":"127.0.0.1","listen_ip":"127.0.0.1","listen_port":9002,"region_x":999,"region_y":1001})
    #con._con.admin_delete_region({"password":"unknownrex",
    #                              "region_name":a["region_name"]})
    #print con.sceneClear("d9d1b302-5049-452d-b176-3a9561189ca4", "cube")
    #print con.sceneUpload("d9d1b302-5049-452d-b176-3a9561189ca4", "cube",
    #                     "/home/caedes/groupmembers.zip")

