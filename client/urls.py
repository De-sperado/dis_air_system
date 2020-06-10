from django.conf.urls import url
from client import views

app_name = 'client'
urlpatterns = [
    url(r'^dashboard/(?P<room_id>\d+)', views.dashboard),
    url(r'^request_on/(?P<room_id>\d+)', views.request_on),
    #url(r'^param/(?P<room_id>\d+)', views.param),
    url(r'^get_status/(?P<room_id>\d+)', views.get_status),
    url(r'^on_off/(?P<room_id>\d+)', views.on_off),
    url(r'^request_off/(?P<room_id>\d+)', views.request_off),
    url(r'^change_temper', views.change_temper),
    url(r'^change_speed', views.change_speed),
    # url(r'^checkout/(?P<room_id>\d+)', views.checkout),
    url(r'^check_out/(?P<room_id>\d+)', views.check_out),
]
