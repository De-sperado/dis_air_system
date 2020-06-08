import datetime
import time
from threading import Thread

from django.test import TestCase

from TemperatureController.controller import MasterController,SlaveController,InfoController
from TemperatureController.tools import *


class ControllerTest(TestCase):


    def test_api(self):
        # 取得控制器对象
        masterController = MasterController.instance()
        # 主机开机
        masterController.control(operation='turn on')
        # 参数初始化
        print(COOL)
        masterController.control(operation='set param',key='mode',value='制冷')
        masterController.control(operation='set param', key='temp', value='25')
        # 监视空调
        tools = masterController.control(operation='get status')
        print(tools)
        # 主机关机
        # masterController.control( operation='turn off')

        slaveController=SlaveController.instance()
        # 入住
        masterController.control(operation='check in', room_id='309c',user_id='shit')
        masterController.control(operation='check in', room_id='311c', user_id='hhh')
        masterController.control(operation='check in', room_id='310c', user_id='f3')
        masterController.control(operation='check in', room_id='312c', user_id='nn')
        # 房间开机
        slaveController.control(operation='login', room_id='309c', user_id='shit')
        slaveController.control(operation='login', room_id='311c', user_id='hhh')
        slaveController.control(operation='login', room_id='310c', user_id='f3')
        slaveController.control(operation='login', room_id='312c', user_id='nn')

        tools = slaveController.control(operation='power on', room_id='309c')
        tools = slaveController.control(operation='power on', room_id='311c')
        tools = slaveController.control(operation='power on', room_id='310c')
        tools = slaveController.control(operation='power on', room_id='312c')

        print(tools)
        time.sleep(10)
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
        tools = slaveController.control(operation='get status', room_id='309c')
        print(tools)
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

