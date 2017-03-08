import json
import struct


class Head():
    length = 10

    def __init__(self):
        self.head_id = 0
        self.data_type = 0
        self.data_id = 0
        self.data_len = 0

    def Read(self, buffer):
        (
            self.head_id,
            self.data_type,
            self.data_id,
            self.data_len
        ) = struct.unpack("2HiH", buffer)


class TransData():
    def __init__(self):
        self.head = Head()
        self.content = ""
        self._codec = "utf-8"

    def Read(self, buffer):
        head_end = content_start = Head.length
        self.head.Read(buffer[:head_end])
        content_len = struct.unpack(
            "H", buffer[content_start:content_start + 2])[0]
        self.content = struct.unpack(
            "{0}s".format(content_len), buffer[content_start + 2:])[0].decode(self._codec)

    def LoadJson(self, filename):
        with open('transdata.json') as f:
            jsdata = json.load(f)

        self.head.head_id = jsdata["head"]["head_id"]
        self.head.data_type = jsdata["head"]["data_type"]
        self.head.data_id = jsdata["head"]["data_id"]
        self.content = jsdata["content"]
        self._codec = jsdata["codec"]
        self.head.data_len = len(self.content.encode(self._codec)) + 2
        #print(self.head.head_id)

    def Pack(self):
        encContent = self.content.encode(self._codec)
        content_len = len(encContent)
        fmt = "HHiHH{0}s".format(content_len)
        return struct.pack(fmt,
                           self.head.head_id,
                           self.head.data_type,
                           self.head.data_id,
                           self.head.data_len,
                           content_len,
                           encContent)

    def SetCodec(self, codec):
        self._codec = codec

