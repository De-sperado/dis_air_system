from django.shortcuts import render
from django.http import JsonResponse,HttpResponse

from TemperatureController.controller import MasterController, SlaveController
from TemperatureController.tools import logger
from .models import ParaForm
from threading import Timer

linkTimer=[0 for i in range(5)] #检测连接的计时器
linkedSlave=[False for i in range(5)]   #标记从控机是否连接即投入使用
roomToIndex={'309':0,'310':1,'311':2,'312':3,'313':4}
linkedNum=0
linkThreshold=20    #连接超时时间为20s
timerStart=False

def power_on(request):
    global timerStart
    global t
    if not timerStart:  #若定时器没开启则开启定时器
        t.start()

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

def check_link():
    global linkedNum
    global  linkTimer
    global  linkedSlave
    global  linkThreshold
    global  t
    if linkedNum:   #当有已连接的从机时执行这个操作
        for i in range(5):
            if linkedSlave[i]:
                if linkTimer[i] > linkThreshold:
                    room_id = roomToIndex.keys()[i]
                    controller = SlaveController.instance()
                    controller.control(operation='power off', room_id=room_id)
                    linkedNum-=1
                    linkedSlave[i]=False
                    return render(request, 'administrator/admin_SlaveStatus.html', {'room_id':room_id, 'link_broken': true})

    t = Timer(1, check_link)
    t.start()

t=Timer(1,check_link)   #计时器

def update_link_timer(request):
    '''更新连接时间'''
    global linkTimer
    global linkedSlave
    global roomToIndex
    global linkedNum
    room_id=request.POST.get('room_id')
    i=roomToIndex[room_id]
    if not linkedSlave[i]:
        linkedSlave[i]=True
        linkedNum+=1
    linkTimer[i] = 0    #更新连接时间
