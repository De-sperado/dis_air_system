from django.shortcuts import render
from django.http import JsonResponse,HttpResponse

from TemperatureController.controller import MasterController
from TemperatureController.tools import logger
from .models import ParaForm

#TODO:
def power_on(request):
    controller = MasterController.instance()
    controller.control(operation='turn on')
    content = {'message': 'OK', 'result': controller.control(operation='get main status')}
    return render(request,'administrator/admin_MasterStatus.html',locals())


#TODO:这个函数修改参数 传入参数key 和value   key可以为 mode temp frequent   value为目标值
def set_param(request):
    mode=request.POST.get('mode')
    default_temp=int(request.POST.get('default_temp'))
    frequency=int(request.POST.get('frequency'))
    print(mode,default_temp,frequency)
    try:
        controller = MasterController.instance()
        controller.control(operation='set param',mode=mode,default_temp=default_temp,frequency=frequency)
        return HttpResponse("Success")
    except RuntimeError as error:
        return HttpResponse("Failed:"+str(error))

#TODO：这个函数就没用了
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
