try:
    from MDLIO_ByteIO import ByteIO
except:
    from ...MDLIO_ByteIO import ByteIO


class Dummy:

    def read(self, reader: ByteIO):
        raise NotImplementedError()

    def __repr__(self):
        template = '<{} {}>'
        member_template = '{}:{}'
        members = []
        for key, item in self.__dict__.items():
            members.append(member_template.format(key, item))
        return template.format(type(self).__name__, ' '.join(members))