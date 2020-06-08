from django.conf.urls import url
from client import views

app_name = 'client'
urlpatterns = [
    #url(r'^check_in', views.check_in),
    url(r'^dashboard', views.dashboard),
    url(r'^request_on', views.request_on),
    url(r'^param', views.request_on),
    url(r'^request_off', views.request_off),
    #url(r'^change_temper', views.change_temper),
    #url(r'^change_speed', views.change_speed),
    #url(r'^request_fee', views.request_fee),
    url(r'^check_out', views.check_out),
]
