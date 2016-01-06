from django.conf.urls import patterns
from django.conf.urls import url

from hzrequestspanel.content import views
from hzrequestspanel.api import hzrequests_rest_api


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(hzrequests_rest_api.HZRequest.url_regex, hzrequests_rest_api.HZRequest.as_view(), name='createrequest'),
)
