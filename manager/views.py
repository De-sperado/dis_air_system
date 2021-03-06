import datetime
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from .models import ReportForm
from TemperatureController.controller import InfoController

from TemperatureController.tools import logger

def func(request):
    return render(request,'manager/manager_report.html')

def query_report(request):
    qtype_get = request.GET.get('qtype')
    room_id_get = request.GET.get('room_id')
    date_get = request.GET.get('date')
    print(qtype_get,room_id_get,date_get)
    try:
        if (not qtype_get) or (not room_id_get) or (not date_get):
            logger.error('缺少参数报表类型，房间号或起始时间')
            raise RuntimeError('缺少参数报表类型，房间号或起始时间')
        date_get_sp = date_get.split("-")
        date_get_da = datetime.datetime(int(date_get_sp[0]), int(date_get_sp[1]), int(date_get_sp[2]))
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
                       'eneygy':content.energy,
                       'detail':content.details
                   }
                   }
        print(content)
        return JsonResponse(content)
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})


def print_report(request):
    qtype_get = request.GET.get('qtype')
    room_id_get = request.GET.get('room_id')
    date_get = request.GET.get('date')
    print(qtype_get,room_id_get,date_get)
    try:
        if (not qtype_get) or (not room_id_get) or (not date_get):
            logger.error('缺少参数报表类型，房间号或起始时间')
            raise RuntimeError('缺少参数报表类型，房间号或起始时间')
        date_get_sp = date_get.split("-")
        date_get_da = datetime.datetime(int(date_get_sp[0]), int(date_get_sp[1]), int(date_get_sp[2]))
        controller = InfoController.instance()
        filename = controller.control(file_type='report', operation='print',
                                     room_id=room_id_get, date=date_get_da,
                                     qtype=qtype_get)
        print(filename)
        file = open(filename, 'r')
        print(file)
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + filename + '"'
        return response
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
