"""实体类"""
import datetime
import json
import threading
from typing import List, Dict, Optional

from TemperatureController.models import DetailModel, Log
from .tools import *


class MasterMachine:
    """
    主控机

    Attributes:
        __mode:             工作模式
        __status:           工作状态
        __start_time:       开机时间，在start()方法里设置
        __temp_low_limit:   最低温度，在set_para()方法里设置
        __temp_high_limit:  最高温度，在set_para()方法里设置
        __default_target_temp: 默认温度
        __default_speed:     默认风速
        __fee_rate:         费率，tuple类型，对应每一级风速的费用
        __rooms:        房间列表
        __frequent:         刷新频率
    """

    __instance_lock = threading.Lock()

    def __init__(self):
        """初始化主控机"""
        self.__mode = COOL
        self.__status = CLOSED
        self.__start_time = None
        self.__finish_time = None
        self.__temp_low_limit = TEMP_LIMT[COOL][0]
        self.__temp_high_limit = TEMP_LIMT[COOL][1]
        self.__default_target_temp = 22
        self.__default_speed = 1
        self.__frequent = 1
        self.__fee_rate = (4, 5, 6)
        self.__rooms = []
        for _ in room_ids:
            self.__rooms.append(Room(_, self.default_target_temp, self.default_speed))
        logger.info('初始化主控机')

    @classmethod
    def instance(cls):
        """Singleton"""
        if not hasattr(cls, '_instance'):
            with cls.__instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls()
        return cls._instance

    def set_para(self, mode:str,default_temp:int,frequency:int) -> None:
        self.__mode=mode
        self.__default_target_temp=default_temp
        self.__frequent=frequency
        logger.info('修改主控机参数为:mode' + mode + ' default_temp=' + str(default_temp)+' frequency='+str(frequency))

    @property
    def mode(self):
        return self.__mode

    @property
    def status(self):
        return self.__status

    @property
    def start_time(self):
        return self.__start_time

    @property
    def temp_low_limit(self):
        return self.__temp_low_limit

    @status.setter
    def status(self, status):
        self.__status = status

    @property
    def temp_high_limit(self):
        return self.__temp_high_limit

    @property
    def default_target_temp(self):
        return self.__default_target_temp

    @property
    def default_speed(self):
        return self.__default_speed

    @property
    def fee_rate(self):
        return self.__fee_rate

    def get_room(self, room_id):
        if room_id not in room_ids:
            logger.error('房间号不存在')
            raise RuntimeError('房间号不存在')
        return self.__rooms[room_ids.index(room_id)]

    def turn_on(self) -> dict:
        """启动主控机"""
        self.__status = STANDBY
        self.__start_time = datetime.datetime.now()
        logger.info(str(self.__start_time) + ' 主控机启动')

    def turn_off(self) -> None:
        """关闭主控机"""
        self.__status = STOPPED
        self.__finish_time = datetime.datetime.now()
        for room in self.__rooms:
            room.status = CLOSED
        logger.info(str(self.__finish_time) + '主控机关机')

    def get_detail(self, room_id: str):
        """获取指定房间的详单"""
        room = self.get_room(room_id)

        details = DBFacade.exec(DetailModel.objects.filter, room_id=room_id, start_time__gte=room.check_in_time,
                                finish_time__lte=room.check_out_time)
        if not details:
            return room.check_in_time,[]
        return room.check_in_time, [
            Detail(d.detail_id, d.room_id, d.start_time, d.finish_time, d.speed, d.fee_rate, d.start_temp,
                   d.finish_temp,
                   d.fee, d.user_id) for d in details]

    def get_invoice(self, room_id: str):
        """获取指定房间的账单"""
        room = self.get_room(room_id)
        details = self.get_detail(room_id)[1]
        details.sort(key=lambda x: x.start_time)
        total_fee = 0
        user_id = details[0].user_id
        for detail in details:
            total_fee += detail.fee

        return Invoice(room_id, room.check_in_time, room.check_out_time, user_id, round(total_fee, 2))

    @staticmethod
    def get_report(room_id: str, start_time: datetime.datetime, finish_time: datetime.datetime):
        """获取指定房间的报表"""
        details = DBFacade.exec(DetailModel.objects.filter, room_id=room_id, start_time__gte=start_time,
                                finish_time__lte=finish_time)
        logs = DBFacade.exec(Log.objects.filter, room_id=room_id, op_time__gte=start_time, op_time__lte=finish_time)
        duration = 0
        fee = 0.0
        # 温控请求起止时间（列出所有记录）、温控请求的起止温度及风量消耗大小（列出所有记录）、每次温控请求所需费用、当日所需总费用
        dd = []
        for d in details:
            duration += (d.finish_time - d.start_time).seconds
            fee += d.fee
            dd.append([d.start_time, d.finish_time, d.start_temp, d.finish_temp, d.fee])
        on_off_times = 0
        temp_times = 0
        speed_times = 0
        for l in logs:
            on_off_times += 1 if l.operation == POWER_ON or l.operation == POWER_OFF else 0
            temp_times += 1 if l.operation == CHANGE_TEMP else 0
            speed_times += 1 if l.operation == CHANGE_SPEED else 0
        return Report(room_id, start_time, finish_time, duration, on_off_times,
                      temp_times, speed_times, len(details), round(fee, 2), dd,round(fee/5, 2))

    def get_main_status(self):
        return {
            'status': self.status,
            'mode': self.mode,
            'frequent': self.__frequent
        }

    def get_slave_status(self, room) -> Dict:
        """获取指定从机的状态"""
        mode = 0 if self.__mode == COOL else 1
        logger.debug('获取房间' + room.room_id + '状态')
        return {
            'room_id': room.room_id,
            'status': room.status,
            'mode': mode,
            'current_temper': round(room.current_temp, 2) if room.current_temp is not None else None,
            'speed': room.current_speed,
            'service_time': room.service_time,
            'target_temper': room.target_temp,
            'user_id': room.user_id,
            'fee': round(room.fee, 2),
            'fee_rate': self.__fee_rate[room.current_speed],
            'energy': round(room.energy, 2)
        }

    def get_all_status(self) -> List[dict]:
        """获取主机关联的所有从机的状态"""
        slave_status = []
        for room in self.__rooms:
            slave_status.append(self.get_slave_status(room))
        logger.info('获取所有从机状态')
        return slave_status


class Room:
    """
    房间

    Attributes:
        __room_id: 房间号
        __status: 房间状态
        __current_temp: 房间当前温度
        __current_speed: 房间当前风速
        __target_temp: 房间目标温度
        __fee: 房间当前费用
        __service_time: 房间服务时长
        __check_in_time: 入住时间
        __check_out_time: 退房时间
    """

    def __init__(self, room_id: str, target_temp: float, target_speed: int):
        """
        初始化房间

        Args:
            room_id: 房间号
            target_temp: 目标温度
            target_speed: 目标风速
        """
        self.__room_id = room_id
        self.__status = AVAILABLE
        self.__current_temp = CURRENT_TEMP
        self.__current_speed = target_speed
        self.__target_temp = target_temp
        self.__fee = 0
        self.__energy = 0
        self.__user_id = ""
        self.__service_time = 0
        self.__check_in_time = ...  # type: datetime.datetime
        self.__check_out_time = ...  # type: datetime.datetime
        logger.info('初始化房间' + room_id)

    @property
    def room_id(self):
        return self.__room_id

    @property
    def user_id(self):
        return self.__user_id

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    def check_in(self, user_id):
        """办理入住"""
        if self.__status != AVAILABLE:
            logger.error('该房间已经有客人入住')
            raise RuntimeError('该房间已经有客人入住')
        self.__status = CLOSED
        self.__fee = 0
        self.__energy = 0
        self.__service_time = 0
        self.__user_id = user_id
        self.__check_in_time = datetime.datetime.now()
        logger.info('房间' + self.__room_id + '用户' + self.__user_id + '入住')

    def turn_on(self):
        """开机"""
        self.__status = STANDBY
        logger.info('房间' + self.__room_id + '开机')

    def turn_off(self):
        """关机"""
        self.__status = CLOSED
        logger.info('房间' + self.__room_id + '关机')

    def check_out(self):
        """退房"""
        if self.__status != CLOSED:
            logger.error('需先关机才能退房')
            raise RuntimeError('需先关机才能退房')
        self.__status = AVAILABLE
        self.__user_id = ""
        self.__check_out_time = datetime.datetime.now()
        logger.info('房间' + self.__room_id + '退房')

    @property
    def current_temp(self):
        return self.__current_temp if self.__current_temp is not ... else None

    @current_temp.setter
    def current_temp(self, current_temp):
        self.__current_temp = current_temp

    @property
    def current_speed(self):
        return self.__current_speed

    @current_speed.setter
    def current_speed(self, current_speed):
        self.__current_speed = current_speed

    @property
    def target_temp(self):
        return self.__target_temp

    @target_temp.setter
    def target_temp(self, target_temp):
        self.__target_temp = target_temp

    @property
    def fee(self):
        return self.__fee

    @fee.setter
    def fee(self, fee):
        self.__fee = fee

    @property
    def energy(self):
        return self.__energy

    @energy.setter
    def energy(self, energy):
        self.__energy = energy

    @property
    def service_time(self):
        return self.__service_time

    @service_time.setter
    def service_time(self, service_time):
        self.__service_time = service_time

    @property
    def check_in_time(self):
        return self.__check_in_time

    @property
    def check_out_time(self):
        return self.__check_out_time


class Detail:
    """
    详单

    Attributes:
        __detail_id: 详单号
        __room_id: 房间号
        __start_time: 记录起始时间
        __finish_time: 记录结束时间
        __start_temp:开始温度
        __finish_temp:结束温度
        __target_speed: 目标风速
        __fee: 费用
    """

    def __init__(self, detail_id: Optional[int], room_id: str, start_time: datetime.datetime,
                 finish_time: datetime.datetime, target_speed: int, fee_rate: int, start_temp: float,
                 finish_temp: float, fee: float, user_id: str):
        """
        初始化详单

        新建Detail时，不需要传入detail_id
        从DetailModel创建Detail时，需传入detail_id

        Args:
            detail_id: 详单号
            room_id: 房间号
            start_time: 记录起始时间
            finish_time: 记录结束时间
            start_temp:开始温度
            finish_temp:结束温度
            target_speed: 目标风速
            fee: 费用
        """
        self.__detail_id = detail_id
        self.__room_id = room_id
        self.__start_time = start_time
        self.__finish_time = finish_time
        self.__target_speed = target_speed
        self.__fee_rate = fee_rate
        self.__start_temp = round(start_temp,2)
        self.__finish_temp = round(finish_temp,2)
        self.__fee = round(fee,2)
        self.__user_id = user_id
        self.__energy = round(fee/5, 2)
        if detail_id is not None:
            logger.info('读取详单' + str(self.__detail_id))
        else:
            logger.info('新建详单(room_id=' + str(self.__room_id) + ' start_time=' + str(self.__start_time) +
                        ' finish_time=' + str(self.__finish_time) + 'user_id=' + user_id)

    @property
    def detail_id(self):
        return self.__detail_id

    @property
    def fee_rate(self):
        return self.__fee_rate

    @property
    def room_id(self):
        return self.__room_id

    @property
    def user_id(self):
        return self.__user_id

    @property
    def start_time(self):
        return self.__start_time

    @property
    def finish_time(self):
        return self.__finish_time

    @property
    def target_speed(self):
        return self.__target_speed

    @property
    def start_temp(self):
        return self.__start_temp

    @property
    def finish_temp(self):
        return self.__finish_temp

    @property
    def fee(self):
        return self.__fee
    @property
    def energy(self):
        return self.__energy
    @staticmethod
    def get_detail_file(room_id, check_in_time, detail_list):

        detail_list.sort(key=lambda item: item.start_time)
        file_dict = {'房间号： ': str(room_id), 'detail': []}
        for detail in detail_list:
            file_dict['detail'].append(
                {
                    '开始时间': detail.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    '结束时间': detail.finish_time.strftime('%Y-%m-%d %H:%M:%S'),
                    '用户': detail.user_id,
                    '开始温度': str(detail.start_temp),
                    '结束温度': str(detail.finish_temp),
                    '风速': str(detail.target_speed),
                    '费率': str(detail.fee_rate),
                    '工作时长': str((detail.finish_time - detail.start_time).seconds),
                    '费用': str(round(detail.fee, 2)),
                    '风量消耗':str(round(detail.energy,2))
                }
            )
        filename = room_id + '-' + check_in_time.strftime('%Y%m%d%H%M%S') + '-detail.txt'

        with open(filename, 'w') as f:
            f.write('房间号:' + file_dict['房间号： ']+'\n')
            for i in range(len(file_dict['detail'])):
                f.write('\n')
                f.write('part' + str(i)+'\n')
                for k, v in file_dict['detail'][i].items():
                    f.write(k + ':' + str(v)+'\n')
        logger.info('保存详单文件' + filename)

        return filename


class Invoice:
    """
    账单

    Attributes:
        __room_id: 房间号
        __check_in_time: 入住时间
        __check_out_time: 退房时间
        __user_id:用户
        __total_fee: 总费用
    """

    def __init__(self, room_id, check_in_time, check_out_time, user_id, total_fee):
        """
        初始化账单

        新建Invoice时，不需要传入invoice_id
        从InvoiceModel创建Invoice时，需传入invoice_id

        Args:
            room_id: 房间号
            check_in_time: 入住时间
            check_out_time: 退房时间
            total_fee: 总费用
        """
        self.__room_id = room_id
        self.__check_in_time = check_in_time
        self.__check_out_time = check_out_time
        self.__total_fee = total_fee
        self.__user_id = user_id
        self.__total_energy = total_fee/5
        logger.info('新建账单(room_id=' + str(self.__room_id) + 'user_id=' + self.__user_id + ' check_in_time=' + str(
            self.__check_in_time) +
                    ' check_out_time=' + str(self.__check_out_time))

    @property
    def room_id(self):
        return self.__room_id

    @property
    def user_id(self):
        return self.__user_id

    @property
    def check_in_time(self):
        return self.__check_in_time

    @property
    def check_out_time(self):
        return self.__check_out_time

    @property
    def total_fee(self):
        return self.__total_fee
    @property
    def total_energy(self):
        return self.__total_energy
    def get_invoice_file(self):
        file_dict = {
            '房间号：': str(self.__room_id),
            '用户：': str(self.__user_id),
            '入住时间：': self.__check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
            '退房时间：': self.__check_out_time.strftime('%Y-%m-%d %H:%M:%S'),
            '费用：': str(round(self.__total_fee, 2)),
            '能量消耗':str(round(self.__total_energy, 2))
        }
        filename = self.__room_id + '-' + self.__check_in_time.strftime('%Y%m%d%H%M%S') + '-invoice.txt'
        """生成账单文件"""

        with open(filename, 'w') as f:
            for k, v in file_dict.items():
                f.write(k + str(v)+'\n')
        logger.info('保存账单文件' + filename)

        return filename


class Report:
    """
    报表

    Attributes:
        __room_id: 房间号
        __start_time: 起 始时间
        __finish_time: 终止时间
        __duration: 服务时长
        __times_of_on_off: 开关机次数
        __times_of_change_temp: 改变温度次数
        __times_of_change_speed: 改变风速次数
        __number_of_detail: 详单条目数
        __fee: 总费用
日报表结构和内容应至少包含：房间号、从控机开关机的次数、温控请求起止时间（列出所有记录）、温控请求的起止温度及风量消耗大小（列出所有记录）、
每次温控请求所需费用、当日所需总费用
    """

    def __init__(self, room_id, start_time, finish_time, duration, on_off_times,
                 temp_times, speed_times, n_details, fee, details,energy):
        """
        初始化报表

        Args:
            room_id: 房间号
            start_time: 起始时间
            finish_time: 终止时间
            duration: 服务时长
            on_off_times: 开关机次数
            temp_times: 改变温度次数
            speed_times: 改变风速次数
            n_details: 详单条目数
            fee: 总费用
        """
        self.__room_id = room_id
        self.__start_time = start_time
        self.__finish_time = finish_time
        self.__duration = duration
        self.__times_of_on_off = on_off_times
        self.__times_of_change_temp = temp_times
        self.__times_of_change_speed = speed_times
        self.__number_of_detail = n_details
        self.__details = details
        self.__fee = fee
        self.__energy=energy
        logger.info('新建报表(room_id=' + str(self.__room_id) + ' start_time=' + str(self.__start_time) +
                    ' finish_time=' + str(self.__finish_time))

    @property
    def room_id(self):
        return self.__room_id

    @property
    def start_time(self):
        return self.__start_time

    @property
    def finish_time(self):
        return self.__finish_time

    @property
    def duration(self):
        return self.__duration

    @property
    def on_off_times(self):
        return self.__times_of_on_off

    @property
    def details(self):
        return self.__details

    @property
    def temp_times(self):
        return self.__times_of_change_temp

    @property
    def speed_times(self):
        return self.__times_of_change_speed

    @property
    def n_details(self):
        return self.__number_of_detail

    @property
    def energy(self):
        return self.__energy

    @property
    def fee(self):
        return self.__fee

    def get_report_file(self):
        report_dict = {
            '房间号：': self.__room_id,
            '开始时间：': self.__start_time.strftime('%Y-%m-%d %H:%M:%S'),
            '结束时间： ': self.__finish_time.strftime('%Y-%m-%d %H:%M:%S'),
            '开关机次数：': str(self.__times_of_on_off),
            '温度更改次数：': str(self.__times_of_change_temp),
            '风速更改次数：': str(self.__times_of_change_speed),
            '包含详单个数：': str(self.__number_of_detail),
            '服务时间： ': str(self.__duration),
            '总费用：': str(round(self.__fee, 2)),
            '总能量：':str(round(self.__energy, 2))
        }
        filename = self.__room_id + '-' + self.__start_time.strftime('%Y%m%d%H%M%S') + '-report.txt'
        with open(filename, 'w') as f:
            for k, v in report_dict.items():
                f.write(k + str(v)+'\n')
            for _ in self.__details:
                print(' \n')
                f.write('开始时间：' + str(_[0])+'\n')
                f.write('结束时间：' + str(_[1])+'\n')
                f.write('开始温度：' + str(round(_[2],2))+'\n')
                f.write('结束温度：' + str(round(_[3],2))+'\n')
                f.write('此次能量消耗：' + str(round(_[4]/5, 2)) + '\n')
                f.write('此次服务费用：' + str(_[4])+'\n')
        logger.info('保存报表文件' + filename)
        return filename
