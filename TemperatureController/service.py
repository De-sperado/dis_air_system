"""
服务类

除AirConditionerService外，均采用单例模式
"""
import datetime
import math
import threading
from typing import List, Tuple, Optional, Dict

from TemperatureController.models import DetailModel, Log
from .tools import *
from TemperatureController.entity import MasterMachine, Detail, Invoice, Report, Room


class RunningSlaver:
    """

    Attributes:
        __room: 房间
        __start_time: 服务开始时间
        __duration: 服务时长
        __waiting_time: 等待时长
        __target_speed: 目标风速
        __fee_rate: 费率
        __fee_since_start: 服务开始以来的费用
    """

    def __init__(self, room: Room, target_speed: int, fee_rate: float):
        """
        初始化空调服务

        Args:
            room: 房间
            target_speed: 目标风速
        """
        self.__room = room
        self.__start_time = ...  # type: datetime.datetime
        self.__duration = 0
        self.__waiting_time = 0
        self.__start_temp = room.current_temp
        self.__target_speed = target_speed
        self.__fee_rate = fee_rate
        self.__fee_rate_per_sec = fee_rate / 60
        self.__energy_rate_per_sec = self.__fee_rate_per_sec / 5
        self.__fee_since_start = 0.0
        self.__energy_since_start = 0.0
        logger.info('初始化RunningSlaver')

    @property
    def room(self):
        return self.__room

    @property
    def start_time(self):
        return self.__start_time

    @property
    def duration(self):
        return self.__duration

    @property
    def waiting_time(self):
        return self.__waiting_time

    @waiting_time.setter
    def waiting_time(self, waiting_time):
        self.__waiting_time = waiting_time

    @property
    def target_speed(self):
        return self.__target_speed

    @target_speed.setter
    def target_speed(self, target_speed):
        self.__target_speed = target_speed

    @property
    def fee_rate(self):
        return self.__fee_rate

    @fee_rate.setter
    def fee_rate(self, fee_rate):
        self.__fee_rate_per_sec = fee_rate / 60
        self.__fee_rate = fee_rate

    @property
    def fee_since_start(self):
        return self.__fee_since_start
    @property
    def energy_since_start(self):
        return self.__energy_since_start
    @property
    def start_temp(self):
        return self.__start_temp

    def start(self):
        """服务开始"""
        self.__duration = 0
        self.__fee_since_start = 0.0
        self.__energy_since_start=0.0
        self.__start_time = datetime.datetime.now()
        self.__start_temp = self.__room.current_temp
        self.__room.status = SERVING
        logger.info('房间' + self.room.room_id + '开始服务')

    def finish(self):
        """服务结束"""
        if self.start_time is not ...:
            detail = Detail(None, self.room.room_id, self.start_time, self.start_time +
                            datetime.timedelta(seconds=self.duration), self.target_speed,
                            self.fee_rate, self.start_temp, self.room.current_temp, self.fee_since_start,
                            self.room.user_id)
            DBFacade.exec(DetailModel.objects.create, room_id=detail.room_id, start_time=detail.start_time,
                          finish_time=detail.finish_time, speed=detail.target_speed,
                          fee_rate=detail.fee_rate, start_temp=self.start_temp, finish_temp=self.room.current_temp,
                          fee=detail.fee, user_id=self.room.user_id)
        self.__waiting_time = 0
        self.__duration = 0
        self.__start_time = ...
        logger.info('房间' + self.room.room_id + '停止服务')

    def update(self, mode):
        """更新正在运行的房间的状态"""
        if self.start_time is not ...:
            self.__duration += UPDATE_FREQUENCY
            self.__room.service_time += UPDATE_FREQUENCY
            self.__fee_since_start += self.__fee_rate_per_sec * UPDATE_FREQUENCY
            self.__room.fee += self.__fee_rate_per_sec * UPDATE_FREQUENCY
            self.__room.energy += self.__energy_rate_per_sec * UPDATE_FREQUENCY
            if mode == COOL:
                self.room.current_temp -= TEMPERATURE_CHANGE_RATE_PER_SEC[self.target_speed] * UPDATE_FREQUENCY
            else:
                self.room.current_temp += TEMPERATURE_CHANGE_RATE_PER_SEC[self.target_speed] * UPDATE_FREQUENCY
        else:
            self.__waiting_time += UPDATE_FREQUENCY


class SlaverQueue:
    """
    空调服务队列

    Attributes:
        __MAX_NUM: 最大服务对象数
        __queue: 服务队列
    """

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__MAX_NUM = MAX_QUEUE
        self.__queue = []
        self.__standy_queue = []
        logger.info('初始化SlaverQueue')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    @property
    def queue(self):
        return self.__queue

    @property
    def standy_queue(self):
        return self.__standy_queue

    def push(self, service: RunningSlaver):
        """
        将服务对象加入服务队列
        """
        if len(self.queue) < self.__MAX_NUM:
            self.queue.append(service)
            service.start()
        else:
            self.queue.append(service)

    def remove(self, room_id):
        """将指定房间的服务对象从服务队列中移除"""
        service = self.get_service(room_id)
        if service is not None:
            service.finish()
            self.queue.remove(service)
        service = self.get_standby_service(room_id)
        if service is not None:
            service.finish()
            self.standy_queue.remove(service)

    def update(self, mode) -> List[RunningSlaver]:
        """
        更新服务队列所有服务对象的状态

        Returns:
            到达目标温度的对象
        """
        reach_temp_services = []
        if len(self.queue) != 0:
            for service in self.queue:
                service.update(mode)
                if mode == COOL:
                    if service.room.current_temp - service.room.target_temp < 0.001:
                        reach_temp_services.append(service)
                else:
                    if service.room.current_temp - service.room.target_temp > 0.001:
                        reach_temp_services.append(service)
        temp=[]
        for service in self.standy_queue:
            # if service.room.current_temp < CURRENT_TEMP:
            #     service.room.current_temp += TARGET_STATUS_TEMP_CHANGE_RATE * UPDATE_FREQUENCY
            # else:
            #     service.room.current_temp -= TARGET_STATUS_TEMP_CHANGE_RATE * UPDATE_FREQUENCY
            if math.fabs(service.room.current_temp - service.room.target_temp) >= 1:
                self.push(service)
                temp.append(service)
        for _ in temp:
            self.standy_queue.remove(_)
        return reach_temp_services

    def dispatch(self):
        for i in range(0, min(MAX_QUEUE, len(self.queue))):
            q = self.queue[i]
            if q.start_time is ...:
                q.start()
        if len(self.queue) > MAX_QUEUE:
            if DISPATCH_METHOD=='RR' and self.queue[MAX_QUEUE].waiting_time > MAX_WAITING_TIME:
                service = self.queue[0]
                logger.info(service.room.room_id + '移出队列并加入队列尾')
                service.room.status=STANDBY
                service.finish()
                self.queue.remove(service)
                self.queue.append(service)
                logger.info(
                    '服务队列：' + self.queue[0].room.room_id + self.queue[1].room.room_id + self.queue[2].room.room_id)

    def get_service(self, room_id):
        for _ in self.__queue:
            if _.room.room_id == room_id:
                return _
        return None
    def get_standby_service(self,room_id):
        for _ in self.__standy_queue:
            if _.room.room_id == room_id:
                return _
        return None

class Dispatcher:
    __instance_lock = threading.Lock()

    def __init__(self):
        self.__slaver_queue = SlaverQueue.instance()
        self.__master_machine = MasterMachine.instance()
        self.timer = RepeatTimer(UPDATE_FREQUENCY, self._task)
        logger.info('初始化Dispatcher')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def _task(self):
        """周期定时任务"""
        reach_temp_services = self.__slaver_queue.update(self.__master_machine.mode)
        for service in reach_temp_services:
            self.__slaver_queue.remove(service.room.room_id)
            logger.info('房间' + service.room.room_id + '到达设定温度')
            service.room.status = STANDBY
            self.__slaver_queue.standy_queue.append(service)
        self.__slaver_queue.dispatch()
        if self.__master_machine.status == RUNNING and len(self.__slaver_queue.queue) == 0:
            self.__master_machine.status = STANDBY
        elif self.__master_machine.status == STANDBY and len(self.__slaver_queue.queue) > 0:
            self.__master_machine.status = RUNNING
        for room_id in room_ids:
            room=self.__master_machine.get_room(room_id)
            if (room.status==CLOSED  or room.status==STANDBY) and math.fabs(room.current_temp-CURRENT_TEMP)>0.01:
                temp=TARGET_STATUS_TEMP_CHANGE_RATE * UPDATE_FREQUENCY
                if room.current_temp < CURRENT_TEMP:
                    if room.current_temp +temp>CURRENT_TEMP:
                        room.current_temp=CURRENT_TEMP
                    else:
                        room.current_temp +=temp
                else:
                    if room.current_temp - temp < CURRENT_TEMP:
                        room.current_temp = CURRENT_TEMP
                    else:
                        room.current_temp -= temp


    def reset(self):
        self.timer.cancel()
        self.timer = RepeatTimer(UPDATE_FREQUENCY, self._task)


class SlaverService:
    """从控机服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        self.__slaver_queue = SlaverQueue.instance()
        self.__Dispatcher = Dispatcher.instance()
        logger.info('初始化PowerService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def get_current_status(self, room_id: str) -> Dict:
        """获取指定从机当前费用"""
        return self.__master_machine.get_slave_status(self.__master_machine.get_room(room_id))

    def login(self, room_id: str, user_id: str):
        room = self.__master_machine.get_room(room_id)
        if room.user_id == user_id:
            return {
                'message': 'OK',
                'user_id': user_id,
                'room_id': room_id
            }
        else:
            logger.error('房间号与用户不匹配')
            return {
                'message': 'ERROR'
            }

    def slave_machine_power_on(self, room_id: str) -> Tuple[float, int]:
        """
        开启指定从机

        Returns:
            要创建的服务的目标温度, 目标风速
        """
        room = self.__master_machine.get_room(room_id)
        if room.status == CLOSED:
            # 按照默认温度风速创建服务
            room.target_temp = self.__master_machine.default_target_temp
            room.current_speed = self.__master_machine.default_speed
            target_temp, speed = self.__master_machine.default_target_temp, self.__master_machine.default_speed
        elif room.status == STANDBY:
            # 按照先前温度和风速创建服务
            target_temp, speed = room.target_temp, room.current_speed
        else:
            logger.error('房间已开机或未入住')
            raise RuntimeError('房间已开机或入住')
        room.turn_on()
        DBFacade.exec(Log.objects.create, room_id=room_id, operation=POWER_ON,
                      op_time=datetime.datetime.now())
        return target_temp, speed

    def slave_machine_power_off(self, room_id):
        """关闭指定从机"""
        room = self.__master_machine.get_room(room_id)
        if room.status == CLOSED:
            logger.error('房间已关机')
            print(f'{room_id}已关机，无需关机')
            # raise RuntimeError('房间已关机')
        self.__slaver_queue.remove(room_id)
        room.turn_off()
        DBFacade.exec(Log.objects.create, room_id=room_id, operation=POWER_OFF,
                      op_time=datetime.datetime.now())

    def init_temp_and_speed(self, room_id: str, target_temp: float, target_speed: int):
        """
        开机时初始化服务

        Args:
            room_id: 房间号
            target_temp: 目标温度
            target_speed: 目标风速
        """
        room = self.__master_machine.get_room(room_id)
        room.target_temp = target_temp
        room.current_speed = target_speed
        service = RunningSlaver(room, target_speed, self.__master_machine.fee_rate[target_speed])
        if math.fabs(room.current_temp - room.target_temp) >= 1:
            self.__slaver_queue.push(service)
        else:
            self.__slaver_queue.standy_queue.append(service)
        logger.info('房间' + room.room_id + '初始化服务, 目标温度: ' + str(target_temp) + ', 风速: ' + str(target_speed))
        return self.__master_machine.get_slave_status(room)

    def change_temp(self, room_id: str, target_temp: float):
        """
        改变目标温度

        Args:
            room_id: 房间号
            target_temp: 目标温度
        """
        if not self.__master_machine.temp_low_limit <= target_temp <= self.__master_machine.temp_high_limit:
            logger.error('目标温度不合法')
            raise RuntimeError('目标温度不合法')
        
        room = self.__master_machine.get_room(room_id)
        if (target_temp>room.current_temp and self.__master_machine.mode==COOL) or (target_temp<room.current_temp and self.__master_machine.mode==HOT):
             return
        room.target_temp = target_temp
        DBFacade.exec(Log.objects.create, room_id=room_id, operation=CHANGE_TEMP,
                      op_time=datetime.datetime.now())
        logger.info('房间' + room_id + '改变目标温度为' + str(target_temp))

    def change_speed(self, room_id: str, target_speed: int):
        """
        改变目标风速

        Args:
            room_id: 房间号
            target_speed: 目标风速
        """
        if target_speed not in (LOW, NORMAL, HIGH):
            logger.error('目标风速不合法')
            raise RuntimeError('目标风速不合法')
        room = self.__master_machine.get_room(room_id)
        if room.status == CLOSED or room.status == AVAILABLE:
            logger.error('未入住或未开机')
            raise RuntimeError('未入住或未开机')
        room.current_speed = target_speed
        air_conditioner_service = self.__slaver_queue.get_service(room_id)
        if air_conditioner_service is not None:  # 在服务队列中
            self.__slaver_queue.remove(air_conditioner_service.room.room_id)
            air_conditioner_service.target_speed = target_speed
            air_conditioner_service.fee_rate = self.__master_machine.fee_rate[target_speed]
            self.__slaver_queue.dispatch()
            self.__slaver_queue.push(air_conditioner_service)
        air_conditioner_service = self.__slaver_queue.get_standby_service(room_id)
        if air_conditioner_service is not None:
            air_conditioner_service.target_speed = target_speed
            air_conditioner_service.fee_rate = self.__master_machine.fee_rate[target_speed]
        DBFacade.exec(Log.objects.create, room_id=room_id, operation=CHANGE_SPEED,
                      op_time=datetime.datetime.now())
        logger.info('房间' + room_id + '改变目标风速为' + str(target_speed))


class AdministratorService:
    """
    管理服务

    Attributes:
        __master_machine: 主控机的对象
    """

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = ...  # type: MasterMachine
        self.__slave_service=...
        logger.info('初始化AdministratorService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def init_master_machine(self) -> None:
        """初始化主控机"""

    def set_master_machine_param(self,mode:str,default_temp:int,frequency:int) -> None:
        """设置主控机参数"""

        if not TEMP_LIMT[mode][0] <= default_temp <= TEMP_LIMT[mode][1]:
            logger.error('目标温度不合法')
            raise RuntimeError('目标温度不合法')
        self.__master_machine.set_para(mode, default_temp,frequency)

    def start_master_machine(self):
        """
        启动主控机

        """
        self.__master_machine = MasterMachine.instance()
        Dispatcher.instance().timer.start()
        self.__master_machine.turn_on()
        self.__slave_service=SlaverService.instance()

    def stop_master_machine(self) -> None:
        """关闭主控机"""
        if self.__master_machine is ...:
            logger.error('主控机未初始化')
            raise RuntimeError('主控机未初始化')
        self.__master_machine.turn_off()
        for room_id in room_ids:
            SlaverQueue.instance().remove(room_id)
        Dispatcher.instance().reset()

    def get_status(self) -> List[dict]:
        """
        获取所有从机状态

        Returns:
            room_id: 房间号
            current_temper: 当前温度
            speed: 当前风速
            mode: 工作模式
            fee: 总费用
            fee_rate: 当前费率
            status: 房间状态
            service_time: 服务时长
            target_temper: 目标温度
        """
        if self.__master_machine is ...:
            logger.error('主控机未初始化')
            raise RuntimeError('主控机未初始化')
        return self.__master_machine.get_all_status()

    def get_main_status(self):
        if self.__master_machine is ...:
            return {'status':'关机',
                    'mode':'制冷',
                    'frequent':'1',
                    'default_temp':'22'}
        return self.__master_machine.get_main_status()

    def check_in(self, room_id: str, user_id: str):
        if self.__master_machine is ...:
            logger.error('主控机未初始化')
            raise RuntimeError('主控机未初始化')
        room=self.__master_machine.get_room(room_id)
        room.check_in(user_id)


    def check_out(self, room_id: str):
        if self.__master_machine is ...:
            logger.error('主控机未初始化')
            raise RuntimeError('主控机未初始化')
        self.__master_machine.get_room(room_id).check_out()


class DetailService:
    """详单服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        logger.info('初始化DetailService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def get_detail(self, room_id: str) -> List[Detail]:
        """获取详单"""
        return self.__master_machine.get_detail(room_id)[1]

    def print_detail(self, room_id: str) -> str:
        """打印详单"""
        check_in_time, details = self.__master_machine.get_detail(room_id)
        return Detail.get_detail_file(room_id, check_in_time, details)


class InvoiceService:
    """账单服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        logger.info('初始化InvoiceService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def get_invoice(self, room_id: str) -> Invoice:
        """获取账单"""
        return self.__master_machine.get_invoice(room_id)

    def print_invoice(self, room_id: str) -> str:
        """打印账单"""
        invoice = self.__master_machine.get_invoice(room_id)
        return Invoice.get_invoice_file(invoice)


class ReportService:
    """报表服务"""

    __instance_lock = threading.Lock()

    def __init__(self):
        self.__master_machine = MasterMachine.instance()
        logger.info('初始化ReportService')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def get_report(self, room_id: str, qtype: str, date: datetime.datetime) -> Report:
        """获取报表"""
        if qtype == 'day':
            start_time = datetime.datetime(date.year, date.month, date.day)
            finish_time = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)
        elif qtype == 'week':
            first_day = date - datetime.timedelta(days=date.weekday())
            last_day = date + datetime.timedelta(days=6 - date.weekday())
            start_time = datetime.datetime(first_day.year, first_day.month, first_day.day)
            finish_time = datetime.datetime(last_day.year, last_day.month, last_day.day, 23, 59, 59)
        elif qtype == 'month':
            start_time = datetime.datetime(date.year, date.month, 1)
            finish_time = datetime.datetime(date.year, date.month + 1, 1) - datetime.timedelta(days=1)
        elif qtype == 'year':
            start_time = datetime.datetime(date.year, 1, 1)
            finish_time = datetime.datetime(date.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            logger.error('不支持的qtype')
            raise RuntimeError('不支持的qtype')
        return self.__master_machine.get_report(room_id, start_time, finish_time)

    def print_report(self, room_id: str, qtype: str, date: datetime.datetime) -> str:
        """打印报表"""
        report = self.get_report(room_id, qtype, date)
        return Report.get_report_file(report)
