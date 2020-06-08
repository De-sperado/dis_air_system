from django.shortcuts import render,redirect
from . import models
from .models import UserForm, RegisterForm, ClientForm
from users.models import Client
# Create your views here.
from TemperatureController.controller import SlaveController
from django.http import JsonResponse

def index(request):
    return render(request,'login/index.html')

def client_login(request):
    if request.method == "POST":
        login_form = ClientForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            user_id_get = login_form.cleaned_data['identity']
            room_id_get = login_form.cleaned_data['roomId']
            try:
                controller = SlaveController.instance()
                content = controller.control(operation='login', room_id=room_id_get, user_id=user_id_get)
                content = {'message': "OK", 'result': content}
                #redirect_to = '/users/client/func/'
                return render(request,'client/dashboard.html',locals())
            except RuntimeError as error:
                print("error了哦！")
                return render(request,'client/dashboard.html',locals())
            #xuyaogai!!!!!!!!!
            #!!!!!!!!!!!!!!!!!
        return render(request, 'login/client_login.html', locals())

    login_form = ClientForm()
    return render(request, 'login/client_login.html', locals())

'''def client_login1(request):
    print('1111111111111')
    if request.method == "POST":
        login_form = ClientForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            identity = login_form.cleaned_data['identity']
            roomId = login_form.cleaned_data['roomId']
            try:
                user = Client.objects.get(identity=identity)
                if user.roomId == roomId:
                    #request.session['is_login'] = True
                    request.session['user_id'] = user.identity
                    request.session['user_room'] = user.roomId
                    redirect_to = '/users/client/func/'
                    return redirect(redirect_to)
                else:
                    message = "身份证号或者房间号不正确！"

            except:
                message = "身份证号不存在！"
        return render(request, 'login/client_login.html', locals())

    login_form = ClientForm()
    return render(request, 'login/client_login.html', locals())
'''
def login(request):
    if request.session.get('is_login', None):
        #不允许重复登录
        return redirect('/index')

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            position = login_form.cleaned_data['position']
            try:
                user = models.User.objects.get(name=username)
                #print(user.position,position)
                if user.password == password and user.position == position:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    # return render(request, 'administrator/dashboard.html', locals())
                    redirect_to = '/users/' + user.position +'/fun/'
                    return redirect(redirect_to)
                else:
                    message = "密码或者职位不正确！"

            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/login/index/")


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/login/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            position = register_form.cleaned_data['position']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                # 当一切都OK的情况下，创建新用户

                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = password1
                new_user.position = position
                new_user.save()
                return redirect('/login/login/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())

