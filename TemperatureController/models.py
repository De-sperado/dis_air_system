"""
持久化层

包含各持久化类
"""
from django.db import models


class DetailModel(models.Model):
    """详单"""

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


class LogModel(models.Model):
    """操作日志"""
    room_id = models.CharField(max_length=16)
    operation = models.CharField(max_length=32)
    op_time = models.DateTimeField()
