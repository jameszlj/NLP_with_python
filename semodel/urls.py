from django.conf.urls import url
from semodel import views

urlpatterns = [
    url(r'^$', views.analyse, name='analyse'),
    url(r'^analyse/$', views.analyse, name='analyse'),
    url(r'^word_class_analyse$', views.word_class_analyse, name='word_class_analyse'),
    url(r'^name_entity_recognize$', views.name_entity_recognize, name='name_entity_recognize'),
    url(r'^dependency_parser$', views.dependency_parser, name='dependency_parser'),
]

"""
       url(r'^$', views.login, name='login'),
       url(r'^login/$', views.login, name='login'),
       url(r'^regist/$', views.regist, name='regist'),
       url(r'^index/$', views.index, name='index'),
       url(r'^logout/$', views.logout, name='logout'),
"""
