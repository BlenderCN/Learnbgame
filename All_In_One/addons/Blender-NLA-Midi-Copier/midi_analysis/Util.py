class Util:
    # returns a hex value for use in bytes.fromhex
    @staticmethod
    def paddedHex(sourceNum):
        returnVal = hex(sourceNum)[2:]
        if (len(returnVal) % 2) != 0:
            returnVal = '0' + returnVal
        return returnVal

    # returns a bytes object shifted left by numBits bits
    @staticmethod
    def lshiftBytes(sourceBytes, numBits):
        return bytes.fromhex(Util.paddedHex(
            int.from_bytes(sourceBytes, "big") << numBits))

    # returns a byte array shifted left by numBits bits
    @staticmethod
    def lshiftByteArray(sourceByteArray, numBits):
        return bytearray.fromhex(Util.paddedHex(
            int.from_bytes(sourceByteArray, "big") << numBits))

    # takes a bytes object formatted in variable length and
    # returns the int value represented
    # does not check if the variable length value is valid, as
    # it ignores the msb of every byte
    @staticmethod
    def varLenVal(varLenBytes):
        if len(varLenBytes) == 0:
            return 0
        varLenArray = bytearray(varLenBytes)
        returnValBytes = bytearray.fromhex(
            Util.paddedHex(varLenArray[0] & b'\x7f'[0]))
        for i in range(len(varLenBytes) - 1):
            nextByte = varLenArray[i+1] & b'\x7f'[0]
            returnValBytes = Util.lshiftByteArray(returnValBytes, 7)
            returnValBytes[len(returnValBytes)-1] = (
                returnValBytes[len(returnValBytes)-1] | nextByte)
        return int.from_bytes(returnValBytes, "big")        

    @staticmethod
    def msbIsOne(byte):  # returns true if the msb of a bytes object is 1
        return (byte[0] & int('80', 16)) > 0

    # strips a variable length quantity off of a byte array
    # and returns the rest
    @staticmethod
    def stripLeadingVariableLength(byteArray):
        varLenEndIndex = 0
        while (varLenEndIndex < len(byteArray) and
               Util.msbIsOne(byteArray[varLenEndIndex:varLenEndIndex + 1])):
                    varLenEndIndex += 1
        # the last byte of a variable length value has msb 0
        varLenEndIndex += 1
        return byteArray[varLenEndIndex:]

    @staticmethod
    def intFromBytes(byteArray, signed=False):
        return int.from_bytes(byteArray, "big", signed=signed)

    # returns None if no controller Number Mapped
    @staticmethod
    def controllerString(controllerNumber):
        if controllerNumber in Util.CONTROLLER_DICTIONARY:
            return Util.CONTROLLER_DICTIONARY[controllerNumber]
        elif 16 <= controllerNumber <= 19:
            return "General Purpose Controller " + str(controllerNumber - 15)
        elif 32 <= controllerNumber <= 63:
            controllerReferenceString = Util.controllerString(controllerNumber - 32)
            if controllerReferenceString is None:
                return None
            return "LSB for " + controllerReferenceString
        elif 75 <= controllerNumber <= 79:
            return "Sound Controller " + str(controllerNumber - 74)
        elif 80 <= controllerNumber <= 83:
            return "General Purpose Controller " + str(controllerNumber - 79)        
        return None

    # maps [byte with event type and channel] & b'\xf0' to event type
    CONTROLLER_DICTIONARY = {0: "Bank Select",
                             1: "Modulation",
                             2: "Breath Controller",
                             4: "Foot Controller",
                             5: "Portamento Time",
                             6: "Data Entry MSB",
                             7: "Main Volume",
                             8: "Balance",
                             10: "Pan",
                             11: "Expression Controller",
                             12: "Effect Control 1",
                             13: "Effect Control 2",
                             # 0-63 for off, 64-127 for on
                             64: "Damper pedal (sustain)",
                             65: "Portamento",
                             66: "Sostenuto",
                             67: "Soft Pedal",
                             68: "Legato Footswitch",
                             69: "Hold 2",
                             70: "Sound Controller 1 (default: Timber Variation)",
                             71: "Sound Controller 2 (default: Timber/Harmonic Content)",
                             72: "Sound Controller 3 (default: Release Time)",
                             73: "Sound Controller 4, (default: Attack Time)",
                             74: "Sound Controller 5, (default: Brightness)",
                             84: "Portamento Control",
                             91: "Effects 1 Depth (formerly External Effects Depth)",
                             92: "Effects 2 Depth (formerly Tremolo Depth)",
                             93: "Effects 3 Depth (formerly Chorus Depth)",
                             94: "Effects 4 Depth (formerly Detune Depth)",
                             95: "Effects 5 Depth (formerly Phaser Depth)",
                             96: "Data Increment",
                             97: "Data Decrement",
                             98: "Non-Registered Parameter Number (LSB)",
                             99: "Non-Registered Parameter Number (MSB)",
                             100: "Registered Parameter Number (LSB)",
                             101: "Registered Parameter Number (MSB)",
                             121: "Reset All Controllers",
                             122: "Local Control",
                             123: "All Notes Off",
                             124: "Omni Off",
                             125: "Omni On",
                             126: "Mono On (Poly Off)",
                             127: "Poly On (Mono Off)"}
