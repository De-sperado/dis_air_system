
from TemperatureController.controller import InfoController,MasterController
from TemperatureController.tools import logger
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render

# Create your views here.
#TODO:新加了一个total_energy
def query_invoice(request):
    if request.method == 'GET':
        return render(request, 'query_invoice.html')
    else:
        room_id_get = request.POST.get('room_id')
        if not room_id_get:
            logger.error('缺少参数:房间号')
            raise RuntimeError('缺少参数:房间号')
        try:
            controller = InfoController.instance()
            content = controller.control(file_type='invoice', operation='query', room_id=room_id_get)
            content = {'message': 'OK',
                       'result': {
                           'room_id': content.room_id,
                           'check_in_time': content.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                           'check_out_time': content.check_out_time.strftime('%Y-%m-%d %H:%M:%S'),
                           'fee': content.total_fee,
                           'user_id':content.user_id,
                           'energy':content.total_energy
                       }
                       }
            return JsonResponse(content)
        except RuntimeError as error:
            return JsonResponse({'message': str(error)})

def print_invoice(request):
    room_id_get = request.POST.get('room_id')
    if not room_id_get:
        logger.error('缺少参数:房间号')
        raise RuntimeError('缺少参数:房间号')
    try:
        controller = InfoController.instance()
        filename = controller.control(file_type='invoice', operation='print invoice', room_id=room_id_get)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
#TODO：新加了一个energy
def query_detail(request):
    if request.method == 'GET':
        return render(request,'query_detail.html')
    else:
        room_id_get = request.POST.get('room_id')

        if not room_id_get:
            logger.error('缺少参数:房间号')
            raise RuntimeError('缺少参数:房间号')
        try:
            controller = InfoController.instance()
            content = controller.control(service='detail', operation='query detail', room_id=room_id_get)
            content = {'message': 'OK',
                       'result': [
                           {
                               'room_id': c.room_id,
                               'start_time': c.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                               'finish_time': c.finish_time.strftime('%Y-%m-%d %H:%M:%S'),
                               'speed': c.target_speed,
                               'fee_rate': c.fee_rate,
                               'fee': round(c.fee, 2),
                               'start_temp':c.start_temp,
                               'finish_temp':c.finish_temp,
                               'energy':c.energy
                           }
                           for c in content
                       ]
                       }
            return JsonResponse(content)
        except RuntimeError as error:
            return JsonResponse({'message': str(error)})

def print_detail(request):
    room_id_get = request.POST.get('room_id')
    if not room_id_get:
        logger.error('缺少参数:房间号')
        raise RuntimeError('缺少参数:房间号')
    try:
        controller = InfoController.instance()
        filename = controller.control(file_type='detail', operation='print detail', room_id=room_id_get)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

def func(request):
    return render(request, 'reception/dashboard.html')

