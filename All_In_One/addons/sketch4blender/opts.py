class Options(dict):
    def __init__(self, strings, line=None):
        super(Options, self).__init__()
        for pair in strings.split(','):
            key, val = pair.split('=')
            print(key, val)
            if key:
                self[key] = val
            # TODO(david): error
