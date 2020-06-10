from django import forms
# Create your models here.
class targetForm(forms.Form):
    room =(
        ('309', '309'),
        ('310', '310'),
        ('311', '311'),
        ('312', '312'),
        ('313', '313'),
     )
    room_id = forms.ChoiceField(label='房间号', choices=room)
    temper_speed = forms.CharField(label="目标温度/风速", max_length=20,
                                         widget=forms.NumberInput(attrs={'class': 'form-control'}))
    #speed = forms.CharField(label="目标速度", max_length=20,
                                       # widget=forms.NumberInput(attrs={'class': 'form-control'}))