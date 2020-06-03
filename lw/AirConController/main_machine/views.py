from django.http import JsonResponse

from air_conditioner.controller import MasterController
from tools import logger


def power_on(request):
    try:
        controller = MasterController.instance()
        controller.control(operation='power on')
        content = {'message': 'OK', 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def init_param(request):
    highest_temper_get = float(request.GET.get('highest_temper'))
    lowest_temper_get = float(request.GET.get('lowest_temper'))
    low_speed_fee_get = float(request.GET.get('low_speed_fee'))
    middle_speed_fee_get = float(request.GET.get('middle_speed_fee'))
    high_speed_fee_get = float(request.GET.get('high_speed_fee'))
    default_temper_get = float(request.GET.get('default_temper'))
    default_speed_get = int(request.GET.get('default_speed'))
    frequent_get = int(request.GET.get('frequent'))
    mode_get = int(request.GET.get('mode'))
    if mode_get == 0:
        mode_get = "制冷"
    else:
        mode_get = "制热"

    try:
        controller = MasterController.instance()
        controller.control(operation='set param', mode=mode_get,
                            temp_low_limit=lowest_temper_get, temp_high_limit=highest_temper_get,
                            default_target_temp=default_temper_get,
                            default_speed=default_speed_get,
                            fee_rate=(low_speed_fee_get, middle_speed_fee_get, high_speed_fee_get),
                           targetFeq=frequent_get)
        content = {'message': "OK", 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def start_up(request):
    try:
        controller = MasterController.instance()
        controller.control( operation='turn on')
        content = {'message': 'OK', 'result': None}
        return JsonResponse(content, safe=False)
    except RuntimeError as error:
        logger.error(error)
        return JsonResponse({'message': str(error)})


def check_room_state(request):
    try:
        controller = MasterController.instance()
        content = {'message': 'OK', 'result': controller.control(operation='get status')}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def close(request):
    try:
        controller = MasterController.instance()
        controller.control( operation='turn off')
        content = {'message': 'OK', 'result': None}
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
