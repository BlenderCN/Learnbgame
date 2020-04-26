import os.path
import os
import re
import sys
import json

class JsonTools():
    def __init__(self, filepath=None, dictionary=None):
        """
            filepath
                jsonデータをロードするパス
            dict
                ロードせずに、辞書を設定する
        """
        open_result = False
        if filepath:
            open_result = self.open(filepath)
        
        if not open_result:
            self.filepath = filepath
            self.dictionary = {}
            if dictionary:
                self.dictionary = dictionary
        return
    
    def open(self, filepath):
        self.filepath = filepath
        if not os.path.exists(filepath):
            return False

        f = open(filepath, "r")
        j = json.load(f)
        f.close()
        self.dictionary = j
        return True
    
    def save(self, filepath=None):
        if filepath:
            self.filepath = filepath
        if not self.filepath:
            print("filepath is None!")
            return False
        #セーブ処理
        f = open(self.filepath, "w")
        json.dump(self.dictionary, f, indent=4)
        f.close()
        return True


    def __get_val(self, datapath):
        keys = datapath.split("/")
        d = self.dictionary
        for key in keys:
            if key in d:
                d = d[key]
            else:
                d = None
                break
        #dには最終的に、最深部の値かNoneが入っているはず。
        return d

    def __nested_dict(self, keys, value):
        reuslt = None
        v = value
        for key in keys[::-1]:
            v = {key:v}
        return v

    def __set_val(self, datapath, value):
        #ここまともに実装できてない
        keys = datapath.split("/")
        d = self.dictionary

        for index, key in enumerate(keys):
            if key in d:
                d = d[key]
            else:
                #ここから未設定だから新規作成する
                d[key] = self.__nested_dict(keys[index+1:], value)
                break

    def val(self, datapath=None, value=None):
        """
            /区切りでデータパスを記述する。
            valueなしで取得、ありで値の設定。
        """

        if value is None:
            return self.__get_val(datapath)
        else:
            self.__set_val(datapath, value)

