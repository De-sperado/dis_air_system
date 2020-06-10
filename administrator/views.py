from django.shortcuts import render
from django.http import JsonResponse,HttpResponse

from TemperatureController.controller import MasterController
from TemperatureController.tools import logger
from .models import ParaForm

def power_on(request):
    controller = MasterController.instance()
    controller.control(operation='turn on')
    content = {'message': 'OK', 'result': controller.control(operation='get main status')}
    return render(request,'administrator/admin_MasterStatus.html',locals())


def set_param(request):
    mode=request.POST.get('mode')
    print(request.POST.get('default_temp'))
    default_temp=int(request.POST.get('default_temp'))
    frequency=int(request.POST.get('frequency'))
    print(mode,default_temp,frequency)
    try:
        controller = MasterController.instance()
        controller.control(operation='set param',mode=mode,default_temp=default_temp,frequency=frequency)
        return HttpResponse("Success")
    except RuntimeError as error:
        return HttpResponse("Failed:"+str(error))



def check_room_state(request):
    try:
        controller = MasterController.instance()
        #content = {'message': 'OK', 'result': controller.control(operation='get status')}
        content = controller.control(operation='get status')
        print(content)
        return render(request,'administrator/admin_SlaversStatus.html',locals())
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

#TODO:从这里获得主控的信息
'''
result为 {
            'status': self.status,
            'mode': self.mode,
            'frequent': self.__frequent
        }
'''
def fun(request):
    try:
        controller = MasterController.instance()
        content = {'message': 'OK', 'result': controller.control(operation='get main status')}
        print(content)
        return render(request,'administrator/admin_MasterStatus.html',locals())
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

def close(request):
    controller = MasterController.instance()
    controller.control( operation='turn off')
    content = {'message': 'OK', 'result': controller.control(operation='get main status')}
    return render(request, 'administrator/admin_MasterStatus.html', locals())
