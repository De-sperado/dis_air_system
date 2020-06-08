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
from administrator import views

app_name = 'administrator'
urlpatterns = [
    url(r'^fun/',views.fun),
    url(r'^power_on', views.power_on),
    url(r'^init_param', views.init_param),
    #url(r'^start_up', views.start_up),
    url(r'^check_room_state', views.check_room_state),
    url(r'^close', views.close),
]
