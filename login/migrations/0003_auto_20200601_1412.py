# Generated by Django 3.0.6 on 2020-06-01 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_auto_20200601_1345'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '客户',
                'verbose_name_plural': '客户',
                'ordering': ['c_time'],
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='position',
            field=models.CharField(choices=[('administrator', '系统管理员'), ('manager', '酒店经理'), ('templates', '前台')], default='客户', max_length=32),
        ),
    ]