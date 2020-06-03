# Generated by Django 3.0 on 2020-06-03 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DetailModel',
            fields=[
                ('detail_id', models.IntegerField(primary_key=True, serialize=False)),
                ('room_id', models.CharField(max_length=16)),
                ('start_time', models.DateTimeField()),
                ('finish_time', models.DateTimeField()),
                ('speed', models.IntegerField()),
                ('start_temp', models.FloatField()),
                ('finish_temp', models.FloatField()),
                ('fee_rate', models.FloatField()),
                ('fee', models.FloatField()),
                ('user_id', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.CharField(max_length=16)),
                ('operation', models.CharField(max_length=32)),
                ('op_time', models.DateTimeField()),
            ],
        ),
    ]
