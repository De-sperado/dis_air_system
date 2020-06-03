import threading
from TemperatureController.service import (
    AdministratorService,  DetailService,
    InvoiceService, ReportService, SlaverService)
from tools import logger

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
        self.__slaverService=SlaverService.instance()
        logger.info('初始化MasterController')

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

    def control(self, **kwargs):
        operation = kwargs.get('operation')
        if operation == 'turn on':
            self.__adminService.start_master_machine()
            self.__masterStart = True
        elif operation == 'power on':
            self.__adminService.init_master_machine()
        elif operation == 'set param':
            self.__adminService.set_master_machine_param(
                kwargs.get('mode'), kwargs.get('temp_low_limit'), kwargs.get('temp_high_limit'),
                kwargs.get('default_target_temp'), kwargs.get('default_speed'), kwargs.get('fee_rate'),
                kwargs.get('targetFeq')
            )
        elif operation == 'turn off':
            self.__adminService.stop_master_machine()
            self.__masterStart = False
        elif operation == 'get status':
            return self.__adminService.get_status()
        elif operation == 'check in':
            room_id = kwargs.get('room_id')
            user_id = kwargs.get('user_id')
            return self.__adminService.check_in(room_id, user_id)
        elif operation == 'check out':
            room_id = kwargs.get('room_id')
            return self.__adminService.check_out(room_id)
        elif operation == 'set status':
            pass
        else:
            logger.error('不支持的操作')
            raise RuntimeError('不支持的操作')


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
        self.__slaverService = SlaverService.instance()
        self.__masterController = MasterController.instance()
        logger.info('初始化SlaveController')

    def control(self, **kwargs):
        if not self.__masterController.IsMasterStart():
            logger.error('主控机未启动')
            raise RuntimeError('主控机未启动')
        operation = kwargs.get('operation')
        room_id = kwargs.get('room_id')
        if room_id is None:
            logger.error('缺少参数room_id')
            raise RuntimeError('缺少参数room_id')
        if operation == 'get fee':
            return self.__slaverService.get_current_fee(room_id)
        elif operation == 'change temp':
            target_temp = kwargs.get('target_temp')
            self.__slaverService.change_temp(room_id, target_temp)
        elif operation == 'change speed':
            target_speed = kwargs.get('target_speed')
            self.__slaverService.change_speed(room_id, target_speed)
        elif operation == 'power on':
            target_temp, speed = self.__slaverService.slave_machine_power_on(room_id)
            return self.__slaverService.init_temp_and_speed(room_id, target_temp, speed)
        elif operation == 'power off':
            self.__slaverService.slave_machine_power_off(room_id)
        elif operation == 'change mode':
            pass
        else:
            logger.error('不支持的操作')
            raise RuntimeError('不支持的操作')


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
        self.__masterController = MasterController.instance()
        logger.info('初始化InfoController')

    def control(self, **kwargs):
        if not self.__masterController.IsMasterStart():
            logger.error('主控机未启动')
            raise RuntimeError('主控机未启动')
        file_type = kwargs.get('file_type')
        operation = kwargs.get('operation')
        room_id = kwargs.get('room_id')
        if file_type == 'report':
            report_service = ReportService.instance()
            qtype = kwargs.get('qtype')
            date = kwargs.get('date')
            if operation == 'query':
                return report_service.get_report(room_id, qtype, date)
            elif operation == 'print':
                return report_service.print_report(room_id, qtype, date)
            else:
                logger.error('不支持的操作')
                raise RuntimeError('不支持的操作')
        elif file_type == 'detail':
            detail_service = DetailService.instance()
            if operation == 'query':
                return detail_service.get_detail(room_id)
            elif operation == 'print':
                return detail_service.print_detail(room_id)
            else:
                logger.error('不支持的操作')
                raise RuntimeError('不支持的操作')
        elif file_type == 'invoice':
            invoice_service = InvoiceService.instance()
            if operation == 'query':
                return invoice_service.get_invoice(room_id)
            elif operation == 'print':
                return invoice_service.print_invoice(room_id)
            else:
                logger.error('不支持的操作')
                raise RuntimeError('不支持的操作')
        else:
            logger.error('不支持的操作')
            raise RuntimeError('不支持的操作')


