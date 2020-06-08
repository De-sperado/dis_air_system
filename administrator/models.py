
from django import forms
# Create your models here.
class ParaForm(forms.Form):
    highest_temper = forms.CharField(label="最高温度", max_length=20,
                                         widget=forms.NumberInput(attrs={'class': 'form-control'}))
    lowest_temper = forms.CharField(label="最低温度", max_length=20,
                                        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    low_speed_fee = forms.CharField(label="低风速", max_length=20,
                                         widget=forms.NumberInput(attrs={'class': 'form-control'}))
    middle_speed_fee = forms.CharField(label="中风速", max_length=20,
                                        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    high_speed_fee = forms.CharField(label="高风速", max_length=20,
                                        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    default_temper = forms.CharField(label="默认温度", max_length=20,
                                           widget=forms.NumberInput(attrs={'class': 'form-control'}))
    default_speed = forms.CharField(label="默认风速", max_length=20,
                                        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    frequent = forms.CharField(label="频率", max_length=20,
                                           widget=forms.NumberInput(attrs={'class': 'form-control'}))
    mode = forms.CharField(label="模式", max_length=20,
                               widget=forms.NumberInput(attrs={'class': 'form-control'}))
