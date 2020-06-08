from django.conf.urls import url
from manager import views

urlpatterns = [
    url(r'^fun/',views.func),
    url(r'^query_report', views.query_report),
    url(r'^print_report', views.print_report),

]
