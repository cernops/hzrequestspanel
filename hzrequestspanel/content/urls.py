from django.conf.urls import url

from hzrequestspanel.content import views


urlpatterns = urls.patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
)
