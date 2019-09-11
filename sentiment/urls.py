from django.conf.urls import url
from sentiment import views

urlpatterns = [
    url(r'^$', views.analyse, name='analyse'),
    url(r'^analyse/$', views.analyse, name='analyse'),
]

"""
       url(r'^$', views.login, name='login'),
       url(r'^login/$', views.login, name='login'),
       url(r'^regist/$', views.regist, name='regist'),
       url(r'^index/$', views.index, name='index'),
       url(r'^logout/$', views.logout, name='logout'),
"""
