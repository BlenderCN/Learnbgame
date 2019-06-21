import struct
import datetime

class BufferReader:
    def __init__(self, buffer):
        self.buffer = buffer
        self.__offset__ = 0

    def IsEOF(self, lookaheadByteCount=0):
        return ((self.__offset__ + lookaheadByteCount) >= len(self.buffer))

    def NextInt8(self, lookahead=False):
        if lookahead:
            return self.buffer[self.__offset__]
        else:
            self.__offset__ += 1
            return self.buffer[self.__offset__ - 1]

    def NextInt32(self, lookahead=False):
        if lookahead:
            return struct.unpack_from("i", self.buffer, self.__offset__)[0]
        else:
            self.__offset__ += 4
            return struct.unpack_from("i", self.buffer, self.__offset__ - 4)[0]

    def NextUInt32(self, lookahead=False):
        if lookahead:
            return struct.unpack_from("I", self.buffer, self.__offset__)[0]
        else:
            self.__offset__ += 4
            return struct.unpack_from("I", self.buffer, self.__offset__ - 4)[0]

    def NextFloat32(self, lookahead=False):
        if lookahead:
            return struct.unpack_from("f", self.buffer, self.__offset__)[0]
        else:
            self.__offset__ += 4
            return struct.unpack_from("f", self.buffer, self.__offset__ - 4)[0]

    def NextChar(self, lookahead=False):
        if lookahead:
            return chr(self.buffer[self.__offset__])
        else:
            self.__offset__ += 1
            return chr(self.buffer[self.__offset__ - 1])

    def GetCurrentOffset(self):
        return self.__offset__

    def SetCurrentOffset(self, offset):
        self.__offset__ = offset

def PreviewObjectDepth(buffer: BufferReader, startDepth=-1):
    offsetTemp = buffer.GetCurrentOffset()
    
    while buffer.NextChar() == "[":
        startDepth += 1

    buffer.SetCurrentOffset(offsetTemp)

    return startDepth

def ReadNullByteString(buffer: BufferReader):
    stringValue = ""
        
    char = buffer.NextChar()
        
    while char != "\x00":
        stringValue += char
        char = buffer.NextChar()

    return stringValue

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

def TranslatePropertyName(originalName: str):
    if originalName == "p":
        return "vertices"
    elif originalName == "n":
        return "normals"
    elif originalName == "ta":
        return "tangents"
    elif originalName == "u0":
        return "uv_map"
    elif originalName == "tri":
        return "faces"

    return originalName

def TransposeCoordinateArray4D(data):
    result = []

    if len(data) % 4 == 0:
        for i in my_range(0, len(data) - 4, 4):
            result.append((data[i], data[i + 1], data[i + 2], data[i + 3]))

        return result
    else:
        return result

def TransposeCoordinateArray3D(data):
    result = []

    if len(data) % 3 == 0:
        for i in my_range(0, len(data) - 3, 3):
            result.append((data[i], data[i + 1], data[i + 2]))

        return result
    else:
        return result

def TransposeCoordinateArray2D(data):
    result = []

    if len(data) % 2 == 0:
        for i in my_range(0, len(data) - 2, 2):
            result.append([data[i], data[i + 1]])

        return result
    else:
        return result

class LogLevel:
    DEBUG = 1
    INFO = 2
    NOTICE = 3
    WARNING = 4
    ERROR = 5
    CRITICAL = 6
    ALERT = 7
    EMERGENCY = 8

    @staticmethod
    def GetLogLevelString(level):
        if level == LogLevel.DEBUG:
            return "DEBUG"
        elif level == LogLevel.INFO:
            return "INFO"
        elif level == LogLevel.NOTICE:
            return "NOTICE"
        elif level == LogLevel.WARNING:
            return "WARNING"
        elif level == LogLevel.ERROR:
            return "ERROR"
        elif level == LogLevel.CRITICAL:
            return "CRITICAL"
        elif level == LogLevel.ALERT:
            return "ALERT"
        elif level == LogLevel.EMERGENCY:
            return "EMERGENCY"
        else:
            return ""

class Log:
    MIN_LOG_LEVEL = LogLevel.INFO

    @staticmethod
    def debug(message):
        Log.log(LogLevel.DEBUG, message)

    @staticmethod
    def info(message):
        Log.log(LogLevel.INFO, message)
    
    @staticmethod
    def notice(message):
        Log.log(LogLevel.NOTICE, message)

    @staticmethod
    def warning(message):
        Log.log(LogLevel.WARNING, message)

    @staticmethod
    def error(message):
        Log.log(LogLevel.ERROR, message)

    @staticmethod
    def critical(message):
        Log.log(LogLevel.CRITICAL, message)

    @staticmethod
    def alert(message):
        Log.log(LogLevel.ALERT, message)

    @staticmethod
    def emergency(message):
        Log.log(LogLevel.EMERGENCY, message)
        assert "Emergency Assert"

    @staticmethod
    def log(level, message):
        if level >= Log.MIN_LOG_LEVEL:
            print(str(datetime.datetime.now()).split('.')[0] + " - " + LogLevel.GetLogLevelString(level) + " ::: " + str(message))
