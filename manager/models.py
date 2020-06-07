
from django import forms

class ReportForm(forms.Form):
    report_type = (
        ('year', '年'),
        ('month', '月'),
        ('week', '周'),
        ('day', '日'),
    )
    room = (
        ('309c', '309c'),
        ('310c', '310c'),
        ('311c', '311c'),
        ('312c', '312c'),
        ('f3', 'f3'),
    )

    qtype = forms.ChoiceField(label='报表类型', choices=report_type)
    room_id = forms.ChoiceField(label='房间号', choices=room)
    date = forms.CharField(label='起始时间', widget=forms.TextInput(attrs={'class': 'form-control'}))
