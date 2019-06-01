
class Version(object):

    def __init__(self, major: int=0, minor: int=0):
        self.major = major
        self.minor = minor

    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor

    def __lt__(self, other):
        return self.major < other.major or (self.major == other.major and self.minor < other.minor)

    def __gt__(self, other):
        return self.major > other.major or (self.major == other.major and self.minor > other.minor)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __str__(self):
        return '.'.join([str(x) for x in [self.major, self.minor]])
