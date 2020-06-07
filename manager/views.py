import datetime
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from .models import ReportForm
from TemperatureController.controller import InfoController

from tools import logger

def func(request):
    report_form = ReportForm()
    return render(request,'manager/func.html',locals())

def query_report(request):
    #print("11111111")
    report_form = ReportForm(request.POST)
    if report_form.is_valid():
        qtype_get = report_form.cleaned_data['qtype']
        room_id_get = report_form.cleaned_data['room_id']
        date_get = report_form.cleaned_data['date']
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
    else:
        return render(request,'/users/manager/func/',{'error:': '请检查填写内容！'})

def print_report(request):
    #print("222222222")
    report_form = ReportForm(request.POST)
    if report_form.is_valid():
        qtype_get = report_form.cleaned_data['qtype']
        room_id_get = report_form.cleaned_data['room_id']
        date_get = report_form.cleaned_data['date']
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
    else:
        return render(request,'/users/manager/func/',{'error:': '请检查填写内容！'})

