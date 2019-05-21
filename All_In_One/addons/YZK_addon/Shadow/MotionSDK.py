#
# @file    tools/sdk/python/MotionSDK.py
# @author  Luke Tokheim, luke@motionnode.com
# @version 2.5
#
# Copyright (c) 2017, Motion Workshop
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import functools
import select
import socket
import struct
import sys

#
# Only load functools in Python version 2.5 or newer.
#
if sys.version_info >= (2, 5):
    import functools


class Client:
    """
    Implements socket connection and basic binary message protocol for
    client application access to all Motion Service streams. Use the static
    Format methods to convert a binary message into the associated object.
    """

    def __init__(self, host, port):
        """
        Create client socket connection to the Motion Service data stream
        on host:port.
        """
        self.__socket = None
        self.__recv_flags = 0
        self.__send_flags = 0
        self.__description = None
        self.__time_out_second = None
        self.__time_out_second_send = None

        # Set the default host name to the local host.
        if (None == host) or (0 == len(host)):
            host = "127.0.0.1"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        self.__socket = s

        # Read the first message from the service. It is a
        # string description of the remote service.
        self.__description = self.__receive()

    def __del__(self):
        """
        Destructor. Close the socket connection.
        """
        self.close()

    def close(self):
        """
        Close the socket connection if it exists.
        """
        if None != self.__socket:
            self.__socket.shutdown(2)
            self.__socket.close()

            self.__socket = None

    def isConnected(self):
        """
        Return true if the current connection is active.
        """
        if None != self.__socket:
            return True
        else:
            return False

    def waitForData(self, time_out_second=None):
        """
        Wait until there is incoming data on this client
        connection and then returns True.
        """
        # Default time out is 5 seconds.
        if None == time_out_second:
            time_out_second = 5

        if time_out_second != self.__time_out_second:
            self.__socket.settimeout(time_out_second)
            self.__time_out_second = self.__socket.gettimeout()

        data = self.__receive()
        if None != data:
            return True
        else:
            return False

    def readData(self, time_out_second=None):
        """
        Read a single sample of data from the open connection.

        Returns a single sample of data, or None if the incoming
        data is invalid.
        """
        if None == self.__socket:
            return None

        # Default time out is 1 second.
        if None == time_out_second:
            time_out_second = 1

        if time_out_second != self.__time_out_second:
            self.__socket.settimeout(time_out_second)
            self.__time_out_second = self.__socket.gettimeout()

        return self.__receive()

    def writeData(self, data, time_out_second=None):
        """
        Write a single sample of data to the open connection.

        Returns True iff the message was successfully written
        to the socket. Otherwise returns False.
        """
        if None == self.__socket:
            return False

        if len(data) <= 0:
            return False

        # Default time out is 1 second.
        if None == time_out_second:
            time_out_second = 1

        if time_out_second != self.__time_out_second_send:
            self.__socket.settimeout(time_out_second)
            self.__time_out_second_send = self.__socket.gettimeout()

        return self.__send(data)

    def __receive(self):
        """
        Read a single binary message defined by a length header.
        """
        if None == self.__socket:
            return None

        if False == self.__select_receive():
            return None

        try:
            header_size = struct.calcsize("!I")

            # Single integer network order (=big-endian) message length header.
            header = self.__socket.recv(header_size, self.__recv_flags)
            if header_size != len(header):
                return None

            # Parse the length field, read the raw data field.
            length = struct.unpack("!I", header)[0]

            # Use one or more socket.recv calls to read the data payload.
            data = b""
            while True:
                message = self.__socket.recv(
                    length - len(data),
                    self.__recv_flags)
                if not message or 0 == len(message):
                    return None

                data += message
                if len(data) == length:
                    break
                elif len(data) > length:
                    return None

            return data
        except socket.timeout:
            pass

        return None

    def __send(self, data):
        """
        Write a single binary message defined by a length header.

        Returns true iff the message was successfully written
        to the socket.
        """
        if None == self.__socket:
            return False

        if False == self.__select_send():
            return None

        try:
            # Convert Python 3 strings to byte string.
            if not isinstance(data, bytes):
                data = data.encode("utf-8")

            length = len(data)
            message = struct.pack("!I" + str(length) + "s", length, data)

            send_result = self.__socket.sendall(message, self.__send_flags)
            if None == send_result:
                return True

        except socket.timeout:
            pass

        return False

    def __select_receive(self):
        """
        Use the select function to wait until there is data available to read
        on the internal socket. Returns True iff there is at least one byte
        ready to be read.
        """
        fd = self.__socket.fileno()

        try:
            list, _, _ = select.select(
                [fd], [], [], self.__time_out_second_send)
            for s in list:
                if fd == s:
                    return True
        except socket.timeout:
            pass

        return False

    def __select_send(self):
        """
        Use the select function to wait until there data can be written to the
        internal socket object.
        """
        fd = self.__socket.fileno()

        try:
            _, list, _ = select.select(
                [], [fd], [], self.__time_out_second_send)
            for s in list:
                if fd == s:
                    return True
        except socket.timeout:
            pass

        return False

#
# END class Client
#


class File:
    """
    Implements a file input stream interface for reading Motion Service
    binary take data files. Provide a simple interface to develop
    external applications that can read Motion take data from disk.

    This class only handles the reading of binary data and conversion
    to arrays of native data types. The Format class implements
    interfaces to the service specific data formats.
    """

    def __init__(self, pathname):
        """
        Open a Motion take data file for reading.

        Set parameter pathname to the file to open as the input stream.
        """
        self.__input = None
        self.__input = open(pathname, "rb")

    def __del__(self):
        """
        Destrucutor. Close the input file stream.
        """
        try:
            self.close()
        except RuntimeError:
            pass

    def close(self):
        """
        Close the input file stream.

        Throws a RuntimeError if the file stream is not open.
        """
        if None != self.__input:
            self.__input.close()
            self.__input = None
        else:
            raise RuntimeError("failed to close input file stream, not open")

    def readData(self, length, real_valued):
        """
        Read a single block of binary data from the current position
        in the input file stream. Convert the block of data into an
        array of length typed elements.

        Integer parameter length defines the required number of typed elements.
        Set boolean parameter real_valued to True if the typed elements are
        real valued, i.e. floats. Set real_valued to false for short integers.
        """
        if None == self.__input:
            return None

        data = None
        if length > 0:
            # Choose the binary format of the array values,
            # "f" == float and "h" == short.
            value_format = "f"
            if False == real_valued:
                value_format = "h"

            element_size = length * struct.calcsize("<" + str(value_format))

            input_buffer = self.__input.read(element_size)
            if element_size == len(input_buffer):
                data = struct.unpack(
                    "<" + str(length) + str(value_format), input_buffer)
            else:
                self.close()

        return data

#
# END class File
#


class Format:
    """
    Motion Service streams send a list of data elements. The static Format
    methods create a map from integer id to array packed data for each
    service specific format.
    """

    class Element:
        """
        Motion Service streams send a list of data elements. The {@link Format}
        functions create a map from integer id to array packed data for each
        service specific format.

        This is an abstract base class to implement a single format specific
        data element. The idea is that a child class implements a format
        specific interface (API) to access individual components of an array of
        packed data.

        For example, the PreviewElement class extends this class
        and provides a PreviewElement.getEuler() method to access
        an array of {x, y, z} Euler angles.
        """

        def __init__(self, data, length, real_valued):
            """
            Initialize element data.
            """
            self.__data = None
            self.__real_valued = None

            if (len(data) == length) or (0 == length):
                self.__data = data
                self.__real_valued = real_valued
            else:
                raise RuntimeError("invalid input data for format element")

        def getData(self, base, length):
            """
            Utility function to copy portions of the packed data array into its
            component elements.

            Parameter base defines starting index to copy data from the
            internal data array.

            Parameter element_length defines the number of data values in this
            component element.

            Returns an array of element_length values, assigned to
            [m_data[i] ... m_data[i+element_length]] if there are valid values
            available or zeros otherwise
            """
            if (None != self.__data) and (base + length <= len(self.__data)):
                return self.__data[base:(base + length)]
            else:
                value = float(0)
                if False == real_valued:
                    value = int(0)
                result = list()
                for i in range(0, length):
                    result.append(value)

        def access(self):
            """
            Direct access to the internal buffer.
            """
            return self.__data

    #
    # END class Element
    #

    class ConfigurableElement(Element):
        """
        The Configurable data services provides access to all data streams in
        a single message. The client selects channels and ordering at the
        start of the connection. The Configurable service sends a map of
        N data elements. Each data element is an array of M single precision
        floating point numbers.
        """

        def __init__(self, data):
            """
            Defines the parameters of this element.
            """
            Format.Element.__init__(self, data, 0, True)

        def value(self, index):
            """
            Get a single channel entry at specified index.
            """
            return self.access()[index]

        def size(self):
            """
            Convenience method. Size accessor.
            """
            return len(self.access())

    #
    # END class ConfigurableElement
    #

    class PreviewElement(Element):
        """
        The Preview service sends a map of N Preview data elements. Use this
        class to wrap a single Preview data element such that we can access
        individual components through a simple API.

        Preview element format:
        id => [global quaternion, local quaternion, local euler, acceleration]
        id => [
            Gqw, Gqx, Gqy, Gqz, Lqw, Lqx, Lqy, Lqz, rx, ry, rz, lax, lay, laz
        ]
        """

        def __init__(self, data):
            """
            Defines the parameters of this element.
            """
            Format.Element.__init__(self, data, 14, True)

        def getEuler(self):
            """
            Get a set of x, y, and z Euler angles that define the
            current orientation. Specified in radians assuming x-y-z
            rotation order. Not necessarily continuous over time, each
            angle lies on the domain [-pi, pi].

            Euler angles are computed on the server side based on the
            current local quaternion orientation.

            Returns a three element array [x, y, z] of Euler angles
            in radians or None if there is no available data
            """
            return self.getData(8, 3)

        def getMatrix(self, local):
            """
            Get a 4-by-4 rotation matrix from the current global or local
            quaternion orientation. Specified as a 16 element array in
            row-major order.

            Set parameter local to true get the local orientation, set local
            to false to get the global orientation.
            """
            return Format.quaternion_to_R3_rotation(self.getQuaternion(local))

        def getQuaternion(self, local):
            """
            Get the global or local unit quaternion that defines the current
            orientation.

            @param local set local to true get the local orientation, set local
            to false to get the global orientation

            Returns a four element array [w, x, y, z] that defines
            a unit length quaternion q = w + x*i + y*j + z*k or None
            if there is no available data
            """
            if (local):
                return self.getData(4, 4)
            else:
                return self.getData(0, 4)

        def getAccelerate(self):
            """
            Get x, y, and z of the current estimate of linear acceleration.
            Specified in g.

            Returns a three element array [x, y, z] of of linear acceleration
            channels specified in g or zeros if there is no available data
            """
            return self.getData(11, 3)

    #
    # END class PreviewElement
    #

    class SensorElement(Element):
        """
        The Sensor service provides access to the current un-filtered sensor
        signals in real units. The Sensor service sends a map of N data
        elements. Use this class to wrap a single Sensor data element such
        that we can access individual components through a simple API.

        Sensor element format:
        id => [accelerometer, magnetometer, gyroscope]
        id => [ax, ay, az, mx, my, mz, gx, gy, gz]
        """

        def __init__(self, data):
            """
            Initialize this container identifier with a packed data
            array in the Sensor format.

            Parameter data is a packed array of accelerometer, magnetometer,
            and gyroscope un-filtered signal data.
            """
            Format.Element.__init__(self, data, 9, True)

        def getAccelerometer(self):
            """
            Get a set of x, y, and z values of the current un-filtered
            accelerometer signal. Specified in g where 1 g =
            -9.8 meters/sec^2.

            Domain varies with configuration. Maximum is [-6, 6] g.

            Returns a three element array [x, y, z] of acceleration
            in gs or zeros if there is no available data
            """
            return self.getData(0, 3)

        def getGyroscope(self):
            """
            Get a set of x, y, and z values of the current un-filtered
            gyroscope signal. Specified in degrees/second.

            Valid domain is [-500, 500] degrees/second.

            Returns a three element array [x, y, z] of angular velocity
            in degrees/second or zeros if there is no available data.
            """
            return self.getData(6, 3)

        def getMagnetometer(self):
            """
            Get a set of x, y, and z values of the current un-filtered
            magnetometer signal. Specified in uT (microtesla).

            Domain varies with local magnetic field strength. Expect values
            on [-60, 60] uT (microtesla).

            Returns a three element array [x, y, z] of magnetic field
            strength in uT (microtesla) or zeros if there is no
            available data.
            """
            return self.getData(3, 3)

    #
    # class SensorElement
    #

    class RawElement(Element):
        """
        The Raw service provides access to the current uncalibrated,
        unprocessed sensor signals in signed integer format. The Raw service
        sends a map of N data elements. Use this class to wrap a single Raw
        data element such that we can access individual components through a
        simple API.

        Raw element format:
        id => [accelerometer, magnetometer, gyroscope]
        id => [ax, ay, az, mx, my, mz, gx, gy, gz]

        All sensors output 12-bit integers. Process as 16-bit short integers on
        the server side.
        """

        def __init__(self, data):
            """
            Initialize this container identifier with a packed data
            array in the Raw format.

            Parameter data is a packed array of accelerometer, magnetometer,
            and gyroscope un-filtered signal data.
            """
            Format.Element.__init__(self, data, 9, False)

        def getAccelerometer(self):
            """
            Get a set of x, y, and z values of the current unprocessed
            accelerometer signal.

            Valid domain is [0, 4095].

            Returns a three element array [x, y, z] of raw accelerometer
            output or zeros if there is no available data.
            """
            return self.getData(0, 3)

        def getGyroscope(self):
            """
            Get a set of x, y, and z values of the current unprocessed
            gyroscope signal.

            Valid domain is [0, 4095].

            Returns a three element array [x, y, z] of raw gyroscope
            output or zeros if there is no available data.
            """
            return self.getData(6, 3)

        def getMagnetometer(self):
            """
            Get a set of x, y, and z values of the current unprocessed
            magnetometer signal.

            Valid domain is [0, 4095].

            Returns a three element array [x, y, z] of raw magnetometer
            output or zeros if there is no available data.
            """
            return self.getData(3, 3)

    #
    # class RawElement
    #

    def __Configurable(data):
        """
        Convert a container of binary data into an associative
        container of ConfigurableElement entries.
        """
        return Format.__IdToValueArray(
            data, 0, Format.ConfigurableElement, True)
    Configurable = staticmethod(__Configurable)

    def __Preview(data):
        """
        Convert a container of binary data into an associative
        container of PreviewElement entries.
        """
        return Format.__IdToValueArray(data, 14, Format.PreviewElement, True)
    Preview = staticmethod(__Preview)

    def __Sensor(data):
        """
        Convert a container of binary data into an associative
        container of SensorElement entries.
        """
        return Format.__IdToValueArray(data, 9, Format.SensorElement, True)
    Sensor = staticmethod(__Sensor)

    def __Raw(data):
        """
        Convert a container of binary data into an associative
        container of RawElement entries.
        """
        return Format.__IdToValueArray(data, 9, Format.RawElement, False)
    Raw = staticmethod(__Raw)

    def __IdToValueArray(data, length, factory, real_valued):
        """
        Utility method to convert a packed binary representation of
        an associative container into that container.
        """
        result = {}

        if None == data:
            return result

        # Choose the binary format of the array values,
        # "f" == float and "h" == short.
        value_format = "f"
        if False == real_valued:
            value_format = "h"

        # Prefix "<" for little-endian byte ordering.
        sizeof_key = struct.calcsize("<I")
        sizeof_value = struct.calcsize("<" + str(value_format))

        itr = 0
        while (itr < len(data)) and ((len(data) - itr) > sizeof_key):
            # Read the integer id for this element.
            key = struct.unpack("<I", data[itr:itr + sizeof_key])[0]
            itr += sizeof_key

            # Optionally read the integer length field of the
            # data array.
            element_length = length
            if (0 == element_length) and ((len(data) - itr) > sizeof_key):
                element_length = struct.unpack(
                    "<I", data[itr:itr + sizeof_key])[0]
                itr += sizeof_key

            # Read the array of values for this element.
            sizeof_array = sizeof_value * element_length
            if (element_length > 0) and ((len(data) - itr) >= sizeof_array):
                value = struct.unpack(
                    str(element_length) + value_format,
                    data[itr:itr + sizeof_array])
                itr += sizeof_array

                result[key] = factory(value)

        # If we did not consume all of the input bytes this is an
        # invalid message.
        if len(data) != itr:
            result = {}

        return result

    __IdToValueArray = staticmethod(__IdToValueArray)

    def quaternion_to_R3_rotation(q):
        """
        Ported from the Boost.Quaternion library at:
        http://www.boost.org/libs/math/quaternion/HSO3.hpp

        Parameter q defines a quaternion in the format [w x y z] where
        q = w + x*i + y*j + z*k.

        Returns an array of 16 elements that defines a 4-by-4 rotation
        matrix computed from the input quaternion or the identity matrix
        if the input quaternion has zero length. Matrix is in row-major
        order.
        """
        if 4 != len(q):
            return None

        a = q[0]
        b = q[1]
        c = q[2]
        d = q[3]

        aa = a * a
        ab = a * b
        ac = a * c
        ad = a * d
        bb = b * b
        bc = b * c
        bd = b * d
        cc = c * c
        cd = c * d
        dd = d * d

        norme_carre = aa + bb + cc + dd

        result = list()
        for i in range(0, 4):
            for j in range(0, 4):
                if i == j:
                    result.append(1)
                else:
                    result.append(0)

        if (norme_carre > 1e-6):
            result[0] = (aa + bb - cc - dd) / norme_carre
            result[1] = 2 * (-ad + bc) / norme_carre
            result[2] = 2 * (ac + bd) / norme_carre
            result[4] = 2 * (ad + bc) / norme_carre
            result[5] = (aa - bb + cc - dd) / norme_carre
            result[6] = 2 * (-ab + cd) / norme_carre
            result[8] = 2 * (-ac + bd) / norme_carre
            result[9] = 2 * (ab + cd) / norme_carre
            result[10] = (aa - bb - cc + dd) / norme_carre

        return result

    quaternion_to_R3_rotation = staticmethod(quaternion_to_R3_rotation)
#
# END class Format
#


class LuaConsole:
    """
    Implements the communication protocol with the Motion Service console.
    Send general Lua scripting commands to the Motion Service and receive
    a result code and printed results.
    """

    # The Lua chunk was successfully parsed and executed. The
    # printed results are in the result string.
    Success = 0
    # The Lua chunk failed due to a compile time or execution
    # time error. An error description is in the result string.
    Failure = 1
    # The Lua chunk was incomplete. The Console service is waiting
    # for a complete chunk before it executes.
    # For example, "if x > 1 then" is incomplete since it requires
    # and "end" token to close the "if" control statement.
    Continue = 2

    def __init__(self, client):
        """
        Constructor. Supply the already open client socket connection
        to the Motion Service console..
        """
        self.__client = client

    def send_chunk(self, chunk, time_out_second=None):
        """
        Write a general Lua chunk to the open Console service
        socket and read back the results.
        """
        result_code = self.Failure
        result_string = None

        # Write the Lua chunk.
        if self.__client.writeData(chunk, time_out_second):
            # Read back the response. This is how the Lua Console
            # service works. It will always respond with at least
            # an error code.
            data = self.__client.readData(time_out_second)
            if None != data and len(data) > 0:
                if not isinstance(data, str):
                    data = str(data, "utf-8")

                code = ord(data[0])
                if code >= self.Success and code <= self.Continue:
                    result_code = code
                    if len(data) > 1:
                        result_string = data[1:]

        return result_code, result_string

    def __SendChunk(client, chunk, time_out_second=None):
        """
        A more Python friendly version of the SendChunk method.
        This will throw an exception if there is an error in the
        scripting command. Otherwise, this will only return the
        printed results.
        """
        lua_console = LuaConsole(client)
        result_code, result_string = lua_console.send_chunk(
            chunk, time_out_second)

        if lua_console.Success == result_code:
            return result_string
        elif lua_console.Continue == result_code:
            raise RuntimeError(
                "Lua chunk incomplete: " + str(result_string))
        else:
            raise RuntimeError(
                "Lua command chunk failed: " + str(result_string))

    SendChunk = staticmethod(__SendChunk)

    class Node:
        """
        Utility class to implement a generic scripting interface
        from the Motion Service console (Lua) to Python and vice versa.

        Dispatch named methods with variable length argument
        lists.

        Implements all Lua node.* methods that return a boolean
        and string value pair. Also supports simple string result
        but the client script must handle this correctly.

        Example usage:

        node = LuaConsole.Node(Client("", 32075))
        result, message = node.start()
        if result:
            # Success. We are reading from at least one device.
            pass
        else:
            # Failure. There are no configured devices or the
            # hardware is not available.
            print message
        """
        def __init__(self, client):
            self.__client = client

        def __getattr__(self, name):
            if sys.version_info >= (2, 5):
                return functools.partial(self.__dispatch, name)
            else:
                return None

        def __dispatch(self, name, *arg_list):
            result = self.__string_call(name, *arg_list)

            if result.startswith("true"):
                return True, result[4:]
            elif result.startswith("false"):
                return False, result[5:]
            else:
                return str(result)

        def __string_call(self, name, *arg_list):
            lua_call = "=node.%s(" % name

            # Create a string valued argument list from a variable
            # length list of arguments. Note that this only supports
            # String and Float valued arguments.
            sep = ""
            for item in arg_list:
                if isinstance(item, str):
                    lua_call += "%s%s" % (sep, "".join(
                        ["'", ("\\'").join(i for i in item.split("'")), "'"]))
                else:
                    lua_call += "%s%s" % (sep, float(item))
                sep = ", "

            lua_call += ")"

            return LuaConsole.SendChunk(self.__client, lua_call, 5)
        #
        # END class Node
        #

#
#
# END class LuaConsole
#


def main():
    """
    Example usage and test function for the Client, File,
    Format, and LuaConsole classes.
    """

    # Open take data file in the Sensor format.
    # Print out the calibrated gyroscope signals.
    DataFile = "../../test_data/sensor.bin"
    if None != DataFile:
        take_file = File(DataFile)
        while True:
            data = take_file.readData(9, True)
            if None == data:
                break

            print("%s\n" % str(Format.SensorElement(data).getGyroscope()))

    # Set the default host and port parameters. The SDK is
    # socket bases so any networked Motion Service is available.
    Host = ""
    PortPreview = 32079
    PortConsole = 32075

    #
    # General Lua scripting interface.
    #
    lua_client = Client(Host, PortConsole)
    lua_chunk = \
        "if not node.is_reading() then" \
        "   node.close()" \
        "   node.scan()" \
        "   node.start()" \
        " end" \
        " if node.is_reading() then" \
        "   print('Reading from ' .. node.num_reading() .. ' device(s)')" \
        " else" \
        "   print('Failed to start reading')" \
        " end"

    print(LuaConsole.SendChunk(lua_client, lua_chunk, 5))

    # Scripting language compatibility class. Translate
    # Python calls into Lua calls and send them to the
    # console service.
    if sys.version_info >= (2, 5):
        node = LuaConsole.Node(lua_client)
        print(node.is_reading())

    # Connect to the Preview data service.
    # Print out the Euler angle orientation output.
    client = Client(Host, PortPreview)
    print("Connected to %s:%d" % (Host, PortPreview))

    if client.waitForData():
        sample_count = 0
        while sample_count < 100:
            data = client.readData()

            preview = Format.Preview(data)
            if len(preview) > 0:
                for item in preview.values():
                    print("Euler = %s" % str(item.getEuler()))
                    break
            else:
                break

            sample_count += 1

    else:
        print("No current data available, giving up")

    client.close()


if __name__ == "__main__":
    sys.exit(main())
