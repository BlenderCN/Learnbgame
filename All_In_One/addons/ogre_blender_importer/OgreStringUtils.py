
class OgreStringUtils:
    def trim(string, left=True, right=True):
        """
        Removes any whitespace characters, be it standard space or
        TABs and so on.
        @remarks
        The user may specify whether they want to trim only the
        beginning or the end of the String ( the default action is
        to trim both).
        """
        lspaces=0;
        rspaces=0;
        if (left):
            for i in range (len(string)):
                if not (string[i] == ' ' or string[i] == '\t' or string[i] == '\r' or string[i] == '\n'):
                    break;
                else:
                    lspaces += 1;
        if (right):
            for i in reversed(range(len(string))):
                if not (string[i] == ' ' or string[i] == '\t' or string[i] == '\r' or string[i] == '\n'):
                    break;
                else:
                    rspaces += 1;
        return string[lspaces:len(string)-rspaces];
