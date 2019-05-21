import io
import re
from pprint import pprint
isfloat = lambda x: x.replace('.','',1).isdigit() and "." in x

class KeyValues:
    kv_regex = re.compile('\"(?P<key>[a-zA-z_|0-9]+)\" ? \"(?P<value>[a-zA-z_| 0-9-./*]+|\"?)\"')

    def __init__(self,file:io.TextIOWrapper):
        self.data = file.read()
        self.holder = []
        self.parse()


    def parse(self):
        while len(self.data)>50:
            open_ = self.data.find('{')+1
            close_ = self.data.find('}')
            local_data = self.data[open_:close_].strip()
            local_holder = {}
            for line in local_data.split('\n'):
                kv = self.kv_regex.search(line)
                if kv is None:
                    continue
                key = kv.group('key')
                value = kv.group('value')
                # print(key,value)
                if kv.group('value').split(' ').__len__() == 3:
                    value = kv.group('value').split(' ')
                    if map(lambda a:a.replace('.','',1).isnumeric(),value):
                        if map(lambda a:isfloat(a),value):
                            value = list(map(float,value))
                        else:
                            value = list(map(int,value))
                elif value.replace('.','',1).isnumeric():
                    if isfloat(value):
                        value = float(value)
                    else:
                        value = int(value)
                local_holder[key] = value
            self.holder.append(local_holder)
            self.data = self.data[close_+1:]
    def dump(self):
        return self.holder


if __name__ == '__main__':
    a = KeyValues(open('../kv.kv','r'))
    pprint(a.dump())