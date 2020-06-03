import datetime

from django.http import JsonResponse, StreamingHttpResponse

from air_conditioner.controller import InfoController

from tools import logger


def query_report(request):
    qtype_get = request.GET.get('qtype')
    room_id_get = request.GET.get('room_id')
    # 传入的是起始时刻
    date_get = request.GET.get('date')
    if (not qtype_get) or (not room_id_get) or (not date_get):
        logger.error('缺少参数报表类型，房间号或起始时间')
        raise RuntimeError('缺少参数报表类型，房间号或起始时间')
    date_get_sp = date_get.split("-")
    date_get_da = datetime.datetime(int(date_get_sp[0]), int(date_get_sp[1]), int(date_get_sp[2]))
    try:
        controller = InfoController.instance()
        content = controller.control(file_type='report', operation='query',
                                     room_id=room_id_get, date=date_get_da,
                                     qtype=qtype_get)
        content = {'message': "OK",
                   'result': {
                       'room_id': content.room_id,
                       'start_time': content.start_time,
                       'finish_time': content.finish_time,
                       'on_off_times': content.on_off_times,
                       'service_time': content.duration,
                       'fee': content.fee,
                       'rdr_number': content.n_details,
                       'change_temp_times': content.temp_times,
                       'change_speed_times': content.speed_times,
                   }
                   }
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def print_report(request):
    qtype_get = request.GET.get('qtype')
    room_id_get = request.GET.get('room_id')
    date_get = request.GET.get('date')
    if (not qtype_get) or (not room_id_get) or (not date_get):
        logger.error('缺少参数报表类型，房间号或起始时间')
        raise RuntimeError('缺少参数报表类型，房间号或起始时间')
    date_get_sp = date_get.split("-")
    date_get_da = datetime.datetime(int(date_get_sp[0]), int(date_get_sp[1]), int(date_get_sp[2]))
    try:
        controller = InfoController.instance()
        filename = controller.control(file_type='report', operation='print', room_id=room_id_get, date=date_get_da,
                                      qtype=qtype_get)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


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
                       'user_id':content.user_id
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
        filename = controller.control(file_type='invoice', operation='print invoice', room_id=room_id_get)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def query_detail(request):
    room_id_get = request.GET.get('room_id')
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
                           'finish_temp':c.finish_temp
                       }
                       for c in content
                   ]
                   }
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
        filename = controller.control(file_type='detail', operation='print detail', room_id=room_id_get)
        file = open(filename, 'r')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
