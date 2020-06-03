import json
from django.shortcuts import render
from air_conditioner.controller import SlaveController
from air_conditioner.controller import MasterController
from _ast import operator
from django.http import JsonResponse


# Create your views here.

def check_in(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = MasterController.instance()
        controller.control(operation='check in', room_id=room_id_get)
        content = {'message': "OK", 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


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


def request_fee(request):
    room_id_get = request.GET.get('room_id')
    try:
        controller = SlaveController.instance()
        content = {'message': 'OK', 'result': controller.control(operation='get fee', room_id=room_id_get)}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
