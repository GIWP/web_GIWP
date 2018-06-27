from django.conf.urls import url, include
from django.contrib import admin
from . import views
__author__ = 'Administrator'


urlpatterns = [
    url(r'^login/', views.login, name='login'),
    url(r'^register/', views.register, name='register'),
    url(r'^fail_login/', views.fail_login, name='fail_login'),
    url(r'^family/$', views.family, name='family'),
    url(r'^doctor/$',  views.doctor, name='doctor'),
    url(r'^doctor_info/$', views.doctor_info, name='doctor_info'), 
    url(r'^manage/', views.manage, name='manage'),
    url(r'^test/$', views.test, name='test'),
    url(r'choice/$',views.choice, name='choice'),
    url(r'appointment/$',views.appointment, name='appointment'),
    url(r'history/$',views.history, name='history'),
    url(r'doctor_view/$', views.doctor_view, name='doctor_view'),
    url(r'^$', views.home, name='home'),

    url(r'^thehomepage/$', views.search, name='search'),
    url(r'^result/$', views.searchlist, name='searchlist'),

]
