
from TemperatureController.controller import InfoController,MasterController
from TemperatureController.tools import logger
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render

# Create your views here.
#TODO:新加了一个total_energy
def query_invoice(request):
    room_id_get = request.GET.get('room_id')
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
    room_id_get = request.GET.get('room_id')
    if not room_id_get:
        logger.error('缺少参数:房间号')
        raise RuntimeError('缺少参数:房间号')
    try:
        controller = InfoController.instance()
        filename = controller.control(file_type='invoice', operation='print', room_id=room_id_get)
        print(filename)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
#TODO：新加了一个energy
def query_detail(request):
    room_id_get = request.GET.get('room_id')

    if not room_id_get:
        logger.error('缺少参数:房间号')
        raise RuntimeError('缺少参数:房间号')
    try:
        controller = InfoController.instance()
        content = controller.control(file_type='detail', operation='query', room_id=room_id_get)
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
        print(content)
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

def print_detail(request):
    room_id_get = request.GET.get('room_id')

    if not room_id_get:
        logger.error('缺少参数:房间号')
        raise RuntimeError('缺少参数:房间号')
    try:
        controller = InfoController.instance()
        filename = controller.control(file_type='detail', operation='print', room_id=room_id_get)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

def func(request):
    return render(request, 'reception/reception_invoice.html')

def bill(request):
    return render(request, 'reception/reception_bill.html')

def checkin(request):
    try:
        controller = MasterController.instance()
        #content = {'message': 'OK', 'result': controller.control(operation='get status')}
        content = controller.control(operation='get status')
        print(content)
        return render(request, 'reception/reception_checkin.html',locals())
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

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
