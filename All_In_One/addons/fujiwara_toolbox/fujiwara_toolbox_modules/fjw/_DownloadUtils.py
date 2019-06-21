import os
import shutil
import urllib.request

class DownloadUtils():
    user_dir = os.path.expanduser('~')
    tmp_dir = user_dir + os.sep + "fjwtmpdl"

    def __init__(self):
        pass
    
    def make_temp(self):
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

    def del_temp(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
    
    def download(self, url, name=None):
        """ダウンロードしてファイルパスを返す"""
        if name is None:
            name = os.path.basename(url)
        print(name)
        self.make_temp()
        dest_path = self.tmp_dir + os.sep + name
        urllib.request.urlretrieve(url, dest_path)
        return dest_path
