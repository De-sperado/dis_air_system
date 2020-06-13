from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from TemperatureController.controller import MasterController, SlaveController
from TemperatureController.tools import *
from .models import ParaForm
from threading import Timer

linkTimer = [0 for i in range(5)]  # 检测连接的计时器
linkedSlave = [False for i in range(5)]  # 标记从控机是否连接即投入使用
roomToIndex = {'309': 0, '310': 1, '311': 2, '312': 3, '313': 4}
indexToRoom = {0: '309', 1: '310', 2: '311', 3: '312', 4: '313'}
linkedNum = 0
linkThreshold = 5  # 连接超时时间为20s
linkBroken = [False for i in range(5)]
timerStart = False


def power_on(request):
    global timerStart
    global t
    if not timerStart:  # 若定时器没开启则开启定时器
        timerStart = True
        t.start()
    controller = MasterController.instance()
    controller.control(operation='turn on')
    content = {'message': 'OK', 'result': controller.control(
        operation='get main status')}
    return render(request, 'administrator/admin_MasterStatus.html', locals())


def set_param(request):
    controller = MasterController.instance()
    status = controller.control(operation='get main status')['status']
    if (status == '关机'):
        return HttpResponse("请先开机！")
    else:
        mode = request.POST.get('mode')
        default_temp = int(request.POST.get('default_temp'))
        frequency = int(request.POST.get('frequency'))
        try:
            controller.control(operation='set param', mode=mode,
                               default_temp=default_temp, frequency=frequency)
            return HttpResponse("Success")
        except RuntimeError as error:
            return HttpResponse("Failed:" + str(error))


def check_room_state(request):
    controller = MasterController.instance()
    try:
        content = controller.control(operation='get status')
        print(content)
        return render(request, 'administrator/admin_SlaversStatus.html', locals())
    except RuntimeError as error:
        content = {'result': controller.control(operation='get main status')}
        message = str(error)
        return render(request, 'administrator/admin_MasterStatus.html', locals())


# TODO:从这里获得主控的信息
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
        content = {'message': 'OK', 'result': controller.control(
            operation='get main status')}
        print(content)
        return render(request, 'administrator/admin_MasterStatus.html', locals())
    except RuntimeError as error:
        return render(request, '/login/login.html', {'message': str(error)})
        # return JsonResponse({'message': str(error)})


def close(request):
    controller = MasterController.instance()
    controller.control(operation='turn off')
    content = {'message': 'OK', 'result': controller.control(
        operation='get main status')}
    return render(request, 'administrator/admin_MasterStatus.html', locals())


def check_link_status():
    global linkedNum
    global linkTimer
    global linkedSlave
    global linkThreshold
    global linkBroken
    global t
    masterController=MasterController.instance()
    salveStatus=masterController.control(operation='get status')

    if linkedNum:  # 当有已连接的从机时执行这个操作
        for i in range(5):
            if linkedSlave[i]:
                linkTimer[i] += 1
                if linkTimer[i] > linkThreshold and salveStatus[i]['status']!=AVAILABLE and salveStatus[i]['status']!=CLOSED:
                    room_id = indexToRoom[i]
                    controller = SlaveController.instance()
                    controller.control(operation='power off', room_id=room_id)
                    linkedNum -= 1
                    linkedSlave[i] = False
                    linkBroken[i] = True

    t = Timer(1, check_link_status)
    t.start()



t = Timer(1, check_link_status)  # 计时器


def link(request):
    '''更新连接时间'''
    global linkTimer
    global linkedSlave
    global roomToIndexT
    global linkedNum
    global linkBroken
    room_id = request.POST.get('room_id')
    i = roomToIndex[room_id]
    if not linkedSlave[i]:
        linkedSlave[i] = True
        linkedNum += 1
    linkTimer[i] = 0  # 更新连接时间
    linkBroken[i] = 0
    return HttpResponse(str(room_id) + 'connecting.')


def check_link(request):
    global linkBroken
    global roomToIndex
    content = {"room_id": None, "linkBroken": 0}
    for i in range(5):
        if linkBroken[i] == True:
            print('i=', i, '\t', indexToRoom[i], '以断开连接')
            # slaveController=SlaveController.instance()
            # kwargs={'poweroff':'poweroff','roomid':indexToRoom[i]}
            # slaveController.control(poweroff='poweroff',room_id=indexToRoom[i])
            content["room_id"] = indexToRoom[i]
            content["linkBroken"] = 1
            linkBroken[i] = False  # 只弹窗一次
    return JsonResponse(content)
    # return render(request, 'administrator/admin_SlaversStatus.html', content)
