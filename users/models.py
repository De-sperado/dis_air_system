from django.db import models
from django import forms
import django.utils.timezone as timezone



class Client(models.Model):
    '''客户表'''
    room = (
        ('309c', '309c'),
        ('310c', '310c'),
        ('311c', '311c'),
        ('312c', '312c'),
        ('f3', 'f3'),
    )
    identity = models.CharField(max_length=128, unique=True)
    roomId = models.CharField(max_length=128, choices=room, default='309c')
    name = models.CharField(max_length=20)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.roomId

    class Meta:
        ordering = ['c_time']
        verbose_name = '客户'
        verbose_name_plural = '客户'

'''class room(models.Model):
  

    roomId = models.CharField(max_length=10,unique=True)
    avail = models.BooleanField(default=True)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.roomId + ':' + str(self.avail)

    class Meta:
        ordering = ['c_time']
        verbose_name = '房间'
        verbose_name_plural = '房间'
'''
class ClientForm(forms.Form):

    identity = forms.CharField(label="身份证号", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(label="姓名",max_length=20,widget=forms.TextInput(attrs={'class': 'form-control'}))
    roomId = forms.CharField(label="房间号", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    #position = forms.ChoiceField(label='身份',choices=character)
