'''这个文件是各类的定义'''
from datetime import datetime
from utils import slave_status

'''主控机的工作状态'''
W_CLOSED = 1
W_RUNNING = 2
W_WAITING = 3

'''主控机的温度模式'''
T_HOT = 4
T_COOL = 5
T_NOTSET = 6


class SlaveDefaultParam:
    '''从控机默认的一些工作参数'''
    DEFAULT_LOW_TEMP = 18
    DEFAULT_HIGH_TEMP = 30
    DEFAULT_SPEED = 2
    DEFAULT_FEE_RATE = {1: 1, 2: 0.2, 3: 0.3, 4: 0.4, 5: 0.5, 6: 0.6, 7: 0.7}
    DEFAULT_MAX_SPEED = 7  # 最大最小风速
    DEFAULT_MIN_SPEED = 1


class MasterMachine:
    '''主控机类'''
    '''下面很多方法都应该向日志文件中存储一些信息，但暂时先没写'''

    def __init__(self):
        '''初始化函数'''
        self.__defaultPara = SlaveDefaultParam()
        self.__tempMode = T_NOTSET
        self.__workMode = W_CLOSED
        self.__startTime = None  # 主控机的开机时间
        self.__roomList = list()  # 所管理的从控机房间号
        self.__activeRoomList = list()  # 当前处于工作状态的从控机列表
        self.__slaveMachine = dict()  # 键是房间号，值是对应的从控机类
        self.__feeRate = self.__defaultPara.DEFAULT_FEE_RATE  # 不同风速对应的费率

    def Start(self):
        '''主控机开机'''
        self.__workMode = W_WAITING # 主控机刚开机时所有从控机一定都不处于工作状态
        self.__startTime= datetime.now()    #datetime.now()返回当前日期和时间，其类型是datetime

    def Close(self):
        '''主控机关机'''
        self.__workMode = W_CLOSED

    def SlaveStart(self, roomId: str):
        '''房间号为roomID的从控机开机'''
        if roomId not in self.__roomList:
            raise RuntimeError('房间不存在')
        else:
            if roomId not in self.__activeRoomList:
                self.__activeRoomList.insert(roomId)  # 将这个房间的从控机加入活跃列表
                if self.__workMode == W_WAITING:
                    self.__workMode = W_RUNNING

    def SlaveClose(self, roomId: str):
        if roomId not in self.__roomList:
            raise RuntimeError('房间不存在')
        else:
            if roomId in self.__activeRoomList:
                self.__activeRoomList.remove(roomId)  # 将这个房间的从控机从活跃列表删除
                if len(self.__activeRoomList) == 0 and self.__workMode == W_RUNNING:
                    self.__workMode = W_WAITING  # 如果没有工作的从控机则转入待机模式

    def ChangeTempMode(self, tempMode):
        '''更改主控机的温度模式'''
        self.__tempMode = tempMode

    def SetDefaultParam(self, lowTemp: int, highTemp: int, minSpeed: int, maxSpeed: int, defaultSpeed: int,
                        feeRate: dict):
        '''更改从控机默认参数'''
        self.__defaultPara.DEFAULT_LOW_TEMP = lowTemp
        self.__defaultPara.DEFAULT_HIGH_TEMP = highTemp
        self.__defaultPara.DEFAULT_SPEED = defaultSpeed
        self.__defaultPara.DEFAULT_MIN_SPEED = minSpeed
        self.__defaultPara.DEFAULT_MIN_SPEED = maxSpeed
        self.__defaultPara.DEFAULT_FEE_RATE = feeRate

    def SetSlaveParam(self, roomId: str, tMode: int, wMode: int, sp: int):
        '''设置roomId房间从控机的工作参数'''

    @property
    def GetDefaultParam(self):
        return self.__defaultPara

    @property
    def GetTempMode(self):
        return self.__tempMode

    @property
    def GetWorkMode(self):
        return self.__workMode

    @property
    def GetStartTime(self):
        return self.__startTime

    @property
    def GetFeeRate(self):
        return self.__feeRate

    def GetSlaveInfo(self,roomId:str):
        '''得到roomId房间的从控机信息'''
        if roomId not in self.__roomList:
            RuntimeError("房间不存在")
        else:
            return self.__slaveMachine[roomId]

    def GetDetail(self,roomId:str):
        '''获取roomId房间的详单'''
        slaveMachine=self.GetSlaveInfo(roomId)

    def GetBill(self,roomId:str):
        '''获取roomId房间的账单'''

    def GetReport(self,roomId:str):
        '''获取roomId房间的报表'''
    def checkIn(self,customerName:str,customerID:str):
        '''为客户办理入住'''
    def checkOut(self,roomId:str):
        '''为roomId房间办理退房手续'''


class Slave:
    def __init__(self, roomID: str, pwd: str, targetTemp: float, targetSpeed: int, defaultMode: int):
        self.__roomID = roomID
        self.__password = pwd
        self.__username = ...
        self.__status = slave_status.AVAILABLE
        self.__currentTemp = ...
        self.__targetTemp = targetTemp
        self.__currentSpeed = targetSpeed
        self.__currentMode = defaultMode
        self.__cost = 0.0
        self.__checkinTime = ...
        self.__checkoutTime = ...
        self.__timer = 0
        self.__serviceTime = 0

    @property
    def roomID(self):
        return self.__roomID

    @property
    def password(self):
        return self.__password

    @property
    def username(self):
        return self.__username

    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, status):
        self.__status = status
    
    @property
    def currentTemp(self):
        return self.__currentTemp if self.__currentTemp is not ... else None
    
    @currentTemp.setter
    def currentTemp(self, temp):
        self.__currentTemp = temp
    
    @property
    def targetTemp(self):
        return self.__targetTemp

    @targetTemp.setter
    def targetTemp(self, temp):
        self.__targetTemp = temp
    
    @property
    def currentSpeed(self):
        return self.__currentSpeed
    
    @currentSpeed.setter
    def currentSpeed(self, speed):
        self.__currentSpeed = speed
    
    @property
    def currentMode(self):
        return self.__currentMode
    
    @currentMode.setter
    def currentMode(self, mode):
        self.__currentMode = mode
    
    @property
    def cost(self):
        return self.__cost
    
    @cost.setter
    def cost(self, cost):
        self.__cost = cost
    
    @property
    def checkinTime(self):
        return self.__checkinTime
    
    @property
    def checkoutTime(self):
        return self.__checkoutTime
    
    @property
    def timer(self):
        return self.__timer
    
    @timer.setter
    def timer(self, timer):
        self.__timer = timer
    
    @property
    def serviceTime(self):
        return self.__serviceTime
    
    @serviceTime.setter
    def serviceTime(self, time):
        self.__serviceTime = time
    
    def check_in(self, username):
        self.__status = slave_status.CLOSED
        self.__username = username
        self.__checkinTime = datetime.datetime.now()

    def check_out(self):
        self.__username = ...
        self.__status = slave_status.AVAILABLE
        self.__checkoutTime = datetime.datetime.now()
    
    def switch_on(self, pwd, defaultTemp):
        if pwd == self.__password:
            self.__status = slave_status.RUNNING
            self.__currentTemp = defaultTemp
        else:
            raise RuntimeError('密码错误')
    
    def switch_off(self):
        self.__status = slave_status.CLOSED
    