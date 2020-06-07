from django.shortcuts import render,redirect
from django.http import JsonResponse

from TemperatureController.controller import MasterController
from tools import logger
from .models import ParaForm

# Create your views here.
def func(request):
    return render(request,'administrator/admin_func.html')

def power_on(request):
    try:
        controller = MasterController.instance()
        controller.control(operation='power on')
        para_form = ParaForm()
        return render(request,'administrator/init.html',locals())
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})

def init_param(request):
    if request.method == "POST":
        para_form = ParaForm(request.POST)
        if para_form.is_valid():
            highest_temper_get = float(para_form.cleaned_data['highest_temper'])
            lowest_temper_get = float(para_form.cleaned_data['lowest_temper'])
            low_speed_fee_get = float(para_form.cleaned_data['low_speed_fee'])
            middle_speed_fee_get = float(para_form.cleaned_data['middle_speed_fee'])
            high_speed_fee_get = float(para_form.cleaned_data['high_speed_fee'])
            default_temper_get = float(para_form.cleaned_data['default_temper'])
            default_speed_get = float(para_form.cleaned_data['default_speed'])
            frequent_get = float(para_form.cleaned_data['frequent'])
            mode_get = float(para_form.cleaned_data['mode'])
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
                request.session['is_on']=True
                #start_up的代码
                try:
                    controller = MasterController.instance()
                    controller.control(operation='turn on')
                    content = {'message': 'OK', 'result': None}
                    return JsonResponse(content, safe=False)
                except RuntimeError as error:
                    logger.error(error)
                    return JsonResponse({'message': str(error)})
                #return redirect('/users/administrator/func/')
            except RuntimeError as error:
                return JsonResponse({'message': str(error)})
        else:
            return render(request,'users/administrator/func/',{'message':'请检查输入内容！'})

'''def start_up(request):
    try:
        controller = MasterController.instance()
        controller.control( operation='turn on')
        content = {'message': 'OK', 'result': None}
        return JsonResponse(content, safe=False)
    except RuntimeError as error:
        logger.error(error)
        return JsonResponse({'message': str(error)})
'''

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
        #content = {'message': 'OK', 'result': None}
        request.session['is_on'] = False
        return redirect('/users/administrator/func/')
    except RuntimeError as error:
        return JsonResponse({'message': str(error)})
