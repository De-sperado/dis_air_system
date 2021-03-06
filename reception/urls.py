"""new_软工 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from reception import views

app_name = 'reception'
urlpatterns = [
    url(r'^func/',views.func),
    url(r'^bill/',views.bill),
    url(r'^checkin/',views.checkin),
    url(r'^check_in/', views.check_in),
    url(r'^query_invoice', views.query_invoice),
    url(r'^print_invoice', views.print_invoice),
    url(r'^query_detail', views.query_detail),
    url(r'^print_detail', views.print_detail),
]
