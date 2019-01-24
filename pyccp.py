from pyccp import ccp
from pyccp import master
from pyccp.master import Master
import can
from can.interfaces.vector import VectorBus
import time


"""
     Time       Chn     ID    Name          Event Type   Dir    DLC   Data length   Data                      
 [+] 0.000000   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             01 A9 0A 02 00 00 00 00   connect
     0.000254   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 A9 02 00 00 00 00   
 [+] 0.004389   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             17 AA 00 00 00 00 00 00   exchange id
     0.000248   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 AA 09 02 03 43 00   
 [+] 0.000522   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             12 AB 01 00 00 00 00 00   GET_SEED
     0.000256   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 AB 01 00 01 00 01   
 [+] 0.002338   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             13 AC 59 19 3B A6 00 00   unlock
     0.000244   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 AC 01 3B A6 00 00   
 [+] 0.000468   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             12 AD 02 00 00 00 00 00   GET_SEED
     0.000248   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 AD 01 00 01 00 01   
 [+] 0.002245   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             13 AE 59 19 3B A6 00 00   unlock
     0.000250   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 AE 03 3B A6 00 00   
 [+] 0.000484   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             1B AF 02 01 00 00 00 00   GET_CCP_VERSION
     0.000252   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 AF 02 01 00 00 00   
 [+] 0.000372   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             09 B0 00 00 00 00 00 00   GET_ACTIVE_CAL_PAGE
     0.000250   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 B0 03 00 00 00 50   
 [+] 0.000504   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             02 B1 00 00 00 00 00 50   SET_MTA
     0.000246   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 B1 00 00 00 00 50   
 [+] 0.000378   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             11 B2 00 00 00 00 00 00   SELECT_CAL_PAGE
     0.000256   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 B2 00 00 00 00 00   
 [+] 0.000786   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             02 B3 00 00 00 00 06 80   SET_MTA
     0.000250   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 B3 00 00 00 06 80   
 [+] 0.000556   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             0E B4 00 00 01 00 00 00   BUILD_CHKSUM
     0.076517   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 B4 02 37 00 00 00   
 [+] 0.003470   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             02 B5 00 00 00 00 30 80   SET_MTA
     0.000250   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 B5 00 00 00 30 80   
 [+] 0.000456   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             0E B6 00 00 10 00 00 00   BUILD_CHKSUM
     0.108029   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 B6 02 0D 00 00 00   
 [+] 0.011471   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             0F B7 04 00 D8 3F 01 60   SHORT_UP
     0.000246   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 B7 00 40 9C 45 60   
 [+] 0.000446   CAN 2   301   SET_REQUEST   CAN Frame    Rx     8     8             0F B8 01 00 89 15 01 60   SHORT_UP
     0.000242   CAN 2   302                 CAN Frame    Rx     8     8             FF 00 B8 00 89 15 01 60   
"""


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

    def sendCRO(self, canID, cmd, ctr, b0=0, b1=0, b2=0, b3=0, b4=0, b5=0):
        """Transfer up to 6 data bytes from master to slave (ECU).
        """
        self.transport.send(canID, cmd, ctr, b0, b1, b2, b3, b4, b5)
        self.ctr += 1
        if self.ctr > 255:
            self.ctr = 0

    def getSeed(self, canID, resMask):
        self.sendCRO(canID, ccp.CommandCodes.GET_SEED, self.ctr, resMask)

    def unlock(self, canID, key):
        self.sendCRO(canID, ccp.CommandCodes.UNLOCK, self.ctr, key)

    def getActiveCalPage(self, canID):
        self.sendCRO(canID, ccp.CommandCodes.GET_ACTIVE_CAL_PAGE, self.ctr)

    def selectCalPage(self, canID):
        self.sendCRO(canID, ccp.CommandCodes.SELECT_CAL_PAGE, self.ctr)




class pyCCT(Master):
    """

    """
    RESOURCE_CAL_MASK = 1
    RESOURCE_DAQ_MASK = 2
    RESOURCE_PGM_MASK = 0x40

    def __init__(self, tp, croCanId=0x301, crmCanID=0x302, stationAddr=0x020a, seedKeyFunc=None, buildCrcFunc=None):
        Master.__init__(self, tp)
        self.croCanId = croCanId
        self.crmCanID = crmCanID
        self.stationAddr = stationAddr
        if seedKeyFunc == None:
            self.seedKeyFunc = self.calcKey
        else:
            self.seedKeyFunc = seedKeyFunc
        if buildCrcFunc == None:
            self.buildCrcFunc = self.calcCrc
        else:
            self.buildCrcFunc = buildCrcFunc
        self.connect(self.croCanId,self.stationAddr)
        self.getResponse()
        self.exchangeId(self.croCanId)
        self.lastResData = self.getResponse()
        _,_,self.resMask, self.resProtmask, _ = self.lastResData
        retCnt = 0
        while(self.resMask & pyCCT.RESOURCE_CAL_MASK):
            self.getSeed(self.croCanId, pyCCT.RESOURCE_CAL_MASK)
            self.lastResData = self.getResponse()
            protSts, *seed = self.lastResData
            self.unlock(self.croCanId, self.calcKey(seed))
            self.resMask, *_ = self.lastResData
            retCnt += 1
            if retCnt > 10:
                raise Exception("Unlock resource failed for more than 10 times.")
        retCnt = 0
        while (self.resMask & pyCCT.RESOURCE_DAQ_MASK):
            self.getSeed(self.croCanId, pyCCT.RESOURCE_DAQ_MASK)
            self.lastResData = self.getResponse()
            protSts, *seed = self.lastResData
            self.unlock(self.croCanId, self.calcKey(seed))
            self.resMask, *_ = self.lastResData
            retCnt += 1
            if retCnt > 10:
                raise Exception("Unlock resource failed for more than 10 times.")


    def getResponse(self):
        self.lastRecMsg = self.transport.receive(self.crmCanID, 50)
        if self.lastRecMsg == None:
            raise Exception("No response received from ECU.")
        pacId, retCode, ctr, *data_ = self.lastRecMsg.data
        if pacId != 0xff:
            raise Exception("Except packet ID:0xff, but got :{0}".format(pacId))
        if retCode >= 0x20:
            raise Exception("Command return code is:{0}".format(retCode))
        #Todo, need to check ctr.
        return data_

    def calcKey(self, seed):
        return 0

    def calcCrc(self, data, size):
        return 0





bus = VectorBus(channel=1, bitrate=500000)
tp = VectorTransport(bus)

cct = pyCCT(tp)
"""
ccp_master = CcpMaster(tp)
ccp_master.connect(0x301, 0x020a)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.exchangeId(0x301)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.getSeed(0x301, 1)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.unlock(0x301, 1)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.getSeed(0x301, 2)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.unlock(0x301, 2)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.setMta(0x301, 0x00000050)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.selectCalPage(0x301)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.setMta(0x301, 0x00800050)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.dnload(0x301, 1, [5])
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.setMta(0x301, 0x00800050)
msg = tp.receive(0x302, 50)
print(msg)
ccp_master.upload(0x301, 1)
msg = tp.receive(0x302, 50)
print(msg)
pass
"""