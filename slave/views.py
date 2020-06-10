import json
from django.shortcuts import render
from TemperatureController.controller import SlaveController
from TemperatureController.controller import MasterController
from _ast import operator
from django.http import JsonResponse


# Create your views here.
#TODO：这里有修改 需要获取user_id  这个函数是前台调用的   不是用户调用的  应该换一下位置
def check_in(request):
    room_id_get = request.GET.get('room_id')
    user_id_get=request.GET.get('user_id')
    try:
        controller = MasterController.instance()
        controller.control(operation='check in', room_id=room_id_get,user_id=user_id_get)
        content = {'message': "OK", 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
#TODO:用户登录的部分 根据返回值 若成功 则跳转到房间的界面  若失败 则提示重新输入
'''
返回值的结构
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
'''
def login(request):
    room_id_get = request.GET.get('room_id')
    user_id_get=request.GET.get('user_id')
    try:
        controller = SlaveController.instance()
        content=controller.control(operation='login', room_id=room_id_get,user_id=user_id_get)
        content = {'message': "OK", 'result': content}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
#
def check_out(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = MasterController.instance()
        controller.control(operation='check out', room_id=room_id_get)
        content = {'message': "OK", 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def request_on(request):
    room_id_get = request.GET.get('room_id')
    current_temp_get = float(request.GET.get('current_temper'))
    try:
        controller = SlaveController.instance()
        content = controller.control(operation='power on', room_id=room_id_get,
                                     current_temp=current_temp_get)
        content = {'message': "OK", 'result': content}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def request_off(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = SlaveController.instance()
        controller.control(operation='power off', room_id=room_id_get)
        content = {'message': "OK", 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def change_temper(request):
    room_id_get = request.GET.get('room_id')
    target_temper_get = float(request.GET.get('target_temper'))
    try:
        controller = SlaveController.instance()
        controller.control(operation='change temp', room_id=room_id_get,
                           target_temp=target_temper_get)
        content = {'message': 'OK', 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def change_speed(request):
    room_id_get = request.GET.get('room_id')
    speed_get = int(request.GET.get('speed'))
    try:
        controller = SlaveController.instance()
        controller.control(operation='change speed', room_id=room_id_get, target_speed=speed_get)
        content = {'message': 'OK', 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

#TODO:这个函数返回该从控机所有的状态值
'''
格式
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
            'energy': room.energy
        }
'''
def get_status(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = SlaveController.instance()
        content = {'message': 'OK', 'result': controller.control(operation='get status', room_id=room_id_get)}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
