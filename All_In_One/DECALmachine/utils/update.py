import os
import time
from .. import bl_info
from .. modules.requests_futures.sessions import FuturesSession
from . registration import get_path, get_prefs
from . system import makedir


def write_date(path, date):
    with open(path, "w") as f:
            f.write(date)


def request_update():
    def response_hook(resp, *args, **kwargs):
        if resp:
            if resp.text == "true":
                get_prefs().update_available = True

    revision = bl_info.get("revision")

    if revision:
        data = {"revision": revision}
        headers = {'User-Agent': 'DECALmachine/%s' % (".".join([str(v) for v in bl_info.get("version")]))}

        session = FuturesSession()

        try:
            session.post("https://drum.machin3.io/update", data=data, headers=headers, hooks={'response': response_hook})
        except:
            pass


def update_check():
    get_prefs().update_available = False

    if get_prefs().check_for_updates:
        logspath = makedir(os.path.join(get_path(), "logs"))
        lastupdatepath = os.path.join(logspath, "last_update.check")

        date = time.strftime("%Y%m%d", time.localtime())

        saveddate = None

        # look for a saved date of the last update check
        if os.path.lexists(lastupdatepath):
            with open(lastupdatepath, "r") as f:
                saveddate = f.read()

        # if the file could be read, check if the contents can be converted to int
        if saveddate:
            try:
                saveddate = int(saveddate)

            # contents couldn't be converted to int
            except:
                write_date(lastupdatepath, date)
                saveddate = True

        # first time or empty file
        else:
            write_date(lastupdatepath, date)
            saveddate = True

        # if current date is newer than saved one, make request
        if saveddate and int(date) > saveddate:
            # print("checking for update")

            request_update()

            write_date(lastupdatepath, date)

        # else:
            # print("already checked for update today")
