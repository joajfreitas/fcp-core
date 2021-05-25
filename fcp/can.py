from typing import *
import json
import struct
import datetime
import can


class CANMessage:
    def __init__(
        self, sid: int, dlc: int, timestamp: int, data16: List[int] = [], data64=-1
    ):

        assert isinstance(sid, int) == True
        self.sid = sid
        self.dlc = dlc

        if data64 == -1:
            assert len(data16) == 4
            self.data64 = sum([data << (16 * i) for i, data in enumerate(data16)])
            # assert self.data64 != 0
        else:
            self.data64 = data64

        self.timestamp = timestamp

    def get_data8(self):
        data = []
        for i in range(8):
            data.append((self.data64 >> (8 * i)) & 0xFF)

        return data

    def get_data16(self):
        return [(self.data64 >> 16 * i) & 0xFFFF for i in range(4)]

    def get_msg_id(self):
        return self.sid >> 5

    def get_dev_id(self):
        return self.sid & 0x1F

    def get_data64(self):
        return self.data64

    def encode_json(self):
        """
        Encode message as a utf-8 byte string encoded JSON object.
        Example: {'sid': 100, 'dlc': 8, 'data': [1,2,3,4], 'timestamp': 1}

        """
        return bytes(
            json.dumps(
                {
                    "sid": self.sid,
                    "dlc": self.dlc,
                    "data": self.get_data16(),
                    "timestamp": self.timestamp,
                }
            ),
            "utf-8",
        )

    def encode_bstring(self):
        """
        Encode message as a utf-8 byte string encoded comma separated list of fields.
        Example: 100,8,1,2,3,4,1.
        Encodes sid: 100, dlc: 8, data[0]: 1, data[1]: 2, data[2]: 3, data[3]: 4, timestamp: 1

        """
        data = self.get_data16()
        return bytes(
            str(self.sid)
            + ","
            + str(self.dlc)
            + ","
            + str(data[0])
            + ","
            + str(data[1])
            + ","
            + str(data[2])
            + ","
            + str(data[3])
            + ","
            + str(self.timestamp)
            + "\n",
            "utf-8",
        )

    def encode_struct(self):
        """
        Encode message as a CAN struct:

        .. code:: C

            typedef struct {
                union {
                    struct {
                            uint16_t dev_id:5; // Least significant
                            // First bit of msg_id determines if msg is reserved or not.
                            // 0 == reserved (higher priority) (0-31 decimal)
                            uint16_t msg_id:6; // Most significant
                    };
                    uint16_t sid;
                };
                uint16_t dlc:4;
                uint16_t data[4];
            } CANdata;

        """

        s = struct.pack("HH4HI", self.sid, self.dlc, *self.get_data16(), self.timestamp)
        return s

    def encode_socketcan(self):
        msg = can.Message(
            arbitration_id=self.sid,
            data = self.get_data8(),
            is_extended_id = False
        )

        return msg

    @staticmethod
    def decode_json(j):
        """
        Decode JSON encoded message into CANMessage.

        See encode_json for details on the JSON format used.
        """

        d = json.loads(j.decode())
        msg = CANMessage(
            d.get("sid"), d.get("dlc"), d.get("timestamp"), data16=d.get("data")
        )

        if (msg.sid and msg.dlc and msg.data64 and msg.timestamp) == None:
            raise ValueError("Received invalid message: " + j.decode())
            return

        return msg

    @staticmethod
    def decode_bstring(bstring):
        """
        Decode bytestring encoded message into CANMessage.

        See encode_bstring for details on the string format used.
        """

        sid, dlc, *data, timestamp = bstring.decode().split(",")
        data = [int(d) for d in data]
        sid = int(sid)
        dlc = int(dlc)
        timestamp = int(timestamp)
        msg = CANMessage(sid, dlc, timestamp, data16=data)
        return msg

    @staticmethod
    def decode_CANmessage(message):
        msg = CANMessage()
        msg.sid = message.sid
        msg.dlc = message.dlc
        msg.data = [0, 0, 0, 0]
        for i in range(4):
            msg.data[i] = (message.data >> i * 16) & 0xFFFF
        return msg

    @staticmethod
    def decode_struct(s):
        """
        Decode C struct encoded message into CANMessage.

        See encode_struct for details on the struct format used.
        """
        sid, dlc, *data, timestamp = struct.unpack("HH4HI", s)

        msg = CANMessage(sid, dlc, timestamp, data16=data)

        return msg

    @staticmethod
    def decode_kvaser_csv(csv, start_time):
        try:
            line = csv.split(",")
            timestamp = start_time + datetime.timedelta(seconds=float(line[0]))
            sid = int(line[2])
            dlc = int(line[4])
            data8 = line[5:13]
            data64 = sum(
                [(0 if d == "" else int(d)) << (i * 8) for i, d in enumerate(data8)]
            )
            data = []
            for i in range(4):
                data.append((data64 >> 16 * i) & 0xFFFF)

            return CANMessage(sid, dlc, timestamp, data16=data)

        except Exception as e:
            return None

    @staticmethod
    def decode_socketcan(msg):
        data = sum([b<<(i*8) for i,b in enumerate(msg.data)])
        return CANMessage(
            sid=msg.arbitration_id,
            dlc=msg.dlc,
            timestamp=msg.timestamp,
            data64=data)

    def __repr__(self):
        return f"<CANMessage sid={self.sid}, dlc={self.dlc}, data={self.get_data16()}>"


def test_encode_json():
    msg = CANMessage(100, 8, 100, data16=[1, 2, 3, 4])
    j = json.loads(msg.encode_json())

    assert j["sid"] == 100
    assert j["dlc"] == 8
    assert j["data"] == [1, 2, 3, 4]
    assert j["timestamp"] == 100


def test_encode_bstring():
    msg = CANMessage(100, 8, 100, data16=[1, 2, 3, 4])
    js = msg.encode_bstring().split(b",")
    js = [int(j) for j in js]

    assert js[0] == 100
    assert js[1] == 8
    assert js[2] == 1
    assert js[3] == 2
    assert js[4] == 3
    assert js[5] == 4
    assert js[6] == 100


def test_encode_struct():
    msg = CANMessage(100, 8, 100, data16=[1, 2, 3, 4])
    msg = CANMessage.decode_struct(msg.encode_struct())

    assert msg.sid == 100
    assert msg.dlc == 8
    assert msg.get_data16() == [1, 2, 3, 4]
    assert msg.timestamp == 100


def test_decode_json():
    msg = CANMessage(100, 8, 100, data16=[1, 2, 3, 4])
    msg = CANMessage.decode_json(msg.encode_json())

    assert msg.sid == 100
    assert msg.dlc == 8
    assert msg.get_data16() == [1, 2, 3, 4]
    assert msg.timestamp == 100


def test_decode_bstring():
    msg = CANMessage(100, 8, 100, data16=[1, 2, 3, 4])
    msg = CANMessage.decode_bstring(msg.encode_bstring())

    assert msg.sid == 100
    assert msg.dlc == 8
    assert msg.get_data16() == [1, 2, 3, 4]
    assert msg.timestamp == 100


def test_decode_kvaser_csv():
    msg = CANMessage.decode_kvaser_csv(
        "0.31947,1,1099,2,8,20,178,20,178,61,74,0,0,1",
        datetime.datetime(year=2019, month=9, day=3),
    )

    assert msg.sid == 1099
