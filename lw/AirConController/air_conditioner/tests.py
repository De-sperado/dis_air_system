import datetime
import time
from threading import Thread

from django.test import TestCase

from air_conditioner.controller import MasterController,SlaveController,InfoController
from tools import working_mode, master_machine_status, room_status, logger, room_ids, operations, DBFacade, \
    current_temp, fan_speed


class ControllerTest(TestCase):


    def test_api(self):
        # 取得控制器对象
        masterController = MasterController.instance()
        # 主机开机
        masterController.control(operation='power on')
        # 参数初始化
        print(working_mode.COOL)
        masterController.control(operation='set param', mode=working_mode.COOL,
                           temp_low_limit=16, temp_high_limit=30, default_target_temp=24,
                           default_speed=fan_speed.NORMAL, fee_rate=(0.5, 0.75, 1.5), targetFeq=60)
        # 开始执行
        masterController.control(operation='turn on')
        # 监视空调
        room_status = masterController.control(operation='get status')
        print(room_status)
        # 主机关机
        # masterController.control( operation='turn off')

        slaveController=SlaveController.instance()
        # 入住
        masterController.control(operation='check in', room_id='309c',user_id='shit')
        masterController.control(operation='check in', room_id='311c', user_id='hhh')
        masterController.control(operation='check in', room_id='310c', user_id='f3')
        masterController.control(operation='check in', room_id='312c', user_id='nn')
        # 房间开机
        room_status = slaveController.control(operation='power on', room_id='309c', current_temp=25)
        room_status = slaveController.control(operation='power on', room_id='311c', current_temp=25)
        room_status = slaveController.control(operation='power on', room_id='310c', current_temp=25)
        room_status = slaveController.control(operation='power on', room_id='312c', current_temp=25)
        print(room_status)
        time.sleep(5)
        # 改变目标温度
        slaveController.control(operation='change temp', room_id='309c', target_temp=21)
        slaveController.control(operation='change temp', room_id='310c', target_temp=21)
        slaveController.control(operation='change temp', room_id='311c', target_temp=21)
        slaveController.control(operation='change temp', room_id='312c', target_temp=21)
        time.sleep(20)
        # 改变目标风速
        slaveController.control(operation='change speed', room_id='309c', target_speed=2)
        time.sleep(5)
        # 获取费用
        room_status = slaveController.control(operation='get fee', room_id='309c')
        print(room_status)
        # 房间关机
        slaveController.control(operation='power off', room_id='309c')
        # 退房
        masterController.control(operation='check out', room_id='309c')
        infoController=InfoController.instance()
        # 获取详单
        details = infoController.control(file_type='detail',operation='query', room_id='309c')
        print(details)
        # 打印详单
        filename = infoController.control(file_type='detail',operation='print', room_id='309c')
        print(filename)
        # 获取账单
        invoice = infoController.control(file_type='invoice', operation='query', room_id='309c')
        print(invoice)
        # 打印账单
        filename = infoController.control(file_type='invoice', operation='print', room_id='309c')
        print(filename)
        # 获取报表
        report = infoController.control(file_type='report', operation='query', room_id='309c',
                                    date=datetime.datetime.now(), qtype='day')
        print(report)
        filename = infoController.control(file_type='report', operation='print', room_id='309c',
                                      date=datetime.datetime.now(), qtype='day')
        print(filename)
        # 主机关机
        masterController.control(operation='turn off')

