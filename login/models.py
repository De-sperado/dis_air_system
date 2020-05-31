from django.db import models
from django import forms
# Create your models here.


class User(models.Model):
    '''用户表'''

    character=(
        ('administrator','系统管理员'),
        ('manager','管理员'),
        ('reception','前台'),
        ('client','客户'),
    )

    name=models.CharField(max_length=128,unique=True)
    password=models.CharField(max_length=12)
    position=models.CharField(max_length=32,choices=character,default='客户')
    c_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'

class UserForm(forms.Form):
    character = (
        ('administrator', '系统管理员'),
        ('manager', '管理员'),
        ('reception', '前台'),
        ('client', '客户'),
    )
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=20, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    position = forms.ChoiceField(label='身份',choices=character)

class RegisterForm(forms.Form):
    character = (
        ('administrator', '系统管理员'),
        ('manager', '管理员'),
        ('reception', '前台'),
        ('client', '客户'),
    )

    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=20, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=20, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    position = forms.ChoiceField(label='身份',choices=character)