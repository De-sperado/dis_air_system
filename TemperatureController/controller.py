from .entity import *
from .service import (
    AdministratorService, GetFeeService, DetailService,
    InvoiceService, ReportService, PowerService,
    ChangeTempAndSpeedService, UpdateService)

'''用户类别宏定义'''
CUSTOMER = 11
RECEPTIONIST = 12
MANAGER = 13


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

    def LogService(self, name: str, password: str, kind: int):
        '''处理用户登录服务'''
        if kind == CUSTOMER:
            pass
        elif kind == RECEPTIONIST:
            pass
        else:
            pass


class MasterController:
    '''主控机操作控制器'''
    '''所有与logger有关的都还没写，每一步的logger是应该放在service还是放在controller？'''
    _instance_lock = threading.Lock()

    def __init__(self):
        self.__adminService = AdministratorService.instance()
        self.__masterStart = False
        # logger.info('初始化AdministratorService')
        pass

    @classmethod
    def instance(cls):
        '''支持多线程的单例模式'''
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):  # 获得锁后还要再判断一次是否在等待锁的时候创建了实例
                    cls._instance = cls()
        return cls._instance

    def IsMasterStart(self):
        return self.__masterStart

    def TurnOn(self):
        '''打开主控机'''
        '''应该把初始化和主控机开机和在一个service吗？'''
        pass
        self.__adminService.init_master_machine()
        self.__adminService.start_master_machine()
        self.__masterStart = True

    def TurnOff(self):
        '''主控机关机'''
        # if self.__masterMachine.GetWorkMode()==W_RUNNING:   #若当前有正在运行中的从控机则不能直接关机
        #     raise RuntimeError('有正在运行的从控机，不能关机')
        # else:   #其他两种状态可以关机
        #     self.__masterMachine.Close()
        '''关机的时候是否要判断是否有还在运行的从控机？'''
        self.__adminService.stop_master_machine()
        self.__masterStart = False

    def OpenMenu(self):
        '''打开界面，但是否要把这个在views.py中实现？？？'''
        pass

    def SetMasterParam(self, tMode: int, temp_low_limit: int, temp_high_limit: int,
                       default_target_temp: int, default_speed: int, fee_rate: dict, targetFeq: int):
        '''设置主控机参数'''
        '''应该在服务中还能更改刷新频率!，同时有的参数数据类型有了修改'''
        pass
        self.__adminService.set_master_machine_param(tMode, temp_low_limit, temp_high_limit, default_target_temp,
                                                     default_speed, fee_rate, targetFeq)

    def GetSlavesStatus(self):
        '''获取所有从控机的状态'''
        return self.__adminService.get_status()

    def SetSlaveInfo(self, roomId: str, wind: int, temperature: int, startTime: datetime):
        '''更改从控机当前状态信息'''
        '''应该也可以由主控机从控机的状态？'''
        pass

    def SlaveSwitch(self, roomId: str, mode: str):
        '''更改从控机的开关状态'''
        '''可以由主控机开关从控机？'''
        pass

    def CheckIn(self, roomId: str):
        '''入住'''
        '''有些操作应该判断主控机是否开机，对于这种判断是放在controller还是service中？'''
        pass
        self.__adminService.check_in(roomId)

    def CheckOut(self, roomId: str):
        '''退房'''
        '''有些操作应该判断主控机是否开机，对于这种判断是放在controller还是service中？'''
        pass
        self.__adminService.check_out(roomId)


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
        self.__changeTempAndSpeedService = ChangeTempAndSpeedService.instance()
        self.__powerService=PowerService.instance()
        self.__getFeeService=GetFeeService.instance()
        self.__masterController = MasterController.instance()

    def CheckBill(self, roomId: str):
        '''从控机获取费用等信息'''
        return self.infoController.QueryInfo(roomId)

    def ChangeTemp(self, roomId: str, targetTemp: int):
        '''更改从控机温度'''
        if not self.__masterController.IsMasterStart():
            raise RuntimeError("主控机未开机")
        else:
            self.__changeTempAndSpeedService.change_temp(roomId, targetTemp)
    def ChangeSpeed(self,roomId:str,targetSpeed:int):
        '''更改从控机风速'''
        if not self.__masterController.IsMasterStart():
            raise RuntimeError("主控机未开机")
        else:
            self.__changeTempAndSpeedService.change_speed(self,targetSpeed)


    def SwitchOn(self, roomId: str):
        '''打开roomId从控机'''
        '''这里是设定成开机就是主控机默认温度更好吗？还是让传参设置初始温度？'''
        pass
        initTemp=20 #这个初始温度怎么得到？
        targetTemp,targetSpeed=self.__powerService.slave_machine_power_on(roomId,initTemp)
        return self.__changeTempAndSpeedService.init_temp_and_speed(roomId,targetTemp,targetSpeed)
    def SwitchOff(self, roomId: str):
        '''关闭roomId从控机'''
        self.__powerService.slave_machine_power_off(roomId)
    def GetFee(self,roomId:str):
        '''获取roomId房间的费用'''
        '''对于roomId是否合法的判断要放在service还是在controller？'''
        infoController = InfoController.instance()
        return infoController.GetFee(roomId)


    def ChangeTempMode(self, roomId: str, TargetMode: int):
        '''更改从控机温度模式'''
        '''按照要求从控机应该能更改自己的温度模式但是当模式与主控机不符时以主控机为准'''
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
        self.__getFeeService = GetFeeService.instance()
        self.__masterController = MasterController.instance()
        self.__detailService=DetailService.instance()
        self.__invoiceService=InvoiceService.instance()
        self.__reportService=ReportService.instance()
    def GetDetail(self,roomId:str):
        '''获得详单'''
        if not self.__masterController.IsMasterStart():
            raise RuntimeError("主控机未开机")
        else:
            return self.__detailService.get_detail(roomId)
    def PrintDetail(self,roomId):
        '''打印详单'''
        if not self.__masterController.IsMasterStart():
            raise RuntimeError("主控机未开机")
        else:
            return self.__detailService.print_detail(roomId)

    def GetFee(self, roomId: str):
        '''查询roomId房间中从控机的状态信息'''
        if not self.__masterController.IsMasterStart():
            raise RuntimeError("主控机未开机")
        else:
            return self.__getFeeService.get_current_fee(roomId)
    def GetInvoice(self,roomId:str):
        '''获取账单'''
        if not self.__masterController.IsMasterStart():
            raise RuntimeError("主控机未开机")
        else:
            return self.__invoiceService.get_invoice(roomId)
    def PrintInvoic(self,roomId):
        '''打印账单'''
        if not self.__masterController.IsMasterStart():
            raise RuntimeError("主控机未开机")
        else:
            return self.__invoiceService.print_invoice(roomId)
    def GetReport(self,roomId:str,qtype:str,date:datetime):
        '''获取报表'''
        if not self.__masterController.IsMasterStart():
            raise RuntimeError("主控机未开机")
        else:
            return self.__reportService.get_report(roomId,qtype,date)
    def PrintReport(self,roomId:str,qtype:str,date:datetime):
        '''打印报表'''
        if not self.__masterController.IsMasterStart():
            raise RuntimeError("主控机未开机")
        else:
            return self.__reportService.print_report(roomId,qtype,date)
class DespatcherController:
    '''管理调度队列的类'''
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls):
        '''支持多线程的单例模式'''
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):  # 获得锁后还要再判断一次是否在等待锁的时候创建了实例
                    cls._instance = cls()
        return cls._instance
