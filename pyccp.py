from pyccp.master import Master
import can
from can.interfaces.vector import VectorBus
import time


class canTransport(object):

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


class PyCct(Master):
    """

    """
    RESOURCE_CAL_MASK = 1
    RESOURCE_DAQ_MASK = 2
    RESOURCE_PGM_MASK = 0x40

    DATA_ENDIAN_LITTLE = 0
    DATA_ENDIAN_BIG = 1

    def __init__(self, tp, croCanId=0x301, crmCanID=0x302, stationAddr=0x020a, seedKeyFunc=None, buildCrcFunc=None, endiad=DATA_ENDIAN_LITTLE):
        Master.__init__(self, tp)
        self.croCanId = croCanId
        self.crmCanID = crmCanID
        self.endiad = endiad
        self.stationAddr = stationAddr
        if seedKeyFunc == None:
            self.seedKeyFunc = self.calc_key
        else:
            self.seedKeyFunc = seedKeyFunc
        if buildCrcFunc == None:
            self.buildCrcFunc = self.calc_crc
        else:
            self.buildCrcFunc = buildCrcFunc
        self.connect(self.croCanId,self.stationAddr)
        self.get_response()
        self.exchangeId(self.croCanId)
        self.lastResData = self.get_response()
        _,_,self.resMask, self.resProtMask, _ = self.lastResData
        retCnt = 0
        print(self.resProtMask)
        while(self.resProtMask & PyCct.RESOURCE_CAL_MASK):
            self.getSeed(self.croCanId, PyCct.RESOURCE_CAL_MASK)
            self.lastResData = self.get_response()
            protSts, *seed = self.lastResData
            self.unlock(self.croCanId, self.calc_key(seed))
            self.lastResData = self.get_response()
            Mask, *_ = self.lastResData
            self.resProtMask = self.resProtMask&(~PyCct.RESOURCE_CAL_MASK)
            retCnt += 1
            if retCnt > 10:
                raise Exception("Unlock resource failed for more than 10 times.")
        retCnt = 0
        print(self.resProtMask)
        while (self.resProtMask & PyCct.RESOURCE_DAQ_MASK):
            self.getSeed(self.croCanId, PyCct.RESOURCE_DAQ_MASK)
            self.lastResData = self.get_response()
            protSts, *seed = self.lastResData
            self.unlock(self.croCanId, self.calc_key(seed))
            self.lastResData = self.get_response()
            Mask, *_ = self.lastResData
            self.resProtMask = self.resProtMask & (~PyCct.RESOURCE_DAQ_MASK)
            retCnt += 1
            if retCnt > 10:
                raise Exception("Unlock resource failed for more than 10 times.")

    def set_var_val_phy(self, name, value):
        """
        this function will set the calibration variable to a specific value.
        :param name: calibration variable name.
        :param value: calibration variable value to be seted.
        :return:
        """
        pass

    def get_var_val_phy(self, name):
        """
        this function will use the upload command to get the variable value.
        :param name:  calibration variable name
        :return:
        """
        pass

    def set_var_val_hex(self, name, value):
        """
        this function will set the calibration variable to a specific value.
        :param name: calibration variable name.
        :param value: calibration variable value to be seted.
        :return:
        """
        pass

    def get_var_val_hex(self, name):
        """
        this function will use the upload command to get the variable value.
        :param name:  calibration variable name
        :return:
        """
    def get_response(self):
        self.lastRecMsg = self.transport.receive(self.crmCanID, 50)
        print(self.lastRecMsg)
        if self.lastRecMsg == None:
            raise Exception("No response received from ECU.")
        pacId, retCode, ctr, *data_ = self.lastRecMsg.data
        if pacId != 0xff:
            raise Exception("Except packet ID:0xff, but got :{0}".format(pacId))
        if retCode >= 0x20:
            raise Exception("Command return code is:{0}".format(retCode))
        #Todo, need to check ctr.
        return data_

    def calc_key(self, seed):
        return 0

    def calc_crc(self, data, size):
        return 0





bus = VectorBus(channel=1, bitrate=500000)
tp = canTransport(bus)

cct = PyCct(tp)
