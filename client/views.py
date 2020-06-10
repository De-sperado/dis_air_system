from django.shortcuts import render
from TemperatureController.controller import SlaveController
from TemperatureController.controller import MasterController
from _ast import operator
from django.http import JsonResponse,HttpResponse
import json

# Create your views here.


def check_out(request,room_id):
    try:
        controller1 = SlaveController.instance()
        controller2 = MasterController.instance()
        controller2.control(operation='check out', room_id=room_id)
        status = controller1.control(operation='get status', room_id=room_id)['status']
        return render(request, 'client/client_status.html', {'room_id': room_id, 'status': status})
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})





def request_on(request,room_id):
    try:
        controller = SlaveController.instance()
        content = controller.control(operation='power on', room_id=room_id)
        content = {'message': "OK", 'result': content}
        request.session[room_id] = True
        status = controller.control(operation='get status', room_id=room_id)['status']
        return render(request,'client/client_status.html',locals())
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

def request_off(request,room_id):
    try:
        controller = SlaveController.instance()
        controller.control(operation='power off', room_id=room_id)
        content = {'message': "OK", 'result': None}
        request.session[room_id] = False
        status = controller.control(operation='get status', room_id=room_id)['status']
        return render(request,'client/client_status.html',locals())
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
        return { 11
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
def get_status(request,room_id):
    try:
        controller = SlaveController.instance()
        content = controller.control(operation='get status', room_id=room_id)
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

def dashboard(request, room_id):
    try:
        controller = SlaveController.instance()
        content = controller.control(operation='get status', room_id=room_id)
        status = content['status']
        target_temp = content['target_temper']
        return render(request,'client/client_status.html',{'room_id':room_id,'status':status,'target_temp':target_temp})
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


'''def param(request, room_id):
    try:
        controller = SlaveController.instance()
        status = controller.control(operation='get status', room_id=room_id)['status']
        return render(request,'client/param.html', {'room_id': room_id,'status':status})
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
'''
