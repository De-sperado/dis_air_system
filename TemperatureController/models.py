from django.db import models

#详单类
class DetailModel(models.Model):

    detail_id = models.IntegerField(primary_key=True)
    room_id = models.CharField(max_length=16)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    speed = models.IntegerField()
    start_temp = models.FloatField()
    finish_temp = models.FloatField()
    fee_rate = models.FloatField()
    fee = models.FloatField()
    user_id = models.CharField(max_length=20)

#操作日志类
class Log(models.Model):

    room_id = models.CharField(max_length=16)
    operation = models.CharField(max_length=32)
    op_time = models.DateTimeField()
