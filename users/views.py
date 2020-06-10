from django.shortcuts import render, redirect
from .models import *

# Create your views here.





def checkin(request):
    if request.method == "POST":
        checkin_form = ClientForm(request.POST)
        message = "请检查填写的内容！"
        if checkin_form.is_valid():  # 获取数据
            name = checkin_form.cleaned_data['name']
            identity = checkin_form.cleaned_data['identity']
            #position = checkin_form.cleaned_data['position']

            same_name_user = Client.objects.filter(name=name)
            if same_name_user:  # 用户名唯一
                message = '用户已经存在，请重新选择用户名！'
                return render(request, 'login/register.html', locals())
            # 当一切都OK的情况下，创建新用户

            new_user = Client.objects.create()
            new_user.name = name
            new_user.identity = identity


            new_user.save()
            return redirect('/login/')  # 自动跳转到登录页面
   #register_form = RegisterForm()
    return render(request,'users/reception/reception_checkin.html',locals())

