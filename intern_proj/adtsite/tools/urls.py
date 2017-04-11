from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^result/(?P<job_id>\d+\_\w+)/$', views.query_result, name='result'),
    url(r'^download_rf/(?P<job_id>\d+\_\w+)/$', views.download_rf, name='download_rf'),
    url(r'^download_k/(?P<job_id>\d+\_\w+)/$', views.download_k, name='download_k'),
]
