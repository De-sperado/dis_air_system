from TemperatureController.entity import *
'''用户类别宏定义'''
CUSTOMER =11
RECEPTIONIST=12
MANAGER=13

class LogonController:
    '''登录控制器'''
    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    @classmethod
    def instance(cls):  # 支持多线程的单例模式
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):  # 获得锁后还要再判断一次是否在等待锁的时候创建了实例
                    cls._instance = cls()
        return cls._instance

    def LogService(self,name:str,password:str,kind:int):
        '''处理用户登录服务'''
        if kind == CUSTOMER:
            pass
        elif kind==RECEPTIONIST:
            pass
        else:
            pass

class MasterController:
    '''主控机操作控制器'''
    _instance_lock = threading.Lock()
    def __init__(self):
        self.__masterMachine=MasterMachine.instance()
        pass
    @classmethod
    def instance(cls):
        '''支持多线程的单例模式'''
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):  # 获得锁后还要再判断一次是否在等待锁的时候创建了实例
                    cls._instance = cls()
        return cls._instance
    def TurnOn(self):
        '''打开主控机，打开主控机的时候是否应该在主控机中初始化所有房间从控机的dict？'''
        self.__masterMachine.Start()
    def TurnOff(self):
        '''主控机关机'''
        if self.__masterMachine.GetWorkMode()==W_RUNNING:   #若当前有正在运行中的从控机则不能直接关机
            raise RuntimeError('有正在运行的从控机，不能关机')
        else:   #其他两种状态可以关机
            self.__masterMachine.Close()
    def OpenMenu(self):
        '''打开界面，但是否要把这个在views.py中实现？？？'''
        pass
    def SetMode(self,tMode:int):
        '''设置主控机的温度模式'''
        if self.__masterMachine.GetWorkMode() == W_CLOSED:
            raise RuntimeError('主控机未启动')
        else:
            self.__masterMachine.ChangeTempMode(tMode)
    def SetRefreshFeq(self,targetFeq:int):
        '''更改监测界面的刷新频率'''
        if self.__masterMachine.GetWorkMode() == W_CLOSED:
            raise RuntimeError('主控机未启动')
        else:
            pass
    def SetPrice(self,**kwargs):
        '''更改不同风速的费率，kwargs传入的是字典，key是风速，value是该风速的费率'''
        if self.__masterMachine.GetWorkMode() == W_CLOSED:
            raise RuntimeError('主控机未启动')
        else:
            pass
    def SetSlaveInfo(self,roomId:str,wind:int,temperature:int,startTime:datetime):
        '''更改从控机当前状态信息,是否考虑参数直接传一个slave对象？'''
        pass
    def SlaveSwitch(self,roomId:str,mode:str):
        '''更改从控机的开关状态'''
        if mode == 'on':

            self.__masterMachine.SlaveStart(roomId)
            '''根据从控机对象到底保存在什么地方应该还要添加与调度队列的绑定'''
            pass
        else:
            self.__masterMachine.SlaveStart(roomId)
            '''消除与调度队列的关联'''
            pass

class SlaveController:
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls):
        '''支持多线程的单例模式'''
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):  # 获得锁后还要再判断一次是否在等待锁的时候创建了实例
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.infoController=InfoController.instance()
        self.masterController=MasterController.instance()
    def CheckBill(self,roomId:str):
        '''从控机获取费用等信息'''
        return self.infoController.QueryInfo(roomId)
    def SetSlave(self,roomId:str,temperature:int,wind:int,startTime:datetime):
        '''从控机更改状态，是否考虑参数直接传一个slave对象？'''
        self.masterController.SetSlaveInfo(roomId,temperature,wind,startTime)
    def SwitchOn(self,roomId:str):
        '''打开roomId从控机'''
        self.masterController.SlaveSwitch(roomId,'on')
    def SwitchOff(self,roomId:str):
        '''关闭roomId从控机'''
        self.masterController.SlaveSwitch(roomId, 'off')
    def ChangeTemp(self,roomId:str):
        '''改变从控机温度'''
        pass
    def ChangeWindSpeed(self,roomId:str,tWindSpeed:int):
        '''改变从控机风速'''
    def SetMode(self,roomId:str,TargetMode:int):
        '''这个mode是什么mode？'''
        pass





class InfoController:
    '''控制信息查询和报表的控制器'''
    _instance_lock = threading.Lock()
    @classmethod
    def instance(cls):
        '''支持多线程的单例模式'''
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):  # 获得锁后还要再判断一次是否在等待锁的时候创建了实例
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.__masterMachine=MasterMachine.instance()
    def QueryInfo(self,roomId:str):
        '''查询roomId房间中从控机的状态信息'''
        pass
