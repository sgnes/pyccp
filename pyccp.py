from pyccp import ccp
from pyccp import master
from pyccp.master import Master
import can
from can.interfaces.vector import VectorBus
import time

class VectorTransport(object):

    def __init__(self, bus):
        self.parent = None
        self.bus = bus

    def send(self, canID, b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0, b7 = 0):
        self.message = can.Message(arbitration_id = canID, is_extended_id = 0, dlc = 8, data = bytearray((b0, b1, b2, b3, b4, b5, b6, b7)))
        self.bus.send(self.message)

    def __str__(self):
        return "[Current Message]: {}".format(self.message)

    __repr__ = __str__

    def receive(self, canID, timeout):
        rx_time = time.time()
        msg = None
        while timeout > 0:
            msg = self.bus.recv()
            if msg.arbitration_id == canID:
                return msg
            time_passed = time.time() - rx_time
            timeout -= time_passed*1000
        return msg

class CcpMaster(Master):

    def sendCRO(self, canID, cmd, ctr, b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0):
        """Transfer up to 6 data bytes from master to slave (ECU).
        """
        self.transport.send(canID, cmd, ctr, b0, b1, b2, b3, b4, b5)
        self.ctr += 1
        if self.ctr > 255:
            self.ctr = 0

bus = VectorBus(channel=1, bitrate=500000)
tp = VectorTransport(bus)


ccp_master = CcpMaster(tp)
ccp_master.connect(0x301, 0x020a)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.exchangeId(0x301)
msg = tp.receive(0x302, 50)
print(msg)
pass
